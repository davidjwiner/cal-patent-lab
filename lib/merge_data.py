#!/usr/bin/env python
from collections import Counter
import csv
import json
import notebooks.parser_new_data as parser
from os import listdir
from os import path
import re
import sys

# Patent ID -> art unit, examiner file is the output of our PAIR API scraper
# Art unit -> class file derived from pages at
# https://www.uspto.gov/patents-application-process/patent-search/understanding-patent-classifications/patent-classification


# Load a JSON dump of cases downloaded from the PTAB API
# Return a dictionary mapping case numbers to various attributes
def load_ptab_api_data(ptab_data_filename, fwd_dir):
    api_cases = json.load(open(ptab_data_filename))
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
            trial_id = case["trialNumber"].upper()
            fwd_filename = path.join(fwd_dir, "{}.txt".format(trial_id))
            if path.isfile(fwd_filename):
                decision_str = parser.parseDecision(fwd_filename)
                if decision_str == "ambiguous":
                    print("{}: decision is ambiguous for {}, leaving blank".format(fwd_filename, trial_id))
                    num_ambiguous += 1
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


# Load patent ID -> art unit and patent examiner data from USPTO-provided file
def load_patent_au_examiner_data(patent_au_ex_filename):
    patent_au_ex_data = dict()
    reader = csv.DictReader(open(patent_au_ex_filename))
    
    for row in reader:
        patent_id = row.pop("patentId")
        patent_au_ex_data[patent_id] = row
    
    return patent_au_ex_data


def build_patent_data(ptab_data, patent_au_ex_data):
    patent_data = dict()
    for case in ptab_data:
        patent_id = case.get("patentNumber")
        if not patent_id:
            print("Case {} does not have a patent number".format(case["trialNumber"]))
            continue
        
        if patent_id in patent_data:
            continue
        # Create entry for patent ID since it doesn't exist
        patent_data[patent_id] = dict()
        if patent_id in patent_au_ex_data:
            patent_data[patent_id].update(patent_au_ex_data[patent_id])
    
    return patent_data


# Write JSON representation of patent->attribute dictionary
def export_case_decisions_attrs(data_dict, out_filename):
    fd = open(out_filename, "w")
    json.dump(data_dict, fd, indent=2)
    fd.close()


# Test if any member of a collection of items is in another collection
def contains(source, has):
    for item in has:
        if item in source:
            return True
    return False


def mode(lst):
    ctr    = Counter(lst)
    values = ctr.values()
    idx    = values.index(max(values))
    items  = ctr.items()
    return items[idx][0]


def main():
    argv = sys.argv[1:]
    if len(argv) != 5:
        print("Usage: merge_data.py ptab_api_metadata_input "
              "path/to/ptab_fwd_files "
              "pair_api_metadata_input "
              "ptab_api_metadata_output "
              "patent_data_output")
        sys.exit(1)
    ptab_data_filename    = argv[0]
    fwd_dir               = argv[1]
    patent_au_ex_filename = argv[2]
    ptab_out_filename     = argv[3]
    patent_out_filename   = argv[4]
    
    ptab_data          = load_ptab_api_data(ptab_data_filename, fwd_dir)
    patent_au_ex_data = load_patent_au_examiner_data(patent_au_ex_filename)
    patent_data       = build_patent_data(ptab_data, patent_au_ex_data)
    
    # TODO: export trial, patent data to JSON files
    export_case_decisions_attrs(ptab_data, ptab_out_filename)
    export_case_decisions_attrs(patent_data, patent_out_filename)

if __name__ == "__main__":
    main()

