#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: help text strings and functions

HELP_TEXT="
NAME
   dnnotion

SYNOPSIS
   dnnotion [FLAGS] [COMMAND] [OPTIONS]]

DESCRIPTION
   dnnotion is the frontend for a neural network framework. The framework is
   geared to natural language processing and includes a total of six models of
   which 3 a convolution models and 3 are recurrent models.

FLAGS
  -h,--help
       show this screen.
  -y,--dryrun
       print commands only. do not run them

COMMANDS
  -t,--train PROJID MODE MODEL [OPTIONS]
   Train a project model.
   PROJID - project path or id.
   MODEL - specific model.
   MODE [loop,sweep,random] - training execution method.
   * fixed [ITERATIONS] - train model with fixed hyper parameters for [NUMLOOPS]
   iterations.
   * ordered [restart] - train the model by trying all hyper parameters within
   a set range of predefined values. adding restart will clear the cached list
   of previous session parameters and restart the sweep. without restart
   any previously attempted parameters sets will be skipped.
   * random RANDOMMODE - train the model by randomly trying hyper parameters
   drawn from a pool or range of values.
    RANDOMMODE
    * restart - will clear the cached list of previous session parameters and
    restart the sweep. without restart any previously attempted parameters
    sets will be skipped.
    * ignoreN - ignore the sweep history and sweep for N iterations.
  -a,--archive
   from the parent directory, save source files to tar ball
  -c,--command PROJID OPERATION COMMANDID ARGS
   run a command saved in a project directory
   OPERATION
   * list - show all commands for a project
   * run - run a project command
   * edit - start default text editor and load command source code.
   * copy PROJID - copy project command
   * delete PROJID - delete project command
   COMMANDID - command number as listed when running with 'list' option.
   ARGS - values to pass to command at invocation.
  -u,--upload
   upload latest archive to dnnotion.com
  -r,--runs PROJID SOURCE JOBID METRIC [A,D] [all topN]
   Display and filter run results for a sweep or run using standard metrics.
   SOURCE
   * sweep - JOBID is a sweep. (default)
   * run - JOBID is a run.
   * pipe - read epoch data from stdin
   [A,D] - Result sort order. A scending   D scending. default = D
   [all topN] - number of epochs to display. default = top10
   JOBID - the id of a sweep or a run.
   METRIC - [T,V][F1,ACC,OK,TPR,TNR,FPR,FNR] [G,L]
   * [T,V] - T raining  V alidation
   * [ACC,etc] - metric as displayed during training.
   * [G,L]=VALUE - G reater equal  L ess equal.
  -d,--documents PROJID JOBID FILTER
   Display log data.
   JOBID the id of a run with valid result log..
   FILTER - (A,T,V) (T,F)
   * [A,T,V] - A ll  T raining  V alidation
   * [T,F]=LABEL - T rue predictions. F alse predictions.
     * LABEL - label as displayed in run log or a double letter index (AA,BB,..)
     indicating the alphabetically indexed offset from the first indexed label.
  -w,--words PROJID SOURCE JOBID FILTER [FILTER_OPTIONS]
   print the stats for all examples containing KEY
   SOURCE
    * sweep - stats for all runs in a sweep
    * run -  stats for a specific run
   JOBID sweep or run log id
   FILTER include matching words. grep style extended regular expression.
   OPTIONS
   * result - print the result entry for each matching key.
  -p,--project PROJID OPERATION [OPTIONS]
   Project management commands.
   OPERATION
   * new - Create a new project.
   Directories are created in: projects, logs, and trained. the project name
   is derived by concatenating the parent directory name with PROJID
   * delete - Remove all directories and files related to project PROJID.
   * add MODEL RESOURCE
     MODEL - keyword associated with a model type
     RESOURCE
     * hparams - add model hyperparameters to project
     * ranges RANGETYPE - add model hyperparameters training ranges
     to project configuration
     RANGETYPE
     * random - model random ranges
     * sweep - model sweep ranges
   * copy RESOURCE [MODEL] PROJID - copy all or part of a project to another
     RESOURCE
     * hparams - project hyper parameters
     * ranges - project training ranges
     * all - all files in project directory
     MODEL - model to copy
     PROJID - destination project id
   * edit RESOURCE - start an console editor and load RESOURCE for editting
     RESOURCE
     * config - edit project configuration file
     * cmd COMMANDID - edit project command COMMANDID file
  -l,--logs PROJID OPERATION [OPERATION_OPTIONS]
   Display available log files and or contents.
   OPERATION
   * ls LOGTYPE [LENGTH] - list file names and details
     LENGTH - length of listing assuming one file per line
     * all - all entries
     * lastN - last N (an integer) entries
     * beforeN - include N (an integer) before
     * afterN - include N (an integer) after
   * cat LOGTYPE JOBID - display file contents
   LOGTYPE
   * sweep
   * run
   * result
 "