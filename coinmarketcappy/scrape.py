import bs4
import requests
import re
from string import whitespace
from .utils import *


default_dates = 'all'
SNAPS_URL = 'https://coinmarketcap.com/historical/'
DOMINANCE_URL = 'https://graphs2.coinmarketcap.com/global/dominance/'
MARKETCAP_URL = 'https://graphs2.coinmarketcap.com/global/marketcap-total/'
MARKETCAP_ALTCOIN_URL = 'https://graphs2.coinmarketcap.com/global/marketcap-altcoin/'
# Coinmarketcap asks that you don't submit more that 10 requests per minute, hence the 6 second wait.
# Remove/reduce if you need to download a large number of dates that would take forever otherwise.
RATE_LIMIT = 6


def historical_snapshots(dates=default_dates, out_file=None, cache_file=None, rformat='json', wformat='json',
                         rate_limit=RATE_LIMIT):
    """
    Retrieves all the data from the specified file or coinmarketcap.com and caches it to a local file
    for faster subsequent access times
    For a list of all available dates refer to https://coinmarketcap.com/historical/

    NOTE: A separate request submitted for each date provided so it might take a while if retrieving many dates
        at once

    :param rate_limit:
    :param dates: dates to retrieve data for. If 'all' is passed in then all dates are fetched from the website first
        must be in the format 'yyyymmdd' (e.g. 20180423)
    :param out_file: if provided info will be saved to this file (local file name or absolute path)
    :param cache_file: file to check for some or all of the requested dates (local file name or absolute path)
    :param rformat: format of the cache file to check
    :param wformat: format output file to write to
    :param rate_limit: time to wait between requests to coinmarketcap
    :return: json format data
    """
    if dates == 'all':
        print('Fetching all dates...')
        dates = available_snaps()
    elif (type(dates) == list) or (type(dates) == tuple):
        pass
    elif type(dates) == int:
        dates = [dates]
    elif (type(dates) == str) and dates.isdigit():
        dates = [dates]
    else:
        raise ValueError('Please use a valid format for the "dates" attribute')
    # Retrieves data, caches it to a file and reads from it before returning
    result = _retrieve_snaps(dates, cache_file, rformat, rate_limit)
    if out_file:
        print('Writing to file...')
        write_to_file(result, out_file, wformat)
        result = read_from_file(out_file, wformat)
    return result.copy()


def _retrieve_snaps(dates=default_dates, file=None, rformat=None, rate_limit=RATE_LIMIT):
    """
    Retrieves data from file if available or coinmarketcap.com
    For a list of all available dates refer to https://coinmarketcap.com/historical/

    NOTE: There's a separate request submitted

    :param dates: dates to retrieve data for. If 'all' then all dates are fetched from the website first
    :param file: cache file to check for some or all of the requested dates (local file name or absolute path)
    :param rformat: format of the cache file to check
    :param rate_limit: time to wait between requests to coinmarketcap
    :return: json format data
    """
    missing = list()
    fetched_data = dict()

    if dates == 'all':
        print('Fetching all dates...')
        dates = available_snaps()

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
        response = requests.get(SNAPS_URL + str(dates[i]))
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
                fetched_data[dates[i]][rank]["market_cap"] =\
                    int(td[3].get_text().strip('$' + whitespace).replace(',', ''))
            except ValueError:
                fetched_data[dates[i]][rank]["market_cap"] =\
                    td[3].get_text().strip('$' + whitespace).replace(',', '')
            fetched_data[dates[i]][rank]["price"] = float(td[4].get_text().strip('$' + whitespace).replace(',', ''))
            try:  # CIRCULATING SUPPLY CAN BE A QUESTION MARK
                fetched_data[dates[i]][rank]["circulating_supply"] =\
                    int(td[5].get_text().strip('*' + whitespace).replace(',', ''))
            except ValueError:
                fetched_data[dates[i]][rank]["circulating_supply"] =\
                    td[5].get_text().strip('*' + whitespace).replace(',', '')
            try:  # 24hr_vol CAN BE THE STRING 'Low Vol'
                fetched_data[dates[i]][rank]["24hr_vol"] =\
                    int(td[6].get_text().strip('$' + whitespace).replace(',', ''))
            except ValueError:
                fetched_data[dates[i]][rank]["24hr_vol"] = td[6].get_text().strip('$' + whitespace).replace(',', '')
        time.sleep(rate_limit)
    return fetched_data.copy()


def dominance(start=None, end=None, formatted='raw', epoch=False, out_file=None, wformat='json'):
    """
    Retrieves the "Percentage of Market Capitalization (Dominance)" chart data from conmarketcap.com

    :param start: starting date to retrieve for, in epoch time
    :param end: end date to retrieve for, in epoch time
    :param formatted: either 'alt' or 'raw'. If 'alt' then all alcoins are summed up. If 'raw' then the
        coinmarketcap format is kept (e.g. top 10 + others)
    :param epoch: True if you want the dates returned to be in epoch format, False if you want datetime format
    :param out_file: if provided info will be saved to this file
    :param wformat: format to write to cache ('json' by default)
    :return: the retrieved data as a dictionary in the format {key: list_of_values} where key is
        bitcoin or altcoins or ethereum, etc and list_of_values is a list of pairs [[date, percent], [date, percent]...]
    """
    if type(epoch) != bool:
        raise ValueError('Please make sure you are using a boolean for the epoch parameter')

    url = start_end(start, end, DOMINANCE_URL)
    response = requests.get(url)
    # TODO if response code not 200 then handle
    # TODO make this into a function
    json_response = response.json()

    # If raw, return as is rounded to 2 decimals
    if formatted == 'raw':
        if epoch:  # If epoch is True then just round the percent values and don't convert epochs
            for x in json_response:
                json_response[x] = [[x[0], round(x[1], 2)] for x in json_response[x]]
        else:  # If epoch is False then convert epochs and round
            for x in json_response:
                json_response[x] = [[epoch_to_date(x[0]), round(x[1], 2)] for x in json_response[x]]
        if out_file:
            write_to_file(json_response, out_file, wformat)
        return json_response.copy()

    # If alt, sum all the altcoins and round to 2 decimals
    elif formatted == 'alt':
        result = dict()
        result['altcoins'] = dict()
        btc_temp = json_response['bitcoin'].copy()
        del json_response['bitcoin']  # Remove btc so that it is not included in calculations or made into a dict

        for entry in json_response:  # Go through each entry and date for altcoins and add up marketcap percentages
            for date in json_response[entry]:
                if date[0] not in result['altcoins']:
                    result['altcoins'][date[0]] = 0
                result['altcoins'][date[0]] += date[1]

        if epoch:  # Round precentages and convert epochs if necessary
            for x in result:
                result[x] = [[y, round(result[x][y], 2)] for y in sorted(result[x].keys())]
            result['bitcoin'] = [[x[0], round(x[1], 2)] for x in btc_temp]
        else:
            for x in result:
                result[x] = [[epoch_to_date(y), round(result[x][y], 2)] for y in sorted(result[x].keys())]
            result['bitcoin'] = [[epoch_to_date(x[0]), round(x[1], 2)] for x in btc_temp]
        if out_file and wformat:
            write_to_file(json_response, out_file, wformat)
        return result.copy()
    else:
        raise ValueError('Please enter a valid return format. Valid options are "raw" or "alt"')


def total_market_cap(start=None, end=None, exclude_btc=False, epoch=False, out_file=None, wformat='json'):
    """
    Retrieves the "Total Market Capitalization" chart data from conmarketcap.com (option to exclude bitcoin)

    :param start: starting date to retrieve for, in epoch time
    :param end: end date to retrieve for, in epoch time
    :param exclude_btc: if True, the "Total Market Capitalization (Excluding Bitcoin)" is scraped instead
    :param epoch: True if you want the dates returned to be in epoch format, False if you want datetime format
    :param out_file: if provided info will be saved to this file
    :param wformat: format to write to cache ('json' by default)
    :return: the retrieved data either as a dictionary in the format {key: list_of_values}
        or a dictionary in the format {key: dict_of_values}
    """
    if (type(epoch) != bool) or (type(exclude_btc) != bool):
        raise ValueError('Please make sure you are using a boolean for the epoch and exclude_btc parameters')

    url = start_end(start, end, MARKETCAP_ALTCOIN_URL if exclude_btc else MARKETCAP_URL)
    response = requests.get(url)
    json_response = response.json()

    if epoch:
        if out_file:
            write_to_file(json_response['market_cap_by_available_supply'], out_file, wformat)
        return json_response['market_cap_by_available_supply'].copy()
    else:
        temp = [[epoch_to_date(x[0]), x[1]] for x in json_response['market_cap_by_available_supply']]
        if out_file:
            write_to_file(temp, out_file, wformat)
        return temp.copy()


def available_snaps(out_file=None, wformat=None):
    """
    Retrieves all dates for which historical data is available

    :param out_file: file to write info to
    :param wformat: format to write the info
    :return: a list of string dates in ascending order
    """
    dates = set()
    response = requests.get(SNAPS_URL)
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
    ret = sorted(list(dates))
    if out_file and wformat:
        write_to_file(ret, out_file, wformat)
    elif out_file or wformat:
        raise ValueError('When saving available_snaps both out_file and wformat must be present')
    return ret.copy()
