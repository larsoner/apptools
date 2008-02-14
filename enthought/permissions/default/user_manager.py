#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought permissions package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from enthought.pyface.action.api import Action
from enthought.traits.api import Bool, Event, HasTraits, implements, \
        Instance, List, Unicode

# Local imports.
from enthought.permissions.i_user import IUser
from enthought.permissions.i_user_manager import IUserManager
from enthought.permissions.permission import ManageUsersPermission
from enthought.permissions.permissions_manager import PermissionsManager
from enthought.permissions.secure_proxy import SecureProxy
from i_user_database import IUserDatabase


class UserManager(HasTraits):
    """The default user manager implementation."""

    implements(IUserManager)

    #### 'IUserManager' interface #############################################

    management_actions = List(Instance(Action))

    user = Instance(IUser)

    user_actions = List(Instance(Action))

    user_authenticated = Event(IUser)

    #### 'UserManager' interface ##############################################

    # The user database.
    user_db = Instance(IUserDatabase)

    ###########################################################################
    # 'IUserManager' interface.
    ###########################################################################

    def bootstrapping(self):
        """Return True if we are bootstrapping, ie. no users have been defined.
        """

        return self.user_db.bootstrapping()

    def authenticate_user(self):
        """Authenticate the user."""

        if self.user_db.authenticate_user(self.user):
            self.user.authenticated = True

            # Tell the policy manager before everybody else.
            PermissionsManager.policy_manager.load_policy(self.user)

            self.user_authenticated = self.user

    def unauthenticate_user(self):
        """Unauthenticate the user."""

        if self.user.authenticated and self.user_db.unauthenticate_user(self.user):
            self.user.authenticated = False

            # Tell the policy manager before everybody else.
            PermissionsManager.policy_manager.load_policy(None)

            self.user_authenticated = None

    def matching_user(self, name):
        """Select a user."""

        return self.user_db.matching_user(name)

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _management_actions_default(self):
        """Return the list of management actions."""

        user_db = self.user_db
        actions = []
        perm = ManageUsersPermission()

        if user_db.can_add_user:
            act = Action(name="&Add a User...", on_perform=user_db.add_user)
            actions.append(SecureProxy(act, permissions=[perm], show=False))

        if user_db.can_modify_user:
            act = Action(name="&Modify a User...",
                    on_perform=user_db.modify_user)
            actions.append(SecureProxy(act, permissions=[perm], show=False))

        if user_db.can_delete_user:
            act = Action(name="&Delete a User...",
                    on_perform=user_db.delete_user)
            actions.append(SecureProxy(act, permissions=[perm], show=False))

        return actions

    def _user_actions_default(self):
        """Return the list of user actions."""

        actions = []

        if self.user_db.can_change_password:
            actions.append(_ChangePasswordAction())

        return actions

    def _user_default(self):
        """Return the default current user."""

        return self.user_db.user_factory()

    def _user_db_default(self):
        """Return the default user database."""

        # Defer to an external user database if there is one.
        try:
            from enthought.permissions.external.user_database import UserDatabase
        except ImportError:
            from enthought.permissions.default.user_database import UserDatabase

        return UserDatabase()


class _ChangePasswordAction(Action):
    """An action that allows the current user to change their password.  It
    isn't exported through actions/api.py because it is specific to this user
    manager implementation."""

    #### 'Action' interface ###################################################

    enabled = Bool(False)

    name = Unicode("&Change Password...")

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        super(_ChangePasswordAction, self).__init__(**traits)

        PermissionsManager.user_manager.on_trait_event(self._refresh_enabled, 'user_authenticated')

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        """Perform the action."""

        um = PermissionsManager.user_manager
        um.user_db.change_password(um.user)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _refresh_enabled(self, user):
        """Invoked whenever the current user's authorisation state changes."""

        self.enabled = user is not None
