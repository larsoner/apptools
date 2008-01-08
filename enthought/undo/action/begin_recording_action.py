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


# Enthought library imports.
from enthought.traits.api import Unicode

# Local imports.
from abstract_undo_action import AbstractUndoAction


class BeginRecordingAction(AbstractUndoAction):
    """ An action that starts the recording of commands to a script. """

    #### 'Action' interface ###################################################

    name = Unicode("Begin recording")

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        """ Perform the action. """

        self.undo_manager.begin_recording()
