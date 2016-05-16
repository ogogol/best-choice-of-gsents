# -*- coding: utf-8 -*-
import re
from difference import *
from jellyfish import levenshtein_distance as levenshtein
from jellyfish import jaro_winkler as jaro
from jellyfish import nysiis
from difflib import get_close_matches

patternPunctuation = re.compile(r'\b([,\.:;!\?]{1,2}) |\-')
patternComma = re.compile(r'\d(, )')
patternPunctuationWithoutSpace = re.compile(r'\b([,\.;!\?])')
patternSent = re.compile(r'.+')
patternSents = re.compile(r'"([\w\d\s\':]+?)"')
patternSpaces = re.compile(r'\s{2,7}')
patternAnd = re.compile(r'&')

def cleaningText(txt):
    #очищает текст от знаков препинания и подготавливает для работы
    if isinstance(txt, str):
        l = patternPunctuation.sub(' ', txt)
        l = patternComma.sub(' ', l)
        l = patternPunctuationWithoutSpace.sub('', l)
        l = patternAnd.sub(' and ', l)
        txt = patternSpaces.sub(' ', l).lower()

    elif isinstance(txt, list):
        for i, l in enumerate(txt):
            l = patternPunctuation.sub(' ', l)
            l = patternComma.sub(' ', l)
            l = patternPunctuationWithoutSpace.sub('', l)
            l = patternAnd.sub(' and ', l)
            txt[i] = patternSpaces.sub(' ', l).lower()

    return txt


def isTheSameWords(n, orSentWds, comSentWds, cutoff = 2):
    #возращает флаг TRUE если оригинале и в предложении есть в окрестности n +-cutoff одинаковые слова
    isWds = False
    start = max([0, n-cutoff])
    end = min(n+cutoff, len(comSentWds), len(orSentWds))
    for i in range(start, end):
        if comSentWds[n] == orSentWds[i]:
            isWds = True
    for i in range(start, end):
        if comSentWds[n+1] == orSentWds[i]:
            isWds = True

    return isWds


def addWordOrNotChoice(orSent, gSentWds, googleSentenceWords):
    #возращает наиболее близкий к оригиналу вариант из двух предложений, в одном из которых добавлено или удалено слово
    orSent = unicode(orSent)
    if levenshtein(orSent, unicode(' '.join(gSentWds))) >= levenshtein(orSent, unicode(' '.join(googleSentenceWords))):
        gSentWds = [w for w in googleSentenceWords]
    else:
        googleSentenceWords = [w for w in gSentWds]

    return gSentWds, googleSentenceWords


def delAddWordOrNotChoice(orSent, gSentWds1, gSentWds2, googleSentenceWords):
    #возращает наиболее близкий к оригиналу вариант из трех предложений,
    #в одном из которых добавлено или удалено слово, в другом и то и другое
    orSent = unicode(orSent)
    if levenshtein(orSent, unicode(' '.join(gSentWds1))) > levenshtein(orSent, unicode(' '.join(gSentWds2))):
        if levenshtein(orSent, unicode(' '.join(gSentWds2))) > levenshtein(orSent, unicode(' '.join(googleSentenceWords))):
            gSentWds1 = [w for w in googleSentenceWords]
            gSentWds2 = [w for w in googleSentenceWords]
        else:
            gSentWds1 = [w for w in gSentWds2]
            googleSentenceWords = [w for w in gSentWds2]
    else:
        if levenshtein(orSent, unicode(' '.join(gSentWds1))) < levenshtein(orSent, unicode(' '.join(googleSentenceWords))):
            googleSentenceWords = [w for w in gSentWds1]
            gSentWds2 = [w for w in gSentWds1]
        else:
            gSentWds1 = [w for w in googleSentenceWords]
            gSentWds2 = [w for w in googleSentenceWords]

    return gSentWds1, gSentWds2, googleSentenceWords


def isSumma2WordsTheBest(baseWord, word1, word2, n, comSentWds):
    #проверяет не больше ли подходит два слова из предложения вместе на слово из оригинала,
    #чем каждое само по себе
    #возращает лучший вариант списка слов предожении, либо с одним слитым, либо с двумя
    baseWord = unicode(baseWord)
    word1 = unicode(word1)
    word2 = unicode(word2)
    leve_2words = levenshtein(baseWord, word1+word2)
    if leve_2words < levenshtein(baseWord, word1) and leve_2words < levenshtein(baseWord, word2):
        comSentWds[n] += comSentWds[n+1]
        del comSentWds[n+1]

    return comSentWds


def joinCorrectSentWordsList(orSentWords, comSentWords):
    #проверяет все слова предожения на слияние подряд идущих слов
    #возращает скорретированный список слов предожения
    sentLen = len(comSentWords)
    orSentLen = len(orSentWords)
    count = 1
    for i, val in enumerate(orSentWords):
        if i < sentLen - count:
            if i < orSentLen - 1:
                if not isTheSameWords(i, orSentWords, comSentWords):
                    comSentWords = isSumma2WordsTheBest(orSentWords[i], comSentWords[i], comSentWords[i+1], i, comSentWords)
                    count += 1
            else:
                comSentWords = isSumma2WordsTheBest(orSentWords[i], comSentWords[i], comSentWords[i+1], i, comSentWords)
                count += 1

    return comSentWords


def twoWordsRunning(sentWds):
    #возращает список порядковых номеров двух подряд одинаковых слов
    r = []
    for i, w in enumerate(sentWds):
        if i + 1 < len(sentWds):
            if w == sentWds[i+1]:
                r.append(i)

    return r


def twoCoupleWordsRunning(sentWds):
    #возращает список порядковых номеров двух подряд одинаковых пары слов
    r = []
    for i, w in enumerate(sentWds):
        if i + 3 < len(sentWds):
            if w == sentWds[i+2] and sentWds[i+1] == sentWds[i+3]:
                r.append(i)

    return r

def delWordsRunning(oneOrCouple, orSentWdsRunning, originalSentenceWords, gSentWdsRunning, googleSentenceWords):
    #удаляет лишний дубль в предложении, если такового нет в оригинальном
    #разбита на две функции эта и del2WordsRunning
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

def del2WordsRunning(originalSentenceWords, googleSentenceWords):
    #удаляет лишний дубль в предложении, если такового нет в оригинальном
    #разбита на две функции эта и delWordsRunning
    gSentWdsRunning = [i for i in twoWordsRunning(googleSentenceWords)]
    if len(gSentWdsRunning) > 0:
        orSentWdsRunning = [i for i in twoWordsRunning(originalSentenceWords)]
        googleSentenceWords = delWordsRunning(1, orSentWdsRunning, originalSentenceWords, gSentWdsRunning, googleSentenceWords)

    gSentWdsRunning = [i for i in twoCoupleWordsRunning(googleSentenceWords)]
    if len(gSentWdsRunning) > 0:
        orSentWdsRunning = [i for i in twoCoupleWordsRunning(originalSentenceWords)]
        googleSentenceWords = delWordsRunning(2, orSentWdsRunning, originalSentenceWords, gSentWdsRunning, googleSentenceWords)

    return googleSentenceWords

def makeSentsWdsList(sents):
    #возращает список списков слов предложений
    sentWds = []
    for i, s in enumerate(sents):
        sentWds.append(s.split())

    return sentWds

def getImputedBeforeSent(lineSentWds, sentWds):
    #возращает список слов начального предожения, которое было в строке до начала ввода
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
    #корректирует список предожений с учетом, того что уже было в строке до ввода
    oldSentWds = getImputedBeforeSent(lineSentWds, sentWds)
    correctedSentsWds = []
    for i, s in enumerate(sentWds):
        correctedSentsWds.append(oldSentWds+s)

    return correctedSentsWds


def suitableWordsList (n, wd, wds, sentLen, about = True):
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
        if about == False:
            approx_w = get_close_matches(wd, wds[i], 1, 0.6)
            if len(approx_w) > 0:
                suitedWords.append(approx_w[0])
        else:
            for w in wds[i]:
                if wd == w:
                    for value in wds[i]:
                        if suitedWords.count(value) == 0:
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
                elif levenshtein(nysiis(unicode(sentWds[i])), nysiis(unicode(maxSentWds[i]))) >\
                        levenshtein(nysiis(unicode(sentWds[i])), nysiis(unicode(maxSentWds[i+1]))):
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
    #возращает наиболее подходящее предложение для сравнения из последней 1/4 списка вариантов
    bestSent = gSent
    n = int(len(sents)/4)
    s = sents[::-1]
    orSent = unicode(orSent)
    for i in range(n):
        if levenshtein(orSent, unicode(bestSent)) > levenshtein(orSent, unicode(s[i+1])):
            bestSent = s[i+1]

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
        #print(value[1], originalSentenceWords[value[2]], value[0], wdLst, w)
        if len(w) > 0:
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
        #print(value[1], originalSentenceWords[value[2]], value[0], wList, w)
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
    googleSentenceWords = joinCorrectSentWordsList(originalSentenceWords, googleSentenceWords)
    gSent_new = ' '.join(googleSentenceWords)

    exWds, misWds, wrWds, rWds = getSentsDifference(oSent, gSent_new, wds)

    #print(misWds, wrWds)
    googleSentenceWords = correctWrongWords(wrWds, wds, originalSentenceWords, googleSentenceWords)
    googleSentenceWords = correctMissedWords(misWds, wds, originalSentenceWords, googleSentenceWords)
    googleSentenceWords = del2WordsRunning(originalSentenceWords, googleSentenceWords)

    return ' '.join(googleSentenceWords)


def googleSentensBestChoice(originalSentence, lineSentence, sents):
    #главная функция по коррекции наговоренного предложения в строке ввода к масимальной похожести на оригинальное,
    #на основе разпознанных вариантов от гугла
    originalSentence = cleaningText(originalSentence)
    lineSentence = cleaningText(lineSentence)
    sents = cleaningText(sents)

    #------------------------- надо будет убрать
    if originalSentence == lineSentence:
        return lineSentence
    #-------------------------

    sentsWds = makeSentsWdsList(sents)
    orSentWds = originalSentence.split()
    lineSentWds = lineSentence.split()

    correctedSentsWds = correctSents(lineSentWds, sentsWds)
    correctedSents = [' '.join(s) for s in correctedSentsWds]

    words = wordsList(orSentWds, lineSentWds, correctedSentsWds)
    similarSent = getSimilarSent(originalSentence, lineSentence, correctedSents) # выбираем лучшее предложение из последних
    googleSentenceWords = correctImputedSentence(originalSentence, similarSent, words)

    #print("%s, Предложения %s" % (len(sents), sents))
    #print("Words %s" % words)
    #print("Сравниваемое - %s" % similarSent)

    return googleSentenceWords
