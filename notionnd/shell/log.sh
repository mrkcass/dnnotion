#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: Functions and data types for logs and various log data

sweeplog_id_to_filename()
{
   local projid="$1"; local logid="$2"

   local projlogs="$(project_id_to_pastlogdir $projid)"
   echo "$projlogs/run.$logid.sweep"
}

runlog_id_to_filename()
{
   local projid="$1"; local logid="$2"

   local projlogs="$(project_id_to_pastlogdir $projid)"
   echo "$projlogs/run.$logid.log"
}

resultlog_id_to_filename()
{
   local projid="$1"; local logid="$2"

   local projlogs="$(project_id_to_pastlogdir $projid)"
   echo "$projlogs/run.$logid.result"
}

new_sweep_id()
{
   local projid=$1
   bnum=$(ls -l $(project_id_to_pastlogdir $projid) | awk {'print $9'} | tail -n 1 | grep -oE '[1-9][0-9]+')
   bnum=$((bnum+1))
   echo $bnum
}

logs_main()
{
   local projid="$1"; local logop="$2"; local options="$3";

   if [[ "$logop" == "ls" ]]; then
      print_files $projid "$options"
   elif [[ "$logop" == "cat" ]]; then
      print_log $projid "$options"
   fi
}

print_log()
{
   local projid="$1"; local options="$2";

   local idtype="$(find_nth_word "$options" 1)"
   local logid="$(find_nth_word "$options" 2)"

   if [[ ! $(find_anyword "$idtype" "run sweep result") ]]; then
      echo "Error unknown LOGTYPE: $idtype"
      exit 1
   fi

   if [[ ! $(is_int $logid) ]]; then
      echo "Error illegal LOGID: $logid"
      exit 1
   fi

   if [[ "$idtype" == "sweep" ]]; then
      logdata="$(get_sweeplog_data $projid $logid)"
   elif [[ "$idtype" == "result" ]]; then
      logdata="$(get_resultlog_data $projid $logid)"
   else
      logdata="$(get_runlog_data $projid $logid)"
   fi

   echo "$logdata"
}

print_files()
{
   local projid="$1"; local options="$2"

   local logtype="$(find_nth_word "$options" 1)"
   local quantity="$(find_nth_word "$options" 2)"

   if [[ ! $(find_anyword "$logtype" "run sweep result") ]]; then
      echo "Error unknown LOGTYPE: $logtype"
      exit 1
   fi

   local projlogs="$(project_id_to_pastlogdir $projid)"

   if [[ $logtype == "sweep" ]]; then
      full_list="$(ls -haltr $projlogs/*.sweep)"
   elif [[ $logtype == "result" ]]; then
      full_list="$(ls -haltr $projlogs/*.result)"
   else
      full_list="$(ls -haltr $projlogs/*.log)"
   fi

   full_list="$(echo "$full_list" | awk '{print $NF,"   ",$6,$7,$8}')"
   if [[ $(has_regex "$quantity" '(^| )last') ]]; then
      local max_out=$(regexw $(regexw "$quantity" "last[0-9]+") "[0-9]+")
      filelist="$(echo "$full_list" | tail -n $max_out)"
   else
      filelist="$full_list"
   fi

   echo "$filelist"
}

show_top_epoch()
{
   local projid=$1; local logidtype=$2; local logid=$3; local metric=$4; local options="$5"

   local epochdata_hdr=""
   local runfile=""
   local epochdata=""
   local -A best=()
   local best_list=""
   local best_list_len=0

   local runbest_epochdata=""

   if [[ $logidtype == "sweep" ]]; then
      runbest_epochdata="$(sweeplog_get_runbest_epochdata $projid $logid $metric)"
   elif [[ $logidtype == "pipe" ]]; then
      runbest_epochdata="$(cat /dev/stdin)"
      options="$metric $options"
      metric=$logid
   elif [[ $logidtype == "run" ]]; then
      runbest_epochdata="$(runlog_get_epochdata $projid $logid)"
   fi
   local runbest_epochdata_hdrs=$(regexs "$runbest_epochdata" "run\.[0-9]{4}\.log[\ ]+epoch[\ ]+[0-9]+")

  while read -r epochdata_hdr; do
      epochdata="$(regexl "$runbest_epochdata" "$epochdata_hdr" 0 13)"
      run_metric_val="$(epochdata_get_metric $metric "$epochdata")"
      if [[ $(epochdata_metric_evaluate $metric $run_metric_val) ]]; then
         runkey="x_$best_list_len"
         best[$runkey]="$epochdata"
         best_list+="x_"$best_list_len"_"$run_metric_val$'\n'
         best_list_len=$(($best_list_len+1))
      fi
   done <<< "$runbest_epochdata_hdrs"

   local order="r"
   if [[ $(has_regex "$options" '(^| )A( |$)') ]]; then
      order=""
   fi
   best_list="$(echo "$best_list" | sort -g$order -t '_' -k 3)"

   local num_out=0
   local max_out=1000000

   if [[ $(has_regex "$options" '(^| )top') ]]; then
      max_out=$(regexw $(regexw "$options" "top[0-9]+") "[0-9]+")
   fi

  while read -r best_line; do
      best_key="$(regexw "$best_line" "x_[0-9]+")"
      if [[ $(has_regex "$best_key" "[0-9]+") ]]; then
         if [[ $(has_regex "$options" 'hparams') ]]; then
            epochdata_to_hparams $projid "${best[$best_key]}"
         elif [[ $(has_regex "$options" 'files') ]]; then
            epochdata_to_runfile $projid "${best[$best_key]}"
         else
            echo "${best[$best_key]}"
         fi
         num_out=$(($num_out+1))
         if ((num_out >= max_out)); then
            break
         fi
      fi
   done <<< "$best_list"
}


sweephdr_to_runid()
{
   local header="$1"

   find_nth_word "$header" 8
}


sweeplog_get_sweephdrs()
{
   local projid=$1; local logid=$2

   local sweep_log=$(sweeplog_id_to_filename $projid $logid)
   cat $sweep_log | grep "TRAINID:"
}

sweeplog_get_runlog_ids()
{
   local projid=$1; local sweepid=$2

   local sweep_hdrs="$(sweeplog_get_sweephdrs $projid $sweepid)"

  while read -r header; do
      sweephdr_to_runid "$header"
   done <<< "$sweep_hdrs"
}

sweeplog_get_runlogs()
{
   local projid=$1; local sweepid=$2

   local run_ids="$(sweeplog_get_runlog_ids $projid $sweepid)"

   local runid=""

  while read -r runid; do
      runlog_id_to_filename $projid $runid
   done <<< "$run_ids"
}

sweeplog_get_resultlogs()
{
   local projid=$1; local sweepid=$2

   local run_ids="$(sweeplog_get_runlog_ids $projid $sweepid)"

   local runid=""

  while read -r runid; do
      resultlog_id_to_filename $projid $runid
   done <<< "$run_ids"
}

sweeplog_get_runbest_epochdata()
{
   local projid=$1; local logid=$2; local metric=$3;

   local run_ids="$(sweeplog_get_runlog_ids $projid $logid)"
   local epochdata=""
   local last=""

   while read -r runid; do
      if [[ "$runid" == "$last" ]]; then
         continue
      fi
      epochdata="$(runlog_get_epochdata $projid $runid)"
      best_in_run="$(epochdata_best_epoch $metric "$epochdata")"
      echo "$best_in_run"
      last="$runid"
   done <<< "$run_ids"
}

doccmd_main()
{
   local projid=$1; local logid=$2; local options=$3;

   local filter="$(find_nth_word "$options" 1)"
   local result_set=${filter:0:1}
   local result_type=${filter:1:1}

   local runlog="$(get_runlog_data $projid $logid)"
   local hparams="$(runlogdata_get_hparamdata "$runlog")"
   local dataset="$(hparamdata_get_value "ds" "$hparams")"
   local max_len="$(hparamdata_get_value "dx" "$hparams")"
   local resultlog="$(get_resultlog_data $projid $logid)"

   if [[ $result_set == "V" ]]; then
      resultlog="$(echo "$resultlog" | grep -F "test")"
   elif [[ $result_set == "T" ]]; then
      resultlog="$(echo "$resultlog" | grep -F "train")"
   fi
   if [[ $result_type == "T" ]]; then
      resultlog="$(echo "$resultlog" | grep -F "pass")"
   elif [[ $result_type == "F" ]]; then
      resultlog="$(echo "$resultlog" | grep -F "fail")"
   fi

   while read -r line; do
      ex_id="$(echo "$line" | awk "{print \$1}")"
      echo "--------------------------------------------------------------------"
      echo "$(grep -m 1 -F "$ex_id" $dataset | cut -d' ' -f 1-$max_len)"
   done <<< "$resultlog"
}

output_header()
{
   local sweep_log=$1; local sweep_status=$2

   if [[ $debug == "false" ]]; then
      echo "$(date)" | tee $sweep_log > $sweep_status
      echo " " | tee -a $sweep_log >> $sweep_status
   else
      echo "$(date)" > $sweep_status
      echo " " | tee -a >> $sweep_status
   fi
}

wordcmd_main()
{
   local projid=$1; local style=$2; local logid=$3; local key="$4"; local options="$5"

   echo " "
   if [[ $(has_word "$logid" "-") ]]; then
      local rangelo="$(regexw "$logid" '^[0-9]+')"
      local rangehi="$(regexw "$logid" '[0-9]+$')"
      echo "Searching from: $(resultlog_id_to_filename $projid $rangelo)"
      echo "Searching   to: $(resultlog_id_to_filename $projid $rangehi)"
   else
      local rangelo=$logid
      local rangehi=$logid
      echo "Searching   in: $(resultlog_id_to_filename $projid $logid)"
   fi

   local runlog="$(get_runlog_data $projid $rangelo)"
   local hparams="$(runlogdata_get_hparamdata "$runlog")"
   local dataset="$(hparamdata_get_value "ds" "$hparams")"

   echo "Searching  for: $key"
   local search_exids="$(dataset_search "$dataset" "$key")"
   echo "Matching examples found: $(find_num_lines "$search_exids")"

   local resultlog=""
   local exid_results=""
   local exid_stats=""
   for id in $(seq $rangelo $rangehi); do
      slogid="$(printf "%04d" $id)"
      resultlog="$(get_resultlog_data $projid $slogid)"
      if [[ $(finds "$resultlog" "Error, File not found") ]]; then
         echo "Error, Log not found: $resultlog"
         exit 1
      fi
      exid_results="$(resultlogdata_get_results "$resultlog" "$search_exids")"
      exid_stats="$(resultlogdata_calc_stats "$exid_results")"
      if [[ $(has_word "$options" "verbose") ]]; then
         echo "$exid_results"
      fi
      echo "$exid_stats"
   done
}

dataset_search()
{
   local fname="$1"; local sterm="$2"
   match="$(grep -E "$sterm" $fname | grep -oE '^[^,]+')"
   echo "$match"
}

get_sweeplog_data()
{
   local projid="$1"; local logid="$2"

   log_file="$(sweeplog_id_to_filename $projid $logid)"

   if [[ ! -e $log_file ]]; then
      echo "Error, File not found: $log_file"
      exit 1
   fi

   local log_data="$(cat $log_file)"

   echo "$log_data"
}

get_runlog_data()
{
    local projid="$1"; local logid="$2"

   log_file="$(runlog_id_to_filename $projid $logid)"

   if [[ ! -e $log_file ]]; then
      echo "Error, File not found: $log_file"
      exit 1
   fi

   local log_data="$(cat $log_file)"

   echo "$log_data"
}

get_resultlog_data()
{
    local projid="$1"; local logid="$2"

   result_file="$(resultlog_id_to_filename $projid $logid)"

   if [[ ! -e $result_file ]]; then
      echo "Error, File not found: $result_file"
      exit 1
   fi

   local result_data="$(cat $result_file)"

   echo "$result_data"
}

runlogdata_get_hparamdata()
{
   local log_data="$1"

   local log_params="$(echo "$log_data" | grep -E 'param [a-z0-9]{2} : .*')"

   local params=""

  while read -r line; do
      params+="$(echo "$line" | awk '{print $2," ", $4}')"
      params+=$'\n'
   done <<< "$log_params"

   echo "$params"
}

runlog_get_epochdata()
{
   local projid="$1"; local logid="$2"

   local log_file="$(runlog_id_to_filename $projid $logid)"
   local epochs="$(cat "$log_file" | grep -A 13 -E 'epoch')"

   logname="$(path_file_name "$log_file")"

   epochs="$(find_subst "^[\ \t]+epoch" "$logname epoch" "$epochs")"

   echo "$epochs"
}

runlog_get_hparamdata()
{
   local projid="$1"; local logid="$2"

   local log_file="$(runlog_id_to_filename $projid $logid)"
   local params="$(cat "$log_file" | grep -oE 'hyper parameters|param [a-z0-1]{2} .*')"

   logname="$(path_file_name "$log_file")"

   params="$(find_subst "^[\ \t]+hyper parameters" "$logname hyper parameters" "$params")"

   echo "$params"
}

resultlogdata_get_results()
{
   local log_data="$1"; local log_ids="$2"

   local results=""
   local num_total=0
   local num_found=0

   local -A result_entries=()

   while read -r line; do
      set -- $line
      key=$1
      result_entries[$key]="$line"
   done <<< "$log_data"

   while read -r exid; do
      if [[ "${result_entries[$exid]}" != "" ]]; then
         results+="${result_entries[$exid]}"$'\n'
         num_found=$(($num_found+1))
      fi
      num_total=$(($num_total+1))
   done <<< "$log_ids"

   echo "$results"
}


resultlogdata_calc_stats()
{
   local log_data="$1"

   local stats=""

   local num_exids=0
   local num_test=0
   local num_train=0
   local num_test_pass=0
   local num_test_fail=0
   local num_train_pass=0
   local num_train_fail=0

  while read -r line; do
      res_id="$(echo "$line" | awk '{print $1}')"
      res_set="$(echo "$line" | awk '{print $2}')"
      res_outcome="$(echo "$line" | awk '{print $3}')"
      num_exids=$(($num_exids+1))
      if [[ "$res_set" == "test" ]]; then
         num_test=$(($num_test+1))
         if [[ "$res_outcome" == "pass" ]]; then
            num_test_pass=$(($num_test_pass+1))
         else
            num_test_fail=$(($num_test_fail+1))
         fi
      else
         num_train=$(($num_train+1))
         if [[ "$res_outcome" == "pass" ]]; then
            num_train_pass=$(($num_train_pass+1))
         else
            num_train_fail=$(($num_train_fail+1))
         fi
      fi
   done <<< "$log_data"

   local train_acc=$(math_fdiv $num_train_pass $num_train)
   local test_acc=$(math_fdiv $num_test_pass $num_test)
   local all_pass=$(($num_train_pass+$num_test_pass))
   local all_fail=$(($num_train_fail+$num_test_fail))
   local all_acc=$(math_fdiv $all_pass $num_exids)

   echo "All: $num_exids/$all_pass/$all_fail/$all_acc Train: $num_train/$num_train_pass/$num_train_fail/$train_acc Test: $num_test/$num_test_pass/$num_test_fail/$test_acc"
}

show_top_k()
{
   local projid=$1; local sweepid=$1; local k=$2

   local run_log=""
   local run_id=""

   local sweep_log=$(sweeplog_id_to_filename $projid $sweepid)

   local sweeps=$(cat $sweep_log | grep "TRAINID:")

   local precisions=""
   while read -r sweep; do
      run_id=$(echo $sweep | awk '{print $8}')
      run_log=$(runlog_id_to_filename $projid $runid)
      if [[ -e $run_log ]]; then
         f1="$(cat $sweep_log | grep -A 1 "RUNID: $run_id" | tail -n 1 | awk '{print $11}')"
         acc="$(cat $sweep_log | grep -A 1 "RUNID: $run_id" | tail -n 1 | awk '{print $13}')"
         if [[ $(expr $f1 \< $acc) ]]; then
            precision=$f1
         else
            precision=$acc
         fi
         if [[ "$precision"  != "" ]]; then
            precisions+="$precision $sweep"
            precisions+=$'\n'
         fi
      fi
   done <<< "$sweeps"

   precisions=$(echo "$precisions" | sort | tail -n $k)

   while read -r sweep; do
      run_id=$(echo $sweep | awk '{print $7}')
      precision=$(echo "$sweep" | awk '{print $1}')
      sweep_config=$(echo "$sweep" | awk '{for (i=2; i<NF; i++) printf $i " "; print $NF}')
      if [[ "$precision" != "" && "$precision" != "TRAINID:" ]]; then
         echo "$runid"
         cat $sweep_log | grep -A 2 "RUNID: $run_id"
      fi
   done <<< "$precisions"
}