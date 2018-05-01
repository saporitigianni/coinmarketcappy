.. -*-restructuredtext-*-

coinmarketcappy: Python wrapper and scraper for coinmarketcap data
==================================================================

.. image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
    :target: https://www.python.org/

.. image:: https://img.shields.io/pypi/v/coinmarketcappy.svg
    :target: https://pypi.org/project/coinmarketcappy/

.. image:: https://img.shields.io/pypi/l/coinmarketcappy.svg
    :target: https://pypi.org/project/coinmarketcappy/

.. image:: https://img.shields.io/pypi/pyversions/coinmarketcappy.svg
    :target: https://pypi.org/project/coinmarketcappy/

Installation
------------

To install coinmarketcappy, simply use pip:

.. code:: bash

    $ pip install coinmarketcappy

or install directly from source to include latest changes:

.. code:: bash

    $ pip install git+https://github.com/saporitigianni/coinmarketcappy.git

or clone and then install:

.. code:: bash

    $ git clone https://github.com/saporitigianni/coinmarketcappy.git
    $ cd coinmarketcappy
    $ python3 setup.py install

Usage
-----
Every method supports the arguments 'out_file' and 'wformat' to save the information to a file.
If 'out_file' is present then the info will be saved to that file. Use absolute path unless you want to save locally.
If 'wformat' is not specified, it will default to 'json' ('csv' also supported)

All methods except for available_snaps and historical_snapshots also support the 'epoch' parameter. If True it will
return all times as epochs, if False it will return them as date and time (e.g. '2018-05-01 00:19:31')

To get Historical Snapshots (taken every Sunday since 20130428) or Global Charts data:
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code:: python

    import coinmarketcappy as cmc

    # Get all available historical snapshots to choose from
    # or visit https://coinmarketcap.com/historical/
    dates = cmc.available_snaps()

    # Retrieve info for the last 10 snapshots
    snaps = cmc.historical_snapshots(dates[-10:])

    # Percentage of Market Capitalization (Dominance)
    dom = cmc.dominance()

    # Total Market Capitalization
    cap = cmc.total_market_cap()

    # Total Market Capitalization (Excluding Bitcoin)
    cap = cmc.total_market_cap(exclude_btc=True)

To get tickers and simple global data:
""""""""""""""""""""""""""""""""""""""

.. code:: python

    import coinmarketcappy as cmc

    # Get a list of all tickers organized by rank
    tickers = cmc.get_tickers()

    # Get a specific ticker (by its name not symbol. e.g. bitcoin, ethereum,... not btc, eth)
    ticker = cmc.get_ticker(name='bitcoin')

    # Get ticker's historical data (also by its name)
    temp = cmc.get_ticker_historical(name='bitcoin')

    # Get global data in ERU
    glob = cmc.get_global_data(convert='eur')

Acknowledgements
----------------

This data is being sourced either from the `coinmarketcap API <https://coinmarketcap.com/api/>`_ or is being scraped from `coinmarketcap.com <https://coinmarketcap.com/>`_.
Its `free to use <https://coinmarketcap.com/faq/>`_ so please respect their rate limit. :octocat:

Contributing
------------

Please read the `CONTRIBUTING <https://github.com/saporitigianni/coinmarketcappy/blob/master/CONTRIBUTING.md>`_ document before making changes that you would like adopted in the code.

Code of Conduct
---------------

Everyone interacting in the ``coinmarketcappy`` project's codebase, issue
trackers, chat rooms, and mailing lists is expected to follow the
`PyPA Code of Conduct <https://www.pypa.io/en/latest/code-of-conduct/>`_.

Buy me a coffee?
----------------

| ETH 0xaD1F09626b9B8e701D5f0F4a237193Df73d3C445
| BTC 199zsVqCusefv8yjdYQhUQZmLCyh75dqNV
| LTC LUBqs7VxC43ttPsQuM1jaZFmshKTAU1Rs9
