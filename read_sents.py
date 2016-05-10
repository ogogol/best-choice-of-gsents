# -*- coding: utf-8 -*-
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

import re
patternSent = re.compile(r'.+')
patternSents = re.compile(r'"([\w\d\s\']+?)"')

def readTest(file):
    f = open (file, 'r')
    line = [line for line in f]
    f.close()
    originalSentences = []
    lineSentences = []
    sentss = []
    rightAnswers = []

    for i in range(1,len(line),4):
        originalSentences.append(patternSent.match(line[i]).group())
        lineSentences.append(patternSent.match(line[i+1]).group())
        sentss.append(patternSents.findall(line[i+2]))
        rightAnswers.append(patternSent.match(line[i+3]).group())

    return originalSentences, lineSentences, sentss, rightAnswers

