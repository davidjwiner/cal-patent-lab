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
    invalMatcher1 = re.compile('ORDERED.{0,120}?[cC]laim(s)?\s+\d+.{0,120}?(unpatentable|UNPATENTABLE|anticipated|ANTICIPATED|cancell?ed|CANCELL?ED)')
    invalMatcher2 = re.compile('[aA]dverse\s+[jJ]udgment.{0,120}?[cC]laim(s)?\s+\d+.+?(granted|GRANTED)')
    valMatcher1 = re.compile("no\s+trial\s+.{0,10}?instituted")
    valMatcher2 = re.compile("[jJ]oint\s+?[mM]otions?(\s+?[tT]o\s+?[tT]erminate)?.{0,120}?(granted|GRANTED)")
    valMatcher3 = re.compile("([pP]etitions?|[iI]nstiution|[rR]equest).{0,120}?([rR]ehearing|[iI]nter\s+?[pP]artes|INTER\s+?PARTES|IPR|[rR]ehearing|challeng).{0,120}?(denied|DENIED|dismissed|DISMISSED)")
    valMatcher4 = re.compile("not\s+(persuaded|demonstrated).{0,120}?reasonable\s+likelihood.{0,120}?prevail")
    ambigMatcher1 = re.compile("[rR]equest\s+?for\s+?[rR]ehearing.{0,120}?(instituted|INSTITUTED)")
    with open(infile) as f:
        # Read entire file, convert to single line for regex searching purposes
        text = f.read().replace('\n', ' ')
        inv1 = invalMatcher1.search(text)
        inv2 = invalMatcher2.search(text)
        val1 = valMatcher1.search(text)
        val2 = valMatcher2.search(text)
        val3 = valMatcher3.search(text)
        val4 = valMatcher4.search(text)
        amb1 = ambigMatcher1.search(text)
        
        valid = val1 or val2 or val3 or val4
        invalid = inv1 or inv2
        ambiguous = amb1
        
        if invalid and not valid and not ambiguous:
            decision = "invalidated"
        elif valid and not invalid and not ambiguous:
            decision = "not invalidated"
        else:
            if not invalid and not valid and not ambiguous:
                print("WARNING: ambiguous decision in {}: inval=None, val=None".format(infile, invalid, valid))
            elif invalid and valid and not ambiguous:
                print("WARNING: ambiguous decision in {}: inval={}, val={}".format(infile, invalid.group(0), valid.group(0)))
            else:
                print("WARNING: uncorrectable ambiguous decision in {}".format(infile))
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
