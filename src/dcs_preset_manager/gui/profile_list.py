import os
import json

from PySide2 import QtWidgets, QtSvg

from . import RESOURCE_DIR
from .profile_list_item import ProfileListItem
from ..profiles import Profile
from ..utils import error_dialog


class ProfileListLayout(QtWidgets.QVBoxLayout):

    def __init__(self, profiles):
        super().__init__()

        self._profiles = profiles

        group_box = QtWidgets.QGroupBox('Profiles')
        group_box.setMaximumWidth(300)
        self.addWidget(group_box)

        vlayout = QtWidgets.QVBoxLayout()
        group_box.setLayout(vlayout)

        # Where we select the active profile for the profile contents (right)
        self.profile_list = QtWidgets.QListWidget()
        self.profile_list.setMinimumWidth(150)
        self.profile_list.model().dataChanged.connect(self.on_profile_rename)  # noqa
        self.profile_list.currentItemChanged.connect(self.on_profile_selection_changed)
        vlayout.addWidget(self.profile_list)

        # Then we have some buttons
        profile_actions = QtWidgets.QWidget()
        vlayout.addWidget(profile_actions)

        profile_actions_layout = QtWidgets.QHBoxLayout()
        profile_actions_layout.setContentsMargins(0, 0, 0, 0)
        profile_actions.setLayout(profile_actions_layout)

        self._btn_profile_add = svg_button('plus.svg', 'Add new profile')
        self._btn_profile_add.clicked.connect(self.add_profile)
        profile_actions_layout.addWidget(self._btn_profile_add)

        self._btn_profile_trash = svg_button('trash-2.svg', 'Delete selected profile')
        self._btn_profile_trash.clicked.connect(self.del_profile)
        profile_actions_layout.addWidget(self._btn_profile_trash)

        self._btn_profile_copy = svg_button('copy.svg', 'Duplicate selected profile')
        self._btn_profile_copy.clicked.connect(self.clone_profile)
        profile_actions_layout.addWidget(self._btn_profile_copy)

        profile_actions_layout.addStretch()

        self._btn_profile_import = svg_button('upload.svg', 'Import profile from JSON')
        self._btn_profile_import.clicked.connect(self.handle_profile_import)
        profile_actions_layout.addWidget(self._btn_profile_import)

        self._btn_profile_export = svg_button('download.svg', 'Export selected profile')
        self._btn_profile_export.clicked.connect(self.handle_profile_export)
        self._btn_profile_export.setEnabled(False)
        profile_actions_layout.addWidget(self._btn_profile_export)

    def on_profile_selection_changed(self, itm):
        self._btn_profile_export.setEnabled(itm is not None)

    def populate(self):
        first = None
        for profile_name, profile in self._profiles.items():
            itm = ProfileListItem(profile_name, profile)
            self.profile_list.addItem(itm)
            if not first:
                first = itm

        if first:
            self.profile_list.setItemSelected(first, True)

    def current_profile(self):
        profiles = self.profile_list.selectedItems()
        if not profiles:
            return None

        return profiles[0].profile

    def add_profile(self, _):
        new_name = 'New Profile'
        i = 1
        while new_name in self._profiles:
            new_name = 'New Profile %i' % i
            i += 1

        profile = Profile(new_name, self._profiles)

        itm = ProfileListItem(profile.name, profile)
        self.profile_list.addItem(itm)
        self.profile_list.editItem(itm)
        self.profile_list.setItemSelected(itm, True)

    def clone_profile(self, _):
        itm = self.profile_list.selectedItems()
        if not itm:
            return
        itm = itm[0]

        name_prefix = '%s Copy' % itm.profile.name
        new_name = name_prefix
        i = 1
        while new_name in self._profiles:
            new_name = '%s %i' % (name_prefix, i)
            i += 1

        profile = itm.profile.clone(new_name)

        itm = ProfileListItem(profile.name, profile)
        self.profile_list.addItem(itm)
        self.profile_list.editItem(itm)
        self.profile_list.setItemSelected(itm, True)

    def del_profile(self, _):
        itm = self.profile_list.selectedItems()
        if not itm:
            return
        itm = itm[0]
        if itm.profile.name in self._profiles:
            del(self._profiles[itm.profile.name])
        self.profile_list.takeItem(self.profile_list.row(itm))

    def on_profile_rename(self, top_left, bottom_right):
        if top_left != bottom_right:
            return

        itm = self.profile_list.itemFromIndex(top_left)
        if not isinstance(itm, ProfileListItem):
            return

        new_title = itm.text().strip()
        if new_title != itm.text():
            # This will trigger this function again
            itm.setText(new_title)
            return

        if new_title == itm.profile.name:
            return

        if new_title in self._profiles:
            itm.setText(itm.profile.name)
            error_dialog('Profile names must be unique')
            return

        # Delete and Add under new name
        del self._profiles[itm.profile.name]
        itm.profile.name = new_title.strip()
        self._profiles[new_title] = itm.profile


    def handle_profile_import(self, _):
        load_fn, load_filter = QtWidgets.QFileDialog.getOpenFileName(
            filter='JSON (*.json)'
        )

        if not load_fn:
            return

        # Name prefix to file name
        name_prefix = 'Imported Profile'

        try:
            with open(load_fn) as fh:
                name_prefix = os.path.splitext(os.path.basename(fh.name))[0]
                data = json.load(fh)
        except Exception as e:
            error_dialog('Failed to load JSON: %s' % str(e))
            return

        # Get a non-conflicting name
        new_name = name_prefix
        i = 1
        while new_name in self._profiles:
            new_name = '%s %i' % (name_prefix, i)
            i += 1

        profile = Profile(new_name, self._profiles, data)

        itm = ProfileListItem(profile.name, profile)
        self.profile_list.addItem(itm)
        self.profile_list.editItem(itm)
        self.profile_list.setItemSelected(itm, True)


    def handle_profile_export(self, _):
        '''
        Export profile JSON to file
        '''

        profile = self.current_profile()

        if not profile:
            error_dialog('You must select a profile')
            return

        save_filename, selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            filter='JSON (*.json)'
        )

        if not save_filename:
            return

        with open(save_filename, 'w') as fh:
            fh.write(profile.as_json())


def svg_button(icon, tooltip):

    svg = QtSvg.QSvgWidget(os.path.join(RESOURCE_DIR, icon))

    layout = QtWidgets.QHBoxLayout()
    layout.setContentsMargins(7, 7, 7, 7)
    layout.addWidget(svg)

    btn = QtWidgets.QPushButton()
    btn.setLayout(layout)
    btn.setFixedSize(35, 35)
    btn.setToolTip(tooltip)

    return btn
