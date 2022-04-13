import sys
import os
import json

from PySide2 import QtWidgets, QtGui
from decimal import Decimal

from .gui import RESOURCE_DIR

FONT_FAMILY = None


class ProfileJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            i_val = int(obj)
            if i_val == obj:
                return i_val
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def as_json(obj):
    return json.dumps(
        obj,
        cls=ProfileJSONEncoder,
        indent=2,
        separators=(',', ': '))


def get_monospace_font():
    global FONT_FAMILY

    if not FONT_FAMILY:
        font_id = QtGui.QFontDatabase.addApplicationFont(
            os.path.join(RESOURCE_DIR, 'RobotoMono-Regular.ttf'))

        loaded_font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)

        FONT_FAMILY = loaded_font_family[0] if loaded_font_family else 'monospace'

    font = QtGui.QFont(FONT_FAMILY)
    font.setStyleHint(QtGui.QFont.TypeWriter)
    return font


def get_storage_dir():
    if sys.platform == 'win32':
        return os.path.join(os.path.expandvars('%APPDATA%'), 'dcs_preset_manager')
    return os.path.join(os.path.expanduser('~/.config'), 'dcs_preset_manager')


def error_dialog(msg):
    dlg = QtWidgets.QMessageBox()
    dlg.setIcon(QtWidgets.QMessageBox.Critical)
    dlg.setText(msg)

    font = get_monospace_font()
    dlg.setFont(font)

    dlg.setWindowTitle('Error')
    dlg.exec_()
