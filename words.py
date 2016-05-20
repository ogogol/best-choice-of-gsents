# -*- coding: utf-8 -*-
from jellyfish import levenshtein_distance as levenshtein
from difflib import get_close_matches
from jellyfish import nysiis

def makeSentsWdsList(sents):
    #возращает список списков слов предложений
    sentWds = []
    for i, s in enumerate(sents):
        sentWds.append(s.split())

    return sentWds


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


def concatWords(orSentWords, comSentWords):
    #проверяет все слова предожения на слияние подряд идущих слов
    #возращает скорретированный список слов предожения
    sentLen = len(comSentWords)
    orSentLen = len(orSentWords)
    count = 1
    for i, val in enumerate(orSentWords):
        if i < sentLen - count and (val != comSentWords[i] or val != comSentWords[i+1]):
            ny_baseWord = nysiis(unicode(orSentWords[i])).replace("'",'')
            ny_word1 = nysiis(unicode(comSentWords[i])).replace("'",'')
            ny_word2 = nysiis(unicode(comSentWords[i+1])).replace("'",'')
            if  len(ny_baseWord) < len(ny_word1) and len(ny_baseWord) < len(ny_word2):
                continue
            if i < orSentLen - 1:
                if not isTheSameWords(i, orSentWords, comSentWords):
                    comSentWords = isSumma2WordsTheBest(val, comSentWords[i], comSentWords[i+1], i, comSentWords)
                    count += 1
            else:
                comSentWords = isSumma2WordsTheBest(val, comSentWords[i], comSentWords[i+1], i, comSentWords)
                count += 1

    return comSentWords


def splitWords(orSentWords, comSentWords):
    #проверяет все слова предожения на разделение, если это лучше подходит к словам оригинала
    #возращает скорретированный список слов предожения

    count = 0
    for i, val in enumerate(orSentWords):
        if  i == len(comSentWords) + count: count += 1

        if val != comSentWords[i-count]:
            if len(comSentWords[i-count]) < 4: continue
            n = comSentWords[i-count].find(val)
            if n == -1: continue
            gSentWds1 = [w for w in comSentWords]

            if n == 0:
                f_halfW = val
                s_halfW = comSentWords[i-count][len(val):]
            else:
                f_halfW = comSentWords[i-count][:n]
                s_halfW = comSentWords[i-count][n:]

            if min(len(f_halfW),len(s_halfW)) < 2: continue

            comSentWords[i-count] = f_halfW
            comSentWords.insert(i+1-count, s_halfW)
            gSentWds1, comSentWords = addWordOrNotChoice(' '.join(orSentWords), gSentWds1, comSentWords)

    return comSentWords


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
            if approx_w:
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


def makeWordsList(orSentWds, lineSentWds, sentWds):
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

    words = []
    for i, w in enumerate(maxLongSent):
        words.append([w,])

    # наполняем список всех слов с учетом их порядка
    for i, sWds in enumerate(sentWds):
        m = min(len(sWds) + 1, maxSentLen)

        sentWds[i] = splitWords(orSentWds, sWds)
        sentWds[i] = concatWords(orSentWds, sWds)

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

