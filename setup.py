from setuptools import setup
from io import open


def readme():
    with open('README.rst', encoding='utf-8') as f:
        return '\n' + f.read()


MAJOR               = 1
MINOR               = 2
MICRO               = 0
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


setup(name='coinmarketcappy',
      version=VERSION,
      description='Python API wrapper and scraper for coinmarketcappy data',
      long_description=readme(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Financial and Insurance Industry',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Topic :: Office/Business :: Financial',
          'Topic :: Software Development :: Build Tools',
      ],
      keywords=[
          'forex',
          'api',
          'currencies',
          'cryptocurrency',
          'financial',
      ],
      url='https://github.com/saporitigianni/coinmarketcappy',
      download_url='https://pypi.python.org/pypi/coinmarketcappy',
      author='Gianni Saporiti',
      author_email='saporitigianni@outlook.com',
      python_requires='>=3',
      license='MIT',
      packages=['coinmarketcappy'],
      install_requires=[
          'requests',
          'bs4',
      ],
      include_package_data=True,
      zip_safe=False)
