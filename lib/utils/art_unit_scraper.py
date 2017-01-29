
from bs4 import BeautifulSoup
import urllib, unicodecsv, urllib2, time, os
from subprocess import call

links = []
links.append("https://www.uspto.gov/patents-application-process/classes-arranged-art-unit-art-units-1611-1763")
links.append("https://www.uspto.gov/patents-application-process/classes-arranged-art-unit-art-units-1764-2691")
links.append("https://www.uspto.gov/patents-application-process/classes-arranged-art-unit-art-units-2763-2913")
links.append("https://www.uspto.gov/patents-application-process/classes-arranged-art-unit-art-units-2914-3715")
links.append("https://www.uspto.gov/patents-application-process/classes-arranged-art-unit-art-units-3721-3782")
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
		response = urllib2.urlopen(homepage)
		webContent = response.read()

		f = open("html/" + str(curr) + ".html", 'w')
		f.write( webContent)
		f.close()

def convert_pdf(file_name):

	call(["pdftotext", file_name])

def main(csv_name,links):
	with open(csv_name, 'w') as csvfile:
		writer = unicodecsv.writer(csvfile, delimiter=',', encoding = 'utf-8')
		writer.writerow(["Art Unit", "Class", "Class Title", "Subclass From","Subclass To"])
		for link in links:
			r = urllib.urlopen(link).read()
			soup = BeautifulSoup(r)
			div = soup.find("div", {"id": "content"})
			table = div.table
			table = table.tbody
			rows = table.find_all('tr')
			output = []
			# print(rows)
			for row in rows:
				# print(row)
				print(row)
				cells = row.find_all('td')
				# print(cells)
				if len(cells) <1:
					continue
				elif len(cells[0].string.strip())>0:
					temp = []
					for cell in cells:
						if cell.string:
							temp.append(cell.string.strip())
					output.append(temp)
			for row in output:
				writer.writerow(row)





main('art_units.csv',links )





