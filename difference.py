import re
import numpy as np
import nltk
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



pattern1 = re.compile(r'[+-]\s{2,7}|\s{3,7}')
pattern2 = re.compile(r'\- \w')
pattern3 = re.compile(r'\s+')
w = re.compile(r'\w')
p = re.compile(r'\+')
m = re.compile(r'-')

def sentsDifference(orSent, comSent, phone = 0):
	d = Differ()
	if phone:
		diff = ''.join(d.compare(phoneticSent(orSent).lower(), phoneticSent(comSent).lower()))
		s = phoneticSent(comSent).lower().split()
	else:
		diff = ''.join(d.compare(orSent.lower(), comSent.lower()))
		s = pattern3.split(comSent.lower())

	exWds = {}
	misWds = {}
	wrWds = {}
	rWds = {}
	diff1 = pattern1.split(diff)
	for i in range(len(diff1)):
		wd = ''.join(w.findall(diff1[i]))
		plus = ''.join(p.findall(diff1[i]))
		minus = ''.join(m.findall(diff1[i]))
		if len(wd) <= len(plus):
			exWds[i]= [wd,i-len(misWds)]
		elif len(plus)>0:
			wrW = ''.join(w.findall(pattern2.sub('', diff1[i])))
			wrWds[i]= [wrW,i-len(misWds)]
		elif len(wd) <= len(minus):
			misWds[i]= (wd)
		elif len(minus)>0 and len(plus) == 0:
			wrW = ''.join(w.findall(pattern2.sub('', diff1[i])))
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


def getClosePhoneMatches (w, lst, n, cutoff = 0.2):
	phoneLst = {}
	for i, pl in enumerate(lst):
		phoneLst[phoneticWord(pl)] = i
	pLst = [phone for phone in phoneLst.keys()]
	wds = get_close_matches(phoneticWord(w), pLst, n, cutoff)
	wd = lst[phoneLst.get(wds[0])]
	return wd


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


arpabet = nltk.corpus.cmudict.dict()
arpabetWds = nltk.corpus.cmudict.words()

def phoneticSent(sent):
	wds =[]
	for word in sent.lower().split():
		if arpabetWds.count(word) > 0:
			wds.append(''.join(arpabet[word][0]))
		else:
			wds.append(word)
			#print (word, "it's an exception")

	return ' '.join(wds)

def phoneticWord(word):
	w = word.lower()
	if arpabetWds.count(w) > 0:
		phWd = ''.join(arpabet[w][0])
	else:
		phWd = w
		#print (word, "it's an exception")

	return phWd

