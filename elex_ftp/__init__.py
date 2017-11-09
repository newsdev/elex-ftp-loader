#!/usr/bin/env python

import argparse
import datetime
import glob
import itertools
import os
import time

import elex_ftp.fields as fields
import elex_ftp.states as states
import elex_ftp.utils as utils

import untangle


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
    race_data['test'] = utils.str_to_bool(obj.Vote['Test'])
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
        cand['incumbent'] = utils.str_to_bool(c['Incumbent'])
        cand['uncontested'] = utils.str_to_bool(c['Uncontested'])

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
        utils.output_csv(itertools.chain.from_iterable([parse_race(race_path) for race_path in glob.glob('%s*.xml' % self.data_path)]))

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

    def clean_files(self):
        for state in states.STATES:
            os.system('rm -rf %s%s.zip' % (self.data_path, state))
            os.system('rm -rf %s*%s*.xml' % (self.data_path, state))

    def set_states(self, states_to_parse=None):
        if states_to_parse:
            self.states = [s.strip().upper() for s in states_to_parse.split(',')]
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
        os.system('mkdir -p %s' % self.data_path)
        self.ftp_user = os.environ.get('AP_FTP_USER', None)
        self.ftp_pass = os.environ.get('AP_FTP_PASS', None)

        self.set_states(states_to_parse=kwargs.get('states_to_parse', None))
        self.generate_xml_paths()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--states', action='store', help="A comma-separated list of state abbreviations to parse.")
    args = parser.parse_args()

    l = Load(states_to_parse=args.states)
    l.generate_xml_urls()
    l.generate_xml_paths()
    l.download_xml_zips()
    l.unzip_xml_zips()
    l.parse_xml()
    l.clean_files()

if __name__ == '__main__':
    main()
