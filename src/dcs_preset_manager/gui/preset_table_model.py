import re

from decimal import Decimal
from PySide2.QtCore import QAbstractTableModel, Qt

from ..utils import error_dialog

RE_FREQ = re.compile(r'^(?P<exponent>[0-9]+)(?:\.(?P<mantissa>[0-9]{0,3}))?$')


class PresetTableModel(QAbstractTableModel):

    def __init__(self, parent, module, radio_index):
        super().__init__(parent)

        self._module = module
        self._radio_index = radio_index
        self._headers = ['BLUE', 'RED']

    def rowCount(self, parent=None):
        return len(self._module.radios[self._radio_index]['defaults'])

    def columnCount(self, parent=None):
        # Always 2 for BLUE / RED
        return 2

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False

        if not value:
            return False

        # validate the frequency format
        m = RE_FREQ.match(value)
        if not m:
            error_dialog('Please enter a valid frequency')
            return False

        mantissa = int((m.group('mantissa') or '0').ljust(3, '0'))

        f_val = Decimal(value)

        # Validate the value within range
        valid_range = None
        invalid_sep = None

        ranges = []
        for v_min, v_max, sep in self._module.radios[self._radio_index]['ranges']:
            if v_min <= f_val <= v_max:
                valid_range = '%7.03f - %7.03f' % (v_min, v_max)

                # We avoid floating point by doing this in integers
                if mantissa % (Decimal(str(sep))*1000) != 0:
                    print(mantissa, Decimal(str(sep))*1000)
                    invalid_sep = sep
                break

            ranges.append('%7.03f - %7.03f (separation: %.3f)' % (v_min, v_max, sep))

        if valid_range is None:
            error_dialog((
                'Invalid range for this radio, must be in the following '
                'range(s):\n\n  - ' + '\n  - '.join(ranges)))
            return False

        if invalid_sep is not None:
            error_dialog((
                'The frequency must have a separation of: %.03f in the range: '
                '%s' % (invalid_sep, valid_range)))
            return False

        current_pst = self._module['presets'][self._radio_index][self.headerTitle(index.column())][index.row()]
        if current_pst.frequency == f_val:
            return False

        current_pst.frequency = f_val

        # Emit dataChanged
        self.dataChanged.emit(index, index, [Qt.EditRole])

        # return true if successful
        return True

    def flags(self, index):
        if not index.isValid():
            return 0
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None

        try:
            return '%.03f' % (
                self._module['presets']
                [self._radio_index]
                [self._headers[index.column()]]
                [index.row()].frequency)
        except KeyError:
            return 0

    def headerTitle(self, col):  # noqa
        return self._headers[col]

    def headerData(self, col, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[col]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            try:
                return self._module.radios[self._radio_index]['channel_names'][col]
            except KeyError:
                pass
            return col+1
        return None
