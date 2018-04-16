import bs4
import requests
import time
import json
import numpy as np
from string import whitespace


r2013 = [20130428, 20130505, 20130512, 20130519, 20130526, 20130602,
         20130609, 20130616, 20130623, 20130630, 20130707, 20130714,
         20130721, 20130728, 20130804, 20130811, 20130818, 20130825,
         20130901, 20130908, 20130915, 20130922, 20130929, 20131006,
         20131013, 20131020, 20131027, 20131103, 20131110, 20131117,
         20131124, 20131201, 20131208, 20131215, 20131222, 20131229]
r2014 = [20140105, 20140112, 20140119, 20140126, 20140202, 20140209,
         20140216, 20140223, 20140302, 20140309, 20140316, 20140323,
         20140330, 20140406, 20140413, 20140420, 20140427, 20140504,
         20140511, 20140518, 20140525, 20140601, 20140608, 20140615,
         20140622, 20140629, 20140706, 20140713, 20140720, 20140727,
         20140803, 20140810, 20140817, 20140824, 20140831, 20140907,
         20140914, 20140921, 20140928, 20141005, 20141012, 20141019,
         20141026, 20141102, 20141109, 20141116, 20141123, 20141130,
         20141207, 20141214, 20141221, 20141228]
r2015 = [20150104, 20150111, 20150118, 20150125, 20150201, 20150208,
         20150215, 20150222, 20150301, 20150308, 20150315, 20150322,
         20150329, 20150405, 20150412, 20150419, 20150426, 20150503,
         20150510, 20150517, 20150524, 20150531, 20150607, 20150614,
         20150621, 20150628, 20150705, 20150712, 20150719, 20150726,
         20150802, 20150809, 20150816, 20150823, 20150830, 20150906,
         20150913, 20150920, 20150927, 20151004, 20151011, 20151018,
         20151025, 20151101, 20151108, 20151115, 20151122, 20151129,
         20151206, 20151213, 20151220, 20151227]
r2016 = [20160103, 20160110, 20160117, 20160124, 20160131, 20160207,
         20160214, 20160221, 20160228, 20160306, 20160313, 20160320,
         20160327, 20160403, 20160410, 20160417, 20160424, 20160501,
         20160508, 20160515, 20160522, 20160529, 20160605, 20160612,
         20160619, 20160626, 20160703, 20160710, 20160717, 20160724,
         20160731, 20160807, 20160814, 20160821, 20160828, 20160904,
         20160911, 20160918, 20160925, 20161002, 20161009, 20161016,
         20161023, 20161030, 20161106, 20161113, 20161120, 20161127,
         20161204, 20161211, 20161218, 20161225]
r2017 = [20170101, 20170108, 20170115, 20170122, 20170129, 20170205,
         20170212, 20170219, 20170226, 20170305, 20170312, 20170319,
         20170326, 20170402, 20170409, 20170416, 20170423, 20170430,
         20170507, 20170514, 20170521, 20170528, 20170604, 20170611,
         20170618, 20170625, 20170702, 20170709, 20170716, 20170723,
         20170730, 20170806, 20170813, 20170820, 20170827, 20170903,
         20170910, 20170917, 20170924, 20171001, 20171008, 20171015,
         20171022, 20171029, 20171105, 20171112, 20171119, 20171126,
         20171203, 20171210, 20171217, 20171224, 20171231]
r2018 = [20180107, 20180114, 20180121, 20180128, 20180204, 20180211,
         20180218, 20180225, 20180304, 20180311, 20180318, 20180325,
         20180401, 20180408]
default_dates = [*r2013, *r2014, *r2015, *r2016, *r2017, *r2018]
fetched_data = dict()
total_mc = 0
BASE_URL = 'https://coinmarketcap.com/historical/'
# total_length = len(retrieve)
json_tempfile = 'json_historical_20180304.json'
numpy_tempfile = 'numpy_historical_20180225.npy'
csv_tempfile = 'csv_historical_20180225.csv'
NUM_ATTRIBUTES = 7


def retrieve_and_cache(dates=default_dates, outfile=None, cachefile=None, rformat='json'):
    # If a cachefile is passed in then that one is checked for the dates, if not the
    result = retrieve(dates, cachefile)
    if rformat == 'json':
        pass
    elif rformat == 'numpy':
        result = json_to_numpy(result.copy())
    elif rformat == 'csv':
        result = json_to_csv(result.copy())
    else:
        raise ValueError("Please enter a valid rformat. Valid values are 'json', 'numpy', and 'csv'.")
    print('writing.........................')
    # time.sleep(5)
    write_to_file(result, outfile, rformat)
    result = read_from_file(outfile, rformat)
    return result


def retrieve(dates=default_dates, file=None):
    missing = list()
    global fetched_data

    if file is not None:
        fetched_data = read_from_file(file)
        for x in dates:
            if str(x) not in fetched_data:
                missing.append(x)
        if len(missing) == 0:
            return fetched_data
        else:
            dates = missing
        print('{} dates missing from the specified cache file.'.format(len(dates)))

    total_length = len(dates)
    for i in range(total_length):
        # print(i, dates)
        # Retrieve data from coinmarketcap.com and find all token entries (next 3 lines)
        response = requests.get(BASE_URL + str(dates[i]))
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        # print(soup)
        tr = soup.find_all('tr')
        # print(tr)
        # Parses the all coins which should be more than enough to find the top 10 PoS (0th entry is dummy)
        for y in range(1, len(tr)):
            td = tr[y].find_all('td')
            rank = td[0].get_text().strip()
            symbol, name = td[1].get_text().strip().lower().split('\n')
            if dates[i] not in fetched_data:
                fetched_data[dates[i]] = dict()
            fetched_data[dates[i]][rank] = dict()
            fetched_data[dates[i]][rank]["symbol"] = symbol
            fetched_data[dates[i]][rank]["name"] = name
            try:  # MARKET CAP CAN BE A QUESTION MARK
                fetched_data[dates[i]][rank]["market_cap"] = int(td[3].get_text().strip('$' + whitespace).replace(',', ''))
            except:
                fetched_data[dates[i]][rank]["market_cap"] = td[3].get_text().strip('$' + whitespace).replace(',', '')
            fetched_data[dates[i]][rank]["price"] = float(td[4].get_text().strip('$' + whitespace).replace(',', ''))
            try:  # CIRCULATING SUPPLY CAN BE A QUESTION MARK
                fetched_data[dates[i]][rank]["circulating_supply"] = int(td[5].get_text().strip('*' + whitespace).replace(',', ''))
            except:
                fetched_data[dates[i]][rank]["circulating_supply"] = td[5].get_text().strip('*' + whitespace).replace(',', '')
            try:  # 24hr_vol CAN BE THE STRING 'Low Vol'
                fetched_data[dates[i]][rank]["24hr_vol"] = int(td[6].get_text().strip('$' + whitespace).replace(',', ''))
            except:
                fetched_data[dates[i]][rank]["24hr_vol"] = td[6].get_text().strip('$' + whitespace).replace(',', '')
        # print(dates[i])
        # for x in fetched_data:
        #     print(x)
        #     for y in fetched_data[x]:
        #         print('\t', y, ' : ', fetched_data[x][y])
        # Coinmarketcap asks that you don't submit more that 10 requests per minute, feel free to remove if you
        # give no fucks
        time.sleep(1)
    return fetched_data.copy()


def write_to_file(data=None, file=None, wformat='json'):
    if data is None:
        raise Exception('Data missing. Please specify the data to write to file.')
    if file is None:
        raise Exception('File name missing. Please specify the name of a file to write to.')

    if wformat == 'json':
        with open(file, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
    elif wformat == 'numpy':
        np.save(file, data)
    elif wformat == 'csv':
        with open(file, 'w') as f:
            f.write(data)
    else:
        raise ValueError("Please enter a valid rformat. Valid values are 'json', 'numpy', and 'csv'.")


def read_from_file(file=None, rformat='json'):
    if file is None:
        raise Exception('File name missing. Please specify the name of a file to read from.')

    if rformat == 'json':
        with open(file, 'r') as f:
            contents = f.read()
            return json.loads(contents)
    elif rformat == 'numpy':
        return np.load(file)
    elif rformat == 'csv':
        with open(file, 'r') as f:
            contents = f.read()
            return contents
    else:
        raise ValueError("Please enter a valid rformat. Valid values are 'json', 'numpy', and 'csv'.")


def json_to_numpy(data=None, file=None):
    if data is None:
        if file is None:
            raise Exception('Data and file missing, please specify one (not both).')
        else:
            to_convert = read_from_file(file)
    else:
        if file is not None:
            raise Exception('Both data and field specified. Please retry specifying only one.')
        else:
            to_convert = data
    dates = list(to_convert.keys())
    dates.sort()

    max_row_len = max([len(to_convert[x]) for x in to_convert]) + 1
    column_len = NUM_ATTRIBUTES
    number_of_tables = len(to_convert)
    table = np.full((number_of_tables, max_row_len, column_len), '', dtype=object)

    for x in range(number_of_tables):
        table[x, 0, 0] = dates[x]
        for y in range(len(to_convert[dates[x]])):
            table[x, y+1, 0] = y + 1
            table[x, y+1, 1] = to_convert[dates[x]][str(y+1)]['symbol']
            table[x, y+1, 2] = to_convert[dates[x]][str(y+1)]['name']
            table[x, y+1, 3] = to_convert[dates[x]][str(y+1)]['market_cap']
            table[x, y+1, 4] = to_convert[dates[x]][str(y+1)]['price']
            table[x, y+1, 5] = to_convert[dates[x]][str(y+1)]['circulating_supply']
            table[x, y+1, 6] = to_convert[dates[x]][str(y+1)]['24hr_vol']
    return table.copy()


def json_to_csv(data=None, file=None):
    output = ''
    if data is None:
        if file is None:
            raise Exception('Data and file missing, please specify one (not both).')
        else:
            to_convert = read_from_file(file)
    else:
        if file is not None:
            raise Exception('Both data and field specified. Please retry specifying only one.')
        else:
            to_convert = data
    dates = list(to_convert.keys())
    dates.sort()

    for x in to_convert:
        output += x + '\n'
        for y in to_convert[x]:
            output += str(y) + ', '
            output += to_convert[x][y]['symbol'] + ', '
            output += to_convert[x][y]['name'] + ', '
            output += str(to_convert[x][y]['market_cap']) + ', '
            output += str(to_convert[x][y]['price']) + ', '
            output += str(to_convert[x][y]['circulating_supply']) + ', '
            output += str(to_convert[x][y]['24hr_vol']) + '\n'
    return output


if __name__ == '__main__':
    # temp1 = read_from_file(json_tempfile)
    temp = retrieve_and_cache(default_dates, 'json_historical_20180408.json', json_tempfile, rformat='json')
    # temp = read_from_file('json_historical_20180408.json', rformat='json')
    # print(temp)
    # print(temp['20130428'])
    # sett = set()
    # print(temp)
    # for x in temp:
    #     print(x)
    #     for y in temp[x]:
    #         # sett.add(temp[x][y]['24hr_vol'])
    #         print('\t', y, ' : ', temp[x][y])

    # print(sett)
    for x in range(len(temp)):
        print(str(default_dates[x]), isinstance(default_dates[x], int))
        for y in temp[str(default_dates[x])]:
            print('\t', y, ' : ', temp[str(default_dates[x])][y])

    # for x in json_to_numpy(file=json_tempfile)[-1]:
    #     print(x)
    # print(json_to_numpy(file=json_tempfile)[-1])
