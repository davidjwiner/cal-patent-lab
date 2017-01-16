#!/usr/bin/env python
from collections import Counter
import json
from os import listdir
from os.path import isfile, join
import notebooks.parser_new_data as parser
import sys

# Call our custom parser to parse decisions from PTAB decision documents
def parse_decisions_from_case_files(ptab_files):
    decision_table = dict()
    for file_name in ptab_files:
        patent_id = parser.parsePatentId(file_name)
        if not patent_id:
            print("{}: could not parse patent number".format(file_name))
            continue
        decision_string = parser.parseDecision(file_name)
        if decision_string == "ambiguous":
            print("{}: decision is ambiguous for patent {}".format(file_name, patent_id))
            decision_table[patent_id] = "ambiguous"
            continue
        # If this patent was invalidated at any point, keep it invalidated
        decision = (decision_string == "invalidated") \
                   or decision_table.get(patent_id, False)
        decision_table[patent_id] = decision
    return decision_table


# Load a JSON dump of cases downloaded from the PTAB API
# Convert to, return a dictionary mapping patent numbers to various attributes
def load_ptab_api_cases(api_filename):
    fd = open(api_filename)
    api_cases = json.load(fd)
    fd.close()
    
    # Build list of values for each attribute belonging
    # to the appropriate patent number
    api_table = dict()
    for case in api_cases:
        patent_id = case.get("patentNumber")
        if not patent_id:
            print("Case {} does not have a patent number, skipping".format(case["trialNumber"]))
            continue
        status = case["prosecutionStatus"]
        if patent_id not in api_table:
            api_table[patent_id] = dict()
        patent_entry = api_table[patent_id]
        for field in ("patentOwnerName", "inventorName", "prosecutionStatus", \
                      "trialNumber", "petitionerPartyName"):
            existing_record = patent_entry.get(field, [])
            existing_record.append(case.get(field))
            patent_entry[field] = existing_record
    
    # Keep the mode of the following fields for each patent number
    for patent_id in api_table:
        patent_entry = api_table[patent_id]
        for field in ("patentOwnerName", "inventorName"):
            if field not in patent_entry:
                continue
            field_entry_list = patent_entry[field]
            best_entry = mode(field_entry_list)
            patent_entry[field] = best_entry
    return api_table


# Create and return a dictionary mapping patent numbers to various attributes
def join_decsions_with_ptab_data(decision_table, api_table):
    augmented_table = api_table.copy()
    
    for patent_id in decision_table:
        parsed_decision = decision_table[patent_id]
        # If a patent appears in our parsed results but not in the PTAB API data,
        # then skip it because we don't have inventor name, petitioner name,
        # or other data for it
        if patent_id not in augmented_table:
            print("{} not found in data from PTAB API".format(patent_id))
            continue
        
        api_status = augmented_table[patent_id]["prosecutionStatus"]
        # For cases where our parser fails, try to infer the decision
        # from prosecution statuses
        if parsed_decision == "ambiguous":
            # Case is terminated without adverse judgment or final written decision
            if contains(api_status, ["Terminated-Settled", "Terminated-Denied",
                                     "Terminated-Other", "Defective", "Deleted",
                                     "Terminated-Dismissed", "Discarded", "Withdrawn"]):
                parsed_decision = False
            # Patent holder has requested invalidation of parts of their own patent
            elif "Terminated-Adverse Judgment" in api_status:
                parsed_decision = True
            # We can't reliably infer a status, so skip this patent
            else:
                continue
        
        augmented_table[patent_id]["invalidated"] = parsed_decision
        # Do a sanity check between parsed decision and prosecution status
        if parsed_decision is True and "FWD Entered" not in api_status and \
                "Terminated-Adverse Judgment" not in api_status:
            print("Patent:{}, Parsed:{}, API:{}".format(patent_id, parsed_decision, api_status))
    return augmented_table


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
    ctr = Counter(lst)
    values = ctr.values()
    idx = values.index(max(values))
    items = ctr.items()
    return items[idx][0]


def main():
    argv = sys.argv[1:]
    if len(argv) != 3:
        print("Usage: extract_decisions.py path/to/ptab_files "
              "path/to/ptab_api_dump "
              "path/to/output_file")
        sys.exit(1)
    ptab_dir = argv[0]
    api_filename = argv[1]
    out_filename = argv[2]
    ptab_files = [join(ptab_dir, f) for f in listdir(ptab_dir) if isfile(join(ptab_dir, f))]
    
    # Build decision table from parsed PTAB results
    decision_table = parse_decisions_from_case_files(ptab_files)
    
    # Load case data scraped from PTAB API
    api_cases = load_ptab_api_cases(api_filename)
    
    # Link patent numbers to attributes such as inventor name and invalidation status
    augmented_table = join_decsions_with_ptab_data(decision_table, api_cases)
    
    # Export decisions and patent attributes to file
    export_case_decisions_attrs(augmented_table, out_filename)

if __name__ == "__main__":
    main()

