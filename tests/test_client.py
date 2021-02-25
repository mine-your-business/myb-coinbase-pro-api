import pytest
import os
import datetime

from coinbase_pro import CoinbaseProApi

@pytest.fixture(scope='module')
def trade_client():
    return CoinbaseProApi(
        os.environ.get('COINBASE_PRO_TRADE_API_KEY'),
        os.environ.get('COINBASE_PRO_TRADE_API_KEY_SECRET'),
        os.environ.get('COINBASE_PRO_TRADE_API_KEY_PASSPHRASE'),
        "https://api-public.sandbox.pro.coinbase.com"
    )

@pytest.fixture(scope='module')
def transfer_view_client():
    return CoinbaseProApi(
        os.environ.get('COINBASE_PRO_TRANSFER_VIEW_API_KEY'),
        os.environ.get('COINBASE_PRO_TRANSFER_VIEW_API_KEY_SECRET'),
        os.environ.get('COINBASE_PRO_TRANSFER_VIEW_API_KEY_PASSPHRASE'),
        "https://api-public.sandbox.pro.coinbase.com"
    )

@pytest.fixture(scope='module')
def view_client():
    return CoinbaseProApi(
        os.environ.get('COINBASE_PRO_VIEW_API_KEY'),
        os.environ.get('COINBASE_PRO_VIEW_API_KEY_SECRET'),
        os.environ.get('COINBASE_PRO_VIEW_API_KEY_PASSPHRASE'),
        "https://api-public.sandbox.pro.coinbase.com"
    )

@pytest.mark.usefixtures('view_client')
class TestViewClient(object):

    def test_get_accounts_gets_accounts(self, view_client):
        accounts = view_client.get_accounts()
        assert accounts is not None
        assert len(accounts) > 0

    def test_get_account_gets_account_for_currency(self, view_client):
        currency = 'BTC'
        account = view_client.get_account(currency)
        assert account is not None
        assert account['currency'] == currency

    def test_get_withdrawals_gets_withdrawals(self, view_client):
        withdrawals = view_client.get_withdrawals()
        assert withdrawals is not None
        assert len(withdrawals) > 0
        assert float(withdrawals[0]['amount']) > 0.0

    def test_get_coinbase_accounts_gets_accounts(self, view_client):
        accounts = view_client.get_coinbase_accounts()
        assert accounts is not None
        assert len(accounts) > 0

    def test_get_coinbase_account_gets_account_for_currency(self, view_client):
        currency = 'BTC'
        account = view_client.get_coinbase_account(currency)
        assert account is not None
        assert account['currency'] == currency

    def test_get_historic_rates_gets_rates(self, view_client):
        product_id = 'BTC-USD'
        num_candles = 5
        # twice num_candles days ago from today
        range_start = (
            datetime.datetime.today() - 
            datetime.timedelta(days=num_candles*2)
        ).isoformat()
        # num_candles days ago from today
        range_end = (
            datetime.datetime.today() - 
            datetime.timedelta(days=num_candles)
        ).isoformat()
        # Day granularity
        granularity = 86400

        rates = view_client.get_historic_rates(
            product_id,
            range_start,
            range_end,
            granularity
        )

        assert rates is not None
        assert len(rates) == num_candles

@pytest.mark.usefixtures('transfer_view_client')
class TestTransferViewClient(object):

    def test_deposit_from_coinbase_account_deposits_from_coinbase_account(self, transfer_view_client):
        amount = 0.00000001
        currency = 'BTC'

        coinbase_account = transfer_view_client.get_coinbase_account(currency)
        coinbase_account_id = coinbase_account.get('id')
        assert coinbase_account_id is not None

        result = transfer_view_client.deposit_from_coinbase_account(
            amount,
            currency,
            coinbase_account_id
        )

        assert result is not None
        assert result.get('amount') is not None
        assert float(result.get('amount')) == amount
        assert result.get('currency') == currency
