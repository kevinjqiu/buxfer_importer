from invoke import task
from tangerine import TangerineClient
from rogersbank.client import RogersBankClient
from vault import vault_client


class VaultSecretProvider:
    def __init__(self, vault_client, secret_key):
        self._client = vault_client
        self._secret = self._client.read(secret_key)


    def get_username(self):
        return self._secret['data']['username']

    def get_password(self, phrase=None):
        return self._secret['data']['password']

    def get_security_challenge_answer(self, challenge):
        key = 'security_question/{}'.format(challenge)
        return self._secret['data'][key]


@task(pre=[vault_client])
def tangerine(ctx):
    ctx.tangerine_client = TangerineClient(VaultSecretProvider(ctx.vault_client, 'secret/tangerine'))


@task(pre=[vault_client])
def rogersbank(ctx):
    ctx.rogersbank_client = RogersBankClient(VaultSecretProvider(ctx.vault_client, 'secret/rogersbank'))
