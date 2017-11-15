import csv
import os
import unittest

from elex_ftp.fields import FIELDNAMES

class ElectionResultsTestCase(unittest.TestCase):
    data_path = '%s/data/results_national_2017-11-07-zeros.csv' % os.path.dirname(os.path.realpath(__file__))
    results = None

    def setUp(self, **kwargs):
        with open(self.data_path, 'r') as readfile:
            self.results = list(csv.DictReader(readfile))

    def test_fields_vs_headers(self):
        """
        Makes sure our fields match our headers.
        """
        test_headers = set(self.results[0].keys())
        control_headers = set(FIELDNAMES)
        self.assertEqual(test_headers, control_headers)