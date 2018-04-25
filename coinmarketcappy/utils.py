import time
import json


def epoch_to_date(date=None):
    """
    Converts the epoch time to date and time

    :param date: epoch to convert
    :return: date in the format '%Y-%m-%d %H:%M:%S'
    """
    if date is None:
        ValueError('Please enter an epoch time to convert to date')
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date/1000))


def start_end(start=None, end=None, url=None):
    """
    Checks to make sure that either start/end are both specified or neither is specified and concatenates
    them with the provided url

    :param start: epoch time
    :param end: epoch time
    :param url: base url to concatenate start and end with
    :return: url/start/end/
    """
    # Checks to make sure that either start/end are both specified or neither is specified
    if start and end:
        dates = start + '/' + end + '/'
    elif not (start and end):
        dates = None
    else:
        raise ValueError('When providing a date range, a start and end must both be provided.')
    # if end is None:
    #     if start is not None:
    #         raise ValueError('When providing a date range, a start and end must both be provided.')
    #     else:
    #         dates = None
    # else:
    #     if start is None:
    #         raise ValueError('When providing a date range, a start and end must both be provided.')
    #     else:
    #         dates = start + '/' + end + '/'
    # Concatenates the base dominance url with dates if needed
    if dates is None:
        final_url = url
    else:
        final_url = url + dates

    return final_url


def export_csv(data=None, file=None):
    write_to_file(data, file, wformat='csv')


def export_json(data=None, file=None):
    write_to_file(data, file, wformat='json')


# def export_numpy(data=None, file=None):
#     write_to_file(data, file, wformat='numpy')


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

    if not file.endswith('.{}'.format(wformat)):
        file += '.{}'.format(wformat)

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
