import csv
from dateutil.parser import parse
import json
import requests
import sys

# calling the api to get the examiner name and art unit
def get_metadata(patentId):
    # calling the api
    pair_url = "https://pairbulkdata.uspto.gov/api/queries"
    data = {"searchText":"{}".format(patentId),"qf": "patentNumber", "f[Bacet":"false"}
    headers = {"Content-Type":"application/json"}
    r = requests.post(pair_url, json=data)
    # loading the json
    try:
        result = json.loads(r.text)
    except JSONDecodeError:
        print(patentId)

    # trying to read information from the result
    # if not available just return the patent id
    try:
        result = result['queryResults']["searchResponse"][
            'response']["docs"][0]
        examiner_name = result["appExamNameFacet"]
        art_unit      = result['appGrpArtNumber']
        filing_date   = parse(result["appFilingDate"]).strftime("%Y-%m-%d")
        issue_date    = parse(result["patentIssueDate"]).strftime("%Y-%m-%d")
        return examiner_name, art_unit, filing_date, issue_date
    except (IndexError, KeyError):
        print(patentId)
        return None


# create a csv file containing: patent_id, art unit, examiner name
# if not available will just enter None
def create_csv(ptab_api_filename, output_filename):
    api_cases = json.load(open(ptab_api_filename))
    au_examiner_file = open(output_filename, "w")
    p = csv.writer(au_examiner_file)
    p.writerow(["patentId", "artUnit", "examinerName", "filingDate", "issueDate"])
    
    patents = set()
    for case in api_cases:
        patent_id = case.get("patentNumber")
        if patent_id:
            patents.add(patent_id)
    
    count = 0
    num_cases = len(patents)
    for patent_id in patents:
        count += 1
        data = get_metadata(patent_id)
        if data is not None:
            examiner, au, filing_date, issue_date = data
            p.writerow([patent_id, au, examiner, filing_date, issue_date])
            if count % 10 == 0:
                print('Written {}/{} cases in csv file'.format(count, num_cases))
    

if __name__ == '__main__':
    argv = sys.argv[1:]
    if len(argv) != 2:
        print("Usage: pair_api_downloader.py ptab_api_metadata_file "
            "outputfile name")
        sys.exit(1)
    api_data_filename = argv[0]
    output_filename   = argv[1]
    create_csv(api_data_filename, output_filename)
