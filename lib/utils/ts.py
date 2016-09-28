
from bs4 import BeautifulSoup
import urllib, unicodecsv, urllib2, time, os
from subprocess import call

homepage = "https://e-foia.uspto.gov/Foia/"
#Converts string to integer. If "NONE" is in the string, return -1.
def str_to_int(arg):
	if "NONE" in arg or not arg or arg.isspace():
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


#Downloads html of links to all tables in USPTO and saves them to html folder.
def download_html():
	for curr in range(1,1692):
		response = urllib2.urlopen("https://e-foia.uspto.gov/Foia/DispatchBPAIServlet?SearchRng=decDt&docTextSearch=&page=60&d-3995525-p="+ str(curr)+ "&txtInput_EndDate=09%2F21%2F2016&SearchId=&Objtype=ser&txtInput_StartDate=09%2F01%2F1951")
		webContent = response.read()

		f = open("html/" + str(curr) + ".html", 'w')
		f.write( webContent)
		f.close()

def convert_pdf(file_name):

	call(["pdftotext", file_name])

def main(csv_name,start_page,end_page, start_row= None):
	with open(csv_name, 'w') as csvfile:
		writer = unicodecsv.writer(csvfile, delimiter=',', encoding = 'utf-8')
		writer.writerow(["PDF No","Application No", "Appeal No", "Interference No", "Publication No", "Publication Date", "Patent No", "Issue Date", "Decision Date", "Inventor", "Case No"])
		count = 0
		del_lst = []
		for curr in range(start_page,end_page):
			print("Page: " + str(curr))
			link = "html/" + str(curr) + ".html"
			r = urllib.urlopen(link).read()
			soup = BeautifulSoup(r, "lxml")
			table = soup.find("table", {"id": "efoiaLst"})
			table = table.tbody
			rows = table.find_all('tr')

			row_num = 0
			row_range = [i for i in range(len(rows))]
			if curr ==start_page and start_row:
				row_range = [i for i in range(start_row,len(rows))]
				start_row= None
			for i in row_range:
				row = rows[i]
				row_num +=1
				print("Page: " + str(curr) + "  Row: " + str(row_num))
				cols = row.find_all('td')

				app_id = cols[0].a.get('name').strip()

				pdf = cols[0].find_all('a')[1].get('href')
				pdf_no = str(curr) + "_" + str(i+1)
				file_name = "pdf/" + str(curr) +"_" + str(i+1) +  ".pdf"
				download_file(homepage+pdf, file_name)
				del_lst.append(file_name)
				count +=1
				if count ==400:
					count = 0
					for file_name in del_lst:
						convert_pdf(file_name)
						os.remove(file_name)

				appeal_no = cols[1].string.strip()

				interf_no = cols[2].string.strip()

				pub_no = cols[3].string.strip()

				date = convert_date(cols[4].string)

				patent_no = cols[5].string.strip()

				issue_date = convert_date(cols[6].string)

				decis_date = convert_date(cols[7].string)

				inven_name = cols[8].string.strip()

				case_no = cols[9].string.strip()

				output = [pdf_no,app_id,appeal_no, interf_no, pub_no, date, patent_no, issue_date, decis_date, inven_name, case_no]
				new_output = []
				for elem in output:
					if type(elem) == str:
						new_output.append(elem.encode("utf-8"))
					else:
						new_output.append(elem)
				writer.writerow(new_output)
		if count:
			for file_name in del_lst:
				convert_pdf(file_name)
				os.remove(file_name)


main('uspto_data_4.csv', 1361, 1692)

#If you have to run again, check terminal for the last Page: # and Row: # and call the following function:
#Uncomment These Lines===============================
#LastPage = #
#LastRow = #
#main('uspto_data_4(1).csv', LastPage,1021, LastRow)
#====================================================

#If you want to run it again, make sure that you change the output csv name.
# Ex) uspto_data_4.csv -> uspto_data_4(1).csv -> uspto_data_4(2).csv








