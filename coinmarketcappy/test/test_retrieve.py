import coinmarketcappy as cmc

tickers = cmc.get_tickers(start=1, limit=2, convert='EUR')
print(tickers)
print(tickers[0]['price_eur'])

ticker = cmc.get_ticker(name='ethereum', convert='EUR')
print(ticker)
print(ticker['price_eur'])
print(ticker['rank'])

glob = cmc.get_global_data()
print(glob)
print(glob['active_markets'])
