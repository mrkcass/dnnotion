import progressbar


def reduce(model, vocab_filename, vocab_words):
    # output = target_word_1 : [nearby_1, nearby_2]

    outname = filename_pattern.replace(".txt", "_nearby.txt")
    _, outfile = fileOpen(outname, 'w')

    progressCounter = 0
    with progressbar.ProgressBar(max_value=len(vocab_words)) as progress:
        for word in vocab_words:
            nearbys = nearby_words_str(model, word)
            fileWriteLine(outfile, "{} : {}".format(word, nearbys))
            progressCounter += 1
            progress.update(progressCounter)

    fileClose(outfile)
    return 0


def nearby_words_str(model, word):
    nearbys = model.nearby([word], num=201, silent=True)
    nearby_str = "["
    counter = 0
    for item in nearbys:
        if item['word'] == "UNK":
            nearby_str = "["
            break
        if item['word'] != word:
            if counter > 0:
                spacer = " "
            else:
                spacer = ""
            nearby_str += "{}{}~{:.4f}".format(spacer, item['word'], item['distance'])
            counter += 1

    nearby_str += ']'
    return nearby_str


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
