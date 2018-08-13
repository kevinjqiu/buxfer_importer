import json
import datetime
import logging
import hvac
from banks import tangerine, rogersbank
from vault import vault_client
from invoke import task
from dateutil.relativedelta import relativedelta
from buxfer import Client as BuxferClient

FORMAT = '%(asctime)-15s [%(module)s:%(levelname)s] %(message)s'
logging.basicConfig(level='INFO', format=FORMAT)
logger = logging.getLogger(__name__)


def get_date_range():
    today = datetime.date.today()
    from_ = today - relativedelta(months=1)
    to_ = today + relativedelta(days=1)
    return from_, to_


@task(pre=[vault_client])
def buxfer(ctx):
    buxfer = ctx.vault_client.read('secret/buxfer')
    ctx.buxfer_client = BuxferClient(ctx.config.buxfer.api_base_url,
                                     buxfer['data']['username'], buxfer['data']['password'])


def import_tangerine(ctx, account_mappings, from_, to_):
    with ctx.tangerine_client.login():
        accounts = {
            account['number']: account
            for account in ctx.tangerine_client.list_accounts()
        }
        for mapping in account_mappings:
            ofx_account_id = mapping['ofx_account_id']
            buxfer_account_id = mapping['buxfer_account_id']
            logger.info('ofx_account_id: {} <-> buxfer_account_id: {}'.format(ofx_account_id, buxfer_account_id))
            account = accounts.get(ofx_account_id)
            if not account:
                continue

            content = ctx.tangerine_client.download_ofx(account, from_, to_, save=False)
            response = ctx.buxfer_client.upload_statement(buxfer_account_id, content)
            logger.info(response)


def import_rogersbank(ctx, account_mappings, from_, to_):
    with ctx.rogersbank_client.login():
        content = ctx.rogersbank_client.download_statement('00', save=False)

    for mapping in account_mappings:
        ofx_account_id = mapping['ofx_account_id']
        buxfer_account_id = mapping['buxfer_account_id']
        logger.info('ofx_account_id: {} <-> buxfer_account_id: {}'.format(ofx_account_id, buxfer_account_id))

        response = ctx.buxfer_client.upload_statement(buxfer_account_id, content)
        logger.info(response)


@task(name='import', pre=[buxfer, tangerine, rogersbank])
def import_all(ctx, start_date=None, end_date=None):
    ctx.buxfer_client.login()
    if start_date and end_date:
        from_ = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        to_ = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        from_, to_ = get_date_range()
    logger.info('from: {} to: {}'.format(from_, to_))
    for fi, mappings in ctx.config.account_mappings.items():
        if fi == 'tangerine':
            import_tangerine(ctx, mappings, from_, to_)
        elif fi == 'rogersbank':
            import_rogersbank(ctx, mappings, from_, to_)
