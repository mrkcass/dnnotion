#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions and data types used to interface to neural network models


model_run()
{
   local projid=$1; local train_id=$2; local step=$3; local substep=$4; local train_status=$5; local args="$6"

   local runid=$(($train_id+$step+$substep-2))
   local trn_dir="$(project_id_to_traineddir $projid)"
   local str_run_id=$(printf "%04d" $runid)
   local str_train_id=$(printf "%04d" $train_id)
   local str_step=$(printf "%04d" $step)
   local str_substep=$(printf "%04d" $substep)

   local sweeplog=$(sweeplog_id_to_filename $projid $str_train_id)

   local cmd="python -m $model_file --li $str_run_id"

   local log_str="TRAINID: $str_train_id STEP: $str_step SUBSTEP: $str_substep RUNID: $str_run_id COMMAND: $cmd $args"

   if [[ $debug == "false" ]]; then
      rm -rf $trn_dir
      echo "$log_str" | tee -a $sweeplog | tee -a $train_status
      $cmd $args
   else
      echo "$log_str" | tee -a $train_status
   fi

   report $projid $str_run_id $sweeplog $train_status
}

model_info()
{
   local projid=$1; local model=$2

   local trn_dir="$(project_id_to_traineddir $projid)"
   local logresult_dir="$(project_id_to_pastlogdir $projid)"
   local logstatus_dir="$(project_id_to_currentlogdir $projid)"

   local args="--mt $model --st info --sp $trn_dir --lp $logresult_dir --ls $logstatus_dir --ds info"

   local cmd="python -m $model_file"

   echo "$($cmd $args)"
}

model_run_random()
{
   local projid=$1; local train_id=$2; local num_loops=$3; local sweep_history=$4; local train_status=$5; local model=$6; local range_dictp="$7"

   local substep=1

   #local range_dict_global="$(train_get_rangedict $projid $model random)"
   eval "$(dict_local range_dict "$range_dictp")"

   local idx=1
   local num_runs=2
   local -a param_range

   while (($num_loops == 0 || idx <= $num_loops)); do
      sweep_args=""

      for i in "${!range_dict[@]}";  do
         paramid=$i
         read -r -a param_range <<< "${range_dict[$paramid]}"
         rand_key=$(expr $RANDOM % ${#param_range[@]})
         sweep_args+=" --${paramid} ${param_range[$rand_key]}"
      done

      if [[ "$num_loops" == "0" || "$(grep -F -- "$sweep_args" $sweep_history)" == "" ]]; then
         echo "$sweep_args" >> $sweep_history
         model_run_loop $projid $train_id $idx $train_status $model $num_runs "$sweep_args"
      else
         num_loops=$((num_loops+$num_runs))
         echo "Skipping: $sweep_args"
      fi

      idx=$((idx+$num_runs))
   done
}

model_run_loop()
{
   local projid=$1; local train_id=$2; local step=$3; local train_status=$4; local model=$5; local num_loops=$6; local run_args="$7"

   local substep=1
   local trn_dir="$(project_id_to_traineddir $projid)"
   local logresult_dir="$(project_id_to_pastlogdir $projid)"
   local logstatus_dir="$(project_id_to_currentlogdir $projid)"
   run_args+=" --st train --mt $model --sp $trn_dir --lp $logresult_dir --ls $logstatus_dir"

   for lnum in 1..$(seq 1 $num_loops); do
      model_run $projid $train_id $step $substep $train_status "$run_args"
      substep=$((substep+1))
   done
}
