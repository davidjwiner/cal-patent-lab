# parse Guan Cheng's OCR text and extract key data
# output separate text files for each appeal decision
# we want Doc ID, Cause, Patent ID, App ID, Keywords, Date, Inventor,
# Decision, US Code

# This function takes the PTAB OCR text as input and uses the "PAGE 1" delimiter to
# break the PTAB file into separate files for each document
# Return value: number of files generated

import re

def splitDocument(filename):
	with open(filename) as f:
		# newDocBuf is a buffer to read in the file lines
		newDocBuf = ""
		# counter to assist in creating new file names
		count = -1
		for line in f:
			# when encountering this delimiter, write newDoc to another file
			# then reset the newDoc buffer
			if "*** PAGE 1 ***" in line:
				# this check prevents false positives from very beginning of file
				if count>=0:
					# write the legal document to its own file
					newFile = open("./output/file_%s.txt" % (str(count).zfill(3)),'w')
					newFile.write(newDocBuf)
					newFile.close()
					# also make a properties file
					newFile = open("./output/file_%s_properties.txt" % (str(count).zfill(3)), 'w')
					newFile.close()
					
				# increment counter
				count += 1
				# reset the buffer
				newDocBuf = ""
				
			newDocBuf += line
	return count

# this function finds and records the document ID (appeal ID)
def parseDocId(fileIndex):
	with open("./output/file_%s.txt" % (str(fileIndex).zfill(3))) as f:
		for line in f:
			if "Appeal No." in line:
				words = line.split(' ')
				if len(words)>2:
					docId = words[2]
					propertiesFile =  open("./output/file_%s_properties.txt" % (str(fileIndex).zfill(3)), 'a')
					propertiesFile.write("docId: %s" % docId)
					propertiesFile.close()
					return

# Finds and records the patent application ID
def parseAppId(fileIndex):
	infile = "./output/file_{:03}.txt".format(fileIndex)
	outfile = "./output/file_{:03}_properties.txt".format(fileIndex)
	appIdMatcher = re.compile('[Ol0-9]{1,2}/[Ol0-9]{1,3}[\.,][Ol0-9]{3}')
	with open(infile) as f:
		lines = f.readlines()
		for i in range(len(lines)):
			line = lines[i].strip()
			if "Application " in line:
				appIds = appIdMatcher.findall(line)
				if len(appIds) >= 1:
					propertiesFile =  open(outfile, 'a')
					for appId in appIds:
						propertiesFile.write("appId: {}\n".format(appId))
					propertiesFile.close()
					return

def parseDecision(fileIndex):
	infile = "./output/file_{:03}.txt".format(fileIndex)
	outfile = "./output/file_{:03}_properties.txt".format(fileIndex)
	deniedMatcher = re.compile('(DENIED(-IN-PART)?)')
	grantedMatcher = re.compile('([GQ]RANTED(-IN-PART)?)')
	with open(infile) as f:
		for line in f:
			line = line.strip()
			deniedMatchResult = deniedMatcher.search(line)
			grantedMatchResult = grantedMatcher.search(line)
			if deniedMatchResult or grantedMatchResult:
				propertiesFile =  open(outfile, 'a')
				if deniedMatchResult:
					result = deniedMatchResult.group(0)
					propertiesFile.write("decision: {}\n".format(result))
				if grantedMatchResult:
					result = grantedMatchResult.group(0).replace('Q', 'G')
					propertiesFile.write("decision: {}\n".format(result))
				propertiesFile.close()
				return
'''
def parser(filename):
	with open(filename) as f:
		docId = ""
		patentId = ""
		appId = ""
		date = ""
		inventor = ""
		count = 0
		code = ""
		newFilename = "file_"
		for line in f:
			# new document
			if "*** PAGE 1 ***" in line:
				docId = ""
				patentId = ""
				appId = ""
				date = ""
				inventor = ""
				newFilename = "./output/file_"
				code = ""
				count += 1
			# get document ID
			elif "Appeal No." in line:
				if docId=="":
					words = line.split(' ')
					if len(words)>2:
						docId = words[2]
						if count<10:
							newFilename += "00" + str(count)+".txt"
						elif count<100:
							newFilename += "0" + str(count)+".txt"
						else:
							newFilename += str(count)+".txt"
						newDoc = open(newFilename, 'a')
						newDoc.write("docId: "+docId+"\n");
						newDoc.close();
			# get application ID
			elif "Application No." in line:
				if len(docId)>1 and len(appId)<1:
					words = line.split(' ')
					if len(words)>2:
						appId = words[2]
						if len(newFilename)>5:
							newDoc = open(newFilename, 'a')
							newDoc.write("appId: "+appId+"\n");
							newDoc.close();
			# decision
			elif ("GRANTED" in line) or ("DENIED" in line):
				if len(newFilename)>5:
					newDoc = open(newFilename, 'a')
					newDoc.write("decision: "+line+"\n");
					newDoc.close();
	
			# US Code
			elif "U.S.C." in line:
				if len(docId)>1 and len(code)<1:
					code = ""
					words = line.split(' ')
					for i in xrange(len(words)):
						if words[i]=="U.S.C.":
							if len(words[i+1])==2: #that stupid section symbol
								code = words[i+2]
							else:
								code = words[i+1]
							break
					if len(newFilename)>5:
							newDoc = open(newFilename, 'a')
							newDoc.write("code: "+code+"\n");
							newDoc.close();
'''
numFiles = splitDocument("../ptab-data/ptab.sample.200.txt")
for i in xrange(numFiles):
	parseDocId(i)
	parseAppId(i)
	parseDecision(i)
