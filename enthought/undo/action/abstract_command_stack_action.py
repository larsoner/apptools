#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought undo package component>
#------------------------------------------------------------------------------


# Local imports.
from abstract_undo_action import AbstractUndoAction


class AbstractCommandStackAction(AbstractUndoAction):
    """ The abstract base class for all actions that operate on a command
    stack.
    """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """ Initialise the instance. """

        super(AbstractCommandStackAction, self).__init__(**traits)

        self.undo_manager.on_trait_event(self._on_stack_updated, 'stack_updated')

        # Update the action to initialise it.
        self._update_action()

    ###########################################################################
    # Protected interface.
    ###########################################################################

    def _update_action(self):
        """ Update the state of the action. """

        raise NotImplementedError

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _on_stack_updated(self, stack):
        """ Handle changes to the state of a command stack. """

        # Ignore unless it is the active stack.
        if stack is self.undo_manager.active_stack:
            self._update_action()
