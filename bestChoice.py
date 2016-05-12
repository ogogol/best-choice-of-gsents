# -*- coding: utf-8 -*-
from difference import *
from difflib import get_close_matches

def suitableWordsList (wd, wds):
    '''
    поиск слов по неправиьному слову и составление списка слов, стоящих в том же месте, где и неправильное слово
    :param wd: string
    :param wds: list
    :return: suitedWords list
    '''
    suitedWords = []
    for ws in wds:
        for w in ws:
            if wd.lower() == w.lower():
                for value in ws:
                    suitedWords.append(value)

    return suitedWords


def wodrsRightOrder (maxSent, sent):
    '''
    коррекция порядка слов в предложении
    сравнение предложения по отношению к самому длинному и вставка одного '' вместо пропущенного слова
    :param maxSent: string
    :param sent: string
    :return: sentWds: list
    '''
    sentWds = sent.split()
    msl = len(maxSent.split())
    sl = len(sentWds)

    if msl - sl > 0:
        exWds, misWds, wrWds, rWds = sentsDifference(maxSent, sent)
        for key in misWds.keys():
            if key < len(sentWds):
                sentWds.insert(key,'')

    return sentWds


def wordsList(sents):
    '''
    создаем и наполняем двумерный список слов на основе самого длинного предожения
    типа [['Peter'], ['Hobbs', 'hopes'], ['game', 'same', 'came'], ['here'], ['this'], ['mon', 'morning']]
    :param sents: list
    :return: words: list список упорядоченных слов, words_l те же слова но в нижнем регистре
    '''
    # выбираем самое длинное предложение из предложенных гуглом и все предложения разбиваем на слова
    sl = 0
    wd = []
    maxLenSent = ''
    for i, s in enumerate(sents):
        wd.append(s.split())
        if len(wd[i]) >= sl:
            sl = len(wd[i])
            maxLenSent = wd[i]

    # создаем двумерный список слов на основе самого длинного предожения
    l = len(maxLenSent)
    words = [['']*1 for i in range(l)]
    for i in range(l):
        words[i][0] = maxLenSent[i]

    # наполняем двумерный список всех слов с учетом их порядка
    for i, s in enumerate(sents):
        m = min(len(wd[i]) + 1, l)
        mS = ' '.join(maxLenSent[0:m])
        wd[i] = wodrsRightOrder (mS, s)
        for j, value in enumerate(wd[i]):
            if words[j].count(value) == 0:
                words[j].append(value)

    return words


def getSimilarSent(orSent, gSent, sents):
    bestSent = gSent
    sents.append(gSent)
    n = int(len(sents)/4)
    s = sents[::-1]
    for i in range(n):
        if levenshtein(orSent, bestSent) > levenshtein(orSent, s[i+1]):
            bestSent = s[i+1]

    return bestSent


def missedAndWrongWordsCorrection(wordsDict, wds, originalSentenceWords, googleSentenceWords, cutoff):
    '''
    находит пропущенные и неправильные слова и корректирует
    :param wordsDict: dictionary
    :param wds: list
    :param originalSentenceWords: string
    :param googleSentenceWords: string
    :return: googleSentenceWords list
    '''
    for value in wordsDict.values():
        wdLst = suitableWordsList(value[0], wds)
        if value[2] < len(originalSentenceWords):
            w = get_close_matches(originalSentenceWords[value[2]], wdLst, 1, cutoff)
            if len(w) > 0:
                if value[1] < len(googleSentenceWords):
                    googleSentenceWords[value[1]] = w[0]
                else:
                    googleSentenceWords.append(w[0])

    return googleSentenceWords

def googleSentenceCorrection(oSent, gSent, wds, cutoff = 0.4):
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

    exWds, misWds, wrWds, rWds = sentsDifference(oSent, gSent)
    googleSentenceWords = missedAndWrongWordsCorrection(wrWds, wds, originalSentenceWords, googleSentenceWords, cutoff)
    googleSentenceWords = missedAndWrongWordsCorrection(misWds, wds, originalSentenceWords, googleSentenceWords, cutoff/2)

    return ' '.join(googleSentenceWords)


def googleSentensBestChoice(originalSentence, lineSentence, sents):
    #------------------------- надо убрать
    if originalSentence.lower() == lineSentence.lower():
        googleSentenceWords = lineSentence
        return googleSentenceWords
    #------------------------- надо убрать

    words = wordsList(sents)
    similarSent = getSimilarSent(originalSentence, lineSentence, sents) # выбираем лучшее предложение из последних
    googleSentenceWords = googleSentenceCorrection(originalSentence, similarSent, words)

    #print("Words %s" % words)
    #print("Сравниваемое - %s" % similarSent)

    return googleSentenceWords


#-------------ТЕСТ---------------------------
from read_sents import readTest
originalSentences, lineSentences, sentss, rightAnswers = readTest('test.txt')

for i, orS in enumerate(originalSentences):
    gSeBeCh = googleSentensBestChoice(orS, lineSentences[i], sentss[i])
    if rightAnswers[i] == gSeBeCh:
        print(i, "OK")
    else:
        print(i, "НЕПРАВИЛЬНО")
        print("Предложения\n %s" % sentss[i])
        print("Оригинальное - %s" % originalSentences[i])
        print("Выдал гугл   - %s" % lineSentences[i])
        print("Итоговое     - %s" % gSeBeCh)
        print("Должно быть  - %s" % rightAnswers[i])






