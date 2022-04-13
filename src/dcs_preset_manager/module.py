import os.path

from .preset import Preset
from .extern import SLPP

from . import logger

log = logger.get()


class Module(dict):

    name = None

    dcs_types = []

    display_name = 'Missing display_name configuration'

    in_mission_dict = False

    # Some modules update preset 1 of one of the available radios
    # to match the group frequency, setting this to the radio offset
    # will update the group during the process to match the preset
    # of that radio to ensure validity against the expected presets
    group_radio_preset = None

    radios = []

    def __init__(self, data=None):
        """
        The initial data comes from defaults, this
        represents the data shown in the table, and
        what gets saved out into our profile data
        """

        super().__init__()

        # Public / Exportable Info
        self['managed'] = data['managed'] if data and 'managed' in data else False
        self['presets'] = []

        for radio_id, radio in enumerate(self.radios):
            radio_config = {
                'RED': [],
                'BLUE': [],
            }

            use_khz = radio.get('khz', False)

            for pst, defaults in enumerate(radio['defaults']):
                def_value, def_modulation = defaults

                for side in ['RED', 'BLUE']:
                    try:
                        preset = Preset(data['presets'][radio_id][side][pst], use_khz)
                    except (KeyError, TypeError):
                        preset = Preset({
                            'frequency': def_value,
                            'modulation': def_modulation
                        }, use_khz)

                    radio_config[side].append(preset)

            self['presets'].append(radio_config)

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, item))

    @property
    def managed(self):
        return self['managed']

    @managed.setter
    def managed(self, value):
        self['managed'] = value

    def get_module_dials(self, radio_idx, coalition):
        return {}

    def write_to_module(self, root, log_prefix, coalition, unit_type, unit_id):
        """
        Write the preset configuration to module, this is used
        to write to `Avionics/A-10C_2/1/VHF_AM_RADIO/SETTINGS.lua` etc.

        We need the unit_type as this varies in DCS
        """

        # Output SLPP helper
        slpp = SLPP()
        slpp.variable = 'settings'
        slpp.indent = '\t'

        # Loader / Validator Instance
        settings_slpp = SLPP()

        coalition = coalition.upper()

        # SETTINGS.lua is settings = {presets: { [1]: Hz }}
        root_dir = os.path.join(root, 'Avionics', unit_type, str(unit_id))

        updates = {
            'frequencies': 0,
            'units': 0,
            'dials': 0,
        }

        has_updates = False

        for radio_idx, radio in enumerate(self['presets']):

            target_dir_name = self.radios[radio_idx].get('target_directory')
            if not target_dir_name:
                continue

            target_dir = os.path.join(root_dir, target_dir_name)
            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)

            target_file = os.path.join(target_dir, 'SETTINGS.lua')

            # We only want to update if there are changes, which means checking the files
            try:
                with open(target_file) as fh:
                    current = settings_slpp.decode(fh.read())
            except FileNotFoundError:
                current = {}

            do_write = False

            # Find our dials and presets
            dials = self.get_module_dials(radio_idx, coalition)
            if current.get('dials', {}) != dials:
                updates['dials'] += 1
                do_write = True

            presets = {}
            for preset_idx, preset in enumerate(radio[coalition], 1):

                new_preset_value = int(preset.frequency * 1000000)
                old_preset_value = int(current.get('presets', {}).get(preset_idx, 0))

                if old_preset_value != new_preset_value:

                    log.info(
                        '%s Updating Preset %s from %s => %s',
                        log_prefix, preset_idx,
                        old_preset_value, new_preset_value)

                    updates['frequencies'] += 1
                    do_write = True

                presets[preset_idx] = new_preset_value

            if do_write:
                has_updates = True
                with open(target_file, 'w') as fh:
                    fh.write(slpp.encode({
                        'dials': dials,
                        'presets': presets}))

        if has_updates:
            updates['avionics'] = 1

        return updates

    def get_lua_dict(self, side):
        """
        Returns the LUA radio dictionary for the mission units
        """

        side = side.upper()

        if not self.in_mission_dict or not self['presets']:
            return None

        radio_dict = {}
        for radio_idx, radio in enumerate(self['presets']):
            modulations = {}
            channels = {}
            if side not in radio:
                continue

            for preset_idx, preset in enumerate(radio[side]):

                # If it's fully int, then make it so
                freq = int(preset['frequency'])
                if freq != preset['frequency']:
                    freq = preset['frequency']

                channels[preset_idx+1] = float(freq)
                modulations[preset_idx+1] = preset.modulation

            data = {
                'channels': channels,
                'modulations': modulations,
            }

            radio_dict[radio_idx+1] = data

        return radio_dict
