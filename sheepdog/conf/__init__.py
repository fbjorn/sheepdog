from dataclasses import dataclass
from pathlib import Path

import yaml
from schema import Regex, Schema

CONF_SCHEMA = {
    'polling_interval': int,
    'slow_threshold': int,
    'db_path': str,
    'host': str,
    'port': int,
    'log_file': str,
    'log_level': Regex(r'DEBUG|INFO|WARNING|ERROR'),
}


@dataclass
class Conf:
    polling_interval: int
    slow_threshold: int
    db_path: str
    host: str
    port: str
    log_file: str
    log_level: str

    @classmethod
    def load(cls, path=None):
        if path is None:
            path = Path(__file__).resolve().parent.parent.parent / 'config.yaml'
            path = path.as_posix()
        with open(path, 'r') as _conf:
            content = yaml.load(_conf)
        Schema(CONF_SCHEMA).validate(content)
        return cls(**content)
