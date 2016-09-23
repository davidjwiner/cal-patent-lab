
from bs4 import BeautifulSoup
import urllib, unicodecsv, urllib2


#Converts string to integer. If "NONE" is in the string, return -1.
def str_to_int(arg):
	if "NONE" in arg:
		return -1
	return int(arg)

#Converts string date "01/24/2001" to int 20010124
def convert_date(arg):
	if "NONE" in arg or not arg or arg.isspace():
		return -1
	date = arg.split("/")
	return int(date[2] + date[0] + date[1])

def download_file(download_url,name):
    response = urllib2.urlopen(download_url)
    file_ = open(name, 'w')
    file_.write(response.read())
    file_.close()
    print("Completed")

with open('uspto_data_2.csv', 'w') as csvfile:
	writer = unicodecsv.writer(csvfile, delimiter=',', encoding = 'utf-8')
	writer.writerow(["Application No", "Appeal No", "Interference No", "Publication No", "Publication Date", "Patent No", "Issue Date", "Decision Date", "Inventor", "Case No"])
	for curr in range(1691,1692):
		print("Page: " + str(curr))
		link = "https://e-foia.uspto.gov/Foia/DispatchBPAIServlet?SearchRng=decDt&docTextSearch=&page=60&d-3995525-p="+ str(curr)+ "&txtInput_EndDate=09%2F21%2F2016&SearchId=&Objtype=ser&txtInput_StartDate=09%2F01%2F1951"
		
		r = urllib.urlopen(link).read()
		soup = BeautifulSoup(r, "lxml")
		table = soup.find("table", {"id": "efoiaLst"})
		table = table.tbody
		rows = table.find_all('tr')

		row_num = 0
		for row in rows:
			row_num +=1
			print("Row: " + str(row_num))
			cols = row.find_all('td')

			app_id = cols[0].a.get('name').strip()

			appeal_no = cols[1].string.strip()

			interf_no = cols[2].string.strip()

			pub_no = cols[3].string.strip()

			date = convert_date(cols[4].string)

			patent_no = cols[5].string.strip()

			issue_date = convert_date(cols[6].string)

			decis_date = convert_date(cols[7].string)

			inven_name = cols[8].string.strip()

			case_no = cols[9].string.strip()

			output = [app_id,appeal_no, interf_no, pub_no, date, patent_no, issue_date, decis_date, inven_name, case_no]
			new_output = []
			for elem in output:
				if type(elem) == str:
					new_output.append(elem.encode("utf-8"))
				else:
					new_output.append(elem)
			writer.writerow(new_output)







# print(table.td.a.get('name'))