#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: associative array functions

function dict_test_serialize()
{
   local -A dict=([key1]="value1" [key2]="value2")
   declare -p dict
}

function dict_test_deserialize()
{
   local dict="$1"

   eval "$(dict_local testdict "$dict")"

   declare -p testdict
}

function dict_name()
{
   local dict="$1"

   local name="$(regexw "$dict" '\-A [0-9a-zA-Z_]+')"
   name="$(regexw "$name" '[0-9A-Za-z_]+$')"
   regexw "$name" '[0-9A-Za-z_]+'
}

function dict_elements()
{
   local dict="$1"
   regexw  "$dict" "[\[][^\)]*"
}

function dict_declare()
{
   local name="$1"; local dict_elements="$2"

   echo "declare -A ${name}=("
   local formed="$(find_subst ' \[([a-zA-Z0-9]{2}\]=)' '\n   \[\1' "$dict_elements")"
   find_subst '^\[' '   \[' "$formed"
   echo ")"
}

function dict_format()
{
   local dict="$1"

   local formed="$(find_subst '\[([a-zA-Z0-9]{2}\]=)' '\n   \[\1' "$dict")"
   formed="$(find_subst '^\[' '   \[' "$formed")"
   formed="$(find_subst '=.\(' '=\(' "$formed")"
   find_subst "\).\$" '\n\)' "$formed"
}

function dict_local()
{
   local name="$1"; local dict="$2"

   find_subst 'declare -A ([A-Za-z0-9_]+)' "local -A $name" "$dict"

}