# -*- coding: utf-8 -*-
from difference import *
from jellyfish import levenshtein_distance as levenshtein
from jellyfish import nysiis
from difflib import get_close_matches

def twoWordsRunning(sentWds):
    r = []
    for i, w in enumerate(sentWds):
        if i + 1 < len(sentWds):
            if w.lower() == sentWds[i+1].lower():
                r.append(i)

    return r

def del2WordsRunning(originalSentenceWords, googleSentenceWords):
    twoWdsRunning = twoWordsRunning(googleSentenceWords)
    if len(twoWordsRunning(originalSentenceWords)) < len(twoWdsRunning):
        gSentWds1 = [w for w in googleSentenceWords]
        count = 0
        for i in twoWdsRunning:
            del gSentWds1[i - count]
            gSentWds1, googleSentenceWords = addWordOrNotChoice(' '.join(originalSentenceWords), gSentWds1, googleSentenceWords)
            count += 1

    return googleSentenceWords

def makeSentsWdsList(sents):
    sentWds = []
    for i, s in enumerate(sents):
        sentWds.append(s.split())

    return sentWds

def getImputedBeforeSent(lineSentWds, sentWds):

    lastImputSentWds = sentWds[len(sentWds)-1]
    oldSentWds = []

    lineSentWdsLen = len(lineSentWds)
    lastSentWdsLen = len(lastImputSentWds)
    if lastSentWdsLen >= lineSentWdsLen:
        return oldSentWds

    end = min(lineSentWdsLen, len(lastImputSentWds))
    lineSenWs_invert = lineSentWds[::-1]
    lastImSenWs_invert = lastImputSentWds[::-1]
    for i, w in enumerate(lineSenWs_invert):

        if i == lastSentWdsLen or w != lastImSenWs_invert[i]:
            oldSentWds = lineSentWds[:lineSentWdsLen - i]
            break

    return oldSentWds

def correctSents(lineSentWds, sentWds):
    oldSentWds = getImputedBeforeSent(lineSentWds, sentWds)
    correctedSentsWds = []
    for i, s in enumerate(sentWds):
        correctedSentsWds.append(oldSentWds+s)

    return correctedSentsWds


def suitableWordsList (n, wd, wds, sentLen):
    '''
    поиск слов по неправильному слову и составление списка слов, стоящих в том же месте, где и неправильное слово
    :param wd: string
    :param wds: list
    :return: suitedWords list
    '''
    suitedWords = []
    wdsL = len(wds)
    if sentLen > wdsL:
        start = 0
        end = wdsL
    else:
        start = max([0, n-1])
        end = min([wdsL, n+4])

    for i in range(start, end):
        for w in wds[i]:
            if wd.lower() == w.lower():
                for value in wds[i]:
                    suitedWords.append(value)

    return suitedWords

def wordsRightOrder(maxSentWds, sentWds):
    '''
    коррекция порядка слов в предложении
    сравнение предложения по отношению к самому длинному и вставка одного '' вместо пропущенного слова
    :param maxSent: string
    :param sent: string
    :return: sentWds: list
    '''
    msl = len(maxSentWds)
    sl = len(sentWds)

    if msl - sl > 0:
        for i in range(msl):
            if i + 1 < msl and i < len(sentWds):
                if sentWds[i] == maxSentWds[i]:
                    continue
                elif levenshtein(nysiis(sentWds[i]), nysiis(maxSentWds[i])) >\
                        levenshtein(nysiis(sentWds[i]), nysiis(maxSentWds[i+1])):
                    sentWds.insert(i,'')

    return sentWds

def wordsList(orSentWds, lineSentWds, sentWds):
    '''
    создаем и наполняем двумерный список слов на основе самого длинного предожения
    типа [['Peter'], ['Hobbs', 'hopes'], ['game', 'same', 'came'], ['here'], ['this'], ['mon', 'morning']]
    :param sents: list
    :return: words: list список упорядоченных слов, words_l те же слова но в нижнем регистре
    '''

    # выбираем самое длинное предложение из предложенных гуглом и все предложения разбиваем на слова
    maxSentLen = 0
    maxLongSent = ''
    for i, sw in enumerate(sentWds):
        if len(sw) >= maxSentLen:
            maxSentLen = len(sw)
            maxLongSent = sw

    maxLongSent = joinCorrectSentWordsList(orSentWds, maxLongSent)

    words = []
    for i, w in enumerate(maxLongSent):
        words.append([w,])

    # наполняем список всех слов с учетом их порядка
    for i, sWds in enumerate(sentWds):
        m = min(len(sWds) + 1, maxSentLen)

        sentWds[i] = joinCorrectSentWordsList(orSentWds, sWds)
        if m <= len(orSentWds):
            mS = orSentWds[0:m]
        else:
            mS = maxLongSent[0:m]

        sentWds[i] = wordsRightOrder(mS, sentWds[i])
        for j, value in enumerate(sentWds[i]):
            if j < len(words):
                if words[j].count(value) == 0:
                    words[j].append(value)
            else:
                words.append([value,])

    return words


def getSimilarSent(orSent, gSent, sents):
    bestSent = gSent
    n = int(len(sents)/4)
    s = sents[::-1]
    for i in range(n):
        if levenshtein(orSent, bestSent) > levenshtein(orSent, s[i+1]):
            bestSent = s[i+1]

    return bestSent


def correctWrongWords(wordsDict, wds, originalSentenceWords, googleSentenceWords, cutoff):
    '''
    находит неправильные слова и корректирует
    :param wordsDict: dictionary
    :param wds: list
    :param originalSentenceWords: string
    :param googleSentenceWords: string
    :return: googleSentenceWords list
    '''

    for value in wordsDict.values():
        if value[2] < len(originalSentenceWords):
            wdLst = suitableWordsList(value[1], originalSentenceWords[value[2]], wds, len(googleSentenceWords))
            if wdLst == []:
                wdLst = suitableWordsList(value[1], value[0], wds, len(googleSentenceWords))
        else:
            wdLst = suitableWordsList(value[1], value[0], wds, len(googleSentenceWords))

        w = get_close_matches(originalSentenceWords[value[2]], wdLst, 1, cutoff)

        if len(w) > 0:
            if value[1] < len(googleSentenceWords):
                googleSentenceWords[value[1]] = w[0]
            else:
                googleSentenceWords.append(w[0])

    return googleSentenceWords

def addWordOrNotChoice(orSent, gSentWds, googleSentenceWords):
    if levenshtein(orSent, ' '.join(gSentWds)) >= levenshtein(orSent, ' '.join(googleSentenceWords)):
        gSentWds = [w for w in googleSentenceWords]
    else:
        googleSentenceWords = [w for w in gSentWds]

    return gSentWds, googleSentenceWords

def delAddWordOrNotChoice(orSent, gSentWds1, gSentWds2, googleSentenceWords):
    if levenshtein(orSent, ' '.join(gSentWds1)) > levenshtein(orSent, ' '.join(gSentWds2)):
        if levenshtein(orSent, ' '.join(gSentWds2)) > levenshtein(orSent, ' '.join(googleSentenceWords)):
            gSentWds1 = [w for w in googleSentenceWords]
            gSentWds2 = [w for w in googleSentenceWords]
        else:
            gSentWds1 = [w for w in gSentWds2]
            googleSentenceWords = [w for w in gSentWds2]
    else:
        if levenshtein(orSent, ' '.join(gSentWds1)) < levenshtein(orSent, ' '.join(googleSentenceWords)):
            googleSentenceWords = [w for w in gSentWds1]
            gSentWds2 = [w for w in gSentWds1]
        else:
            gSentWds1 = [w for w in googleSentenceWords]
            gSentWds2 = [w for w in googleSentenceWords]

    return gSentWds1, gSentWds2, googleSentenceWords

def correctMissedWords(wordsDict, wds, originalSentenceWords, googleSentenceWords, cutoff):
    '''
    находит пропущенные слова и корректирует
    :param wordsDict: dictionary
    :param wds: list
    :param originalSentenceWords: string
    :param googleSentenceWords: string
    :return: googleSentenceWords list
    '''

    gSentWds1 = [w for w in googleSentenceWords]
    gSentWds2 = [w for w in googleSentenceWords]
    orSent = ' '.join(originalSentenceWords)

    for value in wordsDict.values():
        wList = suitableWordsList(value[1], value[0], wds, len(googleSentenceWords))
        if wList == [] and value[1] < len(wds) and value[1] < len(googleSentenceWords) and \
                            value[0] != googleSentenceWords[value[1]]:
                wList = wds[value[1]]

        w = get_close_matches(value[0], wList, 1, cutoff)

        if len(w) > 0:
            if value[1] < len(googleSentenceWords):
                del gSentWds1[value[1]]
                gSentWds1.insert(value[1], w[0])
                gSentWds2.insert(value[1], w[0])
                gSentWds1, gSentWds2, googleSentenceWords = delAddWordOrNotChoice(orSent, gSentWds1, gSentWds2, googleSentenceWords)

            else:
                gSentWds1.append(w[0])
                gSentWds1, googleSentenceWords = addWordOrNotChoice(orSent, gSentWds1, googleSentenceWords)


    return googleSentenceWords


def correctImputedSentence(oSent, gSent, wds, cutoff = 0.4):
    '''
    проверка предложения и замена неправильных слов на правильные
    :param oSent: string оригинальное предложение
    :param gSent: string лучшее предложение для сравнения от гугла
    :param wds: list список упорядоченных слов всех фраз от гугла
    :param cutoff: num порог отсечения подобия слов, используется если не найдено ни одного 100% подходящего
    :return: googleSentenceWords - string скорректированное предложение
    '''
    originalSentenceWords = oSent.split()
    googleSentenceWords = gSent.split()
    googleSentenceWords = joinCorrectSentWordsList(originalSentenceWords, googleSentenceWords)
    gSent_new = ' '.join(googleSentenceWords)

    exWds, misWds, wrWds, rWds = getSentsDifference(oSent, gSent_new, wds)
    #print(misWds, wrWds)
    googleSentenceWords = correctWrongWords(wrWds, wds, originalSentenceWords, googleSentenceWords, cutoff)
    googleSentenceWords = correctMissedWords(misWds, wds, originalSentenceWords, googleSentenceWords, cutoff)

    googleSentenceWords = del2WordsRunning(originalSentenceWords, googleSentenceWords)

    return ' '.join(googleSentenceWords)


def googleSentensBestChoice(originalSentence, lineSentence, sents):
    #------------------------- надо будет убрать
    if originalSentence.lower() == lineSentence.lower():
        googleSentenceWords = lineSentence
        return googleSentenceWords
    #-------------------------

    sentsWds = makeSentsWdsList(sents)
    orSentWds = originalSentence.split()
    lineSentWds = lineSentence.split()

    correctedSentsWds = correctSents(lineSentWds, sentsWds)
    correctedSents = [' '.join(s) for s in correctedSentsWds]

    words = wordsList(orSentWds, lineSentWds, correctedSentsWds)
    similarSent = getSimilarSent(originalSentence, lineSentence, correctedSents) # выбираем лучшее предложение из последних
    googleSentenceWords = correctImputedSentence(originalSentence, similarSent, words)

    #print("Предложения %s" % sents)
    print("Words %s" % words)
    print("Сравниваемое - %s" % similarSent)

    return googleSentenceWords
