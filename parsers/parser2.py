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
		result = str(matcher.search(text).group(0))
		if result:
			#remove commas, write to properties file
			result = result.replace(',','')
			with open(outfile, 'a') as propertiesFile:
				propertiesFile.write("PatentId: {}\n".format(result))

parsePatentId(0)