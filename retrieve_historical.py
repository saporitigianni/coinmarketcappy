import bs4
import requests
import time
import json
import re
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
         20180401, 20180408, 20180415]
default_dates = [*r2013, *r2014, *r2015, *r2016, *r2017, *r2018]
BASE_URL = 'https://coinmarketcap.com/historical/'
DOMINANCE_URL = 'https://graphs2.coinmarketcap.com/global/dominance/'
# Coinmarketcap asks that you don't submit more that 10 requests per minute, hence the 6 second sleep.
# Remove/reduce if you need to download a large number of dates that would take forever otherwise.
RATE_LIMIT = 6


def retrieve_and_cache(dates=default_dates, out_file=None, cache_file=None, rformat='json', wformat='json'):
    """
    Retrieves all the data from the specified file or coinmarketcap.com and caches it to a local file
    for faster subsequent access times

    :param dates: dates to retrieve data for. If 'all' is passed in then all dates are fetched from the website first
    :param out_file: file to write the requested data to
    :param cache_file: file to check for some or all of the requested dates
    :param rformat: format of the cache file to check
    :param wformat: format output file to write to
    :return: json format data
    """
    if dates == 'all':
        print('Fetching all dates...')
        dates = available_dates()
    # Retrieves data, caches it to a file and reads from it before returning
    result = retrieve(dates, cache_file, rformat)
    print('Writing to file...')
    write_to_file(result, out_file, wformat)
    result = read_from_file(out_file, wformat)
    return result.copy()


def retrieve(dates=default_dates, file=None, rformat=None):
    """
    Retrieves data from file if available or coinmarketcap.com

    :param dates: dates to retrieve data for. If 'all' is passed in then all dates are fetched from the website first
    :param file: cache file to check for some or all of the requested dates
    :param rformat: format of the cache file to check
    :return: json format data
    """
    missing = list()
    fetched_data = dict()

    if dates == 'all':
        print('Fetching all dates...')
        dates = available_dates()

    if file is not None:
        fetched_data = read_from_file(file, rformat)
        # Figure out what dates are missing
        for x in dates:
            if str(x) not in fetched_data:
                missing.append(x)
        # If none are missing then return only the requested dates
        if len(missing) == 0:
            final_fetched = dict()
            for x in dates:
                final_fetched[str(x)] = fetched_data[str(x)].copy()
            return final_fetched.copy()
        # If there are missing dates, retrieve the ones that are present from the file
        # and make a list of the missing ones as strings
        else:
            temp = dict()
            for x in set(dates).difference(set(missing)):
                temp[str(x)] = fetched_data[str(x)].copy()
            fetched_data = temp.copy()
            dates = [str(x) for x in missing]
        print('{} dates missing from the specified cache file...'.format(len(dates)))

    total_length = len(dates)
    for i in range(total_length):
        print('Retrieving {}'.format(dates[i]))
        # Retrieve data from coinmarketcap.com and find all token entries (next 3 lines)
        response = requests.get(BASE_URL + str(dates[i]))
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        tr = soup.find_all('tr')
        # Parses the all coins which should be more than enough to find the top 10 PoS (0th entry is dummy)
        for y in range(1, len(tr)):
            td = tr[y].find_all('td')
            rank = td[0].get_text().strip()
            symbol, name = td[1].get_text().strip().lower().split('\n')
            # Add dates and token info broken into categories (rest of function)
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
        time.sleep(RATE_LIMIT)
    return fetched_data.copy()


def write_to_file(data=None, file=None, wformat='json'):
    """
    Writes json or csv data to file

    :param data: json format data to write to file
    :param file: file to write to
    :param wformat: format to write to file on
    :return: None
    """
    if data is None:
        raise Exception('Data missing. Please specify the data to write to file.')
    if file is None:
        raise Exception('File name missing. Please specify the name of a file to write to.')

    if wformat == 'json':
        with open(file, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
    elif wformat == 'csv':
        with open(file, 'w') as f:
            f.write(json_to_csv(data))
    else:
        raise ValueError("Please enter a valid wformat. Valid values are 'json' and 'csv'.")


def read_from_file(file=None, rformat='json'):
    """
    Reads from file and converts to json format if it isn't already

    :param file: file to read from
    :param rformat: format of the file
    :return: the data retrieved from file
    """
    if file is None:
        raise Exception('File name missing. Please specify the name of a file to read from.')

    if rformat == 'json':
        with open(file, 'r') as f:
            contents = f.read()
            return json.loads(contents)
    elif rformat == 'csv':
        with open(file, 'r') as f:
            contents = f.read()
            contents = csv_to_json(contents)
            return contents
    else:
        raise ValueError("Please enter a valid rformat. Valid values are 'json' and 'csv'.")


def json_to_csv(data=None):
    """
    Specify data to convert to csv format (not both)

    :param data: json formatted data to convert to csv format
    :return: csv format data
    """
    # Verifies that one and only one of the input types is specified
    if data is None:
        raise ValueError('Data missing. Please specify the data to convert.')

    output = ''
    # Organizes the dates so that the output csv file is properly organized as well
    dates = list(data.keys())
    dates.sort()

    # Goes through each date (outer loop) and each rank (inner) to convert to csv format
    for x in data:
        output += x + '\n'
        for y in data[x]:
            output += str(y) + ', '
            output += data[x][y]['symbol'] + ', '
            output += data[x][y]['name'] + ', '
            output += str(data[x][y]['market_cap']) + ', '
            output += str(data[x][y]['price']) + ', '
            output += str(data[x][y]['circulating_supply']) + ', '
            output += str(data[x][y]['24hr_vol']) + '\n'
    return output


def csv_to_json(data=None):
    """
    Takes properly formatted csv data and returns it in json format

    :param data: csv formatted data to convert to json format
    :return: json format data
    """
    if data is None:
        raise ValueError('Data missing. Please specify the data to convert.')

    converted = dict()
    base = None
    for line in data.splitlines():
        split = [x.strip() for x in line.split(',')]
        if len(split) == 1:
            base = split[0]
            converted[base] = dict()
            continue
        else:
            converted[base][split[0]] = dict()
            converted[base][split[0]]['symbol'] = split[1]
            converted[base][split[0]]['name'] = split[2]
            converted[base][split[0]]['market_cap'] = split[3]
            converted[base][split[0]]['price'] = split[4]
            converted[base][split[0]]['circulating_supply'] = split[5]
            converted[base][split[0]]['24hr_vol'] = split[6]
    return converted


def retrieve_dominance(start=None, end=None, formatted='alt'):
    """
    Retrieves the "Percentage of Market Capitalization (Dominance)" chart data from conmarketcap.com

    :param start: starting date to retrieve for
    :param end: end date to retrieve for
    :param formatted: either 'alt' or 'raw'. If 'alt' then all alcoins are summed up. If 'raw' then the
        coinmarketcap format is kept (e.g. bitcoin, ethereum, ripple, ... Others)
    :return: the retrieved data either as a dictionary in the format {key: list_of_values}
        or a dictionary in the format {key: dict_of_values}
    """
    response = requests.get(DOMINANCE_URL)
    json_response = response.json()
    if formatted == 'raw':
        return json_response
    elif formatted == 'alt':
        result = dict()
        result['bitcoin'] = dict(json_response['bitcoin'].copy())
        result['altcoins'] = dict()
        for entry in json_response:
            if entry == 'bitcoin':
                continue
            for date in json_response[entry]:
                if date[0] not in result['altcoins']:
                    result['altcoins'][date[0]] = 0
                result['altcoins'][date[0]] += date[1]
    return result


def epoch_to_date(date=None):
    pass


def available_dates():
    """
    Retrieves all dates for which historical data is available

    :return: a list of string dates in ascending order
    """
    dates = set()
    response = requests.get(BASE_URL)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    ul = soup.find_all('ul')
    for entry in ul:
        a = entry.find_all('a')
        if len(a) == 0:
            continue
        for x in a:
            if 'href' in x.attrs:
                match = re.match(r'/historical/([0-9]{8,8})/', x['href'])
                if match is not None:
                    dates.add(match.group(1))
    return sorted(list(dates))


if __name__ == '__main__':
    # temp = retrieve_and_cache('all', 'historical_20180415.json', 'historical_20180415.json',
    #                           rformat='json', wformat='json')
    # temp = read_from_file('csv_historical_20180408.csv', rformat='csv')
    # print(temp)
    # print(available_dates())
    dominance = retrieve_dominance()
    for x in dominance:
        print(x, dominance[x])
    # print(retrieve_dominance())

    # for a in range(len(temp)):
    #     print(str(default_dates[a]), isinstance(default_dates[a], int))
    #     for b in temp[str(default_dates[a])]:
    #         print('\t', b, ' : ', temp[str(default_dates[a])][b])
