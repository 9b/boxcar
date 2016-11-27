"""Generate variations of fortune 1000 domains and resolve them."""
from __future__ import print_function
from app.common.misspellings import typoGenerator
from app.common.util import mongo_connect, dt_now
from gevent.pool import Pool
import dns.resolver
import logging
import os
import pymongo
import sys

logging.basicConfig(level=logging.DEBUG)

COMPANY_DATA = os.getcwd() + "/app/data/fortune-1000.txt"
PERMS = mongo_connect('localhost', 27017, 'boxcar', 'perms')
RESOLVES = mongo_connect('localhost', 27017, 'boxcar', 'resolves')
PROCESSED = 0
STATE = list()
REPROCESS_RESOLVED = False
REPROCESS_PROCESSED = False
DEGREE = 2
HARD_SKIP = True
CONCURRENT = 200
SKIP_VALUES = ['', '"', "'"]

RESOLVER = dns.resolver.Resolver()
RESOLVER.nameservers = ['8.8.8.8', '8.8.4.4']
RESOLVER.retry_servfail = False
RESOLVER.timeout = 2
RESOLVER.lifetime = 1


def resolve(seed, domain):
    """Attempt to resolve the domain and save the state in memory."""
    global STATE, PROCESSED
    try:
        results = RESOLVER.query(domain)
        results = [str(x) for x in results]
        record = {'seed': seed, 'domain': domain, 'ip': results,
                  'status': 'resolved'}
        logging.debug("[%d] State saved: (%s, %s)" % (PROCESSED,
                                                      domain, results))
    except:
        record = {'seed': seed, 'domain': domain, 'ip': None,
                  'status': 'failed'}
        logging.debug("[%d] No resolution for %s." % (PROCESSED, domain))
    record['datetime'] = dt_now()
    STATE.append(record)
    PROCESSED += 1


def generate_perms(domain):
    """Generate a bunch of perms based on a seed domain."""
    logging.info("Generating perms for %s." % domain)
    core, tld = domain.split('.')
    core = core.replace("-", "")
    variations = [x.lower() + "." + tld for x in typoGenerator(core, DEGREE)]
    dedup = list(set(variations))
    logging.info("Generated %d perms for %s." % (len(dedup), domain))
    return dedup


def get_perms(company):
    """Get perms from the DB or generate new ones."""
    cache = PERMS.find_one({'seed': company}, {'_id': 0})
    if not cache:
        logging.info("Item not currently in cache!")
        perms = generate_perms(company)
        PERMS.insert({'seed': company, 'perms': perms})
        was_cached = False
    else:
        perms = cache['perms']
        was_cached = True
    return (perms, was_cached)


def prune_resolved(perms):
    """Remove any resolved domains just to save time."""
    to_process = list()
    for item in perms:
        cache = RESOLVES.find_one({'domain': item}, {'_id': 0})
        if not cache:
            to_process.append(item)
            continue
        if cache['ip']:
            logging.debug("Pruned %s from items to process." % item)
            continue
        to_process.append(item)
    diff = len(perms) - len(to_process)
    logging.info("Pruned %d items from the job list." % diff)
    return to_process


def prune_processed(perms):
    """Remove any processed domains just to save time."""
    to_process = list()
    for item in perms:
        cache = RESOLVES.find_one({'domain': item}, {'_id': 0})
        if not cache:
            to_process.append(item)
            continue
    diff = len(perms) - len(to_process)
    logging.info("Pruned %d items from the job list." % diff)
    return to_process


def main():
    """Main."""
    global DEGREE, STATE, PROCESSED
    pool = Pool(CONCURRENT)
    handle = open(COMPANY_DATA, 'r').readlines()
    companies = [x.split(',')[0].strip() for x in handle]
    if len(sys.argv) >= 2:
        logging.info("Running in DEBUG mode.")
        companies = [sys.argv[1]]
        DEGREE = 1

    for company in companies:
        if company in SKIP_VALUES:
            continue
        perms, cache_state = get_perms(company)
        if HARD_SKIP and cache_state:
            logging.info("Hard skipping %s since its processed." % company)
            continue
        if not REPROCESS_RESOLVED:
            perms = prune_resolved(perms)
        if not REPROCESS_PROCESSED:
            perms = prune_processed(perms)
        logging.info("Spawning jobs for %d domains." % (len(perms)))
        if len(perms) == 0:
            continue
        _ = [pool.spawn(resolve, company, url) for url in perms]
        pool.join()
        logging.info("Resolutions complete.")
        PROCESSED = 0
        try:
            RESOLVES.insert(doc_or_docs=STATE, continue_on_error=True)
        except pymongo.errors.DuplicateKeyError:
            logging.error("Ran into duplications issues when saving state.")
            pass
        STATE = list()
        logging.info("State was saved locally.")

if __name__ == '__main__':
    main()
