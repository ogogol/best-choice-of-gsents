import re
import numpy as np
from difflib import Differ

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


patternSentSplitWords = re.compile(r'[+-]\s{2,7}|\s{3,7}')
patternMinusSpaceLetter = re.compile(r'\- \w')
patternPlusSpaceLetter = re.compile(r'\+ \w')
patternSpace = re.compile(r'\s+')
patternLetter = re.compile(r'\w')
patternPlus = re.compile(r'\+')
patternMinus = re.compile(r'-')
patternLetters = re.compile(r'\b\w+')

def getWordOrder(n, wd, sentWords):
    isWd = True
    start = max([0, n-4])
    end = min([len(sentWords), n + 2])
    if wd in sentWords[start:end]:
        num = sentWords.index(wd, start, end)
    else:
        num = n
        isWd = False

    return num, isWd


def separateComparedWords(comparedWords, orSentWords, comSentWords):
    '''
    разделяет список сравненых слов на 4 типа, и выдает четыре словаря:
    :param comparedWords: list список сравниваемых слов со знаками +- типа:[+ m- b- u- t-, - i- n, ...]
    :return: excessWds, missedWds, wrongWds, rightWds - dictionaries
    лишние слова, пропущенные слова, неправиьные и правильные слова, где ключом является порядок слова
    '''
    excessWds = {}; missedWds = {}; wrongWds = {}; rightWds = {}
    count = 0
    lts = ''
    for i, cW in enumerate(comparedWords):
        wd = ''.join(patternLetter.findall(cW))
        plusesLen = len(''.join(patternPlus.findall(cW)))
        minusesLen = len(''.join(patternMinus.findall(cW)))

        sent_count = i-len(missedWds)-count
        orSent_count = i-len(excessWds)-count

        sent_num, isWd = getWordOrder(sent_count, wd, comSentWords)
        orSent_num, isOrWd = getWordOrder(orSent_count, wd, orSentWords)

        if plusesLen >= len(wd):
            excessWds[i-count] = [wd, sent_num, sent_num]

        elif minusesLen >= len(wd):
            missedWds[i-count] = [wd, orSent_num, orSent_num]

        elif plusesLen == 0 and minusesLen == 0:
            rightWds[i-count] = [wd, sent_num, orSent_num]

        else:           # plusesLen > 0 or (minusesLen > 0 and plusesLen == 0)
            wrW = ''.join(patternLetter.findall(patternMinusSpaceLetter.sub('', cW)))
            sent_num, isWd = getWordOrder(sent_count, lts + wrW, comSentWords)
            or_W = ''.join(patternLetter.findall(patternPlusSpaceLetter.sub('', cW)))
            orSent_num, isOrWd = getWordOrder(orSent_count, or_W, orSentWords)
            if isOrWd != True:
                or_W = ''.join(patternLetter.findall(patternMinusSpaceLetter.sub('', cW)))
                orSent_num, isOrWd = getWordOrder(orSent_count, or_W, orSentWords)

            if isWd:
                if lts != '' and isOrWd == True:# если произошло неправильное разбиение,
                    #  то последнее слово, находящееся в оригинальном предложении добавляем в список пропущенных слов
                    missedWds[i-count+1] = [orSentWords[orSent_num], orSent_num, orSent_num]
                    orSent_num -= 1
                wrongWds[i-count] = [lts + wrW, sent_num, orSent_num]
                lts = ''
            else: #неправильное разбиение слов типа indiana разбито на 3 слова in dia na, складываем обратно
                count += 1
                lts += wrW
                continue


    #print(missedWds, wrongWds,)
    #print(orSentWords)
    #print(comSentWords)
    return excessWds, missedWds, wrongWds, rightWds

def getFirstLettersTheSame(wd1, wd2):
    d = Differ()
    diff = ''.join(d.compare(wd1.lower(), wd2.lower()))
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

def getSentsDifference(orSent, comSent):
    '''
    сравнивает два предложения, оригинальное и сравниваемое, и выдает четыре словаря:
    :param orSent: string оригинальное предложение
    :param comSent: string сравниваемое
    :return: excessWds, missedWds, wrongWds, rightWds - dictionaries
    лишние слова, пропущенные слова, неправиьные и правильные слова, где ключом является порядок слова в строке сравнения
    '''
    d = Differ()
    diff = ''.join(d.compare(orSent.lower(), comSent.lower()))#строка сравнения предложений типа: + m- b- u- t-  - i- n-  - a- n  y

    orSentWords = patternSpace.split(orSent.lower())
    comSentWords = patternSpace.split(comSent.lower())
    comparedWords = patternSentSplitWords.split(diff)#массив слов со знаками +- типа:[+ m- b- u- t-, - i- n, ...]

    excessWds, missedWds, wrongWds, rightWds = separateComparedWords(comparedWords, orSentWords, comSentWords)
    excessWds, missedWds, wrongWds, rightWds = correctWrongDetectedWords(excessWds, missedWds, wrongWds, rightWds, orSentWords, comSentWords)

    return excessWds, missedWds, wrongWds, rightWds

