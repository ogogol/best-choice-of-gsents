from difference import *
from difflib import get_close_matches

def exceptedWordsList(pos, s, nWds = 1):
    ex_wds = []
    for i in range(nWds):
        if pos - i - 1 >= 0:
            ex_wds.append(s[pos-i-1].lower())
        if len(s) > pos+i+1:
            ex_wds.append(s[pos+i+1].lower())

    return ex_wds

def suitedWordsList (exceptedWds, wds):
    '''
    поиск слов по неправиьному слову и составление списка слов, стоящих в том же месте, где и неправильное слово
    :param wd: string
    :param wds: list
    :return: suitedWords list
    '''
    suitedWords = []
    for ws in wds:
        if exceptedWds.count(ws) == 0:
            suitedWords.append(ws)

    return suitedWords

# создаем и наполняем список слов
def wordsList(sents):
    words = []
    for s in sents:
        wd = s.split()
        for w in wd:
            if words.count(w) == 0:
                words.append(w)

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

def getMaxSentLen(sents):
    '''
    выбираем самое длинное предложение из предложенных гуглом
    :param sents:
    :return:
    '''

    maxSentLen = 0
    wd = []
    for i, s in enumerate(sents):
        wd.append(s.split())
        if len(wd[i]) >= maxSentLen:
            maxSentLen = len(wd[i])

    return maxSentLen


   # проверка предложения и замена неправильных слов на правильные
def googleSentenceCorrection(oSent, gSent, wds, sents, cutoff = 0.5):
    originalSentWords = oSent.split()
    googleSentWords = gSent.split()
    maxSentLen = getMaxSentLen(sents)

    for i, or_w in enumerate(originalSentWords):
        if i < len(googleSentWords):
            exWds = exceptedWordsList(i, googleSentWords)
            suitWds = suitedWordsList(exWds, wds)
            ws = get_close_matches(or_w, suitWds, 1, cutoff)
            if len(ws) > 0:
                googleSentWords[i] = ws[0]

        elif i < maxSentLen:
            isWordChange = 0
            for w in wds:
                if or_w.lower() == w.lower():
                    googleSentWords.append(w)
                    isWordChange = 1

            if isWordChange == 0:
                ws = get_close_matches(or_w, wds, 1, cutoff)
                if len(ws) > 0 and exWds.count(ws[0]) == 0:
                    googleSentWords.append(ws[0])

    return ' '.join(googleSentWords)

def googleSentensBestChoice(originalSentence, lineSentence, sents):
    similarSent = getSimilarSent(originalSentence, lineSentence, sents) # выбираем лучшее предложение из последних
    words = wordsList(sents)
    googleSentenceWords = googleSentenceCorrection(originalSentence, similarSent, words, sents)

    print("Words %s" % words)
    print("Сравниваемое - %s" % similarSent)

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