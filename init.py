#!/usr/bin/env python

import argparse
import csv
import os
import sys

from elections import Election

AP_FTP_USER = os.environ.get('AP_FTP_USER', None)
AP_FTP_PASS = os.environ.get('AP_FTP_PASS', None)

class Load(object):

    def __init__(self, **kwargs):
        self.racedate = None

        if os.environ.get('RACEDATE', None):
            self.racedate = os.environ['RACEDATE']

        if kwargs.get('racedate', None):
            self.racedate = kwargs['racedate']

        self.races = None
        self.reporting_units = None
        self.candidates = None
        self.ballot_measures = None

        if os.path.isfile('races.csv') and os.path.isfile('reporting_units.csv') and os.path.isfile('candidates.csv') and os.path.isfile('ballot_measures.csv'):
            self.load_from_files()
        else:
            self.load_results(test=kwargs.get('test', False))

        self.output(self.races, 'races.csv')
        self.output(self.reporting_units, 'reporting_units.csv')
        self.output(self.candidates, 'candidates.csv')

        parser = argparse.ArgumentParser(description='Output AP election data as CSV.')
        parser.add_argument('--races', help='print races to stdout', dest='races', action='store_true')
        parser.add_argument('--reporting_units', help='print reporting units to stdout', dest='reporting_units', action='store_true')
        parser.add_argument('--candidates', help='print candidates to stdout', dest='candidates', action='store_true')

        for k,v in vars(parser.parse_args()).items():
            if v:
                self.output(getattr(self, k))

    def load_from_files(self):
        with open('races.csv', 'r') as readfile:
            self.races = list(csv.DictReader(readfile))

        with open('reporting_units.csv', 'r') as readfile:
            self.reporting_units = list(csv.DictReader(readfile))

        with open('candidates.csv', 'r') as readfile:
            self.candidates = list(csv.DictReader(readfile))

    def load_results(self, test=False):
        e = Election(electiondate=self.racedate, username=AP_FTP_USER, password=AP_FTP_PASS, test=test)
        self.races = list([r.serialize() for r in e.races])
        self.reporting_units = list([r.serialize() for r in e.reporting_units])
        self.candidates = list([r.serialize() for r in e.candidates])

    def output(self, data, outputfile=None):
        fieldnames = data[0]
        if outputfile:
            with open(outputfile, 'w') as writefile:
                writer = csv.DictWriter(writefile, fieldnames=fieldnames)
                writer.writeheader()
                for r in data:
                    writer.writerow(r)
        else:
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            for r in data:
                writer.writerow(r)

if __name__ == "__main__":
    l = Load(test=True)