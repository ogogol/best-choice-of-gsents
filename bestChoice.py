# -*- coding: utf-8 -*-
from cleaningText import cleaningText
from difference import *
from words import *



def delWordsRunning(oneOrCouple, orSentWdsRunning, originalSentenceWords, gSentWdsRunning, googleSentenceWords):
    #удаляет лишний дубль в предложении, если такового нет в оригинальном
    #разбита на две функции эта и wordsRunning
    if len(orSentWdsRunning) < len(gSentWdsRunning):
        gSentWds1 = [w for w in googleSentenceWords]
        count = 0
        for i in gSentWdsRunning:
            del gSentWds1[i - count]
            if oneOrCouple > 1:
                del gSentWds1[i - count]
            gSentWds1, googleSentenceWords = addWordOrNotChoice(' '.join(originalSentenceWords), gSentWds1, googleSentenceWords)
            count += 1

    return googleSentenceWords


def wordsRunning(originalSentenceWords, googleSentenceWords):
    #удаляет лишний дубль в предложении, если такового нет в оригинальном
    #разбита на две функции эта и delWordsRunning
    gSentWdsRunning = [i for i in twoWordsRunning(googleSentenceWords)]
    if gSentWdsRunning:
        orSentWdsRunning = [i for i in twoWordsRunning(originalSentenceWords)]
        googleSentenceWords = delWordsRunning(1, orSentWdsRunning, originalSentenceWords, gSentWdsRunning, googleSentenceWords)

    gSentWdsRunning = [i for i in twoCoupleWordsRunning(googleSentenceWords)]
    if gSentWdsRunning:
        orSentWdsRunning = [i for i in twoCoupleWordsRunning(originalSentenceWords)]
        googleSentenceWords = delWordsRunning(2, orSentWdsRunning, originalSentenceWords, gSentWdsRunning, googleSentenceWords)

    return googleSentenceWords


def correctSents(lineSentWds, sentWds):
    #корректирует список предожений с учетом, того что уже было в строке до ввода
    oldSentWds = getImputedBeforeSent(lineSentWds, sentWds)
    correctedSentsWds = []
    for i, s in enumerate(sentWds):
        correctedSentsWds.append(oldSentWds+s)

    return correctedSentsWds


def getSimilarSent(orSent, gSent, sents):
    #возращает наиболее подходящее предложение для сравнения из последней 1/2 списка вариантов
    bestSent = gSent

    bestSents = get_close_matches(orSent, sents[int((len(sents)/2.0)-1):], 2, 0.2)

    for s in bestSents:
        leve_or_best = levenshtein(unicode(orSent), unicode(bestSent))
        leve_or_sNext = levenshtein(unicode(orSent), unicode(s))
        if leve_or_best > leve_or_sNext:
            bestSent = s

    return bestSent


def correctWrongWords(wordsDict, wds, originalSentenceWords, googleSentenceWords, cutoff = 0.4):
    '''
    находит неправильные слова и корректирует
    :param wordsDict: dictionary
    :param wds: list
    :param originalSentenceWords: string
    :param googleSentenceWords: string
    :return: googleSentenceWords list
    '''
    gSentLen = len(googleSentenceWords)
    for value in wordsDict.values():
        if value[2] < len(originalSentenceWords):
            wdLst = suitableWordsList(value[1], originalSentenceWords[value[2]], wds, gSentLen, False)
            if wdLst == []:
                wdLst = suitableWordsList(value[1], value[0], wds, gSentLen)
        else:
            wdLst = suitableWordsList(value[1], value[0], wds, gSentLen)

        w = get_close_matches(originalSentenceWords[value[2]], wdLst, 1, cutoff)

        if w:
            if value[1] < len(googleSentenceWords):
                googleSentenceWords[value[1]] = w[0]
            else:
                googleSentenceWords.append(w[0])

    return googleSentenceWords


def correctMissedWords(wordsDict, wds, originalSentenceWords, googleSentenceWords, cutoff = 0.6):
    '''
    вставляет пропущенные слова, если это улучшает результат
    :param wordsDict: dictionary
    :param wds: list
    :param originalSentenceWords: string
    :param googleSentenceWords: string
    :return: googleSentenceWords list
    '''
    gSentWds1 = [w for w in googleSentenceWords]
    gSentWds2 = [w for w in googleSentenceWords]
    orSent = ' '.join(originalSentenceWords)
    gSentLen = len(googleSentenceWords)
    for value in wordsDict.values():
        wList = suitableWordsList(value[1], value[0], wds, gSentLen, False)

        w = get_close_matches(value[0], wList, 1, cutoff)

        if w:
            if value[1] < len(googleSentenceWords):
                del gSentWds1[value[1]]
                gSentWds1.insert(value[1], w[0])
                gSentWds2.insert(value[1], w[0])
                gSentWds1, gSentWds2, googleSentenceWords = delAddWordOrNotChoice(orSent, gSentWds1, gSentWds2, googleSentenceWords)

            else:
                gSentWds1.append(w[0])
                gSentWds1, googleSentenceWords = addWordOrNotChoice(orSent, gSentWds1, googleSentenceWords)

    return googleSentenceWords


def correctImputedSentence(oSent, gSent, wds):
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

    googleSentenceWords = splitWords(originalSentenceWords, googleSentenceWords)
    googleSentenceWords = concatWords(originalSentenceWords, googleSentenceWords)

    gSent_new = ' '.join(googleSentenceWords)

    exWds, misWds, wrWds, rWds = getSentsDifference(oSent, gSent_new, wds)

    googleSentenceWords = correctWrongWords(wrWds, wds, originalSentenceWords, googleSentenceWords)
    if oSent == ' '.join(googleSentenceWords):
        return ' '.join(googleSentenceWords)
    googleSentenceWords = correctMissedWords(misWds, wds, originalSentenceWords, googleSentenceWords)

    if oSent == ' '.join(googleSentenceWords):
        return ' '.join(googleSentenceWords)

    googleSentenceWords = wordsRunning(originalSentenceWords, googleSentenceWords)

    return ' '.join(googleSentenceWords)


def googleSentensBestChoice(originalSentence, lineSentence, sents):
    #главная функция по коррекции наговоренного предложения в строке ввода к масимальной похожести на оригинальное,
    #на основе разпознанных вариантов от гугла

    #-------------------------??? надо будет убрать ???
    originalSentence = cleaningText(originalSentence)
    lineSentence = cleaningText(lineSentence)
    sents = cleaningText(sents)
    #-------------------------

    #------------------------- надо будет убрать
    if originalSentence == lineSentence:
        return lineSentence
    #-------------------------

    sentsWds = makeSentsWdsList(sents)
    orSentWds = originalSentence.split()
    lineSentWds = lineSentence.split()

    correctedSentsWds = correctSents(lineSentWds, sentsWds)
    correctedSents = [' '.join(s) for s in correctedSentsWds]

    similarSent = getSimilarSent(originalSentence, lineSentence, correctedSents) # выбираем лучшее предложение из последних
    if originalSentence == similarSent:
        return similarSent

    words = makeWordsList(orSentWds, lineSentWds, correctedSentsWds)
    googleSentence = correctImputedSentence(originalSentence, similarSent, words)

    #print("%s, Предложения %s" % (len(sents), sents))
    #print("Words %s" % words)
    #print("Сравниваемое - %s" % similarSent)

    return googleSentence
