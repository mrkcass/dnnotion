#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: load the dnnotion api


#Name: load_libraries
#Type: linuxshell-library
#Args:
#   $1 - string that may be an integer.
#Return echo: the file portion of a path/file string
#Return val : not used
#Description:
# return the filename part of a valid path with extension (if applicable)
load_libraries()
{
   local path="$1"

   source "$path/shell/main.sh"
   source "$path/shell/menu.sh"
   source "$path/shell/help.sh"


   source "$path/shell/dictionary.sh"
   source "$path/shell/math.sh"
   source "$path/shell/path.sh"
   source "$path/shell/string.sh"
   source "$path/shell/find.sh"
   source "$path/shell/fileops.sh"


   source "$path/shell/project.sh"
   source "$path/shell/hparamdata.sh"
   source "$path/shell/epochdata.sh"
   source "$path/shell/log.sh"
   source "$path/shell/archive.sh"
   source "$path/shell/ranges.sh"
   source "$path/shell/model.sh"
   source "$path/shell/train.sh"
   source "$path/shell/usercommand.sh"
   source "$path/shell/cmdopts.sh"
}

load_libraries $notionnd_path

