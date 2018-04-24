import bs4
import requests
import time
import json
import re
from string import whitespace


default_dates = 'all'
SNAPS_URL = 'https://coinmarketcap.com/historical/'
DOMINANCE_URL = 'https://graphs2.coinmarketcap.com/global/dominance/'
MARKETCAP_URL = 'https://graphs2.coinmarketcap.com/global/marketcap-total/'
MARKETCAP_ALTCOIN_URL = 'https://graphs2.coinmarketcap.com/global/marketcap-altcoin/'
# Coinmarketcap asks that you don't submit more that 10 requests per minute, hence the 6 second wait.
# Remove/reduce if you need to download a large number of dates that would take forever otherwise.
RATE_LIMIT = 6


def historical_snapshots(dates=default_dates, out_file=None, cache_file=None, rformat='json', wformat='json',
                         cache=True, rate_limit=RATE_LIMIT):
    """
    Retrieves all the data from the specified file or coinmarketcap.com and caches it to a local file
    for faster subsequent access times
    For a list of all available dates refer to https://coinmarketcap.com/historical/

    NOTE: A separate request submitted for each date provided so it might take a while if retrieveing mak=ny dates
        at once

    :param rate_limit:
    :param dates: dates to retrieve data for. If 'all' is passed in then all dates are fetched from the website first
    :param out_file: file to write the requested data to (local file or absolute path to file)
    :param cache_file: file to check for some or all of the requested dates (local file or absolute path to file)
    :param rformat: format of the cache file to check
    :param wformat: format output file to write to
    :param cache: If False, the results won't be cached (very slow subsequent access times)
    :param rate_limit: time to wait between requests to coinmarketcap
    :return: json format data
    """
    if dates == 'all':
        print('Fetching all dates...')
        dates = available_dates()
    # Retrieves data, caches it to a file and reads from it before returning
    result = _retrieve_snaps(dates, cache_file, rformat, rate_limit)
    if cache:
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
    :param file: cache file to check for some or all of the requested dates (local file or absolute path to file)
    :param rformat: format of the cache file to check
    :param rate_limit: time to wait between requests to coinmarketcap
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


def write_to_file(data=None, file=None, wformat='json'):
    """
    Writes json or csv data to file

    :param data: json format data to write to file
    :param file: file to write to (local file or absolute path to file)
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

    :param file: file to read from (local file or absolute path to file)
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


def start_end(start=None, end=None, url=None):
    """
    Checks to make sure that either start/end are both specified or neither is specified and concatenates
    them with the provided url

    :return: url/start/end/
    """
    # Checks to make sure that either start/end are both specified or neither is specified
    if end is None:
        if start is not None:
            raise ValueError('When providing a date range, a start and end must both be provided.')
        else:
            dates = None
    else:
        if start is None:
            raise ValueError('When providing a date range, a start and end must both be provided.')
        else:
            dates = start + '/' + end + '/'
    # Concatenates the base dominance url with dates if needed
    if dates is None:
        final_url = url
    else:
        final_url = url + dates

    return final_url


def dominance(start=None, end=None, formatted='raw', epoch=False):
    """
    Retrieves the "Percentage of Market Capitalization (Dominance)" chart data from conmarketcap.com

    :param start: starting date to retrieve for, in epoch time
    :param end: end date to retrieve for, in epoch time
    :param formatted: either 'alt' or 'raw'. If 'alt' then all alcoins are summed up. If 'raw' then the
        coinmarketcap format is kept (e.g. top 10 + others)
    :param epoch: True if you want the dates returned to be in epoch format, False if you want datetime format
    :return: the retrieved data as a dictionary in the format {key: list_of_values} where key is
        bitcoin or altcoins or ethereum, etc and list_of_values is a list of pairs [[date, percent], [date, percent]...]
    """
    if type(epoch) != bool:
        raise ValueError('Please make sure you are using a boolean for the epoch parameter')

    url = start_end(start, end, DOMINANCE_URL)
    response = requests.get(url)
    json_response = response.json()

    # If raw, return as is rounded to 2 decimals
    if formatted == 'raw':
        if epoch:  # If epoch is True then just round the percent values and don't convert epochs
            for x in json_response:
                json_response[x] = [[x[0], round(x[1], 2)] for x in json_response[x]]
        else:  # If epoch is False then convert epochs and round
            for x in json_response:
                json_response[x] = [[epoch_to_date(x[0]), round(x[1], 2)] for x in json_response[x]]
        return json_response

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
        return result
    else:
        raise ValueError('Please enter a valid return format. Valid options are "raw" or "alt"')


def total_market_cap(start=None, end=None, exclude_btc=False, epoch=False):
    """
    Retrieves the "Total Market Capitalization" chart data from conmarketcap.com (option to exclude bitcoin)

    :param start: starting date to retrieve for, in epoch time
    :param end: end date to retrieve for, in epoch time
    :param exclude_btc: if True, the "Total Market Capitalization (Excluding Bitcoin)" is scraped instead
    :param epoch: True if you want the dates returned to be in epoch format, False if you want datetime format
    :return: the retrieved data either as a dictionary in the format {key: list_of_values}
        or a dictionary in the format {key: dict_of_values}
    """
    if (type(epoch) != bool) or (type(exclude_btc) != bool):
        raise ValueError('Please make sure you are using a boolean for the epoch and exclude_btc parameters')

    url = start_end(start, end, MARKETCAP_ALTCOIN_URL if exclude_btc else MARKETCAP_URL)
    response = requests.get(url)
    json_response = response.json()

    if epoch:
        return json_response['market_cap_by_available_supply']
    else:
        return [[epoch_to_date(x[0]), x[1]] for x in json_response['market_cap_by_available_supply']]


def epoch_to_date(date=None):
    if date is None:
        ValueError('Please enter an epoch time to convert to date')
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date/1000))


def available_dates():
    """
    Retrieves all dates for which historical data is available

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
    return sorted(list(dates))

# TODO add saving ability for dominance and total_market_cap