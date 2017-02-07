import json
import requests
import csv
import sys

# calling the api to get the examiner name and art unit
def get_au_examiner(patentId):
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
        examiner_name = result['queryResults']["searchResponse"][
            'response']["docs"][0]["appExamNameFacet"]
        art_unit = result['queryResults']["searchResponse"][
                'response']["docs"][0]['appGrpArtNumber']
    except (IndexError, KeyError):
        print(patentId)
        examiner_name = 'None'
        art_unit = 'None'
    return  examiner_name, art_unit


# create a csv file containing: patent_id, art unit, examiner name
# if not available will just enter None
def create_csv(ptab_api_filename, output_filename):
    api_cases = json.load(open(ptab_api_filename))
    au_examiner_file = open(output_filename, "w")
    p = csv.writer(au_examiner_file)
    p.writerow(["patentId", "Art Unit", "Examiner Name"])
    count = 0
    for case in api_cases:
        count += 1
        try:
            patent_id = case['patentNumber']
        except KeyError:
            print(case)
        examiner, au = get_au_examiner(patent_id)
        p.writerow([patent_id, au, examiner])
        if count % 100 == 0:
            print('Written {} cases in csv file'.format(count))
    

if __name__ == '__main__':
    argv = sys.argv[1:]
    if len(argv) != 2:
        print("Usage: au_api_downloader.py ptab_api_metadata_file "
            "outputfile name")
        sys.exit(1)
    api_data_filename = argv[0]
    output_filename = argv[1]
    create_csv(api_data_filename, output_filename)