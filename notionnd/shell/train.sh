#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions and data types used to coordinate neural network training

train()
{
   local projid=$1; local train_id=$2; local train_status=$3; local model_mode="$4"; local options="$5"

   local mode=$(find_nth_word "$model_mode" 1)
   local model=$(find_nth_word "$model_mode" 2)

   if [[ "$mode" == "random" ]]; then
      train_random $projid $train_id $model $train_status "$options"
   elif [[ "$mode" == "loop" ]]; then
      train_loop $projid $train_id $model $train_status "$options"
   fi
}

train_random()
{
   local projid=$1; local train_id=$2; local model=$3; local train_status=$4; local options="$5"

   local num_loops=2000
   local projectdir="$(project_id_to_projectdir $projectid)"
   local sweep_history="$projectdir/sweep_history_random.log"

   if [[ $debug == "false" ]]; then
     if [[ -e $sweep_history && $(has_regex "$options" "restart") ]]; then
       echo "  Purging sweep history: $sweep_history"
       rm -f $sweep_history
     fi
   fi
   touch $sweep_history

   if [[ $(has_regex "$options" "forever") ]]; then
      num_loops=0
   fi

   local range_dict="$(train_get_rangedict $projid $model random)"

   model_run_random $projid $train_id $num_loops $sweep_history $train_status $model "$range_dict"
}

train_loop()
{
  local projid=$1; local train_id=$2; local model=$3; local train_status=$4; local num_loops=$5

  local hparams_name="${model}_hparams"

  local config_hparams="$(project_config_get_dict $projid $hparams_name)"

  eval "$(dict_local hparams_dict "$config_hparams")"
  local loop_args=""
  local paramid=""

  for i in "${!hparams_dict[@]}";  do
    paramid=$i
    loop_args+=" --${paramid} ${hparams_dict[$paramid]}"
  done

   model_run_loop $projid $train_id 0001 $train_status $model $num_loops "$loop_args"

}

train_range()
{
  local projid=$1; local train_id=$2; local model=$3; local train_status=$4; local options="$5"

  local projectdir="$(project_id_to_projectdir $projectid)"
  local sweep_history="$projectdir/sweep_history_range.log"

  if [[ $debug == "false" ]]; then
    if [[ -e $sweep_history && $(has_regex "$options" "restart") ]]; then
      echo "  Purging sweep history: $sweep_history"
      rm -f $sweep_history
    fi
  fi
  touch $sweep_history

  if [[ "$model" == "rnn" ]]; then
    train_range_rnn $projid $train_id $train_status $sweep_history
  else
    train_range_cnn $projid $train_id $train_status $sweep_history
  fi
}

train_range_cnn()
{
   local projid=$1; local train_id=$1; local train_id=$2; local train_status=$3; local sweep_history=$4

   local run_id=1
   local trn_dir="$(project_id_to_traineddir $projid)"
   local logresult_dir="$(project_id_to_pastlogdir $projid)"
   local logstatus_dir="$(project_id_to_currentlogdir $projid)"
   local sweep_params=" "
   sweep_params+="--mt cnn_nonstatic --sp $trn_dir --lp $logresult_dir --ls $logstatus_dir"


   local bc_range=(25)
   local cd_range=(1.0 .2 .25 .3 .35 .4 .45 .5)
   local cn_range=(100 125 150)
   local dx_range=(60)
   local o1_range=(1.0)
   local o2_range=(1.0)

   for tbc in ${bc_range[@]}; do
   for tcd in ${cd_range[@]}; do
   for tcn in ${cn_range[@]}; do
   for tdx in ${dx_range[@]}; do
   for to1 in ${o1_range[@]}; do
   for to2 in ${o2_range[@]}; do
     sweep_args="--dx $tdx --bc $tbc --cd $tcd --cn [$tcn,$tcn,$tcn,$tcn] --o1 $to1 --o2 $to2"

     if [[ "$(grep -F -- "$sweep_args" $sweep_history)" == "" ]]; then
         echo "$sweep_args" >> $sweep_history
         rm -rf $trn_dir
         model_run $projid $train_id $run_id $train_status "$sweep_params $sweep_args"
         run_id=$((run_id+1))
         rm -rf $trn_dir
         model_run $projid $train_id $run_id $train_status "$sweep_params $sweep_args"
         run_id=$((run_id+1))
      else
         num_loops=$((num_loops+1))
         echo "Skipping: $sweep_args"
      fi
   done
   done
   done
   done
   done
   done
}

train_range_rnn()
{
   local projid=$1; local train_id=$2; local train_status=$3; local sweep_history=$4;

   local run_id=1
   local trn_dir="$(project_id_to_traineddir $projid)"
   local logresult_dir="$(project_id_to_pastlogdir $projid)"
   local logstatus_dir="$(project_id_to_currentlogdir $projid)"
   local sweep_params=" "
   sweep_params+="--mt rnn_nonstatic --sp $trn_dir --lp $logresult_dir --ls $logstatus_dir"


   local rw_range=(30 40 50 60 70 80 90 100 125 150)
   local ws_range=(100 125 150 175 200 250 275)

   for trw in ${rw_range[@]}; do
   #for tws in ${ws_range[@]}; do
      sweep_args="--rw $trw"

      if [[ "$(grep -F -- "$sweep_args" $sweep_history)" == "" ]]; then
         echo "$sweep_args" >> $sweep_history
         rm -rf $trn_dir
         model_run $projid $train_id $run_id $train_status "$sweep_params $sweep_args"
         run_id=$((run_id+1))
         rm -rf $trn_dir
         model_run $projid $train_id $run_id $train_status "$sweep_params $sweep_args"
         run_id=$((run_id+1))
      else
         num_loops=$((num_loops+1))
         echo "Skipping: $sweep_args"
      fi
   #done
   done
}


report()
{
   local projid=$1; local run_id=$2; local sweep_log=$3; local train_status=$4

   if [[ $debug == "true" ]]; then
      run_id=0001
   fi
   #local epochs="$(runlog_get_epochdata $projid $run_id)"
   #local best_epoch="$(epochdata_best_epoch "??VLOK=.499?&VGACC=.61@@IVACC,VF1!!0.0")"
   local epochs="$(runlog_get_epochdata $projid $run_id)"

   local ok_epochs="$(epochdata_filter_on_metric "VLOK=.499" "$epochs")"
   local best_epoch="$(epochdata_best_epoch "VGF1" "$ok_epochs")"

   if [[ $debug == "false" ]]; then
      echo "$best_epoch" | tee -a $sweep_log >> $train_status
   else
      echo "$best_epoch" >> $train_status
   fi
}
