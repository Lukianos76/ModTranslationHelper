import json
from pathlib import Path


class TranslatorAccount:
    def __init__(self, local_path: Path):
        self.__translator_accounts_path = local_path / 'translator accounts.json'
        if self.__translator_accounts_path.exists():
            with self.__translator_accounts_path.open(mode='r', encoding='utf-8-sig') as accounts:
                self.__translator_accounts = json.load(accounts)
        else:
            with self.__translator_accounts_path.open(mode='w') as accounts:
                self.__translator_accounts = {}
                json.dump(self.__translator_accounts, accounts, indent=4)

    def get_translator_account(self, translator_name) -> dict:
        return self.__translator_accounts.get(translator_name, {})

    def add_new_account(self, translator_name: str, **data):
        self.__translator_accounts[translator_name] = data

    def save_accounts(self):
        with self.__translator_accounts_path.open(mode='w', encoding='utf-8-sig') as accounts:
            json.dump(self.__translator_accounts, accounts, indent=4)
