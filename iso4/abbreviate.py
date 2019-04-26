#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os, csv, json, unicodedata, string, nltk
import regex as re
from nltk.stem.wordnet import WordNetLemmatizer

WNL = WordNetLemmatizer()

def abbreviate(title, periods=True, disambiguation_langs=set()):
    """
    Abbreviate title per ISO 4 / CIEPS LTWA.

    Inputs:
        (str) title
            Title to be abbreviated.
        (bool) periods
            Include or omit abbrevation ending periods.
            Default True (include).
        (iterable) disambiguation_langs
            ISO 639-2/B language codes to consider title "written in".
            Only necessary if LTWA distinguishes between abbreviations for the
                same string, but dependent on language;
                e.g. "nombre", "real", "labor".
            In cases where a disambiguating language is required but not supplied,
                function will raise an Exception.
            Default empty set.
    Output:
        (str) abbreviated title
    """

    title = unicodedata.normalize('NFKD', title)

    disambiguation_langs = set(disambiguation_langs)

    # split title either at space, or any words in mapping with spaces
    title_words = list(filter(lambda w: w.strip(), TOKENIZER_REGEX.split(title)))

    result = []

    # Exception for single-word titles
    if len(title_words) == 1 and len(title_words[0].split(' ')) == 1:
        return title

    for orig_word in title_words:
        # normalize and lemmatize
        word_norm = __normalize_word(orig_word)

        # stopword, skip
        if word_norm in STOPWORDS:
            continue

        # if normalized word fails, try lemma
        word_lemma = WNL.lemmatize(word_norm)
        word_candidates = (word_norm, word_lemma) if word_norm != word_lemma else (word_norm,)

        word_abbr = ""
        capitalization = __get_capitalization(orig_word)

        for word in word_candidates:
            # first check for all possible conflicts
            # full word conflicts
            if FULLWORD in CONFLICT_MAP and word in CONFLICT_MAP[FULLWORD]:
                allowed_langs = CONFLICT_MAP[FULLWORD][word].keys()
                possible_langs = allowed_langs & disambiguation_langs
                if len(possible_langs) == 1:
                    word_abbr = CONFLICT_MAP[FULLWORD][word][possible_langs.pop()]
                    break
                else:
                    raise Exception("Ambiguous word in title: {}; must disambiguate between langs: {}".format(word, ', '.join(sorted(allowed_langs))))
            if not word_abbr and PREFIX in CONFLICT_MAP:
                # prefix conflicts
                for prefix in sorted(CONFLICT_MAP[PREFIX].keys()):
                    if word.startswith(prefix):
                        allowed_langs = CONFLICT_MAP[PREFIX][word].keys()
                        possible_langs = allowed_langs & disambiguation_langs
                        if len(possible_langs) == 1:
                            word_abbr = CONFLICT_MAP[PREFIX][word][possible_langs.pop()]
                        else:
                            raise Exception("Ambiguous prefix ({}) in title word: {}; must disambiguate between langs: {}".format(prefix, word, ', '.join(sorted(allowed_langs))))
            if not word_abbr and SUFFIX in CONFLICT_MAP:
                # suffix conflicts
                for suffix in sorted(CONFLICT_MAP[SUFFIX].keys()):
                    if word.endswith(suffix):
                        allowed_langs = CONFLICT_MAP[SUFFIX][word].keys()
                        possible_langs = allowed_langs & disambiguation_langs
                        if len(possible_langs) == 1:
                            word_abbr = CONFLICT_MAP[SUFFIX][word][possible_langs.pop()]
                        else:
                            raise Exception("Ambiguous suffix ({}) in title word: {}; must disambiguate between langs: {}".format(suffix, word, ', '.join(sorted(allowed_langs))))
            if not word_abbr and INFIX in CONFLICT_MAP:
                # infix conflicts
                for infix in sorted(CONFLICT_MAP[INFIX].keys()):
                    if infix in word:
                        allowed_langs = CONFLICT_MAP[INFIX][word].keys()
                        possible_langs = allowed_langs & disambiguation_langs
                        if len(possible_langs) == 1:
                            word_abbr = CONFLICT_MAP[INFIX][word][possible_langs.pop()]
                        else:
                            raise Exception("Ambiguous infix ({}) in title word: {}; must disambiguate between langs: {}".format(infix, word, ', '.join(sorted(allowed_langs))))
            if word_abbr: break
            # done with conflict checks

            # check full word list
            if not word_abbr and FULLWORD in LTWA and word in LTWA[FULLWORD]:
                word_abbr = LTWA[FULLWORD][word]
                break
            if not word_abbr and PREFIX in LTWA:
                # check prefixes in descending length order
                for prefix in sorted(LTWA[PREFIX].keys(), key=lambda p: (-len(p), p)):
                    if word.startswith(prefix):
                        word_abbr = LTWA[PREFIX][prefix]
                        break
            if not word_abbr and SUFFIX in LTWA:
                # check suffixes in descending length order
                for suffix in sorted(LTWA[SUFFIX].keys(), key=lambda p: (-len(p), p)):
                    if word.endswith(suffix):
                        word_abbr = LTWA[SUFFIX][suffix]
                        break
            if not word_abbr and INFIX in LTWA:
                # check infixes in descending length order
                for infix in sorted(LTWA[INFIX].keys(), key=lambda p: (-len(p), p)):
                    if infix in word:
                        word_abbr = LTWA[INFIX][infix]
                        break
            if word_abbr: break

        # done, finalize output with proper parameters
        if word_abbr in ("", NOT_ABBREVIATED):
            word_abbr = __finalize_output(word, capitalization, periods=False)
        else:
            word_abbr = __finalize_output(word_abbr, capitalization, periods)

        result.append(word_abbr)

    return unicodedata.normalize('NFKC', ' '.join(result))


LTWA = {}
LTWA_VERSION = "20170914"

NOT_ABBREVIATED = "n.a."

STOPWORDS = set([''])
CONFLICT_MAP = {}
MULTI_WORD_TERMS = []

TOKENIZER_REGEX = None

PREFIX, SUFFIX, INFIX, FULLWORD = 'psif'

LABEL_LTWA, LABEL_MULTIWORD, LABEL_CONFLICT = 'lmc'

LOWERCASE, UPPERCASE, TITLECASE = 'lut'

def __initialize_ltwa():
    global LTWA, CONFLICT_MAP, MULTI_WORD_TERMS, STOPWORDS, TOKENIZER_REGEX
    json_filepath = os.path.join(os.path.dirname(__file__), "LTWA_{}.json".format(LTWA_VERSION))
    try:
        # Read JSON.
        with open(json_filepath,'r') as inf:
            inf_json = json.load(inf)
            LTWA = inf_json[LABEL_LTWA]
            MULTI_WORD_TERMS = inf_json[LABEL_MULTIWORD]
            CONFLICT_MAP = inf_json[LABEL_CONFLICT]
    except:
        # Create JSON from TSV.
        tsv_filepath = os.path.join(os.path.dirname(__file__), "LTWA_{}.tsv".format(LTWA_VERSION))
        with open(tsv_filepath,'r') as inf:
            # Make list of conflict words to gather information about on pass 2
            conflict_words = set()
            tsv = csv.reader(inf, delimiter='\t')
            # Build LTWA dict
            for line in tsv:
                word, abbr, langs = line
                type = __get_type(word)
                word = __normalize_word(word)
                abbr = __normalize_abbr(abbr)
                # Add type to dict if needed
                if type not in LTWA:
                    LTWA[type] = {}
                # Detect conflict words
                if word in LTWA[type]:
                    conflict_words.add((type, word))
                elif ' ' in word:
                    MULTI_WORD_TERMS.append(re.escape(word))
                LTWA[type][word] = abbr
            # Build conflict map
            for type, word in conflict_words:
                # remove from main list
                LTWA[type].pop(word)
            inf.seek(0)
            for line in tsv:
                word, abbr, langs = line
                type = __get_type(word)
                word = __normalize_word(word)
                if (type, word) in conflict_words:
                    abbr = __normalize_abbr(abbr)
                    if type not in CONFLICT_MAP:
                        CONFLICT_MAP[type] = {}
                    if word not in CONFLICT_MAP[type]:
                        CONFLICT_MAP[type][word] = {}
                    for lang in langs.split(','):
                        CONFLICT_MAP[type][word][lang.strip()] = abbr
        MULTI_WORD_TERMS = sorted(list(set(MULTI_WORD_TERMS)))
        with open(json_filepath,'w') as outf:
            json.dump({
                          LABEL_LTWA : LTWA,
                          LABEL_CONFLICT : CONFLICT_MAP,
                          LABEL_MULTIWORD : MULTI_WORD_TERMS
                      }, outf)

    # Set of stopwords from txt
    sw_filepath = os.path.join(os.path.dirname(__file__), "stopwords.txt")
    with open(sw_filepath,'r') as inf:
        STOPWORDS = set([unicodedata.normalize('NFKD', line.strip()) for line in inf.readlines()])

    # Tokenizer regex from multi words
    TOKENIZER_REGEX = re.compile("({}|\\s+)".format('|'.join(["(?:^|\\s){}(?:\\s|$)".format(w) for w in MULTI_WORD_TERMS])), flags=re.I)


def __get_type(word):
    """Determine type of word based on hyphenation."""
    if word.startswith('-'):
        return INFIX if word.endswith('-') else SUFFIX
    elif word.endswith('-'):
        return PREFIX
    else:
        return FULLWORD

def __get_capitalization(word):
    if word == word.upper():
        return UPPERCASE
    elif word[0].isupper():
        # if titlecase were tested for, this would return LOWERCASE for
        # multiword exps not in full title case
        # e.g. "United states" --> "u. s."
        # so just force title case for anything starting with a capital
        return TITLECASE
    return LOWERCASE

def __normalize_word(word):
    """Strip hyphens, other punctuation, lower, normalize NFKD."""
    parts = []
    for part in word.split(' '):
        part = re.sub(r"(^\-|\p{P}+$)", '', part).strip()
        parts.append(unicodedata.normalize('NFKD', part.lower()))
    return ' '.join(parts).strip()

def __normalize_abbr(abbr):
    """Strip hyphens, period, lower, normalize NFKD (if not "n.a.")."""
    if abbr == NOT_ABBREVIATED:
        return abbr
    parts = []
    for part in abbr.split(' '):
        parts.append(unicodedata.normalize('NFKD', part.strip('- ').rstrip('.').lower()))
    return ' '.join(parts)

def __finalize_output(word, capitalization, periods):
    """Modify output word according to capitalization and period rules."""
    parts = []
    for part in word.split(' '):
        if capitalization == UPPERCASE:
            part = part.upper()
        elif capitalization == TITLECASE:
            part = string.capwords(part)
        if periods:
            part += '.'
        parts.append(part)
    return ' '.join(parts)

__initialize_ltwa()
