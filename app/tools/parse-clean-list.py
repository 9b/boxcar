"""Identify how many items get generated per level of degree for input."""
from __future__ import print_function
import logging
import os

logging.basicConfig(level=logging.DEBUG)

COMPANY_DATA = os.getcwd() + "/app/data/clean-list.txt"


def main():
    """Main."""
    handle = open(COMPANY_DATA, 'r').readlines()
    for x in handle:
        company = (x.split(",")[-2]).replace("http://www.", "")
        print(company)


if __name__ == '__main__':
    main()
