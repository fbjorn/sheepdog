from pathlib import Path
from threading import RLock
from uuid import uuid4

from yaml import dump, load

from sheepdog.database import errors


class KeyValueFileDatabase:
    _INITIAL_STATE = {}

    def __init__(self, filename: str, force_create: bool = True):
        path = Path(filename).resolve()
        if not path.exists():
            if force_create:
                with open(path, 'w') as db_file:
                    dump(self._INITIAL_STATE, db_file)
            else:
                raise errors.DatabaseFileDoesNotExist
        self.path = path
        self._lock = RLock()

    def _read_file(self):
        with self._lock:
            with open(self.path, 'r') as db_file:
                try:
                    return load(db_file.read())
                except Exception:
                    raise errors.DatabaseIsCorrupted

    def set(self, key: str, value):  # noqa
        with self._lock:
            content = self._read_file()
            content[key] = value
            with open(self.path, 'w') as db_file:
                dump(content, db_file)

    def get(self, key: str, default=None):
        value = self._read_file().get(key, None)
        if value is not None:
            return value
        elif value is None and default is not None:
            return default
        else:
            raise errors.KeyDoesNotExist

    @staticmethod
    def _generate_random_key():
        return str(uuid4())[:6]
