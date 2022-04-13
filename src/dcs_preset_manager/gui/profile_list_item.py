from PySide2 import QtWidgets, QtCore


class ProfileListItem(QtWidgets.QListWidgetItem):

    def __init__(self, title, profile):
        super().__init__(title)

        # User Editable
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        self._profile = profile

    @property
    def profile(self):
        return self._profile
