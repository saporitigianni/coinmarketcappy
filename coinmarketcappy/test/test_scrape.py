import coinmarketcappy as cmc
import time


temp = cmc.get_ticker_historical(start=1367174841000, end=1522512352846, name='bitcoin')
print(temp)
time.sleep(6)

temp = cmc.historical_snapshots('20180401',
                                'historical_snaps20180425.json',
                                'historical_snaps.json',
                                rformat='json', wformat='json')
print(temp)
time.sleep(6)

dominance = cmc.dominance(formatted='raw', epoch=True)
for x in dominance:
    print(x, dominance[x])
time.sleep(6)

dominance = cmc.dominance(start=1367121600000, end=1519975624438, formatted='alt', epoch=False)
for x in dominance:
    print(x, dominance[x])
time.sleep(6)

total_mc = cmc.total_market_cap(start=1367121600000, end=1519975624438, exclude_btc=False, epoch=False)
print(total_mc)
time.sleep(6)

total_mc = cmc.total_market_cap(exclude_btc=True, epoch=True)
print(total_mc)

# print(list(dominance['bitcoin'].keys()))
# print(list(dominance['bitcoin'].values()))
# print(list(dominance['altcoins'].values()))
