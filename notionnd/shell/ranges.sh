#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functiuons and data types for maintaining training ranges

train_get_rangedict()
{
   local projid="$1"; local model=$2; local range_type=$3

   local projcfg="$(train_ranges_from_project $projid $model $range_type)"

   if [[ $projcfg != "" ]]; then
      echo "$projcfg"
   elif [[ $range_type == "random" && $model == "rnn_nonstatic" ]]; then
      echo "$(train_ranges_random_rnn_nonstatic)"
   elif [[ $range_type == "random" && $model == "rnn_static" ]]; then
      echo "$(train_ranges_random_rnn_static)"
   elif [[ $range_type == "random" && $model == "rnn_rand" ]]; then
      echo "$(train_ranges_random_rnn_rand)"
   elif [[ $range_type == "sweep" && $model == "rnn_nonstatic" ]]; then
      echo "$(train_ranges_sweep_rnn_nonstatic)"
   elif [[ $range_type == "sweep" && $model == "rnn_static" ]]; then
      echo "$(train_ranges_sweep_rnn_static)"
   elif [[ $range_type == "sweep" && $model == "rnn_rand" ]]; then
      echo "$(train_ranges_sweep_rnn_rand)"
   elif [[ $range_type == "random" && $model == "cnn_nonstatic" ]]; then
      echo "$(train_ranges_random_cnn_nonstatic)"
   elif [[ $range_type == "random" && $model == "cnn_static" ]]; then
      echo "$(train_ranges_random_cnn_static)"
   elif [[ $range_type == "random" && $model == "cnn_rand" ]]; then
      echo "$(train_ranges_random_cnn_rand)"
   elif [[ $range_type == "sweep" && $model == "cnn_nonstatic" ]]; then
      echo "$(train_ranges_sweep_cnn_nonstatic)"
   elif [[ $range_type == "sweep" && $model == "cnn_static" ]]; then
      echo "$(train_ranges_sweep_cnn_static)"
   elif [[ $range_type == "sweep" && $model == "cnn_rand" ]]; then
      echo "$(train_ranges_sweep_cnn_rand)"
   fi
}

train_ranges_rnn_default()
{
   local -A rnn_default_ranges

   rnn_default_ranges[tb]="90"
   rnn_default_ranges[dx]="65"
   rnn_default_ranges[db]="[.9,.5]"
   rnn_default_ranges[dw]="[.5,.815]"
   rnn_default_ranges[fa]="tanh"
   rnn_default_ranges[fd]="0.0"
   rnn_default_ranges[fw]="0"
   rnn_default_ranges[rw]="190"
   rnn_default_ranges[ra]="tanh"
   rnn_default_ranges[rb]=".7"
   rnn_default_ranges[rc]="ugrnn"
   rnn_default_ranges[rd]=".6"
   rnn_default_ranges[rr]="mean"
   rnn_default_ranges[ro]="output"
   rnn_default_ranges[oa]="sigmoid"
   rnn_default_ranges[ob]=".01"
   rnn_default_ranges[o1]=".0005"
   rnn_default_ranges[o2]=".0005"
   rnn_default_ranges[lr]=".0002"

   declare -p rnn_default_ranges | tr -d "'"
}

train_ranges_from_project()
{
   local projid="$1"; local model=$2; local range_type=$3

   #local projcfg="$(project_id_to_projconfig $projid)"
   local rangename="${range_type}_${model}_ranges"

   #local projcfg_data="$(cat $projcfg)"

   #local range_data="$(find_between "$projcfg_data" "declare -A $rangename" ")")"

   #echo "$range_data"
   project_config_get_dict $projid $range_name
}

train_ranges_random_rnn_nonstatic()
{
   local range_dict="$(train_ranges_rnn_default)"

   local projcfg

   eval "$(dict_local random_rnn_nonstatic_ranges "$range_dict")"

   random_rnn_nonstatic_ranges[mt]="rnn_nonstatic"

   declare -p random_rnn_nonstatic_ranges
}

train_ranges_random_rnn_static()
{
   local range_dict="$(train_ranges_rnn_default)"
   eval "$(dict_local random_rnn_static_ranges "$range_dict")"

   random_rnn_static_ranges[mt]="rnn_static"

   declare -p random_rnn_static_ranges
}

train_ranges_random_rnn_rand()
{
   local range_dict="$(train_ranges_rnn_default)"
   eval "$(dict_local random_rnn_rand_ranges "$range_dict")"

   random_rnn_rand_ranges[mt]="rnn_rand"

   declare -p random_rnn_rand_ranges
}

train_ranges_sweep_rnn_rand()
{
  local range_dict="$(train_ranges_rnn_default)"
  eval "$(dict_local sweep_rnn_rand_ranges "$range_dict")"

  sweep_rnn_rand_ranges[mt]="rnn_rand"

  declare -p sweep_rnn_rand_ranges
}

train_ranges_sweep_rnn_static()
{
  local range_dict="$(train_ranges_rnn_default)"
  eval "$(dict_local sweep_rnn_static_ranges "$range_dict")"

  sweep_rnn_static_ranges[mt]="rnn_statis"

  declare -p sweep_rnn_static_ranges
}

train_ranges_sweep_rnn_nonstatic()
{
  local range_dict="$(train_ranges_rnn_default)"
  eval "$(dict_local sweep_rnn_nonstatic_ranges "$range_dict")"

  sweep_rnn_nonstatic_ranges[mt]="rnn_rand"

  declare -p sweep_rnn_nonstatic_ranges
}

train_ranges_cnn_default()
{
  local -A cnn_default_ranges

  cnn_default_ranges[tb]="10 20 30 40 50 60 70 80"
  cnn_default_ranges[dx]="50 55 60 65 70 75 80 85 90 95 100 105 110"
  cnn_default_ranges[db]="[.590,.5] [.591,.5] [.592,.5] [.593,.5] [.594,.5] [.595,.5] [.596,.5] [.597,.5] [.598,.5] [.599,.5] [.6,.5] [.601,.5] [.602,.5]"
  cnn_default_ranges[dw]="[.5,.550] [.5,.551] [.5,.552] [.5,.553] [.5,.554] [.5,.555] [.5,.556] [.5,.557] [.5,.558] [.5,.559] [.5,.560] [.5,.561] [.5,.562] [.5,.563] [.5,.564] [.5,.565] [.5,.566] [.5,.567] [.5,.568] [.5,.569]"
  cnn_default_ranges[cb]="0 .1 .01 .001 .0001 .00001 .000001"
  cnn_default_ranges[cd]="0.0 .1 .2 .3 .4 .5"
  cnn_default_ranges[cn]="[100,100,100] [150,150,150] [200,200,200]"
  cnn_default_ranges[cw]="[2,3,4] [3,3,3] [3,4,5] [4,4,4] [4,5,6] [5,5,5] [5,6,7] [6,6,6] [7,7,7]"

  cnn_default_ranges[wd]="0.0 .1 .2 .3 .4 .5"
  cnn_default_ranges[fw]="0 25 50 75 100 150"
  cnn_default_ranges[fd]="0.0 .1 .2 .3 .4 .5"
  cnn_default_ranges[fb]="0 .1 .01 .001 .0001 .00001 .000001"

  cnn_default_ranges[oa]="relu linear"
  cnn_default_ranges[ob]="0 .1 .01 .001 .0001 .00001 .000001"
  cnn_default_ranges[o1]="1.0 .0009 .0008 .0007 .0006 .0005 .0004 .0003 .0002 .0001"
  cnn_default_ranges[o2]="1.0 .0009 .0008 .0007 .0006 .0005 .0004 .0003 .0002 .0001"
  cnn_default_ranges[lr]=".0006 .0005 .0004 .0003 .0002 .0001"

  cnn_default_ranges[tl]="softmax_cross_entropy sigmoid_cross_entropy mean_squared"
  cnn_default_ranges[to]="Adagrad Adam Ftrl RMSProp SGD"

  declare -p cnn_default_ranges | tr -d "'"
}

train_ranges_random_cnn_nonstatic()
{
  local range_dict="$(train_ranges_cnn_default)"
  eval "$(dict_local random_cnn_nonstatic_ranges "$range_dict")"

  random_cnn_nonstatic_ranges[mt]="cnn_nonstatic"

  declare -p random_cnn_nonstatic_ranges
}

train_ranges_random_cnn_static()
{
  local range_dict="$(train_ranges_cnn_default)"
  eval "$(dict_local random_cnn_static_ranges "$range_dict")"

  random_cnn_static_ranges[mt]="cnn_static"

  declare -p random_cnn_static_ranges
}

train_ranges_random_cnn_rand()
{
  local range_dict="$(train_ranges_cnn_default)"
  eval "$(dict_local random_cnn_rand_ranges "$range_dict")"

  random_cnn_rand_ranges[mt]="cnn_rand"

  declare -p random_cnn_rand_ranges
}

train_ranges_sweep_cnn_nonstatic()
{
  local range_dict="$(train_ranges_cnn_default)"
  eval "$(dict_local sweep_cnn_nonstatic_ranges "$range_dict")"

  sweep_cnn_nonstatic_ranges[mt]="cnn_nonstatic"

  declare -p sweep_cnn_nonstatic_ranges
}

train_ranges_sweep_cnn_static()
{
  local range_dict="$(train_ranges_cnn_default)"
  eval "$(dict_local sweep_cnn_static_ranges "$range_dict")"

  sweep_cnn_static_ranges[mt]="cnn_static"

  declare -p sweep_cnn_static_ranges
}

train_ranges_sweep_cnn_rand()
{
  local range_dict="$(train_ranges_cnn_default)"
  eval "$(dict_local sweep_cnn_rand_ranges "$range_dict")"

  sweep_cnn_rand_ranges[mt]="cnn_rand"

  declare -p sweep_cnn_rand_ranges
}
