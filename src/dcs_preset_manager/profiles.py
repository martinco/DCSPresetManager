import os.path
import json

from .profile import Profile
from .utils import get_storage_dir, as_json
from . import logger

log = logger.get()


class Profiles(dict):
    """
    A container of profiles, just a dict of [profile_name] = <Profile>
    """

    def __init__(self):
        super().__init__()
        self._storage_dir = get_storage_dir()
        self._profiles_json = os.path.join(self._storage_dir, 'profiles.json')
        self.load_profiles()

    def add(self, profile):

        if not isinstance(profile, Profile):
            raise Exception('add requires a Profile')
        self[profile.name] = profile

    def load_profiles(self):

        log.debug('Loading profiles from %s', self._profiles_json)

        try:
            with open(self._profiles_json) as fh:
                profiles = json.load(fh)
        except IOError as e:
            log.error('IOError when loading profiles: %s', str(e))
            return
        except json.decoder.JSONDecodeError:
            log.error('JSON Decoding issue detected, resetting')
            profiles = {}

        for name, content in profiles.items():
            Profile(name, self, content)

    def as_json(self):
        return as_json(self)

    def save(self):
        """
        profiles are stored in %APPDATA% on windows or ~/.config
        """

        if not os.path.isdir(self._storage_dir):
            os.mkdir(self._storage_dir)

        with open(self._profiles_json, 'w') as fh:
            fh.write(self.as_json())
