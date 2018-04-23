#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions and data types used to call user command scripts

USERCMDALIAS="command"

usercmd_handler()
{
   local projid="$1"; local op=$2; local commandid=$3; local cmd_args="$4"

   if [[ "$op" == "list" ]]; then
      usercmd_list $projid
   elif [[ "$op" == "run" ]]; then
      usercmd_run $projid $commandid "$cmd_args"
   elif [[ "$op" == "edit" ]]; then
      usercmd_edit $projid $commandid "$cmd_args"
   elif [[ "$op" == "delete" ]]; then
      usercmd_delete $projid $commandid "$cmd_args"
   elif [[ "$op" == "copy" ]]; then
      usercmd_copy $projid $commandid "$cmd_args"
   fi
}

usercmd_list()
{
   local projid="$1";

   local projdir="$(project_id_to_projectdir $projid)"
   local cmdfiles="$(ls "$projdir")"

  while read -r cmdfile; do
      if [[ $(has_regex "$cmdfile" 'command[0-9]+') ]]; then
         cmd_data="$(cat $projdir/$cmdfile)"
         description="$(find_words_nth_to_end "$(regexs "$cmd_data" "menu_description:")" 2)"
         cmd_idx="$(regexw $cmdfile "[0-9]+$")"
         echo "  ${cmd_idx}: $description"
      fi
   done <<< "$cmdfiles"
   echo " "
}

usercmd_run()
{
   local projid="$1"; local commandid=$2; local cmd_args="$3"

   local projdir="$(project_id_to_projectdir $projid)"
   local cmdfile="$projdir/$USERCMDALIAS$commandid"

   source $cmdfile
}

usercmd_edit()
{
   local projid="$1"; local commandid=$2; local cmd_args="$3"

   local projdir="$(project_id_to_projectdir $projid)"
   local cmdfile="$projdir/$USERCMDALIAS$commandid"

   export TERM="xterm-256color"
   notionnd/programs/micro $cmdfile
}

usercmd_copy()
{
   local projid="$1"; local commandid=$2; local cmd_args="$3"

   local cmdfile="$(project_cmd_path $projid)/$USERCMDALIAS$commandid"

   if [[ ! -e $cmdfile ]]; then
      echo "Error: project $projid does not have a command ->$commandid<-"
      exit 1
   fi

   local dest="$(project_cmd_path $cmd_args)"
   if [[ ! -e $dest ]]; then
      echo "Error: project $cmd_args does not exist"
      exit 1
   fi

   fileops_copy $cmdfile $dest
}

usercmd_delete()
{
   local projid="$1"; local commandid=$2; local cmd_args="$3"

   local cmdfile="$(project_cmd_path $projid)/$USERCMDALIAS$commandid"

   if [[ ! -e $cmdfile ]]; then
      echo "Error: project $projid does not have a command ->$commandid<-"
      exit 1
   fi

   fileops_remove $cmdfile
}