import os

from PySide2 import QtWidgets, QtCore, QtGui


from .. import __version__
from . import RESOURCE_DIR
from .profile_list import ProfileListLayout
from .preset_table_model import PresetTableModel
from ..module import Module
from ..utils import get_monospace_font, error_dialog
from ..mission import MissionSaveWorker
from ..spinner import Spinner
from .. import logger

log = logger.get()


class MainGuiWindow(QtWidgets.QWidget):

    def __init__(self, profiles):

        super().__init__()

        # Popup Spinner
        self._apply_thread = None
        self._apply_spinner = None

        # Selector Helpers
        self.current_profile = None
        self.current_module = None

        self._profiles = profiles
        self._settings = QtCore.QSettings('MartinCo', 'DCSRadioManager')

        # Main Window Layout
        self.setWindowTitle('DCS Radio Manager - v%s' % __version__)
        self.setWindowIcon(QtGui.QIcon(os.path.join(RESOURCE_DIR, 'icon.ico')))
        self.setMinimumSize(QtCore.QSize(1000, 500))

        # Profile Manager
        self._profile_list = ProfileListLayout(profiles)
        self._profile_list.profile_list.itemSelectionChanged.connect(self.handle_profile_change)
        self._profile_list.profile_list.itemChanged.connect(self.handle_changed)

        # Info Layout (No profiles)
        info_msg = QtWidgets.QLabel('Please select or create a new profile')
        info_msg.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.addWidget(info_msg)

        info_page = QtWidgets.QGroupBox('Information')
        info_page.setLayout(info_layout)

        #######################################################################
        # Presets Group: Module Dropdown, Manage Module, Radio Dropdown
        #######################################################################

        preset_grid_layout = QtWidgets.QGridLayout()

        label = QtWidgets.QLabel('Module')
        self._module_dropdown = QtWidgets.QComboBox()
        self._module_dropdown.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self._module_dropdown.currentIndexChanged.connect(self.handle_module_change)

        preset_grid_layout.addWidget(label, 0, 0)
        preset_grid_layout.addWidget(self._module_dropdown, 0, 1)

        # Manage Checkbox
        label = QtWidgets.QLabel('Manage module')
        label.setToolTip('When updating the mission file or directory, apply changes to this module')

        self._manage_check = QtWidgets.QCheckBox()
        self._manage_check.clicked.connect(self.handle_managed_check)
        self._manage_check.setToolTip('When updating the mission file or directory, apply changes to this module')

        preset_grid_layout.addWidget(label, 1, 0)
        preset_grid_layout.addWidget(self._manage_check, 1, 1)

        # Radio Dropdown
        label = QtWidgets.QLabel('Radio')
        self._radio_dropdown = QtWidgets.QComboBox()
        self._radio_dropdown.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self._radio_dropdown.currentIndexChanged.connect(self.handle_radio_change)
        self._radio_dropdown.setFont(get_monospace_font())

        preset_grid_layout.addWidget(label, 2, 0)
        preset_grid_layout.addWidget(self._radio_dropdown, 2, 1)

        # Presets Tabel
        self._table = QtWidgets.QTableView(self)
        self._table.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectItems)
        self._table.setCornerButtonEnabled(False)
        self._table.setSelectionMode(QtWidgets.QTableView.SelectionMode.SingleSelection)

        v_header = self._table.verticalHeader()
        v_header.setVisible(True)
        v_header.setSectionsClickable(False)
        v_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        v_header.setFont(get_monospace_font())

        h_header = self._table.horizontalHeader()
        h_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        h_header.setSectionsClickable(False)

        self._table.setStyleSheet(load_stylesheet())

        # Assemble Presets
        presets_vlayout = QtWidgets.QVBoxLayout()
        presets_vlayout.addLayout(preset_grid_layout)
        presets_vlayout.addWidget(self._table)

        presets_group = QtWidgets.QGroupBox("Presets")
        presets_group.setLayout(presets_vlayout)

        #######################################################################
        # Options Group
        #######################################################################

        self._set_group_chk = QtWidgets.QCheckBox('Set group frequency')
        self._set_group_chk.setToolTip(
            '<p>'
            'Some modules override preset 1 on the "primary" radio with the '
            'group\'s assigned frequency in the mission editor which may lead '
            'to confusion when referencing this master list.'
            '</p>'      
            '<p>Setting this option updates the group when updating the mission where possible</p>')
        self._set_group_chk.clicked.connect(self.handle_group_update_check)

        # Assemble Options
        options_layout = QtWidgets.QHBoxLayout()
        options_layout.addWidget(self._set_group_chk)

        options_group = QtWidgets.QGroupBox('Options')
        options_group.setLayout(options_layout)


        #######################################################################
        # Operations Group
        #######################################################################

        # Save, enabled / disabled based on changes
        self._btn_save = QtWidgets.QPushButton('Save')
        self._btn_save.setToolTip('Save changes to your profiles')
        self._btn_save.setEnabled(False)
        self._btn_save.clicked.connect(self.handle_save_profiles)

        # Directory Miz
        apply_to_miz = QtWidgets.QPushButton(text='Apply to MIZ')
        apply_to_miz.setToolTip(
            '<p>'
                'Select a MIZ file and apply the profile to it.<br><br>'
                'The existing MIZ file will be saved with ".bak" appended'
            '</p>')
        apply_to_miz.clicked.connect(self.apply_profile_miz)

        # Directory
        apply_to_dir = QtWidgets.QPushButton(text='Apply to DIR')
        apply_to_dir.setToolTip('Select a directory containing an extracted miz and apply the profile')
        apply_to_dir.clicked.connect(self.apply_profile_dir)

        # Assemble Operations
        operations_layout = QtWidgets.QHBoxLayout()
        operations_layout.addWidget(self._btn_save)
        operations_layout.addWidget(apply_to_miz)
        operations_layout.addWidget(apply_to_dir)

        operations_group = QtWidgets.QGroupBox('Operations')
        operations_group.setLayout(operations_layout)

        #######################################################################
        # Help Group
        #######################################################################

        github_button = QtWidgets.QPushButton("GitHub")
        github_button.setIcon(QtGui.QIcon(os.path.join(RESOURCE_DIR, 'github.svg')))
        github_button.clicked.connect(
            lambda x: QtGui.QDesktopServices.openUrl(
                QtCore.QUrl("https://github.com/martinco/DCSPresetManager/issues")))

        help_layout = QtWidgets.QHBoxLayout()
        help_layout.addWidget(github_button)

        help_group = QtWidgets.QGroupBox('Help')
        help_group.setLayout(help_layout)

        #######################################################################
        # Presets Layout Assembly
        #######################################################################

        # Assemble the Base Layout under a Widget to add to our stacked base_layout
        base_layout = QtWidgets.QHBoxLayout()
        base_layout.addWidget(options_group)
        base_layout.addWidget(operations_group)
        base_layout.addWidget(help_group)

        options_group.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        # Finally assemble our presets page
        presets_layout = QtWidgets.QVBoxLayout()
        presets_layout.addWidget(presets_group)
        presets_layout.addLayout(base_layout)

        presets_page = QtWidgets.QWidget()
        presets_page.setLayout(presets_layout)

        #######################################################################
        # Presentation Stack Assembly
        #######################################################################

        # Build our presentation stack
        self._content_stack = QtWidgets.QStackedLayout()
        self._content_stack.addWidget(info_page)
        self._content_stack.addWidget(presets_page)

        # Horizontal Main Layout (|Profiles|Contents|)
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self._profile_list)
        main_layout.addLayout(self._content_stack)

        self.setLayout(main_layout)

        #######################################################################
        # Setup Shortcuts / Actions
        #######################################################################

        # Save Shortcut
        save_action = QtWidgets.QAction(self)
        save_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_S))
        save_action.triggered.connect(self.handle_save_profiles)
        self.addAction(save_action)

        #######################################################################
        # Populate Data
        #######################################################################

        self._profile_list.populate()
        self.populate_modules()

        # Then add in our event listeners, we do this last so they don't trigger
        # the handlers during the populate above
        self._profile_list.profile_list.model().rowsInserted.connect(self.handle_changed)
        self._profile_list.profile_list.model().rowsRemoved.connect(self.handle_changed)

        # Restore any saved geometry / window position etc.
        self.restoreGeometry(self._settings.value('geometry', b''))  # noqa

    def populate_modules(self):
        for module in sorted(Module.__subclasses__(), key=lambda x: x.display_name):
            self._module_dropdown.addItem(module.display_name, module)

    def handle_changed(self, *_):
        self._btn_save.setEnabled(True)

    def handle_save_profiles(self):
        self._profiles.save()
        self._btn_save.setEnabled(False)

    def handle_managed_check(self, state):
        self._btn_save.setEnabled(True)
        self.current_module.managed = state

    def handle_group_update_check(self, state):
        self._btn_save.setEnabled(True)
        self.current_profile.update_groups = state

    def handle_module_change(self):
        module_cls = self._module_dropdown.currentData()
        if not module_cls:
            return

        profile = self._profile_list.current_profile()
        if not profile:
            return

        # Get our profile instance of the module
        self.current_module = profile.get_module(module_cls)

        # Update radio state
        self._manage_check.setChecked(self.current_module.managed)

        # Update group check
        self._set_group_chk.setChecked(self.current_profile.update_groups)

        # Reset radios dropdown
        self._radio_dropdown.clear()
        for radio in self.current_module.radios:
            self._radio_dropdown.addItem('%s: %s' % (radio['heading'], radio['description']))

    def handle_radio_change(self, index):
        module = self._module_dropdown.currentData()

        profile = self._profile_list.current_profile()
        if profile is None:
            return

        # Reload our table data model
        model = PresetTableModel(self, profile.get_module(module), index)
        model.dataChanged.connect(self.handle_changed)
        self._table.setModel(model)

    def handle_profile_change(self):
        # When we change profile, we have to regenerate our modules list
        # to instantiate
        self.current_profile = self._profile_list.current_profile()
        if self.current_profile is None:
            self._content_stack.setCurrentIndex(0)
            return

        # Show data entry items
        self._content_stack.setCurrentIndex(1)

        # Reload our data to the new profile
        self.handle_module_change()

    def handle_apply_done(self, update_summary):
        """
        Called by the handle_apply thread when it's completed / errored
        """

        self._apply_spinner.hide()
        self._apply_spinner.setParent(None)
        self._apply_spinner = None

        self._apply_thread.exit()

        if 'exception' in update_summary:
            log.error(update_summary['exception'])
            error_dialog('Failed to update mission data\n\n%s' % (update_summary['exception']))
            return

        # Format message
        msg = 'Successfully updated:\n'
        pad = max(len(x) for x in update_summary.keys())+1
        for key, value in update_summary.items():
            msg += ('  {key:{pad}} {value}\n'.format(
                key='%s:' % key,
                pad=pad,
                value=value,
            ))

        # Say all ok
        dlg = QtWidgets.QMessageBox()
        dlg.setIcon(QtWidgets.QMessageBox.Information)
        dlg.setText(msg)

        font = get_monospace_font()
        dlg.setFont(font)
        dlg.setWindowTitle('Saved')
        dlg.exec_()

    def handle_apply_finished(self):
        """
        This is called when the thread is finished, after the "done" event, so
        if we get here and the spinner is active, something went wrong, though
        not sure what
        """

        if self._apply_spinner:
            self._apply_spinner.hide()
            self._apply_spinner.setParent(None)
            self._apply_spinner = None

            error_dialog("Failed applying the mission data")

    def apply_profile(self, file):

        # We run the thread here, and wait for the response
        self._apply_thread = MissionSaveWorker(file, self._profile_list.current_profile())
        self._apply_thread.done.connect(self.handle_apply_done)
        self._apply_thread.finished.connect(self.handle_apply_finished)
        self._apply_thread.start()

        # Bring up the Spinner
        self._apply_spinner = Spinner(self)
        self._apply_spinner.move(0, 0)
        self._apply_spinner.resize(self.width(), self.height())
        self._apply_spinner.show()

    def apply_profile_miz(self):

        miz_file, selected_filter = QtWidgets.QFileDialog.getOpenFileName(
            filter='DCS Mission File (*.miz);')

        if not miz_file:
            return

        self.apply_profile(miz_file)

    def apply_profile_dir(self):

        miz_dir = QtWidgets.QFileDialog.getExistingDirectory()

        if not miz_dir:
            return

        self.apply_profile(miz_dir)

    def resizeEvent(self, _):
        if self._apply_spinner:
            self._apply_spinner.resize(self.width(), self.height())

    def closeEvent(self, evt):
        if self._btn_save.isEnabled():
            dlg = QtWidgets.QMessageBox()
            dlg.setIcon(QtWidgets.QMessageBox.Critical)
            dlg.setText('You have unsaved changes, do you wish to save before exiting?')
            dlg.setStandardButtons(
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
            ret = dlg.exec()

            if ret == QtWidgets.QMessageBox.Cancel:
                evt.ignore()
                return

            if ret == QtWidgets.QMessageBox.Save:
                self.handle_save()

        # Once we know the geometry we can save it in our settings under geometry
        self._settings.setValue('geometry', self.saveGeometry())

        evt.accept()


def load_stylesheet():
    with open(os.path.join(RESOURCE_DIR, 'table.stylesheet')) as fh:
        return fh.read()
