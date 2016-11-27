"""Identify how many items get generated per level of degree for input."""
from __future__ import print_function
from app.common.misspellings import typoGenerator
import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)

COMPANY_DATA = os.getcwd() + "/app/data/fortune-1000.txt"


def generate_perms(domain, degree):
    """Generate a bunch of perms based on a seed domain."""
    logging.info("Generating perms for %s." % domain)
    core, tld = domain.split('.')
    variations = [x.lower() + "." + tld for x in typoGenerator(core, degree)]
    dedup = list(set(variations))
    logging.info("Generated %d perms for %s." % (len(dedup), domain))
    return dedup


def main():
    """Main."""
    init = sys.argv[1]
    for i in range(0, 5):
        report = generate_perms(init, i)
        logging.debug("Perm report for %s" % init)
        logging.debug("Degree %d, Results %d" % (i, len(report)))


if __name__ == '__main__':
    main()
