from coinmarketcappy import scrape


temp = scrape.historical_snapshots('all',
                                   'historical_snaps.json',
                                   '/Users/giannisaporiti/PycharmProjects/coinmarketcappy/historical_20180422.json',
                                   rformat='json', wformat='json')
print(temp)
# dominance = scrape.dominance(formatted='raw', epoch=True)
# for x in dominance:
#     print(x, dominance[x])

# dominance = scrape.dominance(formatted='alt', epoch=False)
# for x in dominance:
#     print(x, dominance[x])

# total_mc = scrape.total_market_cap(exclude_btc=False, epoch=False)
# print(total_mc)

# total_mc = scrape.total_market_cap(exclude_btc=True, epoch=True)
# print(total_mc)

# print(list(dominance['bitcoin'].keys()))
# print(list(dominance['bitcoin'].values()))
# print(list(dominance['altcoins'].values()))
