import multiprocessing
import tempfile
import zipfile
import os
import pickle

from PySide2 import QtCore
from .extern import SLPP
from . import logger

log = logger.get()


class MissionError(Exception):
    pass


class MissionSaveWorker(QtCore.QThread):

    done = QtCore.Signal(dict)

    def __init__(self, miz, profile, parent=None):
        super().__init__(parent)

        self._miz = miz
        self._profile = profile

    def run(self):
        try:
            result = apply_profile(self._miz, self._profile)
        except Exception as e:
            result = {
                'exception': str(e)
            }

        self.done.emit(result)


def apply_profile(miz, profile):

    if os.path.isdir(miz):
        return apply_profile_to_directory(miz, profile)

    if not miz.lower().endswith('.miz'):
        raise MissionError('Not a valid mission file')

    return apply_profile_to_miz(miz, profile)


def multiprocessing_slpp_worker(lua_dict_file, pipe):
    # Since we can't use shared memory, we use a pipe, and send back our json dict as
    # it's the decoding that causes all our lagging trouble under a thread

    try:
        slpp = SLPP()
        with open(lua_dict_file, 'r', encoding="utf-8") as fh:
            table = slpp.decode(fh.read())

        # We want the SLPP arguments too to rewrite in the same format
        retval = {
            'slpp': {
                'space_after_equals': slpp.space_after_equals,
                'variable': slpp.variable,
            },
            'table': table,
        }
    except Exception as e:
        retval = {
            'exception': str(e)
        }

    pipe.send(pickle.dumps(retval))
    pipe.close()


def apply_profile_to_directory(miz_dir, profile, original_file=None):
    """
    Process extracted directory, could be called by miz
    """

    def lookup_name(name):
        return dictionary.get(name, name)

    log.info('Applying %s to %s', profile.name, miz_dir)

    mission_file = os.path.join(miz_dir, 'mission')

    if not os.path.exists(mission_file):
        raise MissionError('Could not find mission file in the directory')

    dictionary = {}
    try:
        d = SLPP()
        with open(os.path.join(miz_dir, 'l10n', 'DEFAULT', 'dictionary')) as fh:
            dictionary = d.decode(fh.read())
    except Exception:  # noqa
        pass

    # Connection to get our data from child process
    parent_conn, child_conn = multiprocessing.Pipe()

    # Just spawn and let it do its thing
    p = multiprocessing.Process(target=multiprocessing_slpp_worker, args=(mission_file, child_conn,))
    p.start()
    mission_data = pickle.loads(parent_conn.recv())
    p.join()

    if 'exception' in mission_data:
        raise Exception(mission_data['exception'])

    # Rebuild our SLPP to maintain spacing / variable
    mission_slpp = SLPP()
    for key, value in mission_data['slpp'].items():
        setattr(mission_slpp, key, value)
    mission = mission_data['table']

    # Return some stats so we get an indication
    update_info = {
        'presets': 0,
        'modulations': 0,
        'units': 0,
        'groups': 0,
        'avionics': 0,
    }

    mission_update = False

    for coalition, co_data in mission.get('coalition', {}).items():
        for country_id, country_data in co_data.get('country', {}).items():
            for type_class in ['plane', 'helicopter']:
                groups = country_data.get(type_class, {}).get('group', {})
                for _, group_data in groups.items():

                    group_radio_set = False
                    group_name = lookup_name(group_data.get('name', 'Unknown Group'))

                    for _, unit_data in group_data.get('units', {}).items():

                        unit_id = unit_data.get('unitId')
                        unit_name = lookup_name(unit_data.get('name', 'Unknown Unit'))
                        unit_type = unit_data.get('type')

                        # Saves a lot of log duplication
                        # unit_str = blue:Group 1:Group 1-1 (F-14B, 124242)
                        unit_str = '%s:%s:%s (%s, %s)' % (
                            coalition.lower(),
                            group_name, unit_name,
                            unit_type, unit_id)

                        log.debug('%s - Starting processing', unit_str)

                        unit_skill = unit_data.get('skill')
                        if unit_skill != 'Client':
                            log.debug('%s - skill set to %s, must be Client', unit_str, unit_skill)
                            continue

                        updated_unit = False
                        config = profile.by_dcs_type(unit_type)

                        if not config:
                            log.warning(
                                '%s:%s - %s not supported',
                                coalition.lower(), group_name, unit_type)
                            continue

                        if not config.managed:
                            log.info('%s - Module set to non-managed', unit_type)
                            continue

                        if not config.in_mission_dict:
                            log.info('%s - Module not in mission dict, calling module writer', unit_str)
                            updates = config.write_to_module(miz_dir, unit_str, coalition, unit_type, unit_id)
                            for key, count in updates.items():
                                if key not in update_info:
                                    update_info[key] = 0
                                update_info[key] += count
                            continue

                        lua_dict = config.get_lua_dict(coalition)
                        if not lua_dict:
                            log.error(
                                '%s - Failed to get configuration',
                                unit_str,
                            )
                            continue

                        if (
                                config.group_radio_preset is not None
                                and not group_radio_set
                                and profile.update_groups):

                            # Radio to pull frequency from
                            group_freq_from_radio = config.group_radio_preset+1

                            new_group_freq = lua_dict[group_freq_from_radio]['channels'][1]
                            new_group_mod = lua_dict[group_freq_from_radio]['modulations'][1]

                            if (group_data['frequency'] != new_group_freq or
                                    group_data['modulation'] != new_group_mod):

                                log.info(
                                    '%s:%s (%s:%s) - Updating group frequency from %s => %s',
                                    coalition.lower(), group_name, unit_type, group_data.get('groupId'),
                                    group_data['frequency'], new_group_freq
                                )

                                group_data['frequency'] = new_group_freq
                                group_data['modulation'] = new_group_mod

                                # Mark us to write the mission file
                                update_info['groups'] += 1
                                mission_update = True

                        # Iterate over and update; as py3.6 dictionaries are insert-order maintained
                        # this helps keep them consistent with what we received and so if someone diffs, they get
                        # something useful out of it

                        for new_radio_idx, new_radio_presets in lua_dict.items():

                            current = unit_data['Radio'][new_radio_idx]

                            # Friendly name for logging
                            radio_name = config.radios[new_radio_idx-1]['heading']

                            for new_preset_idx, new_preset_val in new_radio_presets['channels'].items():

                                # If new preset val is an integer, use it
                                int_new_preset_val = int(new_preset_val)
                                if int_new_preset_val == new_preset_val:
                                    new_preset_val = int_new_preset_val

                                if current['channels'][new_preset_idx] != new_preset_val:

                                    log.info(
                                        '%s Updating Preset - %s %s from %s => %s',
                                        unit_str, radio_name, new_preset_idx,
                                        current['channels'][new_preset_idx], new_preset_val)

                                    current['channels'][new_preset_idx] = new_preset_val
                                    update_info['presets'] += 1
                                    updated_unit = True
                                else:
                                    log.debug(
                                        '%s No update for Preset %s %s  %s == %s',
                                        unit_str, radio_name, new_preset_idx,
                                        current['channels'][new_preset_idx], new_preset_val)

                            # We only need to do modulations if anything is non 0, or if modulations already exists and
                            # is non-empty in order to keep diffing civilised

                            new_mods = len([x for x in new_radio_presets['modulations'].values() if x != 0])
                            cur_mods = len(current['modulations']) if 'modulations' in current else 0

                            if not new_mods and cur_mods == 0:
                                log.debug('%s - No modulation updates required on %s', unit_str, radio_name)
                                continue

                            if not cur_mods:
                                log.info(
                                    '%s - Adding modulations for Radio %s',
                                    unit_str, radio_name,
                                )

                            if 'modulations' not in current:
                                current['modulations'] = {}

                            # As the insert order for radio was maintained, continue that in mods, so they're consistent
                            for new_mod_idx in current['channels']:
                                new_mod_val = new_radio_presets['modulations'][new_mod_idx]

                                if not cur_mods:
                                    current['modulations'][new_mod_idx] = new_mod_val
                                    updated_unit = True
                                    update_info['modulations'] += 1

                                    log.info(
                                        '%s - Updating modulation %s %s from UNSET => %s',
                                        unit_str, radio_name, new_mod_idx, new_mod_val)

                                elif (current['modulations'][new_mod_idx] !=
                                        new_radio_presets['modulations'][new_mod_idx]):

                                    log.info(
                                        '%s - Updating modulation %s %s from %s => %s',
                                        unit_str, radio_name, new_mod_idx,
                                        current['modulations'][new_mod_idx], new_mod_val)

                                    current['modulations'][new_mod_idx] = new_mod_val
                                    updated_unit = True
                                    update_info['modulations'] += 1

                        if updated_unit:
                            update_info['units'] += 1
                            mission_update = True

    if mission_update:
        with open(mission_file, 'w', encoding="utf-8") as fh:
            fh.write(mission_slpp.encode(mission))

    update_info_str = ', '.join(['%s:%s' % (k, v) for k, v in update_info.items()])

    log.info(
        'Finished applying %s to %s, updates: %s',
        profile.name,
        miz_dir if not original_file else original_file,
        update_info_str)

    return update_info


def apply_profile_to_miz(file, profile):
    """
    Extract the miz file, process, and re-zip
    """

    try:
        tmpdir = extract_miz(file)
    except Exception:
        raise MissionError('Unable to extract mission file')

    log.info('Extracted %s to %s', file, tmpdir.name)

    update_summary = apply_profile_to_directory(tmpdir.name, profile, file)

    # Backup the source, and zip it back up again
    bak_id = 1
    bak_file_prefix = '%s.bak' % file
    bak_file = bak_file_prefix
    while os.path.exists(bak_file):
        bak_file = '%s%s' % (bak_file_prefix, bak_id)
        bak_id += 1

    log.info('Backing up Mission file to %s', bak_file)
    os.rename(file, bak_file)

    # new_file = list(os.path.splitext(file))
    # new_file[0] += '-output'
    # new_file = ''.join(new_file)

    log.info('Rebuilding Mission file %s', file)
    create_miz(file, tmpdir.name)

    tmpdir.cleanup()
    return update_summary


def extract_miz(miz):

    tmpdir = tempfile.TemporaryDirectory()

    with zipfile.ZipFile(miz, 'r') as zh:
        zh.extractall(tmpdir.name)

    return tmpdir


def create_miz(target, base_dir):
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for dir_path, dir_names, filenames in os.walk(base_dir):
            for name in sorted(dir_names):
                path = os.path.join(dir_path, name)
                zf.write(path, os.path.relpath(path, base_dir))
            for name in filenames:
                path = os.path.normpath(os.path.join(dir_path, name))
                if os.path.isfile(path):
                    zf.write(path, os.path.relpath(path, base_dir))
