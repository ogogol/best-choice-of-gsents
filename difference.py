import re
import numpy as np
from difflib import *

def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]


patternWordsSplit = re.compile(r'[+-]\s{2,7}|\s{3,7}')
patternMinusLetter = re.compile(r'\- \w')
patternSpace = re.compile(r'\s+')
w = re.compile(r'\w')
p = re.compile(r'\+')
m = re.compile(r'-')

def sentsDifference(orSent, comSent):
        exWds = {}
        misWds = {}
        wrWds = {}
        rWds = {}

        d = Differ()

        diff = ''.join(d.compare(orSent.lower(), comSent.lower()))
        s = patternSpace.split(comSent.lower())

        diff1 = patternWordsSplit.split(diff)
        for i in range(len(diff1)):
                wd = ''.join(w.findall(diff1[i]))
                plus = ''.join(p.findall(diff1[i]))
                minus = ''.join(m.findall(diff1[i]))
                if len(wd) <= len(plus):
                        exWds[i]= [wd,i-len(misWds)]
                elif len(plus)>0:
                        wrW = ''.join(w.findall(patternMinusLetter.sub('', diff1[i])))
                        wrWds[i]= [wrW,i-len(misWds)]
                elif len(wd) <= len(minus):
                        misWds[i]= (wd)
                elif len(minus)>0 and len(plus) == 0:
                        wrW = ''.join(w.findall(patternMinusLetter.sub('', diff1[i])))
                        wrWds[i]= [wrW,i-len(misWds)]
                else:
                        rWds[i]= [wd,i-len(misWds)]

        delItems =[]

        for key, value in wrWds.items():
                if len(s) > value[1]:
                        if s[value[1]] != wrWds[key][0] and wrWds.get(key+1) != None:
                                if s.count(wrWds.get(key+1)[0]) == 0 and s[value[1]] == wrWds[key][0] + wrWds[key+1][0]:
                                        wrWds[key][0] = wrWds[key][0] + wrWds[key+1][0]
                                        delItems.append(key+1)

        for i in range(len(delItems)):
                del wrWds[delItems[i]]

        return exWds, misWds, wrWds, rWds

def readSents(file):
    f = open (file, 'r')
    l = [line for line in f]
    f.close()

    phs = []
    for i in range(len(l)):
        cntPhrases = l[i].count("transcript: ")
        st = 0
        en = len(l[i])-1
        phrase = ''
        for j in range(cntPhrases):
            stFhr = l[i].index("transcript: ", st, en) + 13
            enFhr = l[i].index('"__proto__:', st, en)
            phrase += l[i] [stFhr:enFhr]
            st = enFhr + 13

        phrase = phrase
        if phrase != '':
            phs.append(phrase)

    return phs

