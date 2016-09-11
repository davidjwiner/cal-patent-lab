# parse Guan Cheng's OCR text and extract key data
# output separate text files for each appeal decision
# we want Doc ID, Cause, Patent ID, App ID, Keywords, Date, Inventor,
# Decision, US Code

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
				newFilename = "file_"
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

parser("../ptab-data/ptab.sample.200.txt")
