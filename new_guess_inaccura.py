# -*- coding: utf-8 -*-

from subprocess import check_output
from diff_match_patch import diff_match_patch

from jellyfish import levenshtein_distance as levenshtein
from difflib import get_close_matches
from difference import getSentsDifference
from best_choice import wordsRunning
#-------------------------Активизировать (убрать решетку)
#from trunk.project.main_apps.audio.text.funcs import prepare_transcriptions


#------------------------------Нужно убрать-------------------------------------------------------
# нужно для тестирования
def replace_oldWord_to_newWord(user_words, original_words, transriptions_dict, inaccuracy_coefficient = 1.85):
    result = []
    unique_or_words = get_unique_words(original_words)

    user_words, result = get_new_guess_result(result, user_words, original_words, unique_or_words,
                                              transriptions_dict, inaccuracy_coefficient)

    if original_words == user_words:
        return ' '.join(user_words), result

    else:
        user_words, result = get_new_guess_result(result, user_words, original_words, unique_or_words,
                                                  transriptions_dict, inaccuracy_coefficient, True)

    user_words = wordsRunning(original_words, user_words, False)

    return ' '.join(user_words), result
#----------------------------------------------------------------------------------------------------------


#------------------------------Нужно убрать-------------------------------------------------------
# брать из базы транскрипции для слов двух предожений оригинала и пользовательского
def make_trascriptions_dict(originalSentences, sentss):
    trascriptions_dict = {}
    for or_s in originalSentences:
        for w in or_s.split():
            if w not in trascriptions_dict:
                trascriptions_dict[w] = ipa_trahcsription(w)

    for sents in sentss:
        for s in sents:
            for w in s.split():
                if w not in trascriptions_dict:
                    trascriptions_dict[w] = ipa_trahcsription(w)

    return trascriptions_dict
#----------------------------------------------------------------------------------------------------------

#------------------------------Нужно переделать-------------------------------------------------------
# установить http://espeak.sourceforge.net/download.html
# и прописать путь
# в случае если нет в базе транскрипции определяет ее
# перенести в  project.main_apps.audio.text.funcs в функцию prepare_transcriptions
def ipa_trahcsription(word):
    transcription = check_output(["C:\Program Files\eSpeak\command_line\espeak.exe", "-q", "--ipa", '-v', 'en', word]).decode('utf-8')
    #------------------------УБРАТЬ
    transcription = transcription.replace(u"ˌ", "")
    transcription = transcription.replace(u"ˈ", "")
    transcription = transcription.replace(u"ð", "z")# нужно для тестирования
    transcription = transcription.replace(u"θ", "s")# нужно для тестирования
    transcription = transcription.replace("d", "t")# нужно для тестирования
    transcription = transcription.replace(u"ŋ", "n")# нужно для тестирования
    transcription = transcription.replace("f", "v")# нужно для тестирования
    transcription = transcription.replace("b", "p")# нужно для тестирования
    transcription = transcription.replace("w", "v")# нужно для тестирования
    transcription = transcription.replace(u"ɹ", "r")# нужно для тестирования
    transcription = transcription.replace(u"ʒən", u"ʒn")# нужно для тестирования
    transcription = transcription.replace(u"ʃən", u"ʃn")# нужно для тестирования
    transcription = transcription.replace(u"ɛ", "e")# нужно для тестирования
    transcription = transcription.replace(u"ɜ", "e")# нужно для тестирования
    transcription = transcription.replace(u"ə", "e")# нужно для тестирования
    transcription = transcription.replace(u"iː", u"ɪ")# нужно для тестирования
    transcription = transcription.replace(u"ɒ", u"ɔ")# нужно для тестирования
    transcription = transcription.replace(u"ʊ", u"u")# нужно для тестирования
    #----------------------------------------------

    return transcription
#-------------------------------------------------------------------------------------------------------


#---------------------------------------------- из переменных transriptions_dict УБРАТЬ
def new_guess_inaccuracy(user_words, original_words, transriptions_dict, inaccuracy_coefficient = 1.85, lang = 'en'):
    '''
    заменяет неправильные слова в предложении пользователя на близкие по написанию или звучанию, если такие находятся
    :param user_words: list - список слов предложения пользователя
    :param original_words: list - список слов оригинального предожения
    :param inaccuracy_coefficient: float - коэффициент упрощения, при 1.5 заменяет of -> that, при 2 уже нет
    :param lang: str - язык
    :return: (user_sentence , result): (str, list) - улучшенное предложение пользователя,
                                        и список из {слово, новое слово, список близких слов, может возвращать порядок}
    '''
    result = []
    unique_or_words = get_unique_words(original_words)

    #transriptions_dict = prepare_transcriptions(user_words + unique_or_words, lang)
    # Поскольку prepare_transcriptions возвращает в значении массив, а нам нужн только первый элемент
    #transriptions_dict = { k:v[0] for k,v in transriptions_dict.items() }

    user_words, result = get_new_guess_result(result, user_words, original_words, unique_or_words,
                                              transriptions_dict, inaccuracy_coefficient)

    if original_words == user_words:
        return ' '.join(user_words), result

    else:
        user_words, result = get_new_guess_result(result, user_words, original_words, unique_or_words,
                                                  transriptions_dict, inaccuracy_coefficient, True)

    user_words = wordsRunning(original_words, user_words, False)

    return ' '.join(user_words), result


def get_new_guess_result(result, user_words, original_words, unique_or_words,
                         transriptions_dict, inaccuracy_coefficient, phone = False):
    '''
    выполняет основную работу по поиску подных неправильным словам в предложении пользователя и их замене
    :param result: list - список из {слово, новое слово, список близких слов, может возвращать порядок}
    :param user_words: list - список слов предложения пользователя
    :param original_words: list - список слов оригинального предожения
    :param unique_or_words: list - список неповторяющихся слов в предложении пользователя
    :param transriptions_dict: dictionary - список транскрипций всех слов в предложениях пользователя и оригинала
    :param inaccuracy_coefficient: float - float - коэффициент упрощения, при 1.5 заменяет of -> that, при 2 уже нет
    :param phone: bool - либо работает с транскрипциями либо нет
    :return: (user_words, result): (list, list)
    '''

    similary_words_num = 4
    similarity_coefficient = 0.5

    exWds, misWds, wrWds, rWds = getSentsDifference(' '.join(original_words), ' '. join(user_words), user_words)

    for key, wrW in wrWds.items():
        or_word = original_words[wrW[2]]
        word = wrW[0]
        word_position = wrW[1]
        #if not phone:
        newWds = get_close_matches(or_word, unique_or_words, similary_words_num, similarity_coefficient)
        #else:
            #newWds = get_close_phone_matches(or_word, unique_or_words, transriptions_dict, similary_words_num, similarity_coefficient)
        mb_words = []
        if newWds:
            for i, nw in enumerate(newWds):
                if not phone:
                    returned_dict = check_similarity_words(word, nw, inaccuracy_coefficient)
                else:
                    returned_dict = check_similarity_words(get_transcription(word, transriptions_dict),
                                                           get_transcription(nw, transriptions_dict),
                                                           inaccuracy_coefficient)
                if returned_dict["is_limitation_more_than_errors"]  == True:
                    mb_words.append(nw)

            if mb_words:
                best_newWord = get_best_newWord(word_position, word, original_words, user_words, mb_words)
                user_words[word_position] = best_newWord

                count = 0
                for d in result:
                    if word == d['word'] and best_newWord == d['newWord']:
                       count += 1
                if count == 0:
                    result.append({
                        'word'      :   word,
                        #'order'     :   wrW[1],
                        'newWord'   :   best_newWord,
                        'words'     :   mb_words
                    })

    return user_words, result


def get_best_newWord(pos, word, original_words, user_words, mb_words):
    '''
    находит лучшую замену заменяемому слову из списка подходящих, близких слов
    :param pos: int - позиция слова в предложении пользователя
    :param word: str - заменяемое слово
    :param original_words: list - список слов оригинального предожения
    :param user_words: list - список слов предложения пользователя
    :param mb_words: list - слова близкие к заменяемому
    :return: newWord: str - слово на которое меняем старое слово
    '''
    newWord = mb_words[0]
    if not mb_words: return ''

    orSent = ' '.join(original_words)
    user_sent = ' '.join(user_words)
    gSentWds1 = [w for w in user_words]
    gSentWds1[pos] = mb_words[0]

    if len(mb_words) == 1:
        if levenshtein(unicode(orSent), unicode(' '.join(gSentWds1))) >= levenshtein(unicode(orSent), unicode(user_sent)):
            newWord = word

    else:
        gSentWds2 = [w for w in user_words]
        gSentWds2[pos] = mb_words[1]

        if levenshtein(unicode(orSent), unicode(' '.join(gSentWds1))) > levenshtein(unicode(orSent), unicode(' '.join(gSentWds2))):
            if levenshtein(unicode(orSent), unicode(' '.join(gSentWds2))) > levenshtein(unicode(orSent), unicode(user_sent)):
                newWord = word
            else:
                newWord = mb_words[1]
        else:
            if levenshtein(unicode(orSent), unicode(user_sent)) <= levenshtein(unicode(orSent), unicode(' '.join(gSentWds1))):
                newWord = word

        if levenshtein(unicode(orSent), unicode(' '.join(gSentWds2))) < levenshtein(unicode(orSent), unicode(' '.join(gSentWds1))):
            newWord = mb_words[1]

    return newWord


def get_close_phone_matches(word, words_list, transriptions_dict, n = 4, cutoff = 0.5):
    '''
    сейчас не используется
    функция подобная get_close_matches, только работает с транскрипциями слов
    :param word: str - слово, к которому подбираютсяблизкие по звучанию слова
    :param words_list: list - список из которого выбираются близкие по звучанию слова
    :param transriptions_dict: dictionary
    :param n: int - максимальное количество отбираемых слов из списка предлагаемых
    :param cutoff: float - порог отсечения близости
    :return: close_matches: list - список отобранных слов
    '''
    close_matches = []
    words_trancrip_dict = {}
    phone_words_list = []
    count = 0
    for i, w in enumerate(words_list):
        w_trans = get_transcription(w, transriptions_dict)
        if w_trans not in phone_words_list:
            words_trancrip_dict[w_trans] = w
            phone_words_list.append(w_trans)
        else:
            words_trancrip_dict[w_trans+str(count)] = w
            count += 1

    close_phone_matches = get_close_matches(get_transcription(word, transriptions_dict), phone_words_list, n, cutoff)
    if close_phone_matches:
        for m in close_phone_matches:
            close_matches.append(words_trancrip_dict.get(m))
            for i in range(4):
                if m+str(i) in words_trancrip_dict:
                    close_matches.append(words_trancrip_dict.get(m+str(i)))

    return close_matches


def get_transcription(word, trascriptions_dict):
    trascription = trascriptions_dict.get(word)
    if trascription == None:
        trascription = ipa_trahcsription(word)

    return trascription

def get_unique_words(words):
    '''
    возращает список уникальных слов
    :param words: list
    :return: list
    '''
    unique_words = []
    for w in words:
        if words.count(w) < 2:
            unique_words.append(w)
        elif unique_words.count(w) == 0:
            unique_words.append(w)

    return unique_words


#------------------------------Можно убрать-------------------------------------------------------
# есть from project.utils.text.funcs import int_diff
def int_diff(text1, text2):
    """

    """
    diff = diff_match_patch()
    diffs = diff.diff_main(text2, text1)
    diff.diff_cleanupEfficiency(diffs)
    diffs_lev = diff.diff_levenshtein(diffs)
    return diffs_lev

def calc_best_percent(diff, text1, text2, inaccuracy_coefficient):
    threshold = float(float(len(text1) + len(text2)) / 2) / inaccuracy_coefficient

    return float(threshold - diff) / threshold

def check_limitation(diff, text1, text2, inaccuracy_coefficient):
    # Среднее арифмитическое, делим на коэфициент подобранный эмпирическим путем
    return diff <= float(float(len(text1) + len(text2)) / 2) / inaccuracy_coefficient

def differ(word, original_word, inaccuracy_coefficient):
    diff = int_diff(word, original_word)
    # Процент дальности от порога
    best_percent = calc_best_percent(diff, word, original_word, inaccuracy_coefficient)
    is_limitation_more_than_errors = check_limitation(diff, word, original_word, inaccuracy_coefficient)

    return {
        "is_limitation_more_than_errors":   is_limitation_more_than_errors,
        "best_percent":                     best_percent,
        "diff":                             diff
    }

def check_similarity_words(word, original_word, inaccuracy_coefficient):
    is_limitation_more_than_errors = False
    best_percent = None
    diff = None

    diff = int_diff(word, original_word)#levenshtein(word, original_word)#
    # Процент дальности от порога
    best_percent = calc_best_percent(diff, word, original_word, inaccuracy_coefficient)
    is_limitation_more_than_errors = check_limitation(diff, word, original_word, inaccuracy_coefficient)

    return {
        "is_limitation_more_than_errors":   is_limitation_more_than_errors,
        "best_percent":                     best_percent,
        "diff":                             diff
    }
# есть from project.utils.text.funcs import int_diff
#------------------------------Можно убрать-------------------------------------------------------
