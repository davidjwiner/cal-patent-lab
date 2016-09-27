# this parser handles the new data about patents which were analyzed post-grant
# Those documents are formatted differently, hence the need for a new parser

import re
import locale
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

casefile_tmpl = "./output/RetrievePdf_{:03}.txt"
propfile_tmpl = "./output/file_{:03}_properties.txt"

def parsePatentId(fileIndex):
	infile = casefile_tmpl.format(fileIndex)
	outfile = propfile_tmpl.format(fileIndex)
	matcher = re.compile('(?<=Patent )\s*[0-9,]+')
	# If we find a mention of Patent followed by numbers w/commas, we find the ID
	with open(infile) as f:
		text = f.read().strip()
		result = matcher.search(text)
		if result:
			#remove commas, write to properties file
			result = result.group(0).replace(',','')
			with open(outfile, 'a') as propertiesFile:
				propertiesFile.write("PatentId: {}\n".format(result))

def parseDecision(fileIndex):
	infile = casefile_tmpl.format(fileIndex)
	outfile = propfile_tmpl.format(fileIndex)
	invalMatcher1 = re.compile('ORDERED.+?claim(s)?\s+\d+.+?(unpatentable|anticipated|cancelled)')
	invalMatcher2 = re.compile('ORDERED.+?adverse\s+judgment.+?claim(s)?\s+\d+.+?(granted|GRANTED)')
	with open(infile) as f:
		text = f.read().replace('\n', ' ')
		result1 = invalMatcher1.search(text)
		result2 = invalMatcher2.search(text)
		with open(outfile, 'a') as propertiesFile:
			if result1 or result2:
				propertiesFile.write("Decision: invalidated\n")
			else:
				propertiesFile.write("Decision: not invalidated\n")

for i in range(60):
	parsePatentId(i)
	parseDecision(i)
