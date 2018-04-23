#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions for processing training stats output

epochdata_best_epoch()
{
   local metric=$1; local epoch_data="$2"

   local epochids="$(epochdata_get_epoch_ids "$epoch_data")"
   local epoch=""
   local best_epoch=""

  while read -r eid; do
      epoch="$(epochdata_get_epoch $eid "$epoch_data")"
      if [[ "$best_epoch" == "" ]]; then
         best_epoch="$epoch"
      else
         result="$(epochdata_compare_epochs $metric "$epoch" "$best_epoch")"
         if [[ $result != "" ]]; then
            best_epoch="$epoch"
         fi
      fi
   done <<< "$epochids"

   echo "$best_epoch"
}

epochdata_filter_on_metric()
{
   local metric=$1; local epoch_data="$2"

   local epochids="$(epochdata_get_epoch_ids "$epoch_data")"
   local epoch=""
   local metric_val=""

  while read -r eid; do
      epoch="$(epochdata_get_epoch $eid "$epoch_data")"
      metric_val="$(epochdata_get_metric $metric "$epoch")"
      if [[ $(epochdata_metric_evaluate $metric $metric_val ) ]]; then
         metric_result="$(epochdata_metric_set "$metric" "$metric_val")"
         epoch="$(epochdata_header_append "$epoch" "$metric_result")"
      fi
   done <<< "$epochids"
}

epochdata_get_epoch()
{
   local epoch_id=$1; local epoch_data="$2"

   echo "$(echo "$epoch_data" | grep -A 13 -E "epoch $epoch_id")"
}

epochdata_get_epoch_ids()
{
   local epoch_data="$1"
   echo "$(echo "$epoch_data" | grep -E "epoch" | grep -oE "[0-9]+")"
   regexw "$(regexw "$(regexs "$epoch_data" '[-]{3,}')" "run\.[0-9]+\.log")" '[0-9]+'
}

epochdata_get_epoch_runfiles()
{
   local epoch_data="$1"
   regexw "$(regexs "$epoch_data" '[-]{3,}')" "run\.[0-9]+\.log"
}

epochdata_to_runfile()
{
   local projid="$1"; local epochdata="$2"

   local epochfnames="$(epochdata_get_epoch_runfiles "$epochdata")"
   local basepath=$(project_id_to_pastlogdir $projid)

  while read -r fname; do
      echo "$basepath/$fname"
   done <<< "$epochfnames"
}

epochdata_to_hparams()
{
   local projid="$1"; local epochdata="$2"

   local epochfnames="$(epochdata_to_runfile $projid "$epochdata")"

  while read -r fname; do
      runlogdata="$(cat $fname)"
      regexw "$runlogdata" "param .*"
   done <<< "$epochfnames"
}

epochdata_compare_epochs()
{
   local metric="$1"; local epoch_a="$2"; local epoch_b="$3"
   local val_a="$(epochdata_get_metric $metric "$epoch_a")"
   local val_b="$(epochdata_get_metric $metric "$epoch_b")"

   local ret_val=0
   local result=""

   result="$(epochdata_metric_compare $metric $val_a $val_b)"
   ret_val=$?

   if [[ $result != "" ]]; then
      echo "$result"
   fi
   return $ret_val
}

epochdata_metric_compare()
{
   local metric="$1"; local val_a="$2"; local val_b="$3"

   if [[ "$val_a" == "" || $val_b == "" ]]; then
      return 0
   elif [[ ! $(is_float $val_a) || ! $(is_float $val_b) ]]; then
      return 0
   elif [[ ${metric:1:1} == "G" && $(math_fgreater $val_a $val_b) ]]; then
      echo "$val_a"
      return 1
   elif [[ ${metric:1:1} == "L" && $(math_fless $val_a $val_b) ]]; then
      echo "$val_a"
      return 1
   else
      return 0
   fi
}

epochdata_get_metric()
{
   local metric=$1; local epochdata="$2"

   local metric_value=""
   if [[ ${metric:0:1} == '?' ]]; then
      epochdata_get_conditional_metric "$metric" "$epochdata"
   elif [[ ${metric:0:1} == 'V' ]]; then
      local -A indexes=(["OK"]=6 ["TPR"]=11 ["FPR"]=13 ["TNR"]=11 ["FNR"]=13 ["PPV"]=11 ["NPV"]=13 ["SPEC"]=11 ["SENS"]=13 ["PREC"]=11 ["RECA"]=13 ["F1"]=11 ["ACC"]=13)
   elif [[ ${metric:0:1} == 'T' ]]; then
      local -A indexes=(["OK"]=6 ["TPR"]=4 ["FPR"]=6 ["TNR"]=4 ["FNR"]=6 ["PPV"]=4 ["NPV"]=6 ["SPEC"]=4 ["SENS"]=6 ["PREC"]=4 ["RECA"]=6 ["F1"]=4 ["ACC"]=6)
   else
      echo "$epochdata" > /dev/tty
      echo " " . /dev/tty
      echo "Error unknown metric set code: ${metric:0:1} in $metric" > /dev/tty
      echo " " > /dev/tty
      exit 1
   fi

   local metricid=$(regexw $metric '^[0-9A-Z]+')
   metricid=${metricid:2}
   local index=${indexes[$metricid]}

   metric_value="$(find_nth_word "$(regexs "$epochdata" " $metricid")" $index)"

   echo "$metric_value"
}

epochdata_get_conditional_metric()
{
   local metric=$1; local epochdata="$2"

   # "??VLOKE=LOCKED?&??VACCG=.5?|TACCG=.95@@IVACC,VF1!!0.0"
   # if (VLOK = LOCKED and (VACC > .5 or TACC > .95))
   # then minimum VACC, VF1
   # else 0.0


   local cond="$(regexw "$metric" "[?]{2}.*[@]{2}")"
   local pred="$(regexw "$metric" "[@]{2}.*$")"
   local metric_value=""


   echo "$metric_value"
}

epochdata_get_set_metric()
{
   local metric=$1; local epochdata="$2"

   # minimum of validation acc and f1
   # "IVACC,VF1"
   # maximum of training acc and f1
   # "TACC,TF1"

   local cond="$(regexw "$metric" "[?]{2}.*[@]{2}")"
   local pred="$(regexw "$metric" "[@]{2}.*$")"
   local metric_value=""


   echo "$metric_value"
}

epochdata_metric_evaluate()
{
   local metric="$1"; local metric_value=$2

   if [[ "$metric_value" == "" ]]; then
      return 0
   elif [[ ! $(is_float $metric_value) ]]; then
      return 0
   elif [[ $(has_regex $metric '=') ]]; then
      local limit=$(regexw $metric '=[.0-9]+')
      limit=${limit:1}
      if [[ ${metric:1:1} == "L" && $(math_flessequal $metric_value $limit) ]]; then
         echo "1"
         return 1
      elif [[ ${metric:1:1} == "G" && $(math_fgreaterequal $metric_value $limit) ]]; then
         echo "1"
         return 1
      fi
   else
      echo "1"
      return 1
   fi
   return 0
}

epochdata_header_append()
{
   local epochdata="$1"; local addstring="$2"

   find_subst '[\ \t]+(epoch [0-9]+[^\-]{2,})[\-]{1,}' " \\1$addstring ---" "$epochdata"
}

epochdata_metric_set()
{
   local metric="$1"; local value="$2"

   find_subst '([^=]+)=[a-zA-Z_0-9\.]+' '\1'"=$value" "$metric"
}