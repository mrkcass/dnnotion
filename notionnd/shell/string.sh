#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: Bash script library functions for various string operations

#Name: is_int
#Type: linuxshell-library
#Args:
#   $1 - string that may be an integer.
#Return echo: "1" if the string is an integer. nothing otherwise
#Return val : 1 if the string is an integer. 0 otherwise
#Description:
# use bash bultin regex to check for string with only characters 0 - 9 or minus sign
is_int()
{
   local string="$1"
   local re='^-?[0-9]+$'
   if ! [[ $string =~ $re ]] ; then
      return 0
   fi
   echo "1"
   return 1
}

#Name: is_float
#Type: linuxshell-library
#Args:
#   $1 - string that may be a float.
#Return echo: "1" if the string is an float. nothing otherwise
#Return val : 1 if the string is a float. 0 otherwise
#Description:
# use bash bultin regex to check for string with only characters 0 - 9 , '.', or
# minus sign
is_float()
{
   local string="$1"
   local re='^-?[0-9]+([.][0-9]+)?$'
   if ! [[ $string =~ $re ]] ; then
      return 0
   fi
   echo "1"
   return 1
}


