"""Utilities to use inside of the code."""
from datetime import datetime
from pymongo import MongoClient


def mongo_connect(host, port, database, collection):
    """Connect to a local mongo collection."""
    return MongoClient(host, port)[database][collection]


def dt_now():
    """Generate a string of the present time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")