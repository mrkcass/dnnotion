#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: Bash script library functions for searching string

#Name: regexs
#Type: linuxshell-library
#Args:
#   $1 - search string to interogate.
#   $2 - regular expression search target.
#Return echo: the search string if found. empty string otherwise
#Return code: not used
#Description:
# use grep regular expression to search for a string within a string.
regexs()
{
   local string="$1"; local search_term="$2"

   echo "$string" | grep -E "$search_term"
}

finds()
{
   local string="$1"; local search_term="$2"

   #echo "$string" | grep -F "$search_term"
   #if [[ "$string" == *"$search_term"* ]]; then
   if [[ "$string" =~ "$search_term" ]]; then
      echo "$search_term"
   fi
}

findl()
{
   local string="$1"; local search_term="$2"

   echo "$string" | grep -F "$search_term"
   #if [[ "$string" == *"$search_term"* ]]; then
   #if [[ "$string" =~ "$search_term" ]]; then
   #   echo "$string"
   #fi
}

findlx()
{
   local string="$1"; local search_term="$2"; local before=$3; local after=$4

   local args=""
   if [[ "$before" != 0 ]]; then
      args+="-B $before"
   fi

   if [[ "$after" != 0 ]]; then
      args+=" -A $after"
   fi

   echo "$string" | grep $args -F "$search_term"
   #if [[ "$string" == *"$search_term"* ]]; then
   #if [[ "$string" =~ "$search_term" ]]; then
   #   echo "$string"
   #fi
}

#Name: regexw
#Type: linuxshell-library
#Args:
#   $1 - search string to interogate.
#   $2 - regular expresssion search target.
#Return echo: string matched by target. empty string otherwise
#Return code: not used
#Description:
# use grep regular expression to search for string within a string. this is used
# to return easily evaluable result that does not require an explicit compare.
regexw()
{
   local string="$1"; local search_term="$2"

   grep -oE "$search_term" <<< "$string"
}

findw()
{
   local string="$1"; local search_term="$2"

   echo "$string" | grep -oF "$search_term"
}

#Name: regexl
#Type: linuxshell-library
#Args:
#   $1 - search string to interogate.
#   $2 - regular expression search target.
#   $3 - if match found also return this number of lines before the match.
#   $4 - if match found also return this number of lines after the match.
#Return echo: the search string if found. empty string otherwise
#Return code: not used
#Description:
# use grep to search and return a specified number of lines above and below the match.
regexl()
{
   local string="$1"; local search_term="$2"; local before=$3; local after=$4

   local args=""
   if [[ "$before" != 0 ]]; then
      args+="-B $before"
   fi

   if [[ "$after" != 0 ]]; then
      args+=" -A $after"
   fi

   grep $args -E "$search_term"  <<< "$string"
}

#Name: has_regex
#Type: linuxshell-library
#Args:
#   $1 - search string to interogate.
#   $2 - regular expression search target.
#Return echo: "1" if the search string is found. nothing otherwise
#Return code: 1 if the target is found. 0 otherwise
#Description:
# use grep regular expression to search for string within a string. this is used
# to return and echo a result that can be evaluated without a string compare.
# for example if [[ $(regexb "source" "target") ]]; then; ....
has_regex()
{
   local string="$1"; local search_term="$2"

   if [[ "$(regexs "$string" "$search_term")" ]]; then
      echo "1"
      return 1
   fi
   return 0
}

has_word()
{
   local string="$1"; local search_term="$2"

   if [[ "$(finds "$string" "$search_term")" ]]; then
      echo "1"
      return 1
   fi
   return 0
}

find_anyword()
{
   local string="$1"; local search_terms="$2"

   local terms_regex="$(tr ' ' '|' <<< "$search_terms")"
   terms_regex='('${terms_regex}')'
   if [[ "$(has_regex "$string" "$terms_regex")" ]]; then
      echo "1"
      return 1
   fi
   return 0
}


#Name: find_subst
#Type: linuxshell-library
#Args:
#   $1 - string that may be an integer.
#Return echo: orig string with 'new' substituted for all
#  occurences of 'pattern.'
#Return code : not used
#Description:
# use sed to find_subst a string within s string with a string.
find_subst()
{
   local pattern="$1"; local new="$2"; local string="$3"

   if [[ "$pattern" ]]; then
      sed -re 's/'"$pattern"'/'"$new"'/' <<< "$string"
   fi
}

#Name: find_nth_word
#Type: linuxshell-library
#Args:
#   $1 - string to search.
#   $2 - integer. the index of the target word. index 0 = word 0
#Return echo: the word in $1 that is at index  $2
#Return code : not used
#Description:
# awk wrapper to return the word
find_nth_word()
{
   local string="$1"; local nth="$2";
   awk -v column=$nth '{print $column}' <<< "$string"
}

find_first_word()
{
   local string="$1"
   awk '{print $1}' <<< "$string"
}

find_last_word()
{
   local string="$1"
   awk '{print $NF}' <<< "$string"
}

find_word_nth_from_last()
{
   local string="$1"; local nth="$2";
   awk -v fromend=$nth '{if (NF>fromend) {i=NF-fromend; print $i}}' <<< "$string"
}

#Name: find_words_nth_to_end
#Type: linuxshell-library
#Args:
#   $1 - string to search.
#   $2 - integer. the index of the target word. index 0 = word 0
#Return echo: the word in $1 that is at index  $2
#Return code : not used
#Description:
# awk wrapper to return all words starting with the nth word
find_words_nth_to_end()
{
   local string="$1"; local nth="$2";
   awk -v firstcolumn=$nth '{for(i=firstcolumn; i<=NF; i++) {i==NF?j="":j=" "; printf "%s%s",$i,j} printf "\n" }'  <<< "$string"
}

find_words_all_but_last()
{
   local string="$1"
   awk '{for(i=1; i<NF; i++) printf "%s ",$i }'  <<< "$string"
}

find_words_atmostn_fromend()
{
   local string="$1"; local n="$2";
   awk -v fromend=$n '{for(i=NF-fromend; i<=NF; i++) printf "%s ",$i; printf "\n" }'  <<< "$string"
}

find_words_begin_to_n()
{
   local string="$1"; local n="$2";
   awk -v frombegin=$n '{for(i=1; i<=frombegin; i++) printf "%s ",$i; printf "\n" }'  <<< "$string"
}

find_words_begin_to_nfromend()
{
   local string="$1"; local n="$2";
   awk -v fromend=$n '{for(i=1; i<=NF-fromend; i++) {i==(NF-fromend)?j="":j=" "; printf "%s%s",$i,j} printf "\n" }'  <<< "$string"
}

find_first_n_lines()
{
   local string="$1"; local n="$2";
   head -n $n <<< "$string"
}

find_last_n_lines()
{
   local string="$1"; local n="$2";
   tail -n $n <<< "$string"
}

find_alllines_startingwith_line()
{
   local string="$1"; local first_line_num="$2";
   tail -n "+"$first_line_num <<< "$string"
}

find_num_lines()
{
   local string="$1";
   wc -l <<< "$string"
}

find_num_words()
{
   local string="$1";
   wc -w <<< "$string"
}

find_num_words_like()
{
   local string="$1"; local term="$2"
   local all_terms="$(regexw "$string" "$term")"
   wc -w <<< "$all_terms"
}

find_between()
{
   local string="$1"; local term1="$2"; local term2="$3"

   sed -n "/$(echo -e "$term1")/, /$(echo -e "$term2")/ p" <<< "$string"
}

find_subst_between()
{
   local string="$1"; local begin="$2"; local end="$3"; local new="$4"
   local lhs="$(find_between "$string" "$begin" "$end")"
   echo "${string/"$lhs"/"$new"}"
}