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
from enthought.pyface.action.api import Action, Group, MenuManager
from enthought.pyface.workbench.api import WorkbenchWindow
from enthought.pyface.workbench.action.api import MenuBarManager
from enthought.pyface.workbench.action.api import ToolBarManager
from enthought.traits.api import Instance, on_trait_change
from enthought.undo.action.api import BeginRecordingAction
from enthought.undo.action.api import ClearRecordingAction, EndRecordingAction
from enthought.undo.action.api import CommandAction, RedoAction, UndoAction

# Local imports.
from example_editor_manager import ExampleEditorManager
from label import LabelIncrementSizeCommand
from label import LabelDecrementSizeCommand
from label import LabelNormalFontCommand
from label import LabelBoldFontCommand
from label import LabelItalicFontCommand


class ExampleUndoWindow(WorkbenchWindow):
    """ The ExampleUndoWindow class is a workbench window that contains example
    editors that demonstrate the use of the undo framework.
    """

    #### Private interface ####################################################

    # The action that exits the application.
    _exit_action = Instance(Action)

    # The File menu.
    _file_menu = Instance(MenuManager)

    # The Label menu.
    _label_menu = Instance(MenuManager)

    # The Undo menu.
    _undo_menu = Instance(MenuManager)

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait initialisers ###################################################

    def __file_menu_default(self):
        """ Trait initialiser. """

        return MenuManager(self._exit_action, name="&File")

    def __undo_menu_default(self):
        """ Trait initialiser. """

        undo_manager = self.workbench.undo_manager

        undo_group = Group(
                    UndoAction(undo_manager=undo_manager),
                    RedoAction(undo_manager=undo_manager)
                )

        script_group = Group(
                    BeginRecordingAction(undo_manager=undo_manager),
                    EndRecordingAction(undo_manager=undo_manager),
                    ClearRecordingAction(undo_manager=undo_manager)
                )

        return MenuManager(undo_group, script_group, name="&Undo")

    def __label_menu_default(self):
        """ Trait initialiser. """

        size_group = Group(CommandAction(command=LabelIncrementSizeCommand),
                           CommandAction(command=LabelDecrementSizeCommand))

        normal = CommandAction(id='normal', command=LabelNormalFontCommand,
                               style='radio', checked=True)
        bold = CommandAction(id='bold', command=LabelBoldFontCommand,
                             style='radio')
        italic = CommandAction(id='italic', command=LabelItalicFontCommand,
                               style='radio')

        style_group = Group(normal, bold, italic, id='style')

        return MenuManager(size_group, style_group, name="&Label")

    def __exit_action_default(self):
        """ Trait initialiser. """

        return Action(name="E&xit", on_perform=self.workbench.exit)

    def _editor_manager_default(self):
        """ Trait initialiser. """

        return ExampleEditorManager()
    
    def _menu_bar_manager_default(self):
        """ Trait initialiser. """

        return MenuBarManager(self._file_menu, self._undo_menu,
                self._label_menu, window=self)

    def _tool_bar_manager_default(self):
        """ Trait initialiser. """

        return ToolBarManager(self._exit_action, show_tool_names=False)

    # ZZZ: This is temporary until we put the script into a view.
    @on_trait_change('workbench.undo_manager.script_updated')
    def _on_script_updated(self, undo_manager):
        if str(undo_manager) == "<undefined>":
            return
            
        script = undo_manager.script

        if script:
            print script,
        else:
            print "Script empty"

    def _active_editor_changed(self, old, new):
        """ Trait handler. """

        # Tell the undo manager about the new command stack.
        if old is not None:
            old.command_stack.undo_manager.active_stack = None

        if new is not None:
            new.command_stack.undo_manager.active_stack = new.command_stack


        # Walk the label editor menu.
        for grp in self._label_menu.groups:
            for itm in grp.items:
                action = itm.action

                # Enable the action and set the command stack and data if there
                # is a new editor.
                if new is not None:
                    action.enabled = True
                    action.command_stack = new.command_stack
                    action.data = new.obj

                    # FIXME v3: We should just be able to check the menu option
                    # corresponding to the style trait - but that doesn't seem
                    # to uncheck the other options in the group.  Even then the
                    # first switch to another editor doesn't update the menus
                    # (though subsequent ones do).
                    if grp.id == 'style':
                        action.checked = (action.data.style == action.id)
                else:
                    action.enabled = False

#### EOF ######################################################################
