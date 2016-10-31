
from bs4 import BeautifulSoup
import urllib, unicodecsv, urllib2, time, os
from subprocess import call
import random

homepage = "https://e-foia.uspto.gov/Foia/"
pdf_name_tmpl = "pdf/{}_{}.pdf"

delay_mean = 4.2
delay_stddev = delay_mean * 0.05

#Converts string to integer. If "NONE" is in the string, return -1.
def str_to_int(arg):
	if not arg or "NONE" in arg or arg.isspace():
		return -1
	return int(arg)

#Converts string date "01/24/2001" to int 20010124
def convert_date(arg):
	if not arg or "NONE" in arg or arg.isspace():
		return -1
	date = arg.split("/")
	return int(date[2] + date[0] + date[1])

def download_file(download_url, name):
	response = urllib2.urlopen(download_url)
	contents = response.read()
	
	# Assuming valid PDFs are at least 3KiB
	if len(contents) < 3072 or 'DTD XHTML 1.0 Transitional' in contents:
		print("Length of contents = {}".format(len(contents)))
		return False
	
	file_ = open(name, 'wb')
	file_.write(contents)
	file_.close()
	return True

#Downloads html of links to all tables in USPTO and saves them to html folder.
def download_html():
	for curr in range(1, 1691 + 1):
		response = urllib2.urlopen("https://e-foia.uspto.gov/Foia/DispatchBPAIServlet?SearchRng=decDt&docTextSearch=&page=60&d-3995525-p="+ str(curr)+ "&txtInput_EndDate=09%2F21%2F2016&SearchId=&Objtype=ser&txtInput_StartDate=09%2F01%2F1951")
		webContent = response.read()
		f = open("html/" + str(curr) + ".html", 'w')
		f.write( webContent)
		f.close()

def is_pdf(file_name):
	if not os.path.isfile(file_name) or os.path.getsize(file_name) < 3072:
		return False
	fd = open(file_name, 'rb')
	contents = fd.read()
	fd.close()
	if 'DTD XHTML 1.0 Transitional' in contents:
		return False
	return True

def main(start_page, end_page):
	count = 0
	retry_list = []
	
	global delay_mean, delay_stddev
	pages = list(range(start_page, end_page + 1))
	random.shuffle(pages)
	
	for page in pages:
		print("Page: {}".format(page))
		link = "html/{}.html".format(page)
		r = urllib.urlopen(link).read()
		soup = BeautifulSoup(r, "lxml")
		table = soup.find("table", {"id": "efoiaLst"})
		table = table.tbody
		rows = table.find_all('tr')

		row_range = list(range(len(rows)))
		random.shuffle(row_range)
		
		for i in row_range:
			row = rows[i]
			print("\nPage: {} Row: {}".format(page, i+1))
			cols = row.find_all('td')
			pdf_link = cols[0].find_all('a')[1].get('href')
			file_name = pdf_name_tmpl.format(page, i+1)
			
			# Skip PDFs for cases that don't have patent numbers
			patent_no = cols[5].string.strip()
			if patent_no == "NONE":
				print("Skipping (not post-grant)")
				continue
			
			# Skip PDFs for cases decided before Sept. 2012
			#decis_date = convert_date(cols[7].string)
			#if decis_date < 20120901:
			#	print("Skipping (case decided before 9/2012)")
			#	continue
			
			# Skip PDFs that we have already downloaded
			if is_pdf(file_name):
				print("Skipping ({} looks valid)".format(file_name))
				continue
			
			#print("Link: ", homepage + pdf_link)
			if download_file(homepage + pdf_link, file_name):
				print("{} downloaded".format(file_name))
			else:
				print("{} failed to download. Adding to retry list".format(file_name))
				retry_list.append((pdf_link, page, i+1))
			count += 1
			
			delay = round(abs(random.gauss(delay_mean, delay_stddev)), 2)
			print("Sleeping {}s".format(delay))
			time.sleep(delay)
	
	while len(retry_list) > 0:
		print("\nRetrying {} files".format(len(retry_list)))
		delay_mean = round(delay_mean * (2**0.5), 3)
		delay_stddev = delay_mean * 0.05
		print("Random delay = normal({}, {})".format(delay_mean, delay_stddev))
		retry_list2 = []
		# Shuffle retry list
		random.shuffle(retry_list)
		for pdf_link, page, row in retry_list:
			file_name = pdf_name_tmpl.format(page, row)
			if is_pdf(file_name):
				continue
			
			print("")
			if not download_file(homepage + pdf_link, file_name):
				print("{} failed to download. Adding to retry list".format(file_name))
				retry_list2.append((pdf_link, page, row))
			
			delay = round(abs(random.gauss(delay_mean, delay_stddev)), 2)
			print("Sleeping {}s".format(delay))
			time.sleep(delay)
		retry_list = retry_list2
		

main(1, 1691)
