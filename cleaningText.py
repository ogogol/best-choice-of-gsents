# -*- coding: utf-8 -*-
import re

patternPunctuation = re.compile(r'\b([,\.:;!\?]{1,2}) |\-')
patternComma = re.compile(r'\d(, )')
patternPunctuationWithoutSpace = re.compile(r'\b([,\.;!\?])')
patternSent = re.compile(r'.+')
patternSents = re.compile(r'"([\w\d\s\':]+?)"')
patternSpaces = re.compile(r'\s{2,7}')
patternAnd = re.compile(r'&')

def cleaningText(txt):
    #очищает текст от знаков препинания и подготавливает для работы
    if isinstance(txt, str):
        l = patternPunctuation.sub(' ', txt)
        l = patternComma.sub(' ', l)
        l = patternPunctuationWithoutSpace.sub('', l)
        l = patternAnd.sub(' and ', l)
        txt = patternSpaces.sub(' ', l).lower()

    elif isinstance(txt, list):
        for i, l in enumerate(txt):
            l = patternPunctuation.sub(' ', l)
            l = patternComma.sub(' ', l)
            l = patternPunctuationWithoutSpace.sub('', l)
            l = patternAnd.sub(' and ', l)
            txt[i] = patternSpaces.sub(' ', l).lower()

    return txt