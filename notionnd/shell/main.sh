#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: dnnotion entry point

command=""
command_proj=""
command_options=""
command_arg=""
debug="false"
projects_dir="projects"
log_dir="logs"
trained_dir="trained"
archive_dir="archive"
proj_config_fname="configuration"


main()
{
    parse_options $*

    local sweep_id=$(new_sweep_id $command_proj)
    local str_sweep_id=$(printf "%04d" $sweep_id)
    local sweep_log=$(sweeplog_id_to_filename $command_proj $str_sweep_id)
    local sweep_status="$(project_id_to_currentlogdir $command_proj $str_sweep_id)/run_status.txt"
    local projectid="$command_proj"
    local projectname="$(project_id_to_projectname $projectid)"
    local projectdir="$(project_id_to_projectdir $projectid)"

    if [[ ! "$projectid" ]]; then
        echo "Error: project not specified"
        exit 1
    fi

    if [[ $command == "train_range" ]]; then
        output_header $sweep_log $sweep_status
        train_range $projectid $sweep_id $sweep_status $command_arg $command_options
    elif [[ $command == "train_random" ]]; then
        output_header $sweep_log $sweep_status
        train_random $projectid $sweep_id $command_arg $sweep_status $command_options
    elif [[ $command == "train_loop" ]]; then
        output_header $sweep_log $sweep_status
        train_loop $projectid $sweep_id $sweep_status $command_arg $command_options
   elif [[ $command == "train" ]]; then
        output_header $sweep_log $sweep_status
        train $projectid $sweep_id $sweep_status "$command_arg" "$command_options"
    elif [[ $(echo "$command" | grep -o "run_top_k") != "" ]]; then
        sweep_history="$projectdir/sweep_history_topk.log"
        output_header $sweep_log $sweep_status
        ref_sweep=$(echo "$command" | awk '{print $2}')
        ref_k=$(echo "$command" | awk '{print $3}')
        run_top_k $ref_sweep $ref_k $sweep_id $sweep_status $sweep_history
    fi
}