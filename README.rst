Boxcar Processor
================
Boxcar processor is a simple system that takes the fortune 1000 company domains and puts them through a typo-permutation engine. These return values are stored locally so save time and then resolved in order to identify which domains are active and which aren't. Results are saved inside of a local MongoDB instance that can later be used to guide processing later on or generate an output report.

Usage
-----
In order to run, make sure you have a local mongo instance listening on 27017 and install the requirements:

    python install -r requirements.txt

Then kick off the actual worker process (this will run a while):

    python run.py

Output is set to DEBUG by default and will let you know what's happening as data is being processed. Various configuration options exist at the top of the run.py file and can be adjusted to meet your needs.

Extras
------
Tools for processing help can be found within app/tools. Additionally, there is a report.py file that will extract the data from the mongoDB collections and place them in a CSV report. A sample report has been placed inside of app/samples.
