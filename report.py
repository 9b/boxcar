"""Generate a report from the all the collected data."""
from __future__ import print_function
from app.common.util import mongo_connect
import csv
import logging

logging.basicConfig(level=logging.DEBUG)

RESOLVES = mongo_connect('localhost', 27017, 'boxcar', 'resolves')


def main():
    """Main."""
    wrote = 0
    file_name = "fortune-1000-typo-report.csv"
    with open(file_name, 'w') as csvfile:
        fieldnames = ['seed', 'domain', 'status', 'datetime']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in RESOLVES.find({}, {'_id': 0, 'ip': 0}):
            writer.writerow(row)
            wrote += 1
    logging.debug("Wrote %d rows to %s" % (wrote, file_name))


if __name__ == '__main__':
    main()
