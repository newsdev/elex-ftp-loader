#!/usr/bin/env python

import argparse
import csv
import datetime
import glob
import itertools
import os
import sys
import subprocess
import time

import elex_ftp.states as states

import untangle


FIELDS = {
    'id': None,
    'raceid': None,
    'racetype': None,
    'racetypeid': None,
    'ballotorder': None,
    'candidateid': None,
    'description': None,
    'delegatecount': None,
    'electiondate': None,
    'electtotal': None,
    'electwon': None,
    'fipscode': None,
    'first': None,
    'incumbent': None,
    'initialization_data': None,
    'is_ballot_position': None,
    'last': None,
    'lastupdated': None,
    'level': None,
    'national': None,
    'officeid': None,
    'officename': None,
    'party': None,
    'polid': None,
    'polnum': None,
    'precinctsreporting': None,
    'precinctsreportingpct': None,
    'precinctstotal': None,
    'reportingunitid': None,
    'reportingunitname': None,
    'runoff': None,
    'seatname': None,
    'seatnum': None,
    'statename': None,
    'statepostal': None,
    'test': None,
    'uncontested': None,
    'candidate_unique_id': None,
    'votecount': None,
    'votepct': None,
    'winner':None
}

FIELDNAMES = ('id','raceid','racetype','racetypeid','ballotorder','candidateid','description','delegatecount','electiondate','electtotal','electwon','fipscode','first','incumbent','initialization_data','is_ballot_position','last','lastupdated','level','national','officeid','officename','party','polid','polnum','precinctsreporting','precinctsreportingpct','precinctstotal','reportingunitid','reportingunitname','runoff','seatname','seatnum','statename','statepostal','test','uncontested','candidate_unique_id','votecount','votepct','winner')


def output_csv(output):
    """
    Handles CSV output.
    Requires an iterable.
    """
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDNAMES)
    writer.writeheader()
    for o in output:
        writer.writerow(o)


def str_to_bool(possible_bool):
    """
    Attempts to coerce various strings to bool.
    Fails to None
    """
    if possible_bool:
        if possible_bool.lower() in ['t', '1', 'yes', 'true']:
            return True

        if possible_bool.lower() in ['f', '0', 'no', 'false']:
            return False

    return False


def parse_race(race_path):
    """
    Handles the parsing of the XML file.
    Transforms from nested XML to lists of candidate-reportingunits.
    Output is a list of dicts.
    """
    obj = untangle.parse(race_path)

    payload = []
    race_data = {}

    race_data['id'] = "%s-%s" % (obj.Vote.Race.ReportingUnit['StatePostal'], obj.Vote.Race['ID'])
    race_data['electiondate'] = obj.Vote['ElectionDate']
    race_data['raceid'] = obj.Vote.Race['ID']
    race_data['racetype'] = obj.Vote.Race['Type']
    race_data['racetypeid'] = obj.Vote.Race['TypeID']
    race_data['officeid'] = obj.Vote.Race['OfficeID']
    race_data['officename'] = obj.Vote.Race['OfficeName']
    race_data['description'] = obj.Vote.Race['Desc']
    race_data['seatname'] = obj.Vote.Race['SeatName']
    race_data['seatnum'] = obj.Vote.Race['SeatNum']
    race_data['test'] = str_to_bool(obj.Vote['Test'])
    race_data['level'] = obj.Vote.Race.ReportingUnit['Level']
    race_data['fipscode'] = obj.Vote.Race.ReportingUnit['FIPSCode']

    race_data['national'] = True
    race_data['reportingunitname'] = obj.Vote.Race.ReportingUnit['Name']
    race_data['statepostal'] = obj.Vote.Race.ReportingUnit['StatePostal']
    race_data['statename'] = states.STATE_ABBR_LOOKUP[race_data['statepostal']]
    race_data['is_ballot_position'] = False

    if race_data['officeid'] == 'I':
        race_data['is_ballot_position'] = True

    if race_data['level'] == 'subunit':
        race_data['level'] = 'county'
    if race_data['statepostal'] == "ME":
        race_data['reportingunitid'] = "township"

    if race_data['level'] == 'state':
        race_data['reportingunitid'] = "state-%s-1" % obj.Vote.Race.ReportingUnit['StatePostal']
    else:
        race_data['reportingunitid'] = "%s-%s-%s" % (race_data['level'], race_data['fipscode'], race_data['raceid'])

    race_data['precinctsreporting'] = obj.Vote.Race.ReportingUnit.Precincts['Reporting']
    race_data['precinctstotal'] = obj.Vote.Race.ReportingUnit.Precincts['Total']
    race_data['precinctsreportingpct'] = 0.0

    try:
        race_data['precinctsreportingpct'] = (float(race_data['precinctsreporting']) / float(race_data['precinctstotal']))
    except:
        pass

    total_votes = sum(int(c['VoteCount']) for c in obj.Vote.Race.ReportingUnit.Candidate)

    for c in obj.Vote.Race.ReportingUnit.Candidate:
        cand = dict(race_data)
        cand['candidateid'] = c['ID']
        cand['candidate_unique_id'] = "polid-%s" % c['PolID']
        cand['polid'] = c['PolID']
        cand['votecount'] = c['VoteCount']
        cand['last'] = c['Last']
        cand['first'] = c['First']
        cand['party'] = c['Party']
        cand['incumbent'] = str_to_bool(c['Incumbent'])
        cand['uncontested'] = str_to_bool(c['Uncontested'])

        cand['votepct'] = 0.0
        cand['winner'] = False
        cand['runoff'] = False

        if c['Winner'] == "X":
            cand['winner'] = True

        if c['Winner'] == "R":
            cand['runoff'] = True

        try:
            if total_votes > 0:
                cand['votepct'] = (float(cand['votecount']) / total_votes)
        except:
            pass

        payload.append(cand)

    return payload


class Load(object):
    ftp_site = None
    ftp_path = None
    ftp_user = None
    ftp_pass = None
    timestamp = None
    data_path = None
    states = None
    xml_urls = None
    xml_paths = None

    def parse_xml(self):
        output_csv(itertools.chain.from_iterable([parse_race(race_path) for race_path in glob.glob('%s*.xml' % self.data_path)]))

    def unzip_xml_zips(self):
        os.system('echo "%s" | xargs -P 25 -n 1 unzip -d %s > /dev/null 2>&1' % (self.xml_paths, self.data_path))

    def download_xml_zips(self):
        os.system('echo "%s" | xargs -P 25 -n 3 curl --silent -L' % self.xml_urls)

    def generate_xml_urls(self):
        self.xml_urls = ""
        for state in self.states:
            ftp_site = "ftp://%s:%s@%s" % (self.ftp_user, self.ftp_pass, self.ftp_site)
            ftp_path = self.ftp_path % (state, state)
            file_name = "%s.zip" % state
            self.xml_urls += '%s%s\n-o\n%s%s\n' % (ftp_site, ftp_path, self.data_path, file_name)

    def clean_old_files(self):
        for state in states.STATES:
            os.system('rm -rf %s%s.zip' % (self.data_path, state))
            os.system('rm -rf %s*%s*.xml' % (self.data_path, state))

    def set_states(self, states=None):
        if states:
            self.states = [s.strip().upper() for s in states.split(',')]
        else:
            self.states = states.STATES

    def xml_path_for_state(self, state):
        return("%s%s.zip" % (self.data_path, state))

    def generate_xml_paths(self):
        self.xml_paths = "\n".join([self.xml_path_for_state(s) for s in self.states])

    def __init__(self, **kwargs):
        self.ftp_site = os.environ.get('AP_FTP_SITE', 'electionsonline.ap.org')
        self.ftp_path = '//%s/xml/%s_erml.zip'
        self.timestamp = str(int(time.mktime(datetime.datetime.timetuple(datetime.datetime.now()))))
        self.data_path = os.environ.get('AP_FTP_LOCAL_DATA_PATH', '/tmp/%s/' % self.timestamp)
        self.ftp_user = os.environ.get('AP_FTP_USER', None)
        self.ftp_pass = os.environ.get('AP_FTP_PASS', None)

        self.set_states(states=kwargs.get('states', None))
        self.generate_xml_paths()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--states', action='store', help="A comma-separated list of state abbreviations to parse.")
    args = parser.parse_args()

    l = Load(states=args.states)
    l.clean_old_files()
    l.generate_xml_urls()
    l.generate_xml_paths()
    l.download_xml_zips()
    l.unzip_xml_zips()
    l.parse_xml()

if __name__ == '__main__':
    main()
