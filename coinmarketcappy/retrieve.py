import requests
from .utils import *

BASE_URL = 'https://api.coinmarketcap.com/v1/'


def get_tickers(start=None, limit=None, convert=None, out_file=None, wformat=None):
    """

    :param start:
    :param limit:
    :param convert:
    :param out_file:
    :param wformat:
    :return:
    """
    url = '{}ticker/'.format(BASE_URL)
    if limit or convert or start:
        url += '?'
    if start:
        url += 'start={}'.format(start)
    if limit:
        url += '&limit={}'.format(limit)
    if convert:
        url += '&convert={}'.format(convert)

    response = requests.get(url)
    json_response = response.json()
    if out_file:
        write_to_file(json_response, out_file, wformat)
    return json_response


def get_ticker(id=None, convert=None, out_file=None, wformat=None):
    """

    :param id:
    :param convert:
    :param out_file:
    :param wformat:
    :return:
    """
    url = '{}ticker/{}/'.format(BASE_URL, id)
    if convert:
        url = '{}?convert={}'.format(url, convert.casefold())

    response = requests.get(url)
    json_response = response.json()
    if out_file:
        write_to_file(json_response, out_file, wformat)
    return json_response


def get_global_data(convert=None, out_file=None, wformat=None):
    """

    :param convert:
    :param out_file:
    :param wformat:
    :return:
    """
    url = '{}global/'.format(BASE_URL)
    if convert:
        url = '{}?convert={}'.format(url, convert.casefold())

    response = requests.get(url)
    json_response = response.json()
    if out_file:
        write_to_file(json_response, out_file, wformat)
    return json_response
