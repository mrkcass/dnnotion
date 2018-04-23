#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions and data types for handling projects

project_id_to_projectname()
{
   local projid="$1"
   echo "$(path_parent_name)$projid"
}

project_id_to_projectdir()
{
   local projid="$1"
   echo "$projects_dir/$(project_id_to_projectname $projid)"
}

project_id_to_logdir()
{
   local projid="$1"
   echo "$log_dir/$(project_id_to_projectname $projid)"
}

project_id_to_pastlogdir()
{
   local projid="$1"
   echo "$log_dir/$(project_id_to_projectname $projid)/past"
}

project_id_to_currentlogdir()
{
   local projid="$1"
   echo "$log_dir/$(project_id_to_projectname $projid)/current"
}

project_id_to_traineddir()
{
   local projid="$1"
   echo "$trained_dir/$(project_id_to_projectname $projid)/current"
}

project_id_to_besttraineddir()
{
   local projid="$1"
   echo "$trained_dir/$(project_id_to_projectname $projid)/best"
}

project_id_to_projconfig()
{
   local projid="$1"
   echo "$(project_id_to_projectdir $projid)/$proj_config_fname"
}

project_cmd_path()
{
   local projid="$1"
   project_id_to_projectdir $projid
}

project_command()
{
   local projidx="$1"; local op="$2"; local options="$3"

   if [[ $op == "new" ]]; then
      projcmd_new $projidx
   elif [[ $op == "delete" ]]; then
      projcmd_delete $projidx
   elif [[ $op == "add" ]]; then
      projcmd_add $projidx "$options"
   elif [[ $op == "copy" ]]; then
      projcmd_copy $projidx "$options"
   elif [[ $op == "edit" ]]; then
      projcmd_edit $projidx "$options"
   fi
}

# not sure if this is used
function project_save()
{
   local destfile="$1"; local savedata="$2"

   local -A foo=(
     [dx]='1000'
     [db]='333'
     [sp]='path/to/trained'
     [lp]='path/to/logs'
   )

   rnn_def="
     [dx]='1000'
     [db]='333'
     [sp]='path/to/trained'
     [lp]='path/to/logs'
     "
   echo "$(dict_serialize "$rnn_def")"
   local xxx="$(declare -p foo)"
   echo "$(dict_serialize "$foo")"
   local yyy="$(find_subst '\[' '\n   \[' "$xxx")"
   find_subst '[\)]' '\n\)' "$yyy" > test.foo
}

function projcmd_add()
{
   local projidx="$1"; local options="$2"

   if [[ $(has_regex "$options" "hparams") ]]; then
      project_add_hparams "$projidx" "$options"
   elif [[ $(has_regex "$options" "ranges") ]]; then
      project_add_ranges "$projidx" "$options"
   fi
}

# -p 1 add hparams rnn_nonstatic
function project_add_hparams()
{
   local projidx="$1"; local options="$2"

   local proj_config="$(project_id_to_projconfig $projidx)"
   local model="$(find_nth_word "$options" 1)"

   if [[ "$(find_num_words "$options")" != "2" ]]; then
      echo "Error: no model specified"
      exit 1
   fi

   if [[ "$model"  == "hparams" ]]; then
      model="$(find_nth_word "$options" 2)"
   fi

   local param_list="$(model_info $projidx $model)"

   printf "\n\n#%s hyper parameters\n" $model >> $proj_config
   echo "declare -A ${model}_hparams=(" >> $proj_config
   while read -r line; do
      if [[ $(has_regex "$line" "param ") ]]; then
         key="$(find_nth_word "$line" 2)"
         if [[ $(has_regex "$line" "\[") ]]; then
            value="$(regexw "$line" "\[.*\]")"
            value="$(find_subst '[,] ' ',' "$value")"
         else
            value="$(find_nth_word "$line" 4)"
         fi
         echo "   [$key]=\"$value\"" >> $proj_config
      fi
   done <<< "$param_list"
   echo ")" >> $proj_config

   echo "  Project $projidx : Added $model hyperparameters"
}

# -p 1 add ranges rnn_nonstatic random
function project_add_ranges()
{
   local projidx="$1"; local options="$2"

   local proj_config="$(project_id_to_projconfig $projidx)"
   local model="$(find_nth_word "$options" 1)"
   local range_type="$(find_nth_word "$options" 3)"
   local range_dict="$(train_get_rangedict 0 $model $range_type)"
   printf "\n\n#%s %s ranges\n" $model $range_type >> $proj_config
   echo "$(dict_format "$range_dict")" >> $proj_config
}

projcmd_new()
{
   local projidx="$1"

   local newproj_name="$(project_id_to_projectname $projidx)"
   local newproj_path_proj="$(project_id_to_projectdir $projidx)"
   local newproj_path_currentlogs="$(project_id_to_currentlogdir $projidx)"
   local newproj_path_pastlogs="$(project_id_to_pastlogdir $projidx)"
   local newproj_path_trained="$(project_id_to_traineddir $projidx)"
   local newproj_path_besttrained="$(project_id_to_besttraineddir $projidx)"
   local newproj_projconfig="$(project_id_to_projconfig $projidx)"

   if [[ ! -e  $newproj_path_proj ]]; then
      path_new_dir $newproj_path_proj
      path_new_file $newproj_projconfig
      path_new_dir $newproj_path_currentlogs
      path_new_dir $newproj_path_pastlogs
      path_new_dir $newproj_path_trained
      path_new_dir $newproj_path_besttrained
      echo " "
      echo "  Created project: $newproj_name"
      echo " "
   else
      echo "Error project exists: $newproj_name"
      exit 1
   fi
}

projcmd_delete()
{
   local projidx="$1"

   local proj_name="$(project_id_to_projectname $projidx)"
   local proj_path_proj="$(project_id_to_projectdir $projidx)"
   local proj_path_logs="$(project_id_to_logdir $projidx)"
   local proj_path_trained="$(project_id_to_traineddir $projidx)"

   if [[ -e  $delproj_path_proj ]]; then
      path_rm_dir $proj_path_proj
      path_rm_dir $proj_path_logs
      path_rm_dir $proj_path_trained
      echo " "
      echo "  Deleted project: $proj_name"
      echo " "
   else
      echo "Error project not found: $proj_name"
      exit 1
   fi
}

projcmd_copy()
{
   local projidx="$1"; local options="$2"

   if [[ $(has_word "$options" "hparams") ]]; then
      local model="$(find_nth_word "$options" 2)"
      local dest_projidx="$(find_nth_word "$options" 3)"
      local src_name="${model}_hparams"
      local src_dict="$(project_config_get_dict $projidx $src_name)"
      project_config_put_dict $dest_projidx "$src_dict"
   elif [[ $(has_word "$options" "cmd") ]]; then
      local cmdid="$(find_nth_word "$options" 2)"
      local dest_projidx="$(find_nth_word "$options" 3)"
      usercmd_copy $projidx $cmdid $dest_projidx
   fi
}

projcmd_edit()
{
   local projidx="$1"; local options="$2"

   if [[ $(has_word "$options" "config") ]]; then
      local filename="$(project_id_to_projconfig $projidx)"
      export TERM="xterm-256color"
      notionnd/programs/micro $filename
   elif [[ $(has_word "$options" "cmd") ]]; then
      local cmdid="$(find_nth_word "$options" 2)"
      usercmd_edit $projidx $cmdid ""
   fi
}

project_config_get_dict()
{
   local projid="$1"; local array_name=$2;

   local projcfg="$(project_id_to_projconfig $projid)"

   local projcfg_data="$(cat $projcfg)"

   local array_data="$(find_between "$projcfg_data" "declare -A $array_name" ")")"

   echo "$array_data"
}

project_config_put_dict()
{
   local projid="$1"; local array="$2"

   local projcfg="$(project_id_to_projconfig $projid)"

   local projcfg_data="$(cat $projcfg)"

   local array_name="$(dict_name "$array")"

   local begin="declare -A $array_name"
   local end=')'

   local newcfg="$(find_subst_between "$projcfg_data" "$begin" "$end" "$array")"

   if [[ ! "$(has_word "$newcfg" $array_name)" ]]; then
      echo -e "\n $array" >> $projcfg
   else
      echo "$newcfg" > $projcfg
   fi
}