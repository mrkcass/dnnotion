#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions to handle file operations

fileops_import()
{
   local projfile="$2"; local fname_src="$1"

   fileops_concat $projfile $fname_src
}

fileops_concat()
{
   local dest_fname="$2"; local src_fname="$1"

   cat $src_fname >> $dest_fname
}

fileops_copy()
{
   local src_fname="$1"; local dest_fname="$2"
   cp -f $src_fname $dest_fname
}

fileops_remove()
{
   local fname="$1"
   rm -f $fname
}

fileops_fname_append()
{
   local fname="$1"; local append="$2"

   local ext="$(regexw "$fname" '\.[A-Za-z_0-9]+$')"

   find_subst "$ext" "$append$ext" "$fname"
}

fileops_first_n_lines()
{
   local filename="$1"; local n="$2";
   head -n $n "$filename"
}

fileops_last_n_lines()
{
   local filename="$1"; local n="$2";
   tail -n $n "$filename"
}