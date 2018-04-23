#!/usr/bin/python

import sys
import os
import getopt
from datetime import datetime
import re
import progressbar
from stop_words import get_stop_words

infileName = ""
infileIsDirectory = False
outfileName = ""
excludefileName = ""


def init():
    global stopWordDict
    stop_words = get_stop_words('english')
    for word in stop_words:
        stopWordDict[word] = 0


def usrmsg(formfeeds, indents, message):
    for i in range(0, formfeeds):
        print ' '
    pad = ''
    for i in range(0, indents):
        pad += '  '
    print '{}{}'.format(pad, message)


def openFile(fname, rwFlag):
    file = None
    error = False

    try:
        file = open(fname, rwFlag)
        if file is None:
            usrmsg(0, 2, 'Cannot open output word file: {}'.format(fname))
            error = True
    except:
        usrmsg(0, 2, 'Error opening word file: {}'.format(fname))
        error = True

    return error, file


def readLines(inFile):
    lines = []
    count = 0
    for line in inFile:
        lines.append(line)
        count += 1
    return lines, count


def loadExcludeDict(fname):
    error = False

    usrmsg(1, 1, "Loading exclude dictionary..")

    dict={}
    error, dictFile = openFile(fname, 'r')

    if dictFile is not None:
        for line in dictFile:
            word = line.strip()
            dict[word] = 1
        dictFile.close()
        usrmsg(0, 2, "Loaded {} unique words".format(len(dict)))

    return error, dict


def splitLine(line):
    line = re.sub(r'[\(\{\[\)\}\]\'\"\+\*\,\/\|\>\<\^\\%;.@#~:=]', ' ', line)
    words = []
    words = line.split()
    return words


def includeWord(word):
    include = True
    if re.search(r'^[0-9a-fx\.\-]+$', word):
        include = False
    elif not re.search(r'^[a-z]+', word):
        include = False
    elif not re.search(r'[a-z0-9]+$', word):
        include = False
    elif len(word) < 4:
        include = False;

    return include


def createDictionary(infile, outfile, excludes):
    error = False
    fin = None
    fout = None
    excludes = {}
    newWords = {}

    error, fin = openFile(infile, 'r')

    if outfile != "":
        error, fout = openFile(outfile, 'w')

    if not error:
        lines, numLines = readLines(fin)
        progressCounter = 0
        with progressbar.ProgressBar(widgets=["    ", progressbar.Percentage(), ' ', progressbar.Bar()], max_value=numLines, term_width=20) as progress:
            for line in lines:
                words = splitLine(line)
                for word in words:
                    word = word.lower()
                    if includeWord(word) and not excludes.has_key(word):
                        if not newWords.has_key(word):
                            newWords[word] = 1
                        else:
                            newWords[word] += 1
                progressCounter += 1
                progress.update(progressCounter)

    if not error:
        sortedKeys = sorted(newWords.keys())
        for key in sortedKeys:
            outword = '{} : {}'.format(key, newWords[key])
            if fout is not None:
                outword += "\n"
                fout.write(outword)
            else:
                usrmsg(0, 0, outword)
        if fout is not None:
            fout.close()

        usrmsg(0, 2, "Created dictionary with {} words.".format(len(newWords)))

    return error


def fileList(infile, outfile, processDirectory):
    error = False
    infiles = []
    outfiles = []

    if processDirectory is True:
        try:
            for file in os.listdir(infile):
                base, extension = os.path.splitext(file)
                if extension == '.txt':
                    if infile.endswith(os.path.sep) is False:
                        infile = infile + os.path.sep
                    infiles.append(infile + file)
                    if outfile.endswith(os.path.sep) is False:
                        outfile = outfile + os.path.sep
                    fulloutname = outfile + base + ".dict"
                    outfiles.append(fulloutname)
        except:
            error = True
    else:
        infiles.append(infile)
        outfiles.append(outfile)

    return error, infiles, outfiles


def processFiles(infile, outfile, excludefile, processDirectory):
    error = False
    fin = None
    fout = None
    excludes = {}
    newWords = {}

    if excludefile != "":
        error, excludes = loadExcludeDict(excludefile)

    error, inFiles, outFiles = fileList(infile, outfile, processDirectory)

    if error is False:
        for inf, outf in zip(inFiles, outFiles):
            outname = os.path.basename(outf)
            usrmsg(0, 1, "Creating Dictionary {}".format(outname))
            error = createDictionary(inf, outf, excludes)
            if error:
                break

    return error


def displayHelp():
    usrmsg(1, 1, 'text2Dictionary.py [OPTIONS] FILE')
    usrmsg(1, 1, 'Create a list of unique words from a text document.')
    usrmsg(1, 2, '-h, --help : show this help screen')
    usrmsg(0, 2, '-d         : Treat FILE as a directory and process each file in directory FILE')
    usrmsg(0, 2, '-o [str]   : Write output to file [str] instead of screen.')
    usrmsg(0, 2, '           : if -d : Write output files to this directory.')
    usrmsg(0, 2, '             otherwise: Write output to file FILE but change extension to dict.')
    usrmsg(0, 2, '-e [str]   : Exclude any word found in file [str].')


def parseOptions():
    global outfileName
    global excludefileName
    global infileName
    global infileIsDirectory

    exit = False
    error = ""
    help = False
    numArgsParsed = 0
    sameName = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdo:e:", ['help'])
    except getopt.GetoptError:
        error = 'invalid or missing argument. -h for help.'
        help = True
        exit = True

    if not help:
        for opt, arg in opts:
            if opt == '-h' or opt == '--help':
                help = True
                exit = True
                numArgsParsed += 1
                break
            elif opt == '-d':
                infileIsDirectory = True
                numArgsParsed += 1
            elif opt == '-o':
                outfileName = arg
                numArgsParsed += 2
            elif opt == '-w':
                sameName = True
                numArgsParsed += 1
            elif opt == '-e':
                excludefileName = arg
                numArgsParsed += 2

    if len(sys.argv) - (numArgsParsed + 1) != 1:
        error = 'input filename not specified.'
        help = True
        exit = True

    if help:
        displayHelp()
    if error != "":
        usrmsg(2, 1, 'Error: {}'.format(error))
    if not exit:
        infileName = sys.argv[len(sys.argv)-1]
        if outfileName == "":
            if infileIsDirectory is True:
                outfileName = infileName
            else:
                name = os.path.basename(infileName)
                outfileName = re.sub(r'\.[A-Za-z0-9_]+$', '.dict', name)

    return exit


if __name__ == "__main__":
    ########################################
    # MAIN
    ########################################

    if not parseOptions():
        startTime = datetime.now()

        processFiles(infileName, outfileName, excludefileName, infileIsDirectory)

        endTime = datetime.now()
        FMT = '%H:%M:%S'
        tdelta = endTime - startTime
        usrmsg(1, 1, 'Completed in : {}'.format(tdelta))