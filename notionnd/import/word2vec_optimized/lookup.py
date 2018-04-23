import progressbar


def lookupNearbyWords(model, filename_pattern, vocab_words):
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


def fileOpen(fname, rwFlag):
    fle = None
    error = False

    try:
        fle = open(fname, rwFlag)
        if fle is None:
            usrmsg(0, 2, 'Cannot open output word file: {}'.format(fname))
            error = True
    except IOError:
        usrmsg(0, 2, 'Error opening word file: {}'.format(fname))
        error = True

    return error, fle


def fileClose(fclose):
    fclose.close()


def fileWrite(fwrite, data):
    fwrite.write(data)


def fileWriteLine(fwrite, data):
    fwrite.write(data + '\n')


def fileReadLines(inFile):
    lines = []
    count = 0
    for line in inFile:
        lines.append(line)
        count += 1
    return lines, count
