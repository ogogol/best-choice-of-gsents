# -*- coding: utf-8 -*-
from difference import *
from difflib import *

def suitableWordsList (wd, wds):
    '''
    поиск слов по неправиьному слову и составление списка слов, стоящих в том же месте, где и неправильное слово
    :param wd:
    :param wds:
    :return:
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
    :param maxSent:
    :param sent:
    :return:
    '''
    msl = len(maxSent)
    sl = len(sent)
    sentWds = sent.split()

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
    :param sents:
    :return:
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
        m = min(len(wd[i]) + 2, l)
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
        if levenshtein(orSent, s[i]) > levenshtein(orSent, s[i+1]):
            bestSent = s[i+1]

    return bestSent


def missedAndWrongWordsCorrection(wordsDict, wds, originalSentenceWords, googleSentenceWords, cutoff):
    '''
    находит пропущенные и неправильные слова и корректирует
    :param wordsDict:
    :param wds:
    :param originalSentenceWords:
    :param googleSentenceWords:
    :return: googleSentenceWords
    '''
    for value in wordsDict.values():
        isWordChange = 0
        wdLst = suitableWordsList(value[0], wds)
        for w in wdLst:
            if originalSentenceWords[value[2]].lower() == w.lower():
                isWordChange = 1
                if value[1] < len(googleSentenceWords):
                    googleSentenceWords[value[1]] = w
                else:
                    googleSentenceWords.append(w)

        if isWordChange == 0:
            if len(wds) >= value[2]:
                w = get_close_matches(value[0], wds[value[2]], 1, cutoff)
                #print("Варианты %s" % w)
                if len(w) > 0:
                    if value[1] < len(googleSentenceWords):
                        googleSentenceWords[value[1]] = w[0]
                    else:
                        googleSentenceWords.append(w[0])

    return googleSentenceWords

def googleSentenceCorrection(oSent, gSent, wds, cutoff = 0.65):
    '''
    проверка предложения и замена неправильных слов на правильные
    :param oSent: оригинальное предложение
    :param gSent: лучшее предложение для сравнения от гугла
    :param wds: список упорядоченных слов всех фраз от гугла
    :param cutoff: порог отсечения подобия слов, используется если не найдено ни одного 100% подходящего
    :return: googleSentenceWords - скорректированное предложение
    '''
    originalSentenceWords = oSent.split()
    googleSentenceWords = gSent.split()

    exWds, misWds, wrWds, rWds = sentsDifference(oSent, gSent)
    #print(misWds)
    googleSentenceWords = missedAndWrongWordsCorrection(wrWds, wds, originalSentenceWords, googleSentenceWords, cutoff)
    googleSentenceWords = missedAndWrongWordsCorrection(misWds, wds, originalSentenceWords, googleSentenceWords, cutoff/3)

    return ' '.join(googleSentenceWords)


def googleSentensBestChoice(originalSentence, lineSentence, sents):
    words = wordsList(sents)
    similarSent = getSimilarSent(originalSentence, lineSentence, sents) # выбираем лучшее предложение из последних
    googleSentenceWords = googleSentenceCorrection(originalSentence, similarSent, words)

    #print("Words %s" % words )
    #print("Сравниваемое - %s" % similarSent)

    return googleSentenceWords


#-------------ТЕСТ---------------------------
from read_sents import readTest
originalSentences, lineSentences, sentss, rightAnswers = readTest('test.txt')

for i, orS in enumerate(originalSentences):
    gSeBeCh= googleSentensBestChoice(orS, lineSentences[i], sentss[i])
    if rightAnswers[i] == gSeBeCh:
        print(i, "OK")
    else:
        print(i, "НЕПРАВИЛЬНО")
        print("Предложения\n %s" % sentss[i])
        print("Оригинальное - %s" % originalSentences[i])
        print("Выдал гугл   - %s" % lineSentences[i])
        print("Итоговое     - %s" % gSeBeCh)
        print("Должно быть  - %s" % rightAnswers[i])






