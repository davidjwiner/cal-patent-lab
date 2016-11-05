# -*- coding: utf-8 -*-0
#!/usr/bin/env python
#
# This parser handles new data about patents which were analyzed post-grant
# Those documents are formatted differently, hence the need for a new parser
# This script takes two arguments:
#   An input directory where converted PDF texts are stored
#   An output directory where files with extracted attributes should be written

import collections
import locale
import re
import sys
from os import listdir
from os.path import isfile, join

#locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

def parsePatentId(infile, outfile):
    matcher = re.compile('(?<=Patent )\s*[0-9,]+')
    # If we find a mention of Patent followed by numbers w/commas, we find the ID
    with open(infile) as f:
        text = f.read().strip()
        result = matcher.search(text)
        if result:
            #remove commas, write to properties file
            result = result.group(0).replace(',', '')
            with open(outfile, 'a') as propertiesFile:
                propertiesFile.write("PatentId: {}\n".format(result))
                return
    print("Warning: no patent ID found for {}".format(infile))
    return

def parseDecision(infile, outfile):
    invalMatcher1 = re.compile('ORDERED.+?claim(s)?\s+\d+.+?(unpatentable|anticipated|cancelled)')
    invalMatcher2 = re.compile('ORDERED.+?[aA]dverse\s+[jJ]udgment.+?claim(s)?\s+\d+.+?(granted|GRANTED)')
    with open(infile) as f:
        # Read entire file, convert to single line for regex searching purposes
        text = f.read().replace('\n', ' ')
        result1 = invalMatcher1.search(text)
        result2 = invalMatcher2.search(text)
        with open(outfile, 'a') as propertiesFile:
            if result1 or result2:
                decision = "invalidated"
            else:
                decision = "not invalidated"
            propertiesFile.write("Decision: {}\n".format(decision))
    return decision

def parseUSCode(infile, outfile):
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
    counter = collections.Counter(uscodeList)
    return counter


if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) != 2:
        print("Usage: parser_new_data.py srcdir destdir")
        sys.exit(1)
    
    srcdir, destdir = argv
    files = [f for f in listdir(srcdir) if isfile(join(srcdir, f))]
    
    uscodeList = []
    uscodeListInvalidated = []
    uscodeListNotInvalidated = []
    
    for f in files:
        parsePatentId(join(srcdir, f), join(destdir, f))
        decision = parseDecision(join(srcdir, f), join(destdir, f))
        uscode = parseUSCode(join(srcdir, f), join(destdir, f))
        # Get the list of all the USCode and concatenate them in a big list
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
