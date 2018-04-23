#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: Bash script library functions for parsing file path strings

#Name: path_file
#Type: linuxshell-library
#Args:
#   $1 - string that may be an integer.
#Return echo: the file portion of a path/file string
#Return val : not used
#Description:
# return the filename part of a valid path with extension (if applicable)
path_file()
{
   local path="$1"
   basename $path
}

#Name: path_absolute
#Type: linuxshell-library
#Args:
#   $1 - string that may be an integer.
#Return echo: absolute path
#Return val : not used
#Description:
# convert a relative file path to an absolute file path.
path_absolute()
{
   local path="$1"
   readlink -f $path
}

path_parent_name()
{
   echo "$(basename $PWD)"
}

path_file_name()
{
   local path="$1"
   echo "$(basename $path)"
}

path_exists()
{
   local path="$1"
   if [[ -e "$path" ]]; then
      echo "1"
      return 1
   else
      return 0
   fi
}

path_dir_name()
{
   local path="$1"
   echo "$(dirname $path)"
}

path_new_dir()
{
   local new_dir_name="$1"

   if [[ $debug == "false" ]]; then
      mkdir -p $1
   else
      echo "created directory: $new_dir_name"
   fi
}

path_rm_dir()
{
   local rm_dir_name="$1"

   if [[ $debug == "false" ]]; then
      rm -rf $rm_dir_name
   else
      echo "removed directory: $rm_dir_name"
   fi
}

path_new_file()
{
   local file_name="$1"

   if [[ $debug == "false" ]]; then
      touch $file_name
   else
      echo "created file: $file_name"
   fi
}


