#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions for archiving source code to private url

archive_source()
{
    local name="dnnotion-$(date +%Y-%m-%d-%H_%M)-$HOSTNAME.tar"
    find . -type d | tar --no-recursion -cf $name -T -
    find . -path "./notionnd/programs/*"            \
           -o -name "*.py"                          \
           -o -name "*.sh"                          \
           -o -name "*.go"                          \
           -o -name "dnnotion"                      \
           -o -name "*.cc"                          \
           -o -name "questions-words.txt"           \
           -o -name "configuration"                 \
           -o -name "command*"                      \
           | tar --append -f $name -T -

    gzip $name
    name+=".gz"
    mv $name $archive_dir
    echo " "
    echo "   Created Archive: $name"
    echo " "
}

update_source()
{
   local path="$1"
   local limiter="$2"

   if [[ "$limiter" == "" ]]; then
      limiter="all"
   fi

   if [[ $(is_int "$path") ]]; then
      local subdir="$(path_last $PWD)"
      local index="$(regexw $subdir "[0-9]+$")"
      if [[ ! $index ]]; then
         if [[ "$path" == "1" ]]; then
            path=$subdir
         else
            path=$subdir$path
         fi
      else
         if [[ "$path" == "1" ]]; then
            path="$(find_subst $subdir $index '')"
         else
            path="$(find_subst $subdir $index $path)"
         fi
      fi
   fi

   if [[ ! $(has_regex "$path" "^../") ]]; then
      path="../$path"
   fi

   if [[ $(path_absolute $path) == $PWD ]]; then
      echo "Illegal overwrite falied: $path -> $path"
      exit 1
   fi

   if [[ "$limiter" != "" && "$limiter" != "all" ]]; then
      for lim in $limiter; do
         if [[ "$lim" == "dnnotion" ]]; then
            cp -fv $path/dnnotion .
         else
            if [[ ! -e $lim ]]; then
               mkdir $lim
            fi
            cp -rfv $path/$lim/*.py ./$lim
         fi
      done
   elif [[ "$path" != "" ]]; then
      cp -rfv $path/*.py .
      if [[ ! -e hparams ]]; then
         mkdir hparams
      fi
      cp -rfv $path/hparams/*.py ./hparams
      if [[ ! -e layers ]]; then
         mkdir layers
      fi
      cp -rfv $path/layers/*.py ./layers
      if [[ ! -e models ]]; then
         mkdir models
      fi
      cp -rfv $path/models/*.py ./models
      if [[ "$limiter" == "all" ]]; then
         cp -fv $path/dnnotion .
      fi
   fi
}

upload()
{
   local home_url="mcass@research.dnnotion.com:neuralnets/dnnotion_nlpclassifier/archive"

   local file="$(ls -lt $archive_dir/dnnotion*.tar.gz | head -n 1 | awk '{print $NF}')"
   if [[ "$file" ]]; then
      scp -P 5167 $file $home_url
   fi
}