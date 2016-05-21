# -*- coding: utf-8 -*-

from jellyfish import levenshtein_distance as levenshtein
from difflib import get_close_matches
from difference import getSentsDifference
from best_choice import wordsRunning
from trunk.project.main_apps.audio.text.funcs import prepare_transcriptions
from trunk.project.utils.text.funcs import int_diff, calc_best_percent, check_limitation, differ

def new_guess_inaccuracy(user_words, original_words, inaccuracy_coefficient = 2, lang = 'en'):
    result = []
    unique_or_words = get_unique_words(original_words)

    transriptions_dict = prepare_transcriptions(user_words + original_words, lang)
    transriptions_dict = {k: v[0] for k, v in transriptions_dict.items()}

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

    similary_words_num = 4
    similarity_coefficient = 0.5

    exWds, misWds, wrWds, rWds = getSentsDifference(' '.join(original_words), ' '. join(user_words), user_words)

    for key, wrW in wrWds.items():
        or_word = original_words[wrW[2]]
        word = wrW[0]
        newWds = get_close_matches(or_word, unique_or_words, similary_words_num, similarity_coefficient)

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
                newWord = get_best_newWord(wrW[1], wrW[0], original_words, user_words, mb_words)
                user_words[wrW[1]] = newWord

                result.append({
                    'word'      :   wrW[0],
                    #'order'     :   wrW[1],
                    'newWord'   :   newWord,
                    'words'     :   mb_words
                })

    return user_words, result


def get_best_newWord(pos, word, original_words, user_words, mb_words):

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

    return trascription


def get_unique_words(words):
    unique_words = []
    for w in words:
        if words.count(w) < 2:
            unique_words.append(w)
        elif unique_words.count(w) == 0:
            unique_words.append(w)

    return unique_words


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