# -*- coding: utf-8 -*-0
#!/usr/bin/env python
#
# this parser handles the new data about patents which were analyzed post-grant
# Those documents are formatted differently, hence the need for a new parser

import collections
import locale
import re

#locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

casefile_tmpl = "./output/RetrievePdf_{:03}.txt"
propfile_tmpl = "./output/file_{:03}_properties.txt"
NUMBER_FILES = 60

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
                decision = "invalidated"
                propertiesFile.write("Decision: {}".format(decision))
            else:
                decision = "not invalidated"
                propertiesFile.write("Decision: {}\n".format(decision))
    return decision


def parseUSCode(fileIndex):
    infile = casefile_tmpl.format(fileIndex)
    outfile = propfile_tmpl.format(fileIndex)
    USCMatcher = re.compile('U.S.C. \§')
    with open(infile) as f:
        # Read the file and check if we can find the mention of U.S.C.
        text = f.read().strip()
        USCMatchResult = USCMatcher.search(text)
        # If we find a mention of U.S.C, we find the code
        if USCMatchResult:
            USCode = re.compile('U.S.C.\s\§\s*[l0-9]+\s*(\([a-z]\))*')
            USCodeResult = list(set([x.group(0)[10:].strip() for
                x in USCode.finditer(text)]))          
            with open(outfile, 'a') as propertiesFile:
                propertiesFile.write("USC: {}\n".format(USCodeResult))
                    
            return USCodeResult
        else:
            return []

# TODO (DS): This function needs to go in a separate file
# TODO (DS): Next meeting, discuss about folder architecture
def getUSCodeStats(uscodeList):
    counter=collections.Counter(uscodeList)
    return counter


if __name__ == "__main__":
    uscodeList = [] 
    uscodeListInvalidated = []
    uscodeListNotInvalidated = []
    for i in range(NUMBER_FILES):
        parsePatentId(i)
        decision = parseDecision(i)
        uscode = parseUSCode(i)
        # Get the list of all the USCode and concatenate them in a big list in order
        # to count the number of occurence of each code       
        uscodeList += uscode
        # TODO(DS): I don't like comparing it to a string. Find a more clever way        
        if decision == "invalidated":
            uscodeListInvalidated += uscode
        else:
            uscodeListNotInvalidated += uscode

    uscodeCounter = getUSCodeStats(uscodeList)
    uscodeInvalidatedCounter = getUSCodeStats(uscodeListInvalidated)
    uscodeNotInvalidatedCounter = getUSCodeStats(uscodeListNotInvalidated)