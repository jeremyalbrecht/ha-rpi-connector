import os

import yaml
from pathlib import Path

def get_config():
    with open(Path(os.getcwd(), "conf", "default.yaml"), 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)
    return config