#!/usr/bin/python

import sys
import getopt
from datetime import datetime
import re
import progressbar
import os
import copy


def usrmsg(formfeeds, indents, message):
    for _ in range(0, formfeeds):
        print ' '
    pad = ''
    for _ in range(0, indents):
        pad += '  '
    print '{}{}'.format(pad, message)


def dir_exists(path):
    if os.path.isdir(path):
        return True
    return False


def get_file_names(extension, directory):
    names = []

    try:
        dir_files = os.listdir(directory)
        for dir_file in dir_files:
            _, file_extension = os.path.splitext(dir_file)
            if not extension:
                names.append(dir_file)
            elif file_extension == extension:
                names.append(dir_file)
    except IOError:
        pass

    return names


def dir_has_file(directory, file_name):
    found = False

    file_names = get_file_names(None, directory)

    #print("files={}".format(file_names))

    if len(file_names) and file_name in file_names:
        found = True

    return found


def file_open(fname, rwFlag):
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


def file_close(file_hndl):
    file_hndl.close()


def file_write(outfile, outtext):
    outfile.write(outtext)
    #print outtext


def file_writeline(outfile, outtext):
    file_write(outfile, outtext + "\n")


def file_readlines(file_hndl):
    lines = []
    for line in file_hndl:
        lines.append(line.rstrip("\n\r"))

    return lines


def make_progress_bar(max_counter):
    widgets = ["       ", progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    return progressbar.ProgressBar(widgets=widgets, max_value=max_counter, term_width=40)


def calc_rates(setinfo):
    rate_rec = {'tp': {'ids': [], 'count': 0, 'rate': 0.0},
                'fp': {'ids': [], 'count': 0, 'rate': 0.0},
                'tn': {'ids': [], 'count': 0, 'rate': 0.0},
                'fn': {'ids': [], 'count': 0, 'rate': 0.0}}

    labels = setinfo['labels']

    rates = {'train': {}, 'test': {}}
    for label in labels:
        rates['train'][label] = copy.deepcopy(rate_rec)
        rates['test'][label] = copy.deepcopy(rate_rec)

    results = setinfo['results']
    for ex_id, ex_result in results.iteritems():
        subset = 'train'
        rates_subset = rates['train']
        if ex_result['set'] == 'test':
            subset = 'test'
            rates_subset = rates['test']
        if ex_result['result'] == 'pass':
            rates_subset[ex_result['expected']]['tp']['ids'].append(ex_id)
            rates_subset[ex_result['expected']]['tp']['count'] += 1
            for label in labels:
                if label != ex_result['expected']:
                    rates_subset[label]['tn']['ids'].append(ex_id)
                    rates_subset[label]['tn']['count'] += 1
        else:
            rates_subset[ex_result['expected']]['fn']['ids'].append(ex_id)
            rates_subset[ex_result['expected']]['fn']['count'] += 1
            rates_subset[ex_result['actual']]['fp']['ids'].append(ex_id)
            rates_subset[ex_result['actual']]['fp']['count'] += 1
            for label in labels:
                if label != ex_result['expected'] and label != ex_result['actual']:
                    rates_subset[label]['tn']['ids'].append(ex_id)
                    rates_subset[label]['tn']['count'] += 1

    for label in labels:
        for settype in ['train', 'test']:
            rates[settype][label]['tp']['rate'] = rates[settype][label]['tp']['count'] / float(rates[settype][label]['tp']['count'] + rates[settype][label]['fp']['count'] )
            rates[settype][label]['fp']['rate'] = rates[settype][label]['fp']['count'] / float(rates[settype][label]['fp']['count'] + rates[settype][label]['tn']['count'] )
            rates[settype][label]['tn']['rate'] = rates[settype][label]['tn']['count'] / float(rates[settype][label]['tn']['count'] + rates[settype][label]['fn']['count'] )
            rates[settype][label]['fn']['rate'] = rates[settype][label]['fn']['count'] / float(rates[settype][label]['tp']['count'] + rates[settype][label]['fn']['count'] )

    for label in labels:
        for rate in ['tp', 'fp', 'tn', 'fn']:
            print("train {} {}: count={} rate={}".format(label, rate, rates['train'][label][rate]['count'], rates['train'][label][rate]['rate']))

    for label in labels:
        for rate in ['tp', 'fp', 'tn', 'fn']:
            print("test  {} {}: count={} rate={}".format(label, rate, rates['test'][label][rate]['count'], rates['test'][label][rate]['rate']))

    return rates


def calc_runstats(setinfo):
    train = {}
    test = {}
    stats = {'train': {'passed': 0, 'failed': 0, 'accuracy': 0.0}, 'test': {'passed': 0, 'failed': 0, 'accuracy': 0.0}}
    for ex_id, ex_result in setinfo['results'].iteritems():
        subset = train
        stats_subset = stats['train']
        if ex_result['set'] == 'test':
            subset = test
            stats_subset = stats['test']
        subset[ex_id] = ex_result
        if ex_result['result'] == 'pass':
            stats_subset['passed'] += 1
        else:
            stats_subset['failed'] += 1

    for set_type in ['train', 'test']:
        total = float(stats[set_type]['passed'] + stats[set_type]['failed'])
        print("mcass: passed={} failed={} total={}".format(stats[set_type]['passed'], stats[set_type]['failed'], total))
        if total > 0.0:
            stats[set_type]['accuracy'] = float(stats[set_type]['passed']) / total
        else:
            stats[set_type]['accuracy'] = 0.0

    return stats


def parse_resultlog(resultlog_name):
    error, fhndl = file_open(resultlog_name, "r")

    rdata = {}
    setinfo = {'labels': [], 'results': {}}
    labels = setinfo['labels']
    rdata = setinfo['results']
    if not error and fhndl:
        flines = file_readlines(fhndl)
        for line in flines:
            parts = line.split()
            ex_id = parts[0]
            ex_set = parts[1]
            ex_result = parts[2]
            ex_label_expected = parts[3]
            ex_label_predicted = parts[4]
            rdata[ex_id] = {'set': ex_set, 'result': ex_result, 'expected': ex_label_expected, 'actual': ex_label_predicted}
            if ex_result == 'pass' and ex_label_expected not in labels:
                labels.append(ex_label_expected)
            if ex_result == 'pass' and ex_label_expected not in labels:
                labels.append(ex_label_expected)

        usrmsg(1, 1, 'loaded result: {}'.format(resultlog_name))

    return setinfo


def parse_perf_section(lines):
    perf_data = {'labels': {}, 'micro_precision': 0.0}
    label_counters_section = True
    label_perf_section = False
    for line in lines:
        if label_counters_section:
            if line != "":
                parts = line.split(' ')
                label = parts[0]
                counters = []
                for idx in xrange(2, len(parts)):
                    counters.append(int(parts[idx]))
                perf_data
            else:
                label_counters_section = False
            perf_data['labels'][label] = {}
            perf_data['labels'][label][counters] = counters


def parse_runlog(runlog_name):
    log_data = {'hyperparams': {},
                'training_perf': {}}
    error, fhndl = file_open(runlog_name, "r")

    if not error and fhndl:
        flines = file_readlines(fhndl)
        hyper_section = False
        training_perf_section = False
        line_buffer = []
        for line in flines:
            line = line.strip()
            if line == "hyper parameters":
                hyper_section = True
            elif line == "dataset truths: training":
                training_perf_section = True
            elif line == "dataset truths: test":
                training_perf_section = False
            elif hyper_section:
                m = re.search(r'param\ ([a-z]{2})\ :\ (.*)', line)
                if m:
                    log_data['hyperparams'][m.group(1)] = m.group(2)
                    print('found param {} = {}'.format(m.group(1), m.group(2)))
                else:
                    hyper_section = False
            elif training_perf_section:
                line_buffer.append(line)
        file_close(fhndl)
    return log_data


def print_final_result(runlog_name):
    error, fhndl = file_open(runlog_name, "r")

    if not error and fhndl:
        flines = file_readlines(fhndl)
        found = False
        last_line = ""
        for line in flines:
            if found or "Final result" in line:
                if not found:
                    usrmsg(0, 1, "******** {}".format(runlog_name))
                    usrmsg(0, 2, last_line)
                    found = True
                usrmsg(0, 2, line)
            else:
                last_line = line
        file_close(fhndl)


def do_commands(poptions):
    error = False
    log_path = poptions['log_path']

    if not dir_exists(log_path):
        usrmsg(0, 2, 'Error locating LOG_PATH: {}'.format(log_path))
        error = True

    if not error:
        for runid in poptions['log_ids']:
            runlog_name = "run.{}.log".format(runid)
            runresult_name = "run.{}.result".format(runid)
            if not dir_has_file(log_path, runlog_name):
                usrmsg(0, 2, 'Error locating run log: {}'.format(runlog_name))
                error = True
            if not dir_has_file(log_path, runresult_name):
                usrmsg(0, 2, 'Error locating run result: {}'.format(runresult_name))
                error = True
            if not error:
                parse_runlog(log_path + "/" + runlog_name)
                setinfo = parse_resultlog(log_path + "/" + runresult_name)
                stats = calc_runstats(setinfo)
                rates = calc_rates(setinfo)
                usrmsg(0, 2, 'train accuracy: {}'.format(stats['train']['accuracy']))
                usrmsg(0, 2, 'test accuracy : {}'.format(stats['test']['accuracy']))

    return error


def display_help():
    usrmsg(1, 1, 'runutil.py LOG_PATH LOG_ID_1, LOG_ID_2, .. LOG_ID_N')
    usrmsg(1, 2, 'Commands for run logs.')


def parse_args(poptions, args):
    error = ""
    poptions['log_path'] = args[0].rstrip('/')
    for idx in xrange(1, len(args)):
        runid = args[idx]
        if re.search(r'[^0-9]', runid):
            error = "non-numeric runid \"{}\"".format(runid)
            break
        else:
            poptions['log_ids'].append(int(runid))

    return error


def parse_options(poptions):
    close = False
    error = ""
    show_help = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ['help'])
    except getopt.GetoptError:
        error = 'invalid or missing argument. -h for show_help.'
        show_help = True
        close = True

    if not show_help:
        for opt, arg in opts:
            if opt == '-h' or opt == '--show_help':
                show_help = True
                close = True
                break

    if show_help is False:
        if len(args) == 0:
            error = 'missing log path and log id.'
            show_help = True
            close = True
        elif len(args) == 1:
            error = 'missing log path or log id.'
            show_help = True
            close = True
        else:
            error = parse_args(poptions, args)
            if error != "":
                show_help = True
                close = True

    if show_help:
        display_help()
    if error != "":
        usrmsg(2, 1, 'Error: {}'.format(error))

    return close


if __name__ == "__main__":
    ########################################
    # MAIN
    ########################################

    options = {
        'log_path': "",
        'log_ids': []}

    if not parse_options(options):
        startTime = datetime.now()

        do_commands(options)

        endTime = datetime.now()
        FMT = '%H:%M:%S'
        tdelta = endTime - startTime
        usrmsg(1, 1, 'Completed in : {}'.format(tdelta))
