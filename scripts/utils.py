import os
import yaml
import sys
from datetime import datetime


def load_config(conf_path):
    if os.path.isfile(conf_path):
        with open(conf_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        # If not a file, treat this as inline YAML string
        config = yaml.safe_load(conf_path)
    assert config is not None, "Failed to load configuration."
    return config


def log(s, label='INFO'):
    time_format = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sys.stdout.write(label + ' [' + time_format + '] ' + str(s) + '\n')
    sys.stdout.flush()
