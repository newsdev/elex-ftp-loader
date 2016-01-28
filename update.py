#!/usr/bin/env python

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

        self.results = None

        self.load_results(test=kwargs.get('test', False))
        self.output_csv()

    def load_results(self, test=False):
        e = Election(electiondate=self.racedate, username=AP_FTP_USER, password=AP_FTP_PASS, test=test)
        self.results = e.candidate_reporting_units

    def output_csv(self, outputfile=None):
        fieldnames = self.results[0].serialize().keys()
        if outputfile:
            with open(outputfile, 'w') as writefile:
                writer = csv.DictWriter(writefile, fieldnames=fieldnames)
                writer.writeheader()
                for r in self.results:
                    writer.writerow(r.serialize())
        else:
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.results:
                writer.writerow(r.serialize())

if __name__ == "__main__":
    l = Load(test=True, outputfile=None)