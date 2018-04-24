from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


MAJOR               = 0
MINOR               = 1
MICRO               = 0
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


setup(name='coinmarketcappy',
      version=VERSION,
      description='Python API wrapper and scraper for coinmarketcap data',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
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
          'financial',
      ],
      url='https://github.com/saporitigianni/coinmarketcappy',
      download_url='https://pypi.python.org/pypi/coinmarketcappy',
      author='Gianni Saporiti',
      author_email='saporitigianni@outlook.com',
      python_requires='>=3',
      license='MIT',
      packages=['coinmarketcap'],
      install_requires=[
          'requests',
          'bs4',
      ],
      include_package_data=True,
      zip_safe=False)
