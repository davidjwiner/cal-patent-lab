#!/usr/bin/env python2

import json
from os import makedirs
from os import path
import random
import urllib2
from subprocess import call
import ssl
import sys
import time

ptab_url_tmpl = "https://ptabdata.uspto.gov/ptab-api/trials?limit=100&offset={}"
delay_mean = 1.0
delay_stddev = delay_mean * 0.07

def get_raw_contents_at(url):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    response = urllib2.urlopen(url, context=ssl_context)
    contents = response.read()
    return contents


def get_json_at(url):
    return json.loads(get_raw_contents_at(url))


def get_num_cases():
    ptab_url = ptab_url_tmpl.format(0)
    response = get_json_at(ptab_url)
    return response["metadata"]["count"]


def random_sleep():
    delay = round(abs(random.gauss(delay_mean, delay_stddev)), 2)
    time.sleep(delay)


# Test if any member of a collection of items is in another collection
def contains(source, has):
    for item in has:
        if item in source:
            return True
    return False


def get_case_metadata():
    num_cases = get_num_cases()
    cases = []
    counter = 0
    # Download information for up to 100 cases at a time
    for offset in range(0, num_cases, 100):
        ptab_url = ptab_url_tmpl.format(offset)
        response = get_json_at(ptab_url)
        cases.extend(response["results"])
        counter += len(response["results"])
        print("Downloaded {} of {} cases".format(counter, num_cases))
        # Add random delay between consecutive requests
        random_sleep()
    return cases


def download_fwd_docs(cases, output_dir):
    counter = 0
    num_cases = len(cases)
    
    # Remove cases that don't have final written decisions
    fwd_cases = []
    for case in cases:
        trial_id = case["trialNumber"].upper()
        doc_filename = path.join(output_dir, "{}.pdf".format(trial_id))
        if case["prosecutionStatus"] == "FWD Entered" and not path.isfile(doc_filename):
            fwd_cases.append(case)
    num_cases = len(fwd_cases)
    print("Found {} cases with final decisions to be downloaded".format(num_cases))
    
    for case in fwd_cases:
        counter += 1
        trial_id = case["trialNumber"].upper()
        print("[{}/{}] Processing {}".format(counter, num_cases, trial_id))
        doc_filename = path.join(output_dir, "{}.pdf".format(trial_id))
        
        # Find link to this case's documents
        docs = None
        for case_link in case["links"]:
            if case_link["rel"] == "documents":
                docs = get_json_at(case_link["href"])
                break
        random_sleep()
        
        # Find the document that has the final written decision
        if docs is None:
            print("Could not fetch document metadata for {}".format(trial_id))
            continue
        docs = docs["results"]
        fwd_doc_link = None
        for doc in docs:
            if fwd_doc_link is not None:
                break
            if doc["type"].lower() == "final decision" \
                    or contains(doc["title"].lower(), ["final written decision", 
                                                       "termination decision document"]):
                if "expunged" in doc["title"].lower():
                    continue
                for doc_link in doc["links"]:
                    if doc_link["rel"] == "download":
                        fwd_doc_link = doc_link["href"]
                        break
        
        # Download and save the decision document
        if fwd_doc_link is None:
            print("Could not find decision document for {}".format(trial_id))
            continue
        try:
            doc_contents = get_raw_contents_at(fwd_doc_link)
        except urllib2.HTTPError as err:
            print(err)
            continue
        
        with open(doc_filename, "w") as fd:
            fd.write(doc_contents)
        
        text_filename = path.join(output_dir, "{}.txt".format(trial_id))
        call(["pdftotext", doc_filename, text_filename])
        random_sleep()


def main():
    argv = sys.argv[1:]
    if len(argv) != 2:
        print("Usage: ptab_api_downloader.py path/to/case_data_output path/to/fwd_files")
        sys.exit(1)
    
    casedata_filename = argv[0]
    output_dir = argv[1]
    # Create output directory to hold decision documents if it doesn't exist
    if not path.exists(output_dir):
        makedirs(output_dir)
    
    cases = get_case_metadata()
    
    # Write case information as JSON to output file
    casedata_fd = open(casedata_filename, "w")
    json.dump(cases, casedata_fd, indent=2)
    casedata_fd.close()
    
    # Download decision documents for cases with final written decisions
    download_fwd_docs(cases, output_dir)


if __name__ == "__main__":
    main()
