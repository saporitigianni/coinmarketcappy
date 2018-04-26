import coinmarketcappy as cmc

tickers = cmc.get_tickers(start=1, limit=2, convert='EUR', epoch=False, out_file='test', wformat='csv')  # only json writes
print(tickers)
print(tickers[0]['price_eur'])

ticker = cmc.get_ticker(name='ethereum', out_file='test', wformat='csv')
print(ticker)
print(ticker['price_eur'])
print(ticker['rank'])

glob = cmc.get_global_data(out_file='test', wformat='csv')
print(glob)
print(glob['active_markets'])
