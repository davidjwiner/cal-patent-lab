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

def parsePatentId(infile):
    matcher1 = re.compile('(?<=Patent )\s*(RE|D|PP)?[0-9,]{3,9}')
    matcher2 = re.compile('(?<=Patent No.)\s*(RE|D|PP)?[0-9,]{3,9}')
    # If we find a mention of Patent followed by numbers w/commas, we find the ID
    with open(infile) as f:
        text = f.read().strip()
        result1 = matcher1.search(text)
        result2 = matcher2.search(text)
        if result1 or result2:
            #remove commas, write to properties file
            result = (result1 or result2).group(0).replace(',', '')
            return result.strip()
    print("Warning: no patent ID found for {}".format(infile))
    return

def parseDecision(infile):
    invalMatcher1 = re.compile("ORDERED.{0,240}?(unpatentable|UNPATENTABLE|anticipated|ANTICIPATED|cancell?ed|CANCELL?ED)")
    invalMatcher2 = re.compile('[aA]dverse\s+[jJ]udgment.{0,120}?[cC]laim(s)?\s+\d+.+?(granted|GRANTED)')
    invalMatcher3 = re.compile("[jJ]udgment\s+(is\s+)?entered")
    with open(infile) as f:
        # Read entire file, convert to single line for regex searching purposes
        text = f.read().replace('\n', ' ')
        inv1 = invalMatcher1.search(text)
        inv2 = invalMatcher2.search(text)
        inv3 = invalMatcher3.search(text)
        invalid = inv1 or inv2 or inv3
        negated = None
        if invalid:
            negated = ("not" in invalid.group(0))
        
        if invalid and not negated:
            decision = "invalidated"
        elif invalid and negated:
            decision = "not invalidated"
        else:
            print("WARNING: ambiguous decision for {}".format(infile))
            decision = "ambiguous"
    return decision

def parseUSCode(infile):
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
    if len(argv) != 1:
        print("Usage: parser_new_data.py srcdir")
        sys.exit(1)
    
    srcdir = argv[0]
    files = [f for f in listdir(srcdir) if isfile(join(srcdir, f))]
    
    uscodeList = []
    uscodeListInvalidated = []
    uscodeListNotInvalidated = []
    
    for f in files:
        parsePatentId(join(srcdir, f))
        decision = parseDecision(join(srcdir, f))
        uscode = parseUSCode(join(srcdir, f))
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
