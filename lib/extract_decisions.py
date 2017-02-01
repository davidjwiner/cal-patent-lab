#!/usr/bin/env python
from collections import Counter
import json
from os import listdir
from os import path
import notebooks.parser_new_data as parser
import sys

# Patent ID -> class file downloaded from
# https://bulkdata.uspto.gov/data2/patent/classification/mcfpat.zip
# Art unit -> class file derived from pages at
# https://www.uspto.gov/patents-application-process/patent-search/understanding-patent-classifications/patent-classification


# Load a JSON dump of cases downloaded from the PTAB API
# Return a dictionary mapping case numbers to various attributes
def load_ptab_api_data(api_data_filename, fwd_dir):
    api_cases = json.load(open(api_data_filename))
    num_decisions = 0
    num_inval = 0
    num_denied = 0
    num_ambiguous = 0
    num_missing = 0
    for case in api_cases:
        if case["prosecutionStatus"] == "Terminated-Denied":
            case["invalidated"] = False
            case["denied"]      = True
            num_decisions += 1
            num_denied += 1
        elif case["prosecutionStatus"] == "Terminated-Adverse Judgment":
            case["invalidated"] = True
            case["denied"]      = False
            num_decisions += 1
            num_inval += 1
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
    print("Invalidated: {}, denied: {}, ambiguous: {}, missing: {}, total: {}".format(num_inval, num_denied, num_ambiguous, num_missing, num_decisions))
    return api_cases


# Load patent ID -> class data from USPTO-provided file
# Return a dictionary mapping patent IDs to class/subclass tuples
def load_patent_class_data(patent_class_filename):
    fd = open(patent_class_filename)
    patent_class_data = dict()
    for line in fd:
        line = line.strip()
        # Skip cross-reference classifications since they don't decide which
        # tech office reviews this patent
        if line[-1] == "X":
            continue
        patent_id = normalize_patent_id(line[:7])  # First 7 characters are patent ID
        main_class, subclass = normalize_class_subclass(line[7:16])  # Next 9 characters are class/subclass
        patent_class_data[patent_id] = (main_class, subclass)
    
    return patent_class_data


# Strip out leading padding zeros from input string
# Input: 7-character string containing patent ID (e.g. 1234567, RE12345)
def normalize_patent_id(patent_id_str):
    # Strip leading zeros after any lettered prefixes like PP or RE
    prefix, num = re.search("(\w*?)(\d+)", patent_id_str).groups()
    num = str(int(num))
    return prefix.upper() + num


# Separate class and subclass, and strip leading padding zeros
# Input: 9-character string containing both the class and subclass
def normalize_class_subclass(class_subclass_str):
    class_str = class_subclass_str[:3]
    subclass_str = class_subclass_str[3:]
    class_str = re.search("0+(\d+)", class_str).group(1)
    return class_str, subclass_str


def load_au_class_data(au_class_filename):
    pass


def find_au_for(patent_class_data, class_id, subclass_id):
    pass



def build_patent_data(api_data, patent_class_data, au_class_data):
    patent_data = dict()
    for case in api_data:
        trial_id  = case["trialNumber"].upper()
        patent_id = case.get("patentNumber")
        if not patent_id:
            print("Case {} does not have a patent number".format(trial_id))
            continue
        # Create entry for patent ID if it doesn't exist
        if patent_id not in patent_data:
            patent_data[patent_id] = dict()
        patent_entry = patent_data[patent_id]
        # TODO: get class/subclass for patent ID
        # TODO: look up AU for class/subclass, add it to entry
        for field in ("patentOwnerName",):
            existing_record = patent_entry.get(field, [])
            existing_record.append(case.get(field))
            patent_entry[field] = existing_record
    
    # Keep the mode of the following fields for each patent number
    for patent_id in patent_data:
        patent_entry = patent_data[patent_id]
        for field in ("patentOwnerName",):
            if field not in patent_entry:
                continue
            patent_entry[field] = mode(patent_entry[field])
    return patent_data


# Write JSON representation of patent->attribute dictionary
def export_case_decisions_attrs(augmented_table, out_filename):
    fd = open(out_filename, "w")
    json.dump(augmented_table, fd, indent=2)
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
    if len(argv) != 4:
        print("Usage: extract_decisions.py ptab_api_metadata_file "
              "path/to/ptab_fwd_files "
              "patent_to_class_file "
              "art_unit_to_class_file ")
        sys.exit(1)
    api_data_filename     = argv[0]
    fwd_dir               = argv[1]
    patent_class_filename = argv[2]
    au_class_filename     = argv[3]
    
    api_data          = load_ptab_api_data(api_data_filename, fwd_dir)
    patent_class_data = load_patent_class_data(patent_class_filename)
    au_class_data     = load_au_class_data(au_class_filename)
    patent_data       = build_patent_data(api_data, patent_class_data, au_class_data)
    
    # TODO: export trial, patent data to JSON files

if __name__ == "__main__":
    main()

