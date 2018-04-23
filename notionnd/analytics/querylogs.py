#!/usr/bin/python

import re
import sys
import getopt
from datetime import datetime
import os
import progressbar


def main(options_dict):
    logfile_list = get_log_list(options_dict['log_dir'], options_dict['start_id'], options_dict['end_id'])


def get_log_list(log_dir, start_id, end_id):
    # logs = {log_id : {'log': "", 'result': ""}}

    log_list = {}

    num_logs = 0
    num_results = 0
    min_id = 1000000
    max_id = 0
    out_of_range = 0
    for f in os.listdir(log_dir):
        if os.path.isfile(os.path.join(log_dir, f)):
            log_id = 0
            mobj = re.search(r'[0-9]+', f)
            if mobj and mobj.group() is not '':
                log_id = int(mobj.group())
                if log_id > max_id and log_id <= end_id:
                    max_id = log_id
                if log_id < min_id and log_id >= start_id:
                    min_id = log_id
            if log_id < start_id or log_id > end_id:
                out_of_range = out_of_range + 1
                continue
            if ".log" in f:
                if log_id not in log_list:
                    log_list[log_id] = {'log': "", 'result': ""}
                log_list[log_id]['log'] = f
                num_logs += 1
            elif ".result" in f:
                if log_id not in log_list:
                    log_list[log_id] = {'log': "", 'result': ""}
                log_list[log_id]['result'] = f
                num_results += 1

    usrmsg(0, 1, 'log directory: {}'.format(log_dir))
    usrmsg(0, 2, 'logs          : {}'.format(num_logs))
    usrmsg(0, 2, 'results       : {}'.format(num_results))
    usrmsg(0, 2, 'first id      : {}'.format(min_id))
    usrmsg(0, 2, 'last id       : {}'.format(max_id))
    usrmsg(0, 2, 'outside range : {}'.format(out_of_range))

    return log_list


def get_logfilelist_stats(logfile_list):
    stats = {}

    for log_id, logrec in logfile_list.iteritems():
        _, fhndl = fopen_read(logrec['log'])
        _, lines = fread_lines(fhndl)
        logstats = get_logfile_stats(lines)
        if logstats['train_precision'] > 0.0 and logstats['test_precision'] > 0.0:
            usrmsg(0, 1, 'log {:5d}: train({:1.4f})  test({:1.4f})'.format(log_id, logstats['train_precision'], logstats['test_precision']))

    return stats


def get_logfile_stats(lines):
    stats = {"train_precision": 0.0, "test_precision": 0.0}

    train_micro_txt = ""
    test_micro_txt = ""
    for line in lines:
        if line.find("micro-precision") != -1:
            if train_micro_txt == "":
                train_micro_txt = line
            elif test_micro_txt == "":
                test_micro_txt = line
                break

    if train_micro_txt != "":
        mobj = re.search(r'[0-9.]+', train_micro_txt)
        if mobj and mobj.group() != "":
            stats["train_precision"] = float(mobj.group())

    if test_micro_txt != "":
        mobj = re.search(r'[0-9.]+', test_micro_txt)
        if mobj and mobj.group() != "":
            stats["test_precision"] = float(mobj.group())

    return stats


def display_help():
    usrmsg(1, 1, 'querylogs.py [options] log_directory')
    usrmsg(1, 1, 'show statistics about a set of logs.')
    usrmsg(1, 2, '-h, --help : show this help screen')
    usrmsg(0, 2, '-s [int]   : starting log id.')
    usrmsg(0, 2, '-e [int]   : ending log id.')


def parse_options(poptions):
    close = False
    error = ""
    show_help = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:e:", ['help'])
    except getopt.GetoptError:
        error = 'invalid or missing argument. -h for --help.'
        show_help = True
        close = True

    if not show_help:
        for opt, arg in opts:
            if opt == '-h' or opt == '--help':
                show_help = True
                close = True
                break
            elif opt == '-s':
                poptions['start_id'] = int(arg.strip())
            elif opt == '-e':
                poptions['end_id'] = int(arg.strip())

    if show_help is False:
        if len(args) != 1:
            poptions['log_dir'] = os.getcwd()
        else:
            poptions['log_dir'] = sys.argv[len(sys.argv) - 1]

    if show_help:
        display_help()
    if error != "":
        usrmsg(2, 1, 'Error: {}'.format(error))

    return close


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Library code
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def usrmsg(formfeeds, indents, message):
    for _ in range(0, formfeeds):
        print ' '
    pad = ''
    for _ in range(0, indents):
        pad += '  '
    print '{}{}'.format(pad, message)


def fopen_read(fname):
    return fopen(fname, "r")


def fopen_write(fname):
    return fopen(fname, "w")


def fopen(fname, rwFlag):
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


def fclose(fclose):
    fclose.close()


def fwrite(outfile, outtext):
    outfile.write(outtext)
    #print outtext


def fwrite_line(outfile, outtext):
    outfile.write(outtext + "\n")


def fread_lines(inFile):
    lines = []
    count = 0
    for line in inFile:
        lines.append(line)
        count += 1
    return count, lines


def files_in_dir(extension, directory):
    error = False
    files = []

    try:
        print "file dir: {}".format(directory)
        dirFiles = os.listdir(directory)
        for dirFile in dirFiles:
            fileExtension = os.path.splitext(dirFile)
            if fileExtension == extension:
                files.append(dirFile)
    except IOError:
        error = True

    return error, files


def file_in_dir(fileName, directory):
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


def make_progress_bar(max_counter):
    widgets = ["       ", progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    return progressbar.ProgressBar(widgets=widgets, max_value=max_counter, term_width=40)


if __name__ == "__main__":
    ########################################
    # MAIN
    ########################################

    options = {
        'log_dir': "",
        'start_id': 0,
        'end_id': 1000000}

    usrmsg(2, 1, 'query logs running.')
    usrmsg(0, 1, ' ')

    if not parse_options(options):
        startTime = datetime.now()

        main(options)

        endTime = datetime.now()
        FMT = '%H:%M:%S'
        tdelta = endTime - startTime
        usrmsg(1, 1, 'Completed in : {}'.format(tdelta))
