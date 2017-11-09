import csv
import sys

import elex_ftp.fields as fields

def output_csv(output):
    """
    Handles CSV output.
    Requires an iterable.
    """
    writer = csv.DictWriter(sys.stdout, fieldnames=fields.FIELDNAMES)
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