import requests
import gzip, json
import copy

from .auth import CoinbaseExchangeAuth

class CoinbaseProApi:

    def __init__(
            self, 
            api_key,
            api_secret_key, 
            api_key_passphrase,
            api_url='https://api.pro.coinbase.com', 
            verbose=False
    ):
        self._auth = CoinbaseExchangeAuth(api_key, api_secret_key, api_key_passphrase)
        self._api_url = api_url
        self._verbose = verbose

    def _request(self, method, path, body=None, params=None):
        url = self._api_url + path

        if self._verbose:
            print(method, url)

        s = requests.Session()
        response = s.request(
            method, 
            url, 
            data=json.dumps(body) if body else None, 
            params=params, 
            auth=self._auth
        )

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content))
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_accounts(self):
        return self._request('GET', '/accounts')

    def get_account(self, currency):
        accounts = self.get_accounts()
        for account in accounts:
            if account['currency'] == currency:
                return account
        return None

    # Default descending order by time
    def get_withdrawals(self, profile_id=None, before=None, after=None, limit=100):
        params = {
            'type': 'withdraw',
            'limit': limit
        }

        if profile_id:
            params['profile_id'] = profile_id

        if before:
            params['before'] = before

        if after:
            params['after'] = after

        return self._request('GET', '/transfers', params=params)
        
    def get_coinbase_accounts(self, currencies=None):
        accounts = self._request('GET', '/coinbase-accounts')
        if currencies:
            return list(filter(lambda account: account['currency'] in currencies, accounts))
        return accounts

    def get_coinbase_account(self, currency=None):
        accounts = self.get_coinbase_accounts(currencies=[currency])
        return accounts[0]

    def deposit_from_coinbase_account(self, amount, currency, coinbase_account_id):
        # Smallest unit is 0.00000001
        body = {
            'amount': round(amount, 8),
            'currency': currency,
            'coinbase_account_id': coinbase_account_id
        }
        return self._request('POST', '/deposits/coinbase-account', body=body)

    # start and end are in ISO 8601 format
    # Return format is a list of lists where each
    # individual list in the list represents a candle and has the format:
    # [ time, low, high, open, close, volume ]
    def get_historic_rates(self, product_id, start, end, granularity):
        params = {
            'start': start,
            'end': end,
            'granularity': granularity
        }
        return self._request('GET', f'/products/{product_id}/candles', params=params)
    
    def get_24_hr_stats(self, product_id):
        return self._request('GET', f'/products/{product_id}/stats')

    def get_latest_trades(self, product_id):
        return self._request('GET', f'/products/{product_id}/trades')

    # cancel_after options: min, hour, day
    # side options: buy, sell
    # type options: limit, market
    def place_limit_order(self, product_id, side, price, size, cancel_after=None):
        # Smallest unit is 0.00000001 - force round down via subtraction
        if size > 0.00000001:
            size = round(size - 0.000000009, 8)

        body = {
            'product_id': product_id,
            'side': side,
            # Smallest unit is 0.01000000
            'price': round(price, 2),
            'size': size,
            'type': 'limit'
        }

        if cancel_after:
            body['cancel_after'] = cancel_after

        return self._request('POST', f'/orders', body=body)
    
    def get_payment_methods(self):
        return self._request('GET', f'/payment-methods')
    
    def get_payment_methods_for_currency(self, currency):
        all_payment_methods = self.get_payment_methods()
        return [method for method in all_payment_methods if method['currency'] == currency]

    def withdraw_to_payment_method(self, amount, currency, payment_method_id):
        if currency == 'USD':
            if amount > 0.01:
                # Smallest unit is 0.01000000 - force round down via subtraction
                amount = round(amount-0.009, 2)
        else:
            if amount > 0.00000001:
                # Smallest unit is 0.00000001 - force round down via subtraction
                amount = round(amount-0.000000009, 8)

        body = {
            'amount': amount,
            'currency': currency,
            'payment_method_id': payment_method_id
        }
        return self._request('POST', f'/withdrawals/payment-method', body=body)
