import coinmarketcappy as cmc
import time


# temp = cmc.get_ticker_historical(name='bitcoin', out_file='test', wformat='csv', epoch=True)
# print(temp)
# time.sleep(6)
# temp = cmc.available_snaps('test', 'csv')
temp = cmc.historical_snapshots(['20180401', '20180408'],
                                'historical_snaps20180425.csv',
                                'historical_snaps.json',
                                rformat='json', wformat='csv')
# for x in temp:
#     print(x)
#     for y in temp[x]:
#         print(y)
# time.sleep(6)
#
# dominance = cmc.dominance(out_file='test', wformat='csv', formatted='raw', epoch=False)
# for x in dominance:
#     print(x, dominance[x])
# time.sleep(6)
#
# dominance = cmc.dominance(start=1367121600000, end=1519975624438, formatted='alt', epoch=False)
# for x in dominance:
#     print(x, dominance[x])
# time.sleep(6)
#
# total_mc = cmc.total_market_cap(exclude_btc=False, epoch=False, out_file='test', wformat='csv')
# print(total_mc)
# time.sleep(6)
#
# total_mc = cmc.total_market_cap(exclude_btc=True, epoch=True)
# print(total_mc)

# print(list(dominance['bitcoin'].keys()))
# print(list(dominance['bitcoin'].values()))
# print(list(dominance['altcoins'].values()))
