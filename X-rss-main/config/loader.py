from pathlib import Path

import yaml

from config.schema import Config
from domain.models.account import Account


CONFIG_PATH = Path("config/config.yaml")

ACCOUNT_PATH = Path("accounts.yaml")


def load_config() -> Config:

    with open(CONFIG_PATH, encoding="utf8") as f:

        data = yaml.safe_load(f)

    return Config(**data)


def load_accounts() -> list[Account]:

    with open(ACCOUNT_PATH, encoding="utf8") as f:

        data = yaml.safe_load(f)

    return [Account(**item) for item in data["accounts"]]
