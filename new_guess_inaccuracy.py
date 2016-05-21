# -*- coding: utf-8 -*-
#from words import
from subprocess import check_output
from jellyfish import levenshtein_distance as levenshtein
from difflib import get_close_matches
from diff_match_patch import diff_match_patch
from difference import getSentsDifference
from best_choice import wordsRunning
#-------------------------Активизировать (убрать решетку)
#from project.main_apps.audio.text.funcs import prepare_transcriptions



#------------------------------Нужно убрать-------------------------------------------------------
# нужно для тестирования
def replace_oldWord_to_newWord(user_words, original_words, transriptions_dict, inaccuracy_coefficient = 1.5):
    result = []
    unique_or_words = get_unique_words(original_words)

    user_words, result = get_new_guess_result(result, user_words, original_words, unique_or_words, transriptions_dict)

    if original_words == user_words:
        print('Обошлось без фонетики!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        return ' '.join(user_words), result
    else:
        user_words, result = get_new_guess_result(result, user_words, original_words,
                                                  unique_or_words, transriptions_dict, True)

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

    transcription = transcription.replace(u"ð", "t")# нужно для тестирования
    transcription = transcription.replace("d", "t")# нужно для тестирования
    #----------------------------------------------

    return transcription
#-------------------------------------------------------------------------------------------------------


#---------------------------------------------- из переменных transriptions_dict УБРАТЬ
def new_guess_inaccuracy(user_words, original_words, transriptions_dict, inaccuracy_coefficient = 1.5, lang = 'en'):
    result = []
    unique_or_words = get_unique_words(original_words)
    #-----------------------------Убрать коммент
    #transriptions_dict = prepare_transcriptions(user_words+original_words, lang)
    #-----------------------------------------------
    user_words, result = get_new_guess_result(result, user_words, original_words, unique_or_words)

    if original_words == user_words:
        return ' '.join(user_words), result

    else:
        user_words, result = get_new_guess_result(result, user_words, original_words,
                                                  unique_or_words, transriptions_dict, True)

    user_words = wordsRunning(original_words, user_words, False)

    return ' '.join(user_words), result


def get_new_guess_result(result, user_words, original_words, unique_or_words, transriptions_dict = {},
                         phone = False, inaccuracy_coefficient = 1.5):

    exWds, misWds, wrWds, rWds = getSentsDifference(' '.join(original_words), ' '. join(user_words), user_words)

    for key, wrW in wrWds.items():
        if not phone:
            newWds = get_close_matches(original_words[wrW[2]], unique_or_words, 4, 0.5)
        else:
            newWds = get_close_phone_matches(original_words[wrW[2]], unique_or_words, transriptions_dict, 4, 0.5)
        mb_words = []
        if newWds:
            for i, nw in enumerate(newWds):
                if not phone:
                    returned_dict = check_similarity_words(original_words[wrW[2]], nw, inaccuracy_coefficient)
                else:
                    returned_dict = check_similarity_words(get_transcription(original_words[wrW[2]], transriptions_dict),
                                                           get_transcription(nw, transriptions_dict),
                                                           inaccuracy_coefficient)
                if returned_dict["is_limitation_more_than_errors"]  == True:
                    mb_words.append(nw)

            if mb_words:
                newWord = get_best_newWord(wrW[1], wrW[0], original_words, user_words, mb_words)
                user_words[wrW[1]] = newWord

                result.append({
                    'word'      :   wrW[0],
                    'order'     :   wrW[1],
                    'newWord'   :   newWord,
                    'words'     :   mb_words
                })

    return user_words, result


def get_best_newWord(pos, word, original_words, user_words, mb_words):

    newWord = mb_words[0]
    if not mb_words: return ''

    gSentWds1 = [w for w in user_words]
    orSent = ' '.join(original_words)
    user_sent = ' '.join(user_words)
    gSentWds1[pos] = mb_words[0]

    if len(mb_words) == 1:
        if levenshtein(unicode(orSent), unicode(' '.join(gSentWds1))) >= levenshtein(unicode(orSent), unicode(user_sent)):
            newWord = word

    else:
        gSentWds2 = [w for w in user_words]
        gSentWds1[pos] = mb_words[0]
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

    close_phone_matches = get_close_matches(ipa_trahcsription(word), phone_words_list, n, cutoff)
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
