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
patternComma = re.compile(r'\d(, )')
patternPunctuation = re.compile(r'\b([,\.:;!\?]{1,2}) |\-')
patternPunctuationWithoutSpace = re.compile(r'\b([,\.;!\?])')
patternSent = re.compile(r'.+')
patternSents = re.compile(r'"([\w\d\s\':]+?)"')
patternSpaces = re.compile(r'\s{2,7}')
patternAnd = re.compile(r'&')

def readTest(file):
    f = open (file, 'r')
    line = []
    for l in f:
        l = patternPunctuation.sub(' ', l)
        l = patternComma.sub(' ', l)
        l = patternPunctuationWithoutSpace.sub('', l)
        l = patternAnd.sub(' and ', l)
        line.append(patternSpaces.sub(' ', l))
    f.close()
    originalSentences = []
    lineSentences = []
    sentss = []
    rightAnswers = []

    for i in range(1,len(line),4):
        originalSentences.append(patternSent.match(line[i]).group().lower())
        lineSentences.append(patternSent.match(line[i+1]).group().lower())
        sentss.append(patternSents.findall(line[i+2]))
        rightAnswers.append(patternSent.match(line[i+3]).group().lower())

    return originalSentences, lineSentences, sentss, rightAnswers


#-------------ТЕСТ---------------------------
import time
from datetime import datetime
from jellyfish import levenshtein_distance as levenshtein
from bestChoice import googleSentensBestChoice

def testingAndWriting():
    f = open ('test_result.txt', 'w')
    tt0 = time.time()
    originalSentences, lineSentences, sentss, rightAnswers = readTest('test.txt')
    sourceLevensh_sum = 0
    resultLevensh_sum = 0
    improvingCount = 0
    wrongCases = []
    for i, orS in enumerate(originalSentences):
        gSeBeCh = googleSentensBestChoice(orS, lineSentences[i], sentss[i])
        if rightAnswers[i] == gSeBeCh:
            sourceLevensh = levenshtein(originalSentences[i], lineSentences[i])
            resultLevensh = levenshtein(originalSentences[i], gSeBeCh)
            if sourceLevensh > resultLevensh:
                improvingCount += 1
            sourceLevensh_sum += sourceLevensh
            resultLevensh_sum += resultLevensh
            f.write('%s. OK, Нач. Л-штэйн - %s, Итоговый - %s\n' % (i+1, sourceLevensh, resultLevensh))
            f.write("Оригинальное - %s\n" % originalSentences[i])
            f.write("В строке     - %s\n" % lineSentences[i])
            f.write("Итоговое     - %s\n" % gSeBeCh)
            f.write('\n')
        else:
            wrongCases.append(i+1)
            f.write('%s. !!!!!!!!!!---НЕПРАВИЛЬНО---!!!!!!!!!!!\n' % (i+1))
            f.write("Должно быть  - %s\n" % rightAnswers[i])
            f.write('\n')
        if i == len(originalSentences) - 1:
            tt1 = time.time()
            f.write('Неправильные проверки %s,  всего - %s\n' % (wrongCases, len(wrongCases)))
            f.write('Количество улучшений %s, процент %s\n' % (improvingCount, int(improvingCount/(i+1)*100)))
            f.write('Средний нач. Л-штейн - %s, средний итоговый - %s\n' % (round(sourceLevensh_sum/(i+1),2),
                                                                        round(resultLevensh_sum/(i+1),2)))
            f.write('Время выполнения %s проверок - %s, %s sec на одну проверку\n'
                    'Дата -%s' % (i+1, round(tt1-tt0,2), round((tt1-tt0)/(i+1), 3), str(datetime.now())))

    f.close()
    return


def testing(full = True):
    tt0 = time.time()
    originalSentences, lineSentences, sentss, rightAnswers = readTest('test.txt')
    sourceLevensh_sum = 0
    resultLevensh_sum = 0
    improvingCount = 0
    wrongCases = []
    for i, orS in enumerate(originalSentences):
        gSeBeCh = googleSentensBestChoice(orS, lineSentences[i], sentss[i])
        if rightAnswers[i] == gSeBeCh:
            sourceLevensh = levenshtein(unicode(originalSentences[i]), unicode(lineSentences[i]))
            resultLevensh = levenshtein(unicode(originalSentences[i]), unicode(gSeBeCh))
            if sourceLevensh > resultLevensh:
                improvingCount += 1
            sourceLevensh_sum += sourceLevensh
            resultLevensh_sum += resultLevensh
            if full:
                print "Оригинальное - %s" % originalSentences[i]
                print "В строке     - %s" % lineSentences[i]
                print u"Итоговое     - %s" % gSeBeCh
            print('%s. OK, Нач. Л-штэйн - %s, Итоговый - %s' % (i+1, sourceLevensh, resultLevensh))
        else:
            wrongCases.append(i+1)
            if full:
                print "Оригинальное - %s" % originalSentences[i]
                print "В строке     - %s" % lineSentences[i]
                print("Итоговое     - %s" % gSeBeCh)
            print '%s. !!!!!!!!!!---НЕПРАВИЛЬНО---!!!!!!!!!!!' % (i+1)
            print "Должно быть  - %s\n" % rightAnswers[i]
        if i == len(originalSentences) - 1:
            tt1 = time.time()
            print '\nНеправильные проверки %s,  всего - %s  ' % (wrongCases, len(wrongCases))
            print 'Количество улучшений %s, процент %s' % (improvingCount, int(improvingCount/float(i+1)*100))
            print 'Средний нач. Л-штейн - %s, средний итоговый - %s' % (round(sourceLevensh_sum/float(i+1),2),
                                                                        round(resultLevensh_sum/float(i+1),2))
            print 'Время выполнения %s проверок - %s, %s sec на одну проверку\nДата - %s' % (i+1, round(tt1-tt0,2), round((tt1-tt0)/(i+1), 3), str(datetime.now()))

    return

testing()


