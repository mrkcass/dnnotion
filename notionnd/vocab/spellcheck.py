#!/usr/bin/python

import sys
import os
import getopt
from datetime import datetime
import progressbar
import re
from multiprocessing import Pool as ThreadPool

dictionaryDir = ""
corpusFileName = ""
outputFileName = ""
masterOnly = False
SUGGESTION_THRESHOLD = 3


##########################################################################
# http://norvig.com/spell-correct.html
from collections import Counter


def EditDist_words(text):
    return re.findall(r'\w+', text.lower())


EditDist_WORDS = {}


def EditDist_init(dictionary):
    global EditDist_WORDS

    EditDist_WORDS = Counter(dictionary.keys())


def EditDist_P(word, N=sum(EditDist_WORDS.values())):
    "Probability of `word`."
    return EditDist_WORDS[word] / N


def EditDist_correction(word):
    "Most probable spelling correction for word."
    return max(EditDist_candidates(word), key=EditDist_P)


def EditDist_candidates(word):
    "Generate possible spelling corrections for word."
    return EditDist_known([word]) or EditDist_known(EditDist_edits1(word)) or EditDist_known(EditDist_edits2(word)) or [word]


def EditDist_known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in EditDist_WORDS)


def EditDist_edits1(word):
    "All edits that are one edit away from `word`."
    letters =   'abcdefghijklmnopqrstuvwxyz'
    splits =     [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes =    [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces =   [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts =    [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def EditDist_edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in EditDist_edits1(word) for e2 in EditDist_edits1(e1))

# http://norvig.com/spell-correct.html end
##########################################################################


def init():
    return 0


def usrmsg(formfeeds, indents, message):
    for _ in range(0, formfeeds):
        print ' '
    pad = ''
    for _ in range(0, indents):
        pad += '  '
    print '{}{}'.format(pad, message)


def openFileR(fname):
    openedFile = None
    error = False

    try:
        openedFile = open(fname, 'r')
        if openedFile is None:
            usrmsg(0, 2, 'Cannot open output word file: {}'.format(fname))
            error = True
    except IOError:
        usrmsg(0, 2, 'Error opening word file: {}'.format(fname))
        error = True

    return error, openedFile


def openFileW(fname):
    openedFile = None
    error = False

    try:
        openedFile = open(fname, 'w')
        if openedFile is None:
            usrmsg(0, 2, 'Cannot open output word file: {}'.format(fname))
            error = True
    except IOError:
        usrmsg(0, 2, 'Error opening word file: {}'.format(fname))
        error = True

    return error, openedFile


def closeFile(fileToClose):
    fileToClose.close()
    return True


def readFileLines(inFile):
    lines = []
    count = 0
    for line in inFile:
        lines.append(line)
        count = count + 1

    return count, lines


def writeFileLine(out, line):
    out.write('{}\n'.format(line))


def writeFile(out, line):
    out.write('{}'.format(line))


def make_progress_bar(max_counter):
    widgets = ["       ", progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    return progressbar.ProgressBar(widgets=widgets, max_value=max_counter, term_width=40)


def loadDictionary(fname, directory, masterDictionary):

    error, fin = openFileR('{}{}{}'.format(directory, os.path.sep, fname))
    totalWords = 0
    uniqueWords = 0

    if not error:
        for line in fin:
            totalWords = totalWords + 1
            words = line.split(':')
            word = words[0].lower().strip()
            if word not in masterDictionary:
                uniqueWords = uniqueWords + 1
                if len(words) > 1:
                    masterDictionary[word] = {'frequency': words[1], 'file': fname}
                else:
                    masterDictionary[word] = {'frequency': -1, 'file': fname}

    closeFile(fin)

    usrmsg(0, 6, 'dictionary {}:'.format(fname))
    usrmsg(0, 8, 'using {} of {} words'.format(uniqueWords, totalWords))

    return error, totalWords, uniqueWords


def fileList(extension, directory):
    error = False
    files = []

    try:
        dirFiles = os.listdir(directory)
        for dirFile in dirFiles:
            _, fileExtension = os.path.splitext(dirFile)
            if fileExtension == extension:
                files.append(dirFile)
    except IOError:
        error = True

    return error, files


def fileInDir(fileName, directory):
    error = False
    found = False

    try:
        dirFiles = os.listdir(directory)
        for dirFile in dirFiles:
            if dirFile == fileName:
                found = True
                break
    except IOError:
        error = True

    return error, found


def loadDictionaries(directory, onlyMaster):
    error = False

    dictionary = {}
    error, inFiles = fileList('.dict', directory)

    usrmsg(0, 4, 'loading {} dictionaries'.format(len(inFiles)))

    if error is False:
        if fileInDir("master.dict", directory):
            loadDictionary("master.dict", directory, dictionary)
        if not onlyMaster:
            for inf in inFiles:
                if inf != "master.dict":
                    error, _, _ = loadDictionary(inf, directory, dictionary)
                    if error:
                        break

    usrmsg(0, 4, 'loading complete: {} unique words'.format(len(dictionary)))

    return error, dictionary


def loadCorpus(corpusName):
    error, corpusFile = openFileR(corpusName)

    if not error:
        count, lines = readFileLines(corpusFile)
        closeFile(corpusFile)

        usrmsg(1, 4, 'loaded corpus {} with {} lines'.format(corpusName, count))
    else:
        usrmsg(1, 4, 'file read error {}'.format(corpusName))

    return count, lines


def dumpUnknownWords(fileName, unknowns, editDict, knowns):
    possibles = {}
    error, out = openFileW(fileName)
    if not error:
        for word, stats in iter(sorted(unknowns.iteritems())):
            suggestionList = []
            if word in editDict:
                suggestionList = editDict[word]
            suggestions_list_freq = []
            has_known_suggestion = False
            for suggestion in suggestionList:
                if suggestion in knowns:
                    suggestions_list_freq.append("{}({})".format(suggestion, knowns[suggestion]['count']))
                    has_known_suggestion = True
                else:
                    suggestions_list_freq.append(suggestion)
            if len(suggestionList) <= SUGGESTION_THRESHOLD and has_known_suggestion:
                possibles[word] = 1
            else:
                suggestionString = ' '.join(suggestions_list_freq)
                writeFileLine(out, '{0: 5d} : {1} : {2}'.format(stats['count'], word, suggestionString))
        closeFile(out)
    return error, possibles


def buildUnknownDict(corpusLines, knownDictionary):
    unknownDict = {'indexes':   [0, 1, 2, 3],
                   'count':     0}
    unknownDict.clear()
    knownUsedDict = {'indexes':   [0, 1, 2, 3],
                     'count':     0}
    knownUsedDict.clear()
    wordCount = 0
    unknownCount = 0
    tokenCount = 0

    progressCounter = 0
    progress = progressbar.ProgressBar(widgets=["       ", progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()],
                                       max_value=len(corpusLines),
                                       term_width=40)
    for line in corpusLines:
        words = line.split()
        for word in words:
            word = word.lower().strip()
            if word[0] is "$":
                tokenCount += 1
            elif word not in knownDictionary:
                unknownCount += 1
                if word in unknownDict:
                    e = unknownDict[word]
                else:
                    e = {'indexes': [], 'count': 0}
                    unknownDict[word] = e
                e['indexes'].append(wordCount)
                e['count'] += 1
            else:
                if word in knownUsedDict:
                    e = knownUsedDict[word]
                else:
                    e = {'indexes': [], 'count': 0}
                    knownUsedDict[word] = e
                e['indexes'].append(wordCount)
                e['count'] += 1
            wordCount += 1
        progressCounter += 1
        progress.update(progressCounter)

    print ' '
    return wordCount, unknownCount, knownUsedDict, unknownDict, tokenCount


def spiltUnknowns(unknownDict, knownDict):
    unknownsAdded = {}
    unknownsRemoved = {}
    knownsFound = {}

    for word, _ in unknownDict.iteritems():
        subwords = re.split(r'_|-|/', word)
        if subwords > 1:
            found = []
            notFound = []
            for subword in subwords:
                if subword in knownDict:
                    found.append(subword)
                else:
                    notFound.append(subword)
            if len(found):
                unknownsRemoved[word] = "split"
                for subword in found:
                    if subword in knownsFound:
                        knownsFound[subword] += 1
                    else:
                        knownsFound[subword] = 1
                for subword in notFound:
                    if subword in unknownsAdded:
                        unknownsAdded[subword] += 1
                    else:
                        unknownsAdded[subword] = 1

    return unknownsAdded, unknownsRemoved, knownsFound


def getEditDistance(words):
    editDict = {'suggestions':   [0, 1, 2, 3]}
    editDict.clear()

    progressCounter = 0
    progress = progressbar.ProgressBar(widgets=["       ", progressbar.Percentage(), ' ', progressbar.Bar()],
                                       max_value=len(words),
                                       term_width=40)
    for word in words:
        if not re.search(r'[_\-\\\/]+', word) and len(word) < 20:
            suggestions = EditDist_candidates(word)
            #usrmsg(0, 4, '{}: {}'.format(word, ' '.join(suggestions)))
            editDict[word] = suggestions
        progressCounter += 1
        progress.update(progressCounter)

    return editDict


def getEditDistanceUnknowns(unknownDict, knowDict):

    EditDist_init(knowDict)

    unknownList = list(unknownDict.keys())
    poolLists = [unknownList]
    numSplits = 4
    for _ in range(numSplits):
        newPoolLists = []
        for plist in poolLists:
            newPoolLists.append(plist[:len(plist) / 2])
            newPoolLists.append(plist[(len(plist) / 2) + 1:])
        poolLists = newPoolLists

    pool = ThreadPool(processes=pow(2, numSplits))
    results = pool.map(getEditDistance, poolLists)
    pool.close()
    pool.join()
    editDict = dict(pair for d in results for pair in d.items())

    return editDict


def outputSpelledCorpus(outname, corpus_lines, replace_words, knowns, edits):
    num_words = 0
    num_known = 0
    num_replaced = 0
    error, fout = openFileW(outname)
    if not error:
        pbar_counter = 0
        pbar = make_progress_bar(len(corpus_lines))
        for line in corpus_lines:
            outwords = []
            words = line.split()
            for word in words:
                outword = word.strip()
                num_words += 1
                if outword in knowns:
                    num_known += 1
                if outword in replace_words:
                    num_replaced += 1
                    suggestion_list = edits[outword]
                    best_freq = 0
                    for suggestion in suggestion_list:
                        if suggestion in knowns:
                            freq = knowns[suggestion]['count']
                            if freq > best_freq:
                                outword = suggestion
                                best_freq = freq
                outwords.append(outword)
            outline = ' '.join(outwords)
            writeFileLine(fout, outline)
            pbar_counter += 1
            pbar.update(pbar_counter)
        fout.close()

    return num_words, num_known, num_replaced


def spellcheck(dictionaryDirectory, corpusName, outputName, onlyMaster):
    usrmsg(2, 4, 'Dictionary path: {}'.format(dictionaryDirectory))

    error, knownDict = loadDictionaries(dictionaryDirectory, onlyMaster)
    if outputName == "":
        outputName = corpusName
    usrmsg(0, 4, 'output: {}'.format(outputName))

    if not error:
        count, lines = loadCorpus(corpusName)

    if not error and count:
        usrmsg(0, 4, 'analyzing corpus, stand by...')
        wordCount, unknownCount, knownUsedDict, unknownDict, tokenCount = buildUnknownDict(lines, knownDict)

        knownCount = wordCount - unknownCount
        knownPerc = float(knownCount * 100) / float(wordCount)
        unknownPerc = float(unknownCount * 100) / float(wordCount)
        tokenPerc = float(tokenCount * 100) / float(wordCount)
        uniqueUnknownPerc = float(len(unknownDict) * 100) / float(len(unknownDict) + len(knownUsedDict))
        uniqueKnownPerc = float(len(knownUsedDict) * 100) / float(len(unknownDict) + len(knownUsedDict))
        usrmsg(0, 4, 'word count           = {}'.format(wordCount))
        usrmsg(0, 4, 'known words          = {} ({:2.2f}%)'.format(knownCount, knownPerc))
        usrmsg(0, 4, 'unknown words        = {} ({:2.2f}%)'.format(unknownCount, unknownPerc))
        usrmsg(0, 4, 'token words          = {} ({:2.2f}%)'.format(tokenCount, tokenPerc))
        usrmsg(0, 4, 'unique known words   = {} ({:2.2f}%)'.format(len(knownUsedDict), uniqueKnownPerc))
        usrmsg(0, 4, 'unique unknown words = {} ({:2.2f}%)'.format(len(unknownDict), uniqueUnknownPerc))

        unknownsAdded, unknownsRemoved, knownsFound = spiltUnknowns(unknownDict, knownDict)
        usrmsg(1, 4, 'split unknowns yields:')
        usrmsg(0, 4, 'unknowns added       = {}'.format(len(unknownsAdded)))
        usrmsg(0, 4, 'unknowns removed     = {}'.format(len(unknownsRemoved)))
        usrmsg(0, 4, 'knowns found         = {}'.format(len(knownsFound)))

        usrmsg(1, 4, 'Checking edit distance:')
        editDict = getEditDistanceUnknowns(unknownDict, knownDict)
        usrmsg(0, 4, 'edit distance check yields:')

        unknownFileName = '{}_unknowns.txt'.format(outputName[:outputName.find('.')])
        error, possibles = dumpUnknownWords(unknownFileName, unknownDict, editDict, knownUsedDict)
        usrmsg(0, 4, 'possible       = {}/{}'.format(len(possibles), len(editDict)))

        usrmsg(1, 4, 'writing: {}'.format(outputName))
        num_output, num_known, num_replaced = outputSpelledCorpus(outputName, lines, possibles, knownUsedDict, editDict)
        usrmsg(1, 5, 'total words  {}'.format(num_output))
        usrmsg(0, 5, 'num replaced {}'.format(num_replaced))
        known_sum = num_known + num_replaced + tokenCount
        known_perc = (float(known_sum) / float(num_output)) * 100.0
        usrmsg(0, 5, 'total known  {}({:.2f}%)'.format(known_sum, known_perc))


def displayHelp():
    usrmsg(1, 1, 'spellcheck.py [OPTIONS] FILE')
    usrmsg(1, 1, 'analyze and correct corpus spelling. default output')
    usrmsg(0, 2, 'file name is FILE_spelled.txt (FILE is without')
    usrmsg(0, 2, 'extension). a master dictionary can be specified')
    usrmsg(0, 2, 'by the name \'master.dict\' in the dictionary directory.')
    usrmsg(0, 2, 'the master dictionary is loaded before the others which')
    usrmsg(0, 2, 'is helpful when evaluating the usefulness of a')
    usrmsg(0, 2, 'domain specific dictionary.')
    usrmsg(1, 1, '-h, --help : show this help screen')
    usrmsg(0, 1, '-d         : dictionary directory')
    usrmsg(0, 1, '-m         : only load the master dictionary.')
    usrmsg(0, 1, '-x         : overwrite the input file.')
    usrmsg(0, 1, '-o         : output to this file name.')


def parseOptions():
    global dictionaryDir
    global corpusFileName
    global outputFileName
    global masterOnly

    exitError = False
    error = ""
    showHelp = False
    numArgsParsed = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hmd:o:", ['help'])
    except getopt.GetoptError:
        error = 'invalid or missing argument. -h for help.'
        showHelp = True
        exitError = True

    if not showHelp:
        for opt, arg in opts:
            if opt == '-h' or opt == '--help':
                showHelp = True
                exitError = True
                numArgsParsed = numArgsParsed + 1
                break
            elif opt == '-d':
                dictionaryDir = arg
                numArgsParsed = numArgsParsed + 2
            elif opt == '-m':
                masterOnly = True
                numArgsParsed = numArgsParsed + 1
            elif opt == '-o':
                outputFileName = arg
                numArgsParsed = numArgsParsed + 2

    if not exitError and (len(sys.argv) - (numArgsParsed + 1) != 1):
        error = 'input filename not specified.'
        showHelp = True
        exitError = True

    if showHelp:
        displayHelp()

    if error != "":
        usrmsg(2, 1, 'Error: {}'.format(error))

    if not exitError:
        corpusFileName = sys.argv[len(sys.argv) - 1]

    return exitError


if __name__ == "__main__":
    ########################################
    # MAIN
    ########################################

    if not parseOptions():
        startTime = datetime.now()

        spellcheck(dictionaryDir, corpusFileName, outputFileName, masterOnly)

        endTime = datetime.now()
        FMT = '%H:%M:%S'
        tdelta = endTime - startTime
        usrmsg(1, 1, 'Completed in : {}'.format(tdelta))
