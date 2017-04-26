#!/usr/bin/env python2
from collections import Counter
import csv
import json
import notebooks.parser_new_data as parser
from os import listdir
from os import path
import re
import sys


# Takes the outputs of the PTAB and PAIR downloaders
# Extracts decisions for cases and adds empty entries for patents involved
# in PTAB cases but without data from the PAIR downloader
# Outputs JSON files containing data for cases and patents


# Load a JSON dump of cases downloaded from the PTAB API
# Return a dictionary mapping case numbers to various attributes
def load_ptab_api_data(ptab_cases_filename, fwd_dir):
    api_cases = json.load(open(ptab_cases_filename))
    # Counters for statistics
    num_decisions     = 0
    num_inval         = 0
    num_adv_judgement = 0
    num_denied        = 0
    num_ambiguous     = 0
    num_missing       = 0
    for case in api_cases:
        if case["prosecutionStatus"] == "Terminated-Denied":
            case["invalidated"] = False
            case["denied"]      = True
            num_decisions += 1
            num_denied    += 1
        elif case["prosecutionStatus"] == "Terminated-Adverse Judgment":
            case["invalidated"] = True
            case["denied"]      = False
            num_decisions     += 1
            num_adv_judgement += 1
        elif case["prosecutionStatus"] == "FWD Entered":
            # Find and parse the decision document to get the actual decision
            trial_id = case["trialNumber"].upper()
            fwd_filename = path.join(fwd_dir, "{}.txt".format(trial_id))
            # If a file with the right name exists:
            if path.isfile(fwd_filename):
                # Extract the decision from the file
                decision_str = parser.parseDecision(fwd_filename)
                # If we couldn't cleanly parse a decision, then don't try to guess
                if decision_str == "ambiguous":
                    print("{}: decision is ambiguous for {}, leaving blank".format(fwd_filename, trial_id))
                    num_ambiguous += 1
                # Otherwise, record the decision that we parsed
                else:
                    case["invalidated"] = (decision_str == "invalidated")
                    case["denied"]      = False
                    num_decisions += 1
                    if case["invalidated"]:
                        num_inval += 1
            else:
                # Missing final decision file, so no information can be extracted
                print("Missing final decision file for {}".format(trial_id))
                num_missing += 1
        # Else: there's no information about invalidation or denied petitions
    print("Invalidated: {}, denied: {}, adverse judgment: {}, ambiguous: {}, missing: {}, total: {}".format(
            num_inval, num_denied, num_adv_judgement, num_ambiguous, num_missing, num_decisions))
    return api_cases


# Load patent ID -> attributes file from PAIR downloader output
def load_patent_attrs(patent_attr_filename):
    patent_attrs = dict()
    reader = csv.DictReader(open(patent_attr_filename))
    
    for row in reader:
        patent_id = row.pop("patentId")
        patent_attrs[patent_id] = row
    return patent_attrs


# Create a patent -> attributes dictionary for all patents involved in PTAB cases
# and try to copy data from the given patent attributes dictionary
def build_contested_patent_data(contested_patent_data, patent_attrs):
    contested_patent_data = dict()
    for case in ptab_cases:
        patent_id = case.get("patentNumber")
        # Skip cases without an associated patent number
        if not patent_id:
            print("Case {} does not have a patent number".format(case["trialNumber"]))
            continue
        
        # Skip patent numbers that we have already processed
        if patent_id in contested_patent_data:
            continue
        # Create and populate entry for new patent number
        contested_patent_data[patent_id] = dict()
        if patent_id in patent_attrs:
            contested_patent_data[patent_id] = patent_attrs[patent_id]
    return contested_patent_data


# Write JSON representation of the given dictionary to the given file
def export_as_json(data_dict, out_filename):
    fd = open(out_filename, "w")
    json.dump(data_dict, fd, indent=2)
    fd.close()


# Test if any member of a collection of items is in another iterable
def contains_any(needles, haystack):
    for item in needles:
        if item in haystack:
            return True
    return False


# Compute the most frequently occurring data value in an iterable
# If there are more than one, then one will be arbitrarily chosen
def mode(lst):
    ctr    = Counter(lst)
    items  = ctr.items()
    values = ctr.values()
    idx    = values.index(max(values))
    return items[idx][0]


def main():
    argv = sys.argv[1:]
    if len(argv) != 5:
        print("Usage: merge_data.py ptab_api_metadata_input "
              "path/to/ptab_fwd_files/ "
              "pair_api_metadata_input "
              "ptab_api_metadata_output "
              "patent_data_output")
        sys.exit(1)
    ptab_cases_filename  = argv[0]
    fwd_dir              = argv[1]
    patent_attr_filename = argv[2]
    ptab_out_filename    = argv[3]
    patent_out_filename  = argv[4]
    
    ptab_cases            = load_ptab_api_data(ptab_cases_filename, fwd_dir)
    patent_attrs          = load_patent_attrs(patent_attr_filename)
    contested_patent_data = build_contested_patent_data(ptab_cases, patent_attrs)
    
    # Export trial, patent data to JSON files
    export_as_json(ptab_cases, ptab_out_filename)
    export_as_json(contested_patent_data, patent_out_filename)

if __name__ == "__main__":
    main()

