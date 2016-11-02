ELEX-FTP-LOADER
===============

A simple script for loading AP elections **results only** into a
Postgres database using the ``COPY`` function and CSV.

Prerequisites
-------------

-  We recommend `How to set up your Mac to develop news applications
   like we
   do <http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html>`__
   for setting up your development environment.

Installation
------------

Clone the repository, create a virtualenvironment and install
requirements.

::

    git clone git@github.com:newsdev/elex-ftp-loader.git
    mkvirtualenv elex-ftp-loader
    cd elex-ftp-loader
    pip install -r requirements.txt

Export environment variables you need.

::

    export RACEDATE=<YYYY-MM-DD>
    export AP_FTP_USER=<YOUR AP FTP USERNAME>
    export AP_FTP_PASS=<YOUR AP FTP PASSWORD>

Usage
-----

If you're using something like `The New York Times's AP election
loader <https://github.com/newsdev/elex-loader>`__, ``elex-ftp-loader``
is a drop-in replacement.

To initialize your database with races, reporting units and candidates:

::

    ./init.sh

To get results one time:

::

    ./update.sh

To run a daemon which inserts results into the database every 60
seconds:

::

    ./daemon.sh
