import os
from pathlib import Path

import yaml

class PayloadLoader:
    _payloads = None

    @classmethod
    def load_payloads(cls, file_path=Path(os.getcwd(), "conf", "payloads.yaml")):
        """Load payloads from the YAML file."""
        if cls._payloads is None:
            with open(file_path, "r") as f:
                cls._payloads = yaml.safe_load(f)
        return cls._payloads

    @classmethod
    def get(cls, category, key):
        """Retrieve a specific payload."""
        payloads = cls.load_payloads()
        return payloads.get(category, {}).get(key)
