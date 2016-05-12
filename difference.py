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
patternSpace = re.compile(r'\s+')
patternLetter = re.compile(r'\w')
patternPlus = re.compile(r'\+')
patternMinus = re.compile(r'-')

def separatedComparedWords(comparedWords):
    '''
    разделяет список сравненых слов на 4 типа, и выдает четыре словаря:
    :param comparedWords: list список сравниваемых слов со знаками +- типа:[+ m- b- u- t-, - i- n, ...]
    :return: excessWds, missedWds, wrongWds, rightWds - dictionaries
    лишние слова, пропущенные слова, неправиьные и правильные слова, где ключом является порядок слова
    '''
    excessWds = {}
    missedWds = {}
    wrongWds = {}
    rightWds = {}
    for i, cW in enumerate(comparedWords):
        wd = ''.join(patternLetter.findall(cW))
        plus = ''.join(patternPlus.findall(cW))
        minus = ''.join(patternMinus.findall(cW))
        if len(wd) <= len(plus):
            excessWds[i] = [wd, i-len(missedWds), i-len(missedWds)]
        elif len(plus)>0:
            wrW = ''.join(patternLetter.findall(patternMinusSpaceLetter.sub('', cW)))
            wrongWds[i] = [wrW, i-len(missedWds), i-len(excessWds)]
        elif len(wd) <= len(minus):
            missedWds[i] = [wd, i-len(excessWds), i-len(excessWds)]
        elif len(minus)>0 and len(plus) == 0:
            wrW = ''.join(patternLetter.findall(patternMinusSpaceLetter.sub('', cW)))
            wrongWds[i] = [wrW, i-len(missedWds), i-len(excessWds)]
        else:
            rightWds[i] = [wd, i-len(missedWds), i-len(excessWds)]

    return excessWds, missedWds, wrongWds, rightWds

def correctedWrongAndMissWordsList(missedWds, wrongWds, orSentWords, comSentWords):
    '''
    сравнивает слова из списка неправильных слов со словами из сравниваемого предложения и корректирует список,
    в случае если слово из предожения оказалось разорванным на два слова типа tumi -> tu mi
    :return: скорректированный wrongWds
    '''
    delItems =[]
    for key, value in wrongWds.items():
        if len(comSentWords) > value[1]:
            if comSentWords[value[1]] != wrongWds[key][0] and wrongWds.get(key+1) != None:
                if comSentWords.count(wrongWds.get(key+1)[0]) == 0 \
                        and comSentWords[value[1]] == wrongWds[key][0] + wrongWds[key+1][0]:
                    wrongWds[key][0] = wrongWds[key][0] + wrongWds[key+1][0]
                    i = wrongWds[key+1][2]
                    missedWds[key+1] = [orSentWords [i], i, i]
                    delItems.append(key+1)

    for i in delItems:
        del wrongWds[i]

    return missedWds, wrongWds

def sentsDifference(orSent, comSent):
    '''
    сравнивает два предложения, оригинальное и сравниваемое, и выдает четыре словаря:
    :param orSent: string оригинальное предложение
    :param comSent: string сравниваемое
    :return: excessWds, missedWds, wrongWds, rightWds - dictionaries
    лишние слова, пропущенные слова, неправиьные и правильные слова, где ключом является порядок слова
    '''

    d = Differ()
    diff = ''.join(d.compare(orSent.lower(), comSent.lower()))#строка сравнения предложений типа: + m- b- u- t-  - i- n-  - a- n  y
    orSentWords = patternSpace.split(orSent.lower())
    comSentWords = patternSpace.split(comSent.lower())
    comparedWords = patternSentSplitWords.split(diff)#массив слов со знаками +- типа:[+ m- b- u- t-, - i- n, ...]

    excessWds, missedWds, wrongWds, rightWds = separatedComparedWords(comparedWords)
    missedWds, wrongWds = correctedWrongAndMissWordsList(missedWds, wrongWds, orSentWords, comSentWords)

    return excessWds, missedWds, wrongWds, rightWds

