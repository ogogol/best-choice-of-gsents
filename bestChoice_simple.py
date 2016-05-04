from difference import *

def exceptedWordsList(pos, s, nWds = 1):
    wds = []
    for i in range(nWds):
        if pos - i - 1 >= 0:
            wds.append(s[pos-i-1].lower())
        if len(s) > pos+i+1:
            wds.append(s[pos+i+1].lower())

    return wds


# создаем и наполняем список слов
def wordsList(sents):
    words = []
    for s in sents:
        wd = s.split()
        for w in wd:
            if words.count(w) == 0:
                words.append(w)

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
def googleSentenceCorrection(oSent, gSent, wds):
    originalSentWords = oSent.split()
    googleSentWords = gSent.split()

    for i, or_w in enumerate(originalSentWords):
        if i < len(googleSentWords):
            exWds = exceptedWordsList(i, googleSentWords)
            for w in wds:
                wl = w.lower()
                if or_w.lower() == wl and exWds.count(wl) == 0:
                    googleSentWords[i] = w

        else:
            for w in wds:
                if or_w.lower() == w.lower():
                    googleSentWords.append(w)

    return googleSentWords


originalSentence = "but in any case I'd rather be seasick than dead "
googleSentence = "but in any case I'd rather be sick than that "
sents = readSents("4.txt")

#sents = readSents("3.txt")

words = wordsList(sents) # получаем список всех слов
bSent = bChoice(originalSentence, googleSentence, sents) # выбираем лучшее предложение из последних
googleSentenceWords = googleSentenceCorrection(originalSentence, bSent, words) # корректируем в нем все несовпадающие слова,
                                                                               # словами из списка слов, за исключением рядом стоящих,
                                                                               # что бы избежать коррекции неправильного порядка


print (words)
print (" Оригинальное -", originalSentence, "\n", "Выдал гугл   -", googleSentence, "\n", "Итоговое     -", ' '.join(googleSentenceWords))
