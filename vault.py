import os
import hvac
from invoke import task


@task
def vault_client(ctx):
    if not os.getenv('VAULT_TOKEN'):
        raise RuntimeError('VAULT_TOKEN must be set')

    ctx.vault_client = hvac.Client(ctx.vault.address, token=os.environ['VAULT_TOKEN'])
