import os
URL = "https://fapi.binance.com/fapi/v1/ticker/24hr?symbol="
testnet_URL = 'https://testnet.binancefuture.com/fapi'
line_token = 'paste your LINE token here'

### use command ' heroku config:set API_key=xxx ' // to set envirolment key
WEBHOOK_PASSPHRASE = os.getenv('passphrase')
# test API
test_API_key='paste your test key here'
test_API_secret='paste your test key here'
# real API
API_key = os.getenv('paste your key here')
API_secret = os.getenv('paste your key here')
