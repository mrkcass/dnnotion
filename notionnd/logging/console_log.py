import sys
import os

logPath = ""
logFileName = ""
logId = ""


def setLogPath(path, logid):
    global logPath
    global logFileName
    global logId

    logPath = path
    logId = logid
    logFileName = '{}/run.{}.log'.format(logPath, logId)


def getLogId():
    return logId


def getLogPath():
    return logPath


def getLogFileName():
    return logFileName


def openFileR(fname):
    return openFile(fname, "r")


def openFileW(fname):
    return openFile(fname, "w")


def openFileA(fname):
    openfile = openFile(fname, "a")
    if not openfile:
        print('Error. can\'t open sfile: {}'.format(fname))
        quit()
    return openfile


def openFile(fname, openFlag):
    openedFile = None
    error = False

    try:
        openedFile = open(fname, openFlag)
        if openedFile is None:
            print('Cannot open file: {}'.format(fname))
            error = True
    except IOError:
        print('Error opening file: {}'.format(fname))
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


def fileList(extension, directory):
    error = False
    files = []

    try:
        dirFiles = os.listdir(os.path.abspath(directory))
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


def usrmsg(formfeeds, indents, message):
    for _ in range(0, formfeeds):
        print ' '
    pad = ''
    for _ in range(0, indents):
        pad += '  '
    print '{}{}'.format(pad, message)
    sys.stdout.flush()

    if logPath != "":
        _, log = openFileA(logFileName)
        if log:
            writeFileLine(log, '{}{}'.format(pad, message))
            closeFile(log)

