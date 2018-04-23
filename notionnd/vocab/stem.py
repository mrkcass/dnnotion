#!/usr/bin/python

import sys
import subprocess
import getopt
from datetime import datetime
import re
import progressbar
from nltk.stem import PorterStemmer as nltk_stemmer_porter
from nltk.stem.lancaster import LancasterStemmer as nltk_stemmer_lancaster
from nltk.stem.snowball import EnglishStemmer as nltk_stemmer_snowball
from nltk.stem import WordNetLemmatizer as nltk_lemmer_wordnet


def process(poptions, pmetrics):
    pmetrics['len1'] = 0
    pmetrics['stemmed'] = 0
    pmetrics['lemmed'] = 0
    pmetrics['not_stemmed'] = 0
    pmetrics['special_words'] = 0
    pmetrics['new_vocab_size'] = 0
    pmetrics['old_vocab_size'] = 0
    pmetrics['total_words'] = 0
    pmetrics['total_lines'] = 0

    stem_vocab(poptions, pmetrics)

    usrmsg(2, 2, "total unique before  = {}".format(pmetrics['old_vocab_size']))
    usrmsg(0, 2, "total unique after   = {}".format(pmetrics['new_vocab_size']))
    if poptions['lem'] is True:
        usrmsg(0, 2, "lemmed         = {}".format(pmetrics['lemmed']))
    if poptions['stem'] is True:
        usrmsg(0, 2, "stemmed        = {}".format(pmetrics['stemmed']))
    usrmsg(0, 2, "unchanged      = {}".format(pmetrics['not_stemmed']))
    usrmsg(0, 2, "special        = {}".format(pmetrics['special_words']))
    usrmsg(0, 2, "length = 1     = {}".format(pmetrics['len1']))

    usrmsg(1, 2, "total corpus words   = {}".format(pmetrics['corpus_num_words']))
    usrmsg(0, 2, "total replaced words = {}".format(pmetrics['corpus_num_replaced']))


def stem_vocab(poptions, pmetrics):
    _, output_vocab_file = fileopenW(poptions['vocab_outfile'])
    _, input_vocab_file = fileopenR(poptions['vocab_infile'])
    _, stem_outfile = fileopenW(poptions['stem_outfile'])
    input_words, special_words, input_numlines, input_numwords = readwords_to_speciallist(input_vocab_file)
    pmetrics['total_words'] = input_numwords
    pmetrics['total_lines'] = input_numlines
    pmetrics['special_words'] = len(special_words)

    usrmsg(1, 2, 'Loading NLTK')
    stemmer = get_algorithm(poptions['algorithm'])
    lemmer = nltk_lemmer_wordnet()

    fileclose(input_vocab_file)
    usrmsg(1, 2, 'Indexing {} words from {} lines'.format(input_numwords, input_numlines))

    tokedwords = set(input_words)
    if poptions['stem'] is True and poptions['lem'] is True:
        usrmsg(1, 2, 'Lemming and Stemming {} words'.format(len(tokedwords)))
    elif poptions['lem'] is True:
        usrmsg(1, 2, 'Lemming {} words'.format(len(tokedwords)))
    pmetrics['old_vocab_size'] = len(tokedwords)

    num_words = 0
    new_words = []
    stem_crossref = {}
    pbar = make_progressbar_for_list()
    for word in pbar(tokedwords):
        num_words += 1
        if len(word) == 1:
            pmetrics['len1'] += 1
            continue

        if poptions['lem'] is True:
            lemmed_word = lemmer.lemmatize(word)
            if lemmed_word is not word:
                pmetrics['lemmed'] += 1
        else:
            lemmed_word = word
        if poptions['stem'] is True:
            stemmed_word = stemmer.stem(lemmed_word)
            if stemmed_word is not lemmed_word:
                pmetrics['stemmed'] += 1
        else:
            stemmed_word = lemmed_word

        if stemmed_word == word:
            pmetrics['not_stemmed'] += 1
            new_words.append(word)
            continue

        if len(stemmed_word) > 1:
            if poptions['stem'] is True and poptions['lem'] is True:
                filewriteline(stem_outfile, "word: {:<30} stemlem: {}".format(word, stemmed_word))
            elif poptions['stem'] is True:
                filewriteline(stem_outfile, "word: {:<30} stem: {}".format(word, stemmed_word))
            elif poptions['lem'] is True:
                filewriteline(stem_outfile, "word: {:<30} lem: {}".format(word, stemmed_word))
            new_words.append(stemmed_word)
            stem_crossref[word] = stemmed_word
        else:
            pmetrics['len1'] += 1
            new_words.append(word)
    fileclose(stem_outfile)

    new_words = set(new_words)
    pmetrics['new_vocab_size'] = len(new_words)
    new_words.update(special_words)
    for word in sorted(new_words):
        filewriteline(output_vocab_file, word)
    fileclose(output_vocab_file)

    apply_stemmed_vocab(poptions, pmetrics, stem_crossref)


def apply_stemmed_vocab(poptions, pmetrics, stems):
    pmetrics['corpus_num_words'] = 0
    pmetrics['corpus_num_replaced'] = 0

    usrmsg(1, 2, 'Loading Corpus: {}'.format(poptions['apply_infile']))
    _, output_file = fileopenW(poptions['apply_outfile'])
    _, input_file = fileopenR(poptions['apply_infile'])

    if poptions['stem'] and poptions['lem']:
        usrmsg(1, 2, "Stemming and Lemming to: {}".format(poptions['apply_outfile']))
    elif poptions['stem']:
        usrmsg(1, 2, "Stemming corpus to: {}".format(poptions['apply_outfile']))
    elif poptions['lem']:
        usrmsg(1, 2, "Lemming corpus to: {}".format(poptions['apply_outfile']))

    listlines, _, _ = readwords_to_wordlists(input_file)
    pbar = make_progressbar_for_list()
    for line in pbar(listlines):
        lineout = []
        wparts = line[0].split(',')
        line[0] = wparts[-1:][0]
        for word in line:
            pmetrics['corpus_num_words'] += 1
            word = word.strip()
            if word in stems:
                lineout.append(stems[word])
                pmetrics['corpus_num_replaced'] += 1
            else:
                lineout.append(word)
        if len(wparts[:-1]):
            lineout[0] = ','.join(wparts[:-1]) + "," + lineout[0]

        filewriteline(output_file, ' '.join(lineout))

    fileclose(output_file)
    fileclose(input_file)


def get_algorithm(algorithm):
    if algorithm == 'porter':
        return nltk_stemmer_porter()
    elif algorithm == 'lancaster':
        return nltk_stemmer_lancaster()
    elif algorithm == 'snowball':
        return nltk_stemmer_snowball()
    else:
        usrmsg(1, 2, "Error unknown algorithm: " + algorithm)
        quit()


def load_nltk_downloader():
    subprocess.Popen(['python', '-c', 'import nltk; nltk.downloader.download()'])


def usrmsg(formfeeds, indents, message):
    for _ in range(0, formfeeds):
        print ' '
    pad = ''
    for _ in range(0, indents):
        pad += '  '
    print '{}{}'.format(pad, message)


def fileopenR(fname):
    return fileopen(fname, "r")


def fileopenW(fname):
    return fileopen(fname, "w")


def fileopenA(fname):
    ofile = fileopen(fname, "a")
    if not ofile:
        print('Error. can\'t open file: {}'.format(fname))
        quit()
    return ofile


def fileopen(fname, rwFlag):
    open_file = None
    error = False

    try:
        open_file = open(fname, rwFlag)
        if open_file is None:
            usrmsg(0, 2, 'Cannot open output word file: {}'.format(fname))
            error = True
    except:
        usrmsg(0, 2, 'Error opening file: {}'.format(fname))
        error = True

    return error, open_file


def fileclose(opn_file):
    opn_file.close()


def filewrite(outfile, outtext):
    outfile.write(outtext)
    #print outtext


def filewriteline(outfile, outtext):
    outfile.write(outtext + "\n")


def readlines(inFile):
    lines = []
    count = 0
    for line in inFile:
        lines.append(line)
        count += 1
    return lines, count


def readwords_to_list(inFile):
    all_words = []
    count = 0
    for line in inFile:
        line_words = line.split(' ')
        all_words += line_words
        count += len(line_words)
    return all_words, count


def readwords_to_wordlists(inFile):
    all_words = []
    linecount = 0
    wordcount = 0
    for line in inFile:
        line_words = line.split(' ')
        cleanwords = []
        for word in line_words:
            cleanwords.append(word.strip())
            wordcount += 1
        all_words.append(cleanwords)
        linecount += 1
    return all_words, linecount, wordcount


def readwords_to_speciallist(inFile):
    all_words = []
    line_count = 0
    word_count = 0
    special_words = []
    for line in inFile:
        line_count += 1
        words = line.split(' \n')
        for word in words:
            word = word.strip()
            if '/' in word:
                new_words = word.split('/')
                words.extend(new_words)
                continue
            if "$" in word:
                special_words.append(word)
            else:
                matchobj = re.match('^([0-9]+)([^0-9]+)', word)
                if matchobj:
                    all_words.append(matchobj.group(2))
                else:
                    all_words.append(word)
            word_count += 1
    return all_words, special_words, line_count, word_count


def make_progressbar(max_counter):
    widgets = ["       ", progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    return progressbar.ProgressBar(widgets=widgets, max_value=max_counter, term_width=40)


def make_progressbar_for_list():
    widgets = ["       ", progressbar.Percentage(
    ), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    return progressbar.ProgressBar(widgets=widgets, term_width=40)


def output_to_default(input_name):
    if re.search(r'\.[0-9a-zA-Z_\-]+$', input_name):
        output_name = re.sub(r'\.[0-9a-zA-Z_\-]+$', '_stm.txt', input_name)
    else:
        output_name = input_name + "_stm.txt"
    return output_name


def output_with_suffix(input_name, suffix):
    if re.search(r'\.[0-9a-zA-Z_\-]+$', input_name):
        output_name = re.sub(r'\.[0-9a-zA-Z_\-]+$', '_' + suffix + '.txt', input_name)
    else:
        output_name = input_name + '_' + suffix + '.txt'
    return output_name


def display_help():
    print ' '
    print 'stemandlem [OPTIONS] VOCABFILE'
    print ' '
    print '  stemming and lemmatiztion using Stanford NLTK'
    print '   as: s, es, ing, ed'
    print ' '
    print 'OPTIONS:'
    print '   -h, --help  : show this help screen'
    print '   -c FILENAME  :  Apply stemmed vocab to corpus file FILENAME.'
    print '   -b FILENAME  :  Send -a output to FILENAME. the default'
    print '                  is the -a FILENAME with the suffix _stm placed'
    print '                  before the extension'
    print '   -o FILENAME  :  Send output of stemmed vocab to FILENAME. the default'
    print '                  is the VOCABFILE with the suffix _stm placed'
    print '                  before the extension'
    print '   -a ALGORITHM : Use this stemming algorithm: porter, lancaster, '
    print '                   or snowball. default = porter'
    print '   -l           : Use Wordnet Lemmatizer instead of stemmer'
    print '   -m           : Use Wordnet Lemmatizer then stem algorithm'
    print '   -s           :  load the Stanford nltk Download service.'


def parse_options(poptions):
    close = False
    error = ""
    show_help = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hpqslmc:b:a:o:", ['help'])
    except getopt.GetoptError:
        error = 'invalid or missing argument. -h for help.'
        show_help = True
        close = True

    if not show_help:
        for opt, arg in opts:
            if opt == '-h' or opt == '--help':
                show_help = True
                close = True
                break
            elif opt == '-o':
                poptions['vocab_outfile'] = arg.strip()
            elif opt == '-a':
                poptions['algorithm'] = arg.strip()
            elif opt == '-c':
                poptions['apply_infile'] = arg.strip()
            elif opt == '-b':
                poptions['apply_outfile'] = arg.strip()
            elif opt == '-l':
                poptions['lem'] = True
                poptions['stem'] = False
            elif opt == '-m':
                poptions['lem'] = True
                poptions['stem'] = True
            elif opt == '-s':
                poptions['downloader'] = True

    if show_help is False and not poptions['downloader']:
        if len(args) != 1:
            error = 'VOCABFILE file name not specified.'
            show_help = True
            close = True
        else:
            poptions['vocab_infile'] = sys.argv[len(sys.argv) - 1]
            if poptions['vocab_outfile'] == "":
                poptions['vocab_outfile'] = output_to_default(poptions['vocab_infile'])
            if poptions['apply_infile'] != "" and poptions['apply_outfile'] == "":
                poptions['apply_outfile'] = output_to_default(poptions['apply_infile'])
            if poptions['apply_infile'] != "" and poptions['stem_outfile'] == "":
                poptions['stem_outfile'] = output_with_suffix(poptions['vocab_infile'], "stems")

    if show_help:
        display_help()
    if error != "":
        usrmsg(2, 1, 'Error: {}'.format(error))

    return close


if __name__ == "__main__":
    ########################################
    # MAIN
    ########################################
    POPTIONS = {
        'vocab_infile': "",
        'vocab_outfile': "",
        'apply_infile': "",
        'apply_outfile': "",
        'lem': False,
        'stem': True,
        'stem_outfile': "",
        'algorithm': "porter",
        'downloader': False,
    }

    PMETRICS = {
        'num_docs': 0,
        'num_vocab_words_before': 0,
        'num_stems': [0]
    }

    if not parse_options(POPTIONS):
        startTime = datetime.now()

        if POPTIONS['downloader']:
            load_nltk_downloader()
        else:
            process(POPTIONS, PMETRICS)

        endTime = datetime.now()
        FMT = '%H:%M:%S'
        tdelta = endTime - startTime
        usrmsg(1, 1, 'Completed in : {}'.format(tdelta))
