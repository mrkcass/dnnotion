#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: Bash script library functions for searching string


#Name: fdiv
#Type: linuxshell-library
#Args:
#   $1 - floating point string quotient.
#   $1 - floating point string divisor.
#Return echo: string floating point number result. 0 on divide by zero
#Return val : 1 if divide by zero. 0 otherwise
#Description:
# use bash bultin regex to check for string with only characters 0 - 9 , '.', or
# minus sign
fdiv()
{
   local quotient="$1"
   local divisor="$2"

   local precision="4"

   if [[ $divisor == "0" ]]; then
      echo "scale=$precision; 0/1" | bc -l
      return 1
   else
      echo "scale=$precision; $quotient/$divisor" | bc -l
      return 0
   fi
}

math_fdiv()
{
   local quotient="$1"
   local divisor="$2"

   local precision="4"

   if [[ $divisor == "0" ]]; then
      echo "scale=$precision; 0/1" | bc -l
   else
      echo "scale=$precision; $quotient/$divisor" | bc -l
   fi
}

math_fmul()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   echo "scale=$precision; $term1 * $term2" | bc -l
}

math_fadd()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   echo "scale=$precision; $term1 + $term2" | bc -l
}

math_fsub()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   echo "scale=$precision; $term1 - $term2" | bc -l
}

math_fequal()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   if [[ $(echo "scale=$precision; $term1 == $term2" | bc -l) == "1" ]]; then
      echo "1"
      return 1
   fi
   return 0
}

math_fnotequal()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   if [[ $(echo "scale=$precision; $term1 != $term2" | bc -l) == "1" ]]; then
      echo "1"
      return 1
   fi
   return 0
}

math_fless()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   if [[ $(echo "scale=$precision; $term1 < $term2" | bc -l) == "1" ]]; then
      echo "1"
      return 1
   fi
   return 0
}

math_flessequal()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   if [[ $(echo "scale=$precision; $term1 <= $term2" | bc -l) == "1" ]]; then
      echo "1"
      return 1
   fi
   return 0
}

math_fgreater()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   if [[ $(echo "scale=$precision; $term1 > $term2" | bc -l) == "1" ]]; then
      echo "1"
      return 1
   fi
   return 0
}

math_fgreaterequal()
{
   local term1="$1"
   local term2="$2"

   local precision="4"
   if [[ $(echo "scale=$precision; $term1 >= $term2" | bc -l) == "1" ]]; then
      echo "1"
      return 1
   fi
   return 0
}
