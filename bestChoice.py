# -*- coding: utf-8 -*-
from difference import *
from difflib import *


# поиск слов по неправиьному слову и составление списка слов, стоящих в том же месте, где и неправильное слово
def suitableWordsList (wd,wds):
    suitWs = []
    for i in range(len(wds)):
        for j in range(len(wds[i])):
            if wd == wds [i][j]:
                for n in range(len(wds[i])):
                    if wd != wds [i][n]:
                        suitWs.append(wds[i][n])

    return suitWs

# коррекция порядка слов в предложении
# сравнение предложения по отношению к самому длинному и вставка одного '' вместо пропущенного слова
def wodrsRightOrder (maxSent, sent):
    msl = len(maxSent)
    sl = len(sent)
    sentWds = sent.split()

    if msl - sl > 0:
        exWds, misWds, wrWds, rWds = sentsDifference(maxSent, sent)
        for key in misWds.keys():
            if key < len(sentWds) - 1:
                sentWds.insert(key,'')

    return sentWds


# создаем и наполняем двумерный список слов на основе самого длинного предожения
# типа [['Peter'], ['Hobbs', 'hopes'], ['game', 'same', 'came'], ['here'], ['this'], ['mon', 'morning']]
def wordsList(sents):
    # выбираем самое длинное предложение из предложенных гуглом и все предложения разбиваем на слова
    s = 0
    wd = []
    for i in range(len(sents)):
        wd.append(sents[i].split())
        if len(wd[i]) >= s:
            s = len(wd[i])
            maxLenSent = wd[i]
            maxSent = sents[i]

    # создаем двумерный список слов на основе самого длинного предожения
    l = len(maxLenSent)
    words = [['']*1 for i in range(l)]
    for i in range(l):
        words[i][0] = maxLenSent[i]

    # наполняем двумерный список всех слов с учетом их порядка
    for i in range(len(sents)):
        m = min(len(wd[i]) + 2, l)
        mS = ' '.join(maxLenSent[0:m])
        wd[i] = wodrsRightOrder (mS, sents[i])
        for j in range(len(wd[i])):
            if words[j].count(wd[i][j]) == 0:
                words[j].append(wd[i][j])

    return words

def bChoice(orSent, gSent, sents):
    bestSent = gSent
    n = int(len(sents)/3)
    s = sents[::-1]
    if levenshtein(orSent, bestSent) > levenshtein(orSent,s[0]):
        for i in range(n):
            if levenshtein(orSent,s[i]) > levenshtein(orSent,s[i+1]):
                bestSent = s[i+1]

    return bestSent


# проверка предложения и замена неправильных слов на правильные
def googleSentenceCorrection(oSent, gSent, wds): #gTrSent,
    originalSentenceWords = oSent.split()
    googleSentenceWords = gSent.split()

    lenOriginalSentenceWords = len(originalSentenceWords)
    lenGoogleSentenceWords = len(googleSentenceWords)
    maxLen = max(len(wds),lenGoogleSentenceWords)

    for i in range(maxLen):
        ok = 0
        if i < lenOriginalSentenceWords:
            if i < lenGoogleSentenceWords:
                if originalSentenceWords[i].lower() != googleSentenceWords[i].lower():
                    wdLst = suitableWordsList(googleSentenceWords[i], wds)
                    for w in wdLst:
                        if originalSentenceWords[i].lower() == w.lower():
                            googleSentenceWords[i] = w
                            ok = 1
                    if ok == 0:
                        w = get_close_matches(originalSentenceWords[i], wdLst, 1, 0.2)
                        if len(w) > 0:
                            googleSentenceWords[i] = w[0]

            elif i < len(wds):
                for j in range(len(wds[i])):
                    if originalSentenceWords[i].lower() == wds[i][j].lower():
                        googleSentenceWords.append(wds[i][j])
        else:
            break

    return googleSentenceWords


originalSentence = "but in any case I'd rather be seasick than dead "
googleSentence = "but in any case I'd rather be sick than that "
sents = readSents("4.txt")


words = wordsList(sents)
print "Words %s " % words
bSent = bChoice(originalSentence, googleSentence, sents) # выбираем лучшее предложение из последних
googleSentenceWords = googleSentenceCorrection(originalSentence, bSent, words)

print "Оригинальное - %s" % originalSentence
print "Выдал гугл   - %s" % googleSentence
print "Итоговое     - %s" % ' '.join(googleSentenceWords)
