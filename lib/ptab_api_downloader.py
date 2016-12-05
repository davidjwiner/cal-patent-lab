#!/usr/bin/env python2

import csv
import json
import random
import urllib2
import ssl
import sys
import time

ptab_url_tmpl = "https://ptabdata.uspto.gov/ptab-api/trials?limit=100&offset={}"
delay_mean = 4.2
delay_stddev = delay_mean * 0.05

def get_url(url):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    response = urllib2.urlopen(url, context=ssl_context)
    contents = response.read()
    decoded = json.loads(contents)
    return decoded


def get_num_cases():
    ptab_url = ptab_url_tmpl.format(0)
    response = get_url(ptab_url)
    return response["metadata"]["count"]


def main():
    argv = sys.argv[1:]
    if len(argv) != 1:
        print("Usage: ptab_api_downloader.py path_to_output_file")
        sys.exit(1)
    
    out_filename = argv[0]
    writer = csv.writer(open(out_filename, "w"))
    
    num_cases = get_num_cases()
    counter = 0
    # Download information for up to 100 cases at a time
    for offset in range(0, num_cases, 100):
        ptab_url = ptab_url_tmpl.format(offset)
        response = get_url(ptab_url)
        for case in response["results"]:
            counter += 1
            print("Processing case {}/{}".format(counter, num_cases))
            case_no = case["trialNumber"]
            patent_no = case["patentNumber"]
            status = case["prosecutionStatus"]
            writer.writerow((case_no, patent_no, status))
        # Add random delay between consecutive requests
        delay = round(abs(random.gauss(delay_mean, delay_stddev)), 2)
        print("Sleeping {}s".format(delay))
        time.sleep(delay)

if __name__ == "__main__":
    main()
