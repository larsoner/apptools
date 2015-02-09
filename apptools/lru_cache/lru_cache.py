# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# Copyright (c) 2015, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# The circular buffer implementation was backported from Python 3.4 and is
# provided under the PSF License available at
# https://docs.python.org/3.4/license.html
#
# Author: Enthought, Inc.
#------------------------------------------------------------------------------


from threading import RLock
import logging

from traits.api import Callable, Dict, Event, HasStrictTraits, Instance, Int, \
    List, Str

logger = logging.getLogger(__name__)


class LRUCache(HasStrictTraits):
    """ A least-recently used cache.

    Items older than `size()` accesses are dropped from the cache.

    This is ported from python 3's functools.lru_cache.

    """

    size = Int

    # Called with the key and value that was dropped from the cache
    cache_drop_callback = Callable

    # This event contains the set of cached cell keys whenever it changes
    updated = Event()

    _lock = Instance(RLock, args=())

    _cache = Dict
    _root = List

    _tag = Str("LRUCache")

    def __init__(self, size, **traits):
        self.size = size
        self._initialize_cache()
        super(LRUCache, self).__init__(**traits)

    def _initialize_cache(self):
        with self._lock:
            self._cache = {}
            # root of the circular doubly linked list
            self._root = []
            # initialize by pointing to self
            self._root[:] = [self._root, self._root, None, None]

    # -------------------------------------------------------------------------
    # LRUCache interface
    # -------------------------------------------------------------------------

    def __contains__(self, key):
        with self._lock:
            return key in self._cache

    def __len__(self):
        with self._lock:
            return len(self._cache)

    def __getitem__(self, key):
        PREV, NEXT = 0, 1   # names for the link fields
        # Size limited caching that tracks accesses by recency
        with self._lock:
            link = self._cache[key]
            if link is not None:
                # Move the link to the front of the circular queue
                link_prev, link_next, _key, result = link
                link_prev[NEXT] = link_next
                link_next[PREV] = link_prev
                last = self._root[PREV]
                last[NEXT] = self._root[PREV] = link
                link[PREV] = last
                link[NEXT] = self._root
                return result

    def __setitem__(self, key, result):
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3   # names for the link fields
        try:
            with self._lock:
                if len(self) == self.size:
                    # Use the old root to store the new key and result.
                    oldroot = self._root
                    oldroot[KEY] = key
                    oldroot[RESULT] = result
                    # Empty the oldest link and make it the new root.
                    # Keep a reference to the old key and old result to
                    # prevent their ref counts from going to zero during the
                    # update. That will prevent potentially arbitrary object
                    # clean-up code (i.e. __del__) from running while we're
                    # still adjusting the links.
                    self._root = oldroot[NEXT]
                    oldkey = self._root[KEY]
                    oldresult = self._root[RESULT]
                    self._root[KEY] = self._root[RESULT] = None
                    # Now update the cache dictionary.
                    del self._cache[oldkey]
                    if self.cache_drop_callback is not None and oldkey != key:
                        self.cache_drop_callback(oldkey, oldresult)
                    # Save the potentially reentrant cache[key] assignment
                    # for last, after the root and links have been put in
                    # a consistent state.
                    self._cache[key] = oldroot
                else:
                    # Put result in a new link at the front of the queue.
                    last = self._root[PREV]
                    link = [last, self._root, key, result]
                    last[NEXT] = self._root[PREV] = self._cache[key] = link
            return None
        finally:
            self.updated = self.keys()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        with self._lock:
            return [(key, link[3]) for key, link in self._cache.items()]

    def keys(self):
        items = self.items()
        return [k for k, v in items]

    def values(self):
        items = self.items()
        return [v for k, v in items]

    def clear(self):
        self._initialize_cache()
        self.updated = []