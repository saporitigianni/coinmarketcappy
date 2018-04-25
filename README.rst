.. -*-restructuredtext-*-

coinmarketcappy: Python wrapper and scraper for coinmarketcap data
=========================

.. image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
    :target: https://www.python.org/

.. image:: https://img.shields.io/pypi/v/coinmarketcappy.svg
    :target: https://pypi.org/project/coinmarketcappy/

.. image:: https://img.shields.io/pypi/l/coinmarketcappy.svg
    :target: https://pypi.org/project/requcoinmarketcappyests/

.. image:: https://img.shields.io/pypi/pyversions/coinmarketcappy.svg
    :target: https://pypi.org/project/coinmarketcappy/

Installation
------------

To install coinmarketcappy, simply use pip:

.. code-block:: bash

    $ pip install coinmarketcappy

Usage
-----
Every method supports the arguments 'out_file' and 'wformat' to save the information to a file.
If 'outfile' is present then the info will be saved to that file. Use absolute path unless you want to save locally.
If 'wformat' is not specified, it will default to 'json' ('csv' also supported for historical_snapshots)

To get historical snapshots (Taken every Sunday since 20130428)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    import coinmarketcappy as cmc

    # Get all available historical snapshots to choose from
    dates = cmc.available_snaps()

    # Retrieve info for the last 10 snapshots
    snaps = cmc.historical_snapshots(dates[-10:])

    # Percentage of Market Capitalization (Dominance)
    dom = cmc.dominance()

    # Total Market Capitalization
    cap = cmc.total_market_cap()

    # Total Market Capitalization (Excluding Bitcoin)
    cap = cmc.total_market_cap(exclude_btc=True)

Contributing
------------

Please read the `CONTRIBUTING <https://github.com/saporitigianni/coinmarketcappy/blob/master/CONTRIBUTING.md>`_ document before making changes that you would like adopted in the code.

Code of Conduct
---------------

Everyone interacting in the ``coinmarketcappy`` project's codebases, issue
trackers, chat rooms, and mailing lists is expected to follow the
`PyPA Code of Conduct <https://www.pypa.io/en/latest/code-of-conduct/>`_.
