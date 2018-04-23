#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: parse command line options

parse_options()
{
   while (( "$#" )); do
      if [[ "$1" == "--help" || "$1" == "-h" ]]; then
         echo "$HELP_TEXT"
         exit 0
      elif [[ "$1" == "--dryrun" || "$1" == "-y" ]]; then
         debug="true"
      elif [[ "$1" == "--train" || "$1" == "-t" ]]; then
         command="train"
         command_proj="$2"
         command_arg="$3 $4"
         command_options="${@:5}"
      elif [[ "$1" == "--runs" || "$1" == "-r" ]]; then
         menu_options="${@:6}"
         show_top_epoch $2 $3 $4 $5 "$menu_options"
         exit 0
      elif [[ "$1" == "--documents" || "$1" == "-d" ]]; then
         menu_options="${@:4}"
         doccmd_main $2 $3 "$menu_options"
         exit 0
      elif [[ "$1" == "--words" || "$1" == "-w" ]]; then
         menu_options="${@:6}"
         wordcmd_main $2 $3 $4 $5 "$menu_options"
         exit 0
      elif [[ "$1" == "--command" || "$1" == "-c" ]]; then
         menu_options="${@:5}"
         usercmd_handler $2 $3 $4 "$menu_options"
         exit 0
      elif [[ "$1" == "--project" || "$1" == "-p" ]]; then
         menu_options="${@:4}"
         project_command $2 $3 "$menu_options"
         exit 0
      elif [[ "$1" == "--logs" || "$1" == "-l" ]]; then
         menu_options="${@:4}"
         logs_main $2 $3 "$menu_options"
         exit 0
         # elif [[ "$1" == "--documents" || "$1" == "-d" ]]; then
         #    menu_options="${@:5}"
         #    print_log $2 $3 $4 "$menu_options"
         #    exit 0
      elif [[ "$1" == "--upload" || "$1" == "-u" ]]; then
         upload
         exit 0
      elif [[ "$1" == "--archive" || "$1" == "-a" ]]; then
         archive_source
         exit 0
      elif [[ "$command" == "" ]]; then
         echo "unknown command: $1"
         exit 1
      fi
      shift
   done
}