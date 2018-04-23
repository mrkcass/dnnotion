#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions to handle user common command operations

#returns the left hand side of x=y
cmdopts_has_option()
{
   local cmd_args="$1"; local find="$2"

   has_word "$cmd_args" "$find"
}

cmdopts_has_value()
{
   local cmd_args="$1"; local find="$2"

   has_word "$cmd_args" "${find}="
}

cmdopts_get_value()
{
   local cmd_args="$1"; local find="$2"

   regexw $(regexw "$(regexw "$cmd_args" $find'=[^\ ^$]+')" '=[^\ ^$]+') '[^=]+'
}