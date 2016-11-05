#!/usr/bin/env python2

from bs4 import BeautifulSoup
import urllib, unicodecsv, urllib2, time, os
from subprocess import call
import random

pdf_name_tmpl = "pdf/{0:03}0-{0:03}9/{1}_{2}.pdf"
text_name_tmpl = "text/{}_{}_{}.txt"

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

def extract_text(pdf_name, case_no, page, line):
	text_name = text_name_tmpl.format(case_no, page, line)
	call(["pdftotext", pdf_name, text_name])

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
	#random.shuffle(pages)
	
	for page in pages:
		print("Page: {}".format(page))
		link = "html/{}.html".format(page)
		r = urllib.urlopen(link).read()
		soup = BeautifulSoup(r, "lxml")
		table = soup.find("table", {"id": "efoiaLst"}).tbody
		rows = table.find_all('tr')

		row_range = list(range(len(rows)))
		#random.shuffle(row_range)
		
		for i in row_range:
			row = rows[i]
			cols = row.find_all('td')
			file_name = pdf_name_tmpl.format(page//10, page, i+1)
			
			# Skip PDFs for cases that don't have patent numbers
			patent_no = cols[5].string.strip()
			if patent_no in ["NONE", ""]:
				#print("Skipping (not post-grant)")
				continue
			
			#Skip PDFs for cases decided before Sept. 16 2012
			decis_date = convert_date(cols[7].string)
			if decis_date < 20120916:
				#print("Skipping (case decided on or before 9/16/2012)")
				continue
			
			interference_no = cols[2].string.strip()
			if interference_no not in ["NONE", ""]:
				#print("Skipping (patent interference case)")
				continue
			
			case_no = cols[9].string.strip()
			
			print("\nPage: {} Row: {}".format(page, i+1))
			if extract_text(file_name, case_no, page, i+1):
				print("Text extraction for {} failed".format(file_name))
			count += 1


main(1, 1691)
