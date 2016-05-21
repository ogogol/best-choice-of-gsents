# -*- coding: utf-8 -*-
import re
from difflib import Differ

patternSentSplitWords = re.compile(r'[+-]\s{2,7}|\s{3,7}')
patternMinusSpaceLetter = re.compile(r"\- \w|\- \'")
patternPlusSpaceLetter = re.compile(r'\+ \w|\+ \'')
patternSpace = re.compile(r'\s+')
patternLetter = re.compile(r'[\w\d\']')
patternPlus = re.compile(r'\+')
patternMinus = re.compile(r'-')
patternLetters = re.compile(r'\b\w+')

def getWordOrderInWords (n, wd, wds, sentLen):
    #поиск слов по неправильному слову и составление списка слов, стоящих в том же месте списка слов, где и неправильное слово
    #:param wd: string
    #:param wds: list
    #:return: suitedWords list

    order = -1
    wdsL = len(wds)
    if sentLen > wdsL:
        start = 0
        end = wdsL
    else:
        start = max([0, n-1])
        end = min([wdsL, n+4])

    for i in range(start, end):
        for j, w in enumerate(wds[i]):
            if wd == w:
                order = i
                break
    return order


def listRightIndex(alist, value):
    return len(alist) - alist[-1::-1].index(value) -1

def getWordOrder(n, wd, sentWords):
    #возращает порядковый номер слова в предложении и флаг TRUE при удачном поиске, и FALSE наоборот
    isWd = False
    start = max([0, n-4])
    sentWordsLen = len(sentWords)
    end = min([sentWordsLen, n + 2])
    if n < sentWordsLen:
        num = n
    else:
        num = sentWordsLen - 1

    matches = sentWords[start:end].count(wd)
    if matches == 0:
        return num, isWd
    elif matches == 1:
        isWd = True
        num = sentWords.index(wd, start, end)
    else:
        isWd = True
        num1 = sentWords.index(wd, start, end)
        num2 = listRightIndex(sentWords[start:end], wd) + start
        if abs(n - num1) < abs(n - num2):
            num = num1
        else:
            num = num2

    return num, isWd


def separateComparedWords(comparedWords, orSentWords, comSentWords, wds):
    '''
    разделяет список сравненых слов на 4 типа, и выдает четыре словаря:
    в качестве ключа порядковый номер слова в строке сравнения
    первое значение само слово
    второе значение порядковый номер его в сравниваемом предложении
    третье значение порядковый номер в оригинальном предожении, с которым происходит сравнение
    :param comparedWords: list список сравниваемых слов со знаками +- типа:[+ m- b- u- t-, - i- n, ...]
    :return: excessWds, missedWds, wrongWds, rightWds - dictionaries
    лишние слова, пропущенные слова, неправиьные и правильные слова, где ключом является порядок слова
    '''
    excessWds = {}; missedWds = {}; wrongWds = {}; rightWds = {}
    count = 0
    lts = ''
    or_lts = ''
    for i, cW in enumerate(comparedWords):
        wd = ''.join(patternLetter.findall(cW))
        wdLen = len(wd)
        plusesLen = len(''.join(patternPlus.findall(cW)))
        minusesLen = len(''.join(patternMinus.findall(cW)))

        sent_count = i-len(missedWds)-count
        orSent_count = i-len(excessWds)-count

        sent_num, isWd = getWordOrder(sent_count, wd, comSentWords)
        orSent_num, isOrWd = getWordOrder(orSent_count, wd, orSentWords)

        if plusesLen >= wdLen:
            excessWds[i-count] = [wd, sent_num, orSent_num]

        elif minusesLen >= wdLen:
            missedWds[i-count] = [wd, sent_count, orSent_num]

        elif plusesLen == 0 and minusesLen == 0:
            if isOrWd:
                rightWds[i-count] = [wd, sent_num, orSent_num]
            else:
                wrongWds[i-count] = [wd, sent_num, orSent_num]

        else:           # plusesLen > 0 or (minusesLen > 0 and plusesLen == 0)
            wrW = ''.join(patternLetter.findall(patternMinusSpaceLetter.sub('', cW)))
            sent_num, isWd = getWordOrder(sent_count, lts + wrW, comSentWords)
            or_W = ''.join(patternLetter.findall(patternPlusSpaceLetter.sub('', cW)))
            orSent_num, isOrWd = getWordOrder(orSent_count, or_W, orSentWords)

            if not isOrWd:
                or_W = ''.join(patternLetter.findall(patternMinusSpaceLetter.sub('', cW)))
                orSent_num, isOrWd = getWordOrder(orSent_count, or_W, orSentWords)

            if isWd:
                if lts != '' and isOrWd == True:# если произошло неправильное разбиение,
                    #  то последнее слово, находящееся в оригинальном предложении добавляем в список пропущенных слов
                    missedWds[i-count+1] = [orSentWords[orSent_num], orSent_num, orSent_num]
                    orSent_num -= 1
                    or_lts = ''

                wrongWds[i-count] = [lts + wrW, sent_num, orSent_num]
                lts = ''
            else: #неправильное разбиение слов типа indiana разбито на 3 слова in dia na, складываем обратно
                count += 1
                lts += wrW
                continue

    return excessWds, missedWds, wrongWds, rightWds

def getFirstLettersTheSame(wd1, wd2):
    #возращает одинаковые первые буквы у двух идущих друг за другом слов
    d = Differ()
    diff = ''.join(d.compare(wd1, wd2))
    diff = patternSpace.sub('',diff)

    return patternLetters.match(diff)


def correctWrongDetectedWords(exsWds, misWds, wrWds, rWds, orSentWds, comSentWds):
    '''
    если два подряд слова начинаются на одни буквы, но первое должно быть лишнее, а второе правильное
    при обработке оба определяются как неправильные типа : w+ h+ o+  + w  a  t  c  h  e  d,
    переписываем первое в лишнее, а второе в правильное
    :param excessWds:
    :param missedWds:
    :param wrongWds:
    :param rightWds:
    :return:
    '''
    delItems = []
    for key, value in wrWds.items():
        if wrWds.get(key+1) != None and \
                        orSentWds[wrWds[key+1][2]] == comSentWds[wrWds[key+1][1]] and\
                        getFirstLettersTheSame(value[0], wrWds[key+1][0]) != None:
            exsWds[key] = [value[0], value[1], value[2]]
            rWds[key+1] = [wrWds[key+1][0], wrWds[key+1][1], wrWds[key+1][2]]

    for i in delItems:
        del wrWds[i]

    return  exsWds, misWds, wrWds, rWds

def getSentsDifference(orSent, comSent, wds):
    '''
    сравнивает два предложения, оригинальное и сравниваемое, и выдает четыре словаря:
    :param orSent: string оригинальное предложение
    :param comSent: string сравниваемое
    :return: excessWds, missedWds, wrongWds, rightWds - dictionaries
    лишние слова, пропущенные слова, неправиьные и правильные слова, где ключом является порядок слова в строке сравнения
    '''
    d = Differ()
    diff = ''.join(d.compare(orSent, comSent))#строка сравнения предложений типа: + m- b- u- t-  - i- n-  - a- n  y

    orSentWords = patternSpace.split(orSent)
    comSentWords = patternSpace.split(comSent)
    comparedWords = patternSentSplitWords.split(diff)#массив слов со знаками +- типа:[+ m- b- u- t-, - i- n, ...]


    excessWds, missedWds, wrongWds, rightWds = separateComparedWords(comparedWords, orSentWords, comSentWords, wds)
    excessWds, missedWds, wrongWds, rightWds = correctWrongDetectedWords(excessWds, missedWds, wrongWds, rightWds, orSentWords, comSentWords)

    return excessWds, missedWds, wrongWds, rightWds

