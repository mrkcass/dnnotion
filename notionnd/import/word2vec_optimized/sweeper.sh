#! /bin/bash


# an idea for syzygy.
# data in syzygy
#    tests
#       setup
#       test
#       teardown
#       evaluate
#           condition
#           expected value
#           expected range
#           actual value
#           sensor array snap shot
#
# neural network apogeeNet
# input
#   sensor array snap shot
# output
#   failure points for each sensor

homepath="../../../../.."
trained="dnnotion_nlpclassifier/bugresNet/trained/word2vec"

declare -A defaults=([td]="$homepath/data/current4/bug_scrape_500000_676000_wv_corpus_peopled_csv_stm.txt"
                     [ed]="questions-words.txt"
                     [sp]="$homepath/$trained/sweep_RESULTIDX_SWEEPPARAM_result"
                     [cs]="16"
                     [es]="250"
                     [ws]="3"
                     [ns]="7"
                     [ss]=".01"
                     [et]="15"
                     [lr]="0.01"
                     [bs]="256"
                     [mc]="3"
                     [si]="False"
                     [se]=".54"
                   )

declare -A opts=([reload]="false"
                 [fixed]="false"
                 [sweep]="false"
                 [index]="0"
                 [corpus]="false"
                 [base]=""
                 [debug]="false"
                 [overrides]="false"
                 [lookup]="false"
                 [td]=""
                 [ed]=""
                 [sp]=""
                 [cs]=""
                 [es]=""
                 [ws]=""
                 [ns]=""
                 [ss]=""
                 [et]=""
                 [lr]=""
                 [bs]=""
                 [mc]=""
                 [si]=""
                 [lf]=""
                 [se]=""
                )

declare -A ranges=( [es]="300 275 250 225 200"
                    [ws]="3 4 5 6 7 8 9 10"
                    [lr]=".001 .002 .003 .004 .005 .006 .007"
                    [ns]="7 20"
                    [ss]=".0005 .0006 .0007 .0008 .0009"
                    [mc]="2 3 4 5 6 7 8 9 10"
                    [bs]="100 500 1000"
                  )

declare -A flags=([td]="--train_data"
                  [ed]="--eval_data"
                  [sp]="--save_path"
                  [cs]="--concurrent_steps"
                  [es]="--embedding_size"
                  [ws]="--window_size"
                  [ns]="--num_neg_samples"
                  [ss]="--subsample"
                  [et]="--epochs_to_train"
                  [lr]="--learning_rate"
                  [bs]="--batch_size"
                  [mc]="--min_count"
                  [si]="--silent"
                  [lf]="--lookup"
                  [se]="--earlystop"
                 )

declare -A outputs=([localAccuracy]="0"
                    [localAccuracies]=""
                    [accuracy]="0"
                    [accuracies]=""
                  )

TFEXPORT="export TF_CPP_MIN_LOG_LEVEL=3"

parseOptions()
{
    local ptype=""
    local numargs=$#
    while (( "$#" )); do
        if [[ "$1" == "--help" || "$1" == "-h" ]]; then
            echo "sweeper.sh"
            echo " "
            echo "  script for sweeping word2vec hyperparameters"
            echo " "
            echo "  usage:"
            echo "    sweeper.sh [-h,-r,-s,-i] CORPUS "
            echo " "
            echo "  -h,--help           : show this screen."
            echo "  -r,--reload [param] : reload best or default model."
            echo "  -s,--sweep [param]  : run the model for with all params fixed except [param]."
            echo "                      :    number of runs equals the range of the sweep param"
            echo "      es                  = embedding size"
            echo "      ws                  = window size"
            echo "      lr                  = learning rate"
            echo "      ns                  = number of negative samples"
            echo "      ss                  = subsample rate"
            echo "      mc                  = minimimum count for inclusion"
            echo "  -f,--fixed          : run the model one time with fixed parameters"
            echo "  -i,--index [param]  : sweep index used when saving. default = 0"
            echo "  -b,--base [param]   : use [param] as basis for this run."
            echo "  -l,--lookup         : find nearbys for each word in the vocabulary."
            echo " "
            echo "  Param Overrides"
            echo "                      : * can be used with -s -r -f -b to override a param"
            echo "      es              : override for embedding size"
            echo "      ws              : override window size"
            echo "      lr              : override learning rate"
            echo "      ns              : override number of negative samples"
            echo "      ss              : override subsample rate"
            echo "      mc              : override minimimum count for inclusion"
            echo "  -d,--dbg            : print commands but do not run them"
            echo " "
            echo "  CORPUS              : create vectors using file CORPUS as input"
            exit 0
        elif [[ "$1" == "--reload" || "$1" == "-r" ]]; then
            ptype="reload"
        elif [[ "$1" == "--sweep" || "$1" == "-s" ]]; then
            ptype="sweep"
        elif [[ "$1" == "--fixed" || "$1" == "-f" ]]; then
            opts[fixed]="true"
        elif [[ "$1" == "--index" || "$1" == "-i" ]]; then
            ptype="index"
        elif [[ "$1" == "--base" || "$1" == "-b" ]]; then
            ptype="base"
        elif [[ "$1" == "--lookup" || "$1" == "-l" ]]; then
            opts[lookup]="true"
        elif [[ "$1" == "--dbg" || "$1" == "-d" ]]; then
            opts[debug]="true"
        elif [[ $ptype == "" && $(isDefaultKey $1) == "true" ]]; then
            ptype=$1
            opts[overrides]="true"
        else
            if [[ $ptype != "" ]]; then
                echo "$ptype"
                opts[$ptype]=$1
                ptype=""
            elif [[ ${opts[corpus]} == "false" ]]; then
                if [[  $ptype != "" ]]; then
                    echo "Error: unexpected option: $ptype"
                    exit
                fi
                opts[corpus]=$1
                defaults[td]=$1
            else
                echo "Error: unkown option: $1"
                exit
            fi
        fi
        shift
    done
}

copyFile()
{
    if [[ ${opts[debug]} == "false" ]]; then
        cp $*
    else
        echo "copyfile: $*"
    fi
}

moveFile()
{
    if [[ ${opts[debug]} == "false" ]]; then
        mv $*
    else
        echo "movefile: $*"
    fi
}

removeFile()
{
    if [[ ${opts[debug]} == "false" ]]; then
        rm $*
    else
        echo "removeFile: $*"
    fi
}

makeDir()
{
    if [[ ${opts[debug]} == "false" ]]; then
        mkdir $*
    else
        echo "makeDir: $*"
    fi
}

execWord2Vec()
{
    if [[ ${opts[debug]} == "false" ]]; then
        # echo "execWord2Vec: $@"
        python word2vec_optimized.py $@
    else
        echo "execWord2Vec: $@"
    fi
}

isDefaultKey()
{
    local key=$1

    if [[ ${defaults[$key]+abc} ]]; then
        if [[ ${opts[debug]} == "true" ]]; then echo "isDefaultKey $key = true" > /dev/tty; fi
        echo "true"
    else
        if [[ ${opts[debug]} == "true" ]]; then echo "isDefaultKey $key = false" > /dev/tty; fi
        echo "false"
    fi
}

sweepPath()
{
    local sweepParam=$1
    local resultIdx=$2
    local sweepPath=$(echo "${defaults[sp]}" | sed "s;SWEEPPARAM;$sweepParam;g" | sed "s;RESULTIDX;$resultIdx;g")

    if [[ ${opts[debug]} == "true" ]]; then echo "sweepPath = $sweepPath" > /dev/tty; fi

    echo "$sweepPath"
}

initSaveFile()
{
    local savePath=$1
    if [ ! -d $savePath ]; then
        makeDir $savePath
    else
        removeFile -rf $savePath/*
    fi
}

sweepLocalAccuracy()
{
    local resultLog=$1

    local accuracy=$(cat $resultLog | grep 'domainaccuracy' | tail -n 1 | grep -oE '[0-9]+\.[0-9]+')

    if [[ ${opts[debug]} == "true" ]]; then echo "domainaccuracy = $accuracy" > /dev/tty; fi

    echo "$accuracy"
}

sweepOverallAccuracy()
{
    local resultLog=$1

    local accuracy=$(cat $resultLog | grep -E '[^l]accuracy.*$' | tail -n 1 | grep -oE '[0-9]+\.[0-9]+')

    if [[ ${opts[debug]} == "true" ]]; then echo "sweepOverallAccuracy = $accuracy" > /dev/tty; fi

    echo "$accuracy"
}

storeAccuracies()
{
    local localAccuracy=$1
    local overallAccuracy=$2

    if [[ ${outputs[localAccuracies]} != "" ]]; then
        outputs[localAccuracies]+=" "
    fi
    outputs[localAccuracies]+="$localAccuracy"

    if [[ ${outputs[accuracies]} != "" ]]; then
        outputs[accuracies]+=" "
    fi
    outputs[accuracies]+="$overallAccuracy"
}

bestAccuracy()
{

    local localAccuracy=$1
    local overallAccuracy=$2
    local best="false"

    if [[ $localAccuracy > ${outputs[localAccuracy]} ]]; then
        best="true"
    elif [[ $localAccuracy ==  ${outputs[localAccuracy]} && $overallAccuracy >  ${outputs[accuracy]} ]]; then
        best="true"
    fi

    if [[ ${opts[debug]} == "true" ]]; then echo "bestAccuracy ( $localAccuracy , $overallAccuracy ) = $best" > /dev/tty; fi

    echo $best
}

saveBest()
{
    local index=${opts[index]}
    local param=${opts[sweep]}
    local resultPath=$(sweepPath ${opts[sweep]} ${opts[index]})

    local resultLog=$resultPath".log"
    local sweepLocalAccuracy=$(sweepLocalAccuracy $resultLog)
    local sweepOverallAccuracy=$(sweepOverallAccuracy $resultLog)
    storeAccuracies $sweepLocalAccuracy $sweepOverallAccuracy
    if [[ $(bestAccuracy $sweepLocalAccuracy $sweepOverallAccuracy) == "true" ]]; then
        local bestPath=$resultPath"_best"
        if [ -d $bestPath ]; then
            removeFile -rf $bestPath
        fi
        copyFile -rf $resultPath $bestPath
        outputs[accuracy]=$sweepOverallAccuracy
        outputs[localAccuracy]=$sweepLocalAccuracy
    fi
}

sweep()
{
    local param=${opts[sweep]}
    local constParams=""
    local savePath=""
    for i in "${!flags[@]}"; do
        if [[ $i == $param ]]; then
            sweepParam=$i
        elif [[ $i == "sp" ]]; then
            savePath=$(echo "${defaults[sp]}" | sed "s;SWEEPPARAM;${opts[sweep]};g" | sed "s;RESULTIDX;${opts[index]};g")
            constParams="$constParams ${flags[sp]}=$savePath/"
        else
            constParams="$constParams ${flags[$i]}=${defaults[$i]}"
        fi
    done
    local range=${ranges[$sweepParam]}
    export TF_CPP_MIN_LOG_LEVEL=3
    for var in $range; do
        initSaveFile $(sweepPath ${opts[sweep]} ${opts[index]})
        if [[ ${opts[debug]} == "false" ]]; then
            execWord2Vec $constParams ${flags[$sweepParam]}=$var | tee $savePath.log
        else
            execWord2Vec $constParams ${flags[$sweepParam]}=$var
        fi
        copyFile -rf $savePath.log $savePath/$savePath.log
        saveBest
    done
    echo " "
    echo "localAccuracies: ${outputs[localAccuracies]}"
    echo "Accuracies: ${outputs[accuracies]}"
}

runDefault()
{
    local fixedParams=""
    local savePath=""

    for i in "${!flags[@]}"; do
        if [[ $i == "sp" ]]; then
            savePath=$(echo "${defaults[sp]}" | sed "s;SWEEPPARAM;fixed;g" | sed "s;RESULTIDX;${opts[index]};g")
            fixedParams+=" ${flags[sp]}=$savePath"
        else
            fixedParams+=" ${flags[$i]}=${defaults[$i]}"
        fi
    done

    export TF_CPP_MIN_LOG_LEVEL=3

    initSaveFile $savePath
    if [[ ${opts[debug]} == "false" ]]; then
        execWord2Vec $fixedParams | tee $savePath.log
    else
        execWord2Vec $fixedParams
    fi
    moveFile -f $savePath.log $savePath/$(basename $savePath.log)

    echo " "
    echo "localAccuracies: ${outputs[localAccuracies]}"
    echo "Accuracies: ${outputs[accuracies]}"
}

flagFromLog()
{
    local flag=$1
    local resultLog=$2
    # the -- of the flag needs to be escaped

    local gexp=$(echo "$flag=[^\ ]+" | sed 's/\-/\\\-/g')
    # look for the flag in the log
    local param=$(echo "$resultLog" | grep -m 1 -oE "${gexp}" | tr -d '[:space:]')

    echo $param
}

flagValueFromLog()
{
    local flag=$1
    local resultLog=$2
    # the -- of the flag needs to be escaped
    local gexp=$(echo "$flag=[^\ ]+" | sed 's/\-/\\\-/g')
    # look for the flag in the log
    local flagAndValue=$(echo "$resultLog" | grep -m 1 -oE "${gexp}" | tr -d '[:space:]')

    local value=$(echo "$flagAndValue" | grep -oE "=.*" | sed 's:=::g')

    if [[ ${opts[debug]} == "true" ]]; then echo "flagValueFromLog $flag = $value" > /dev/tty; fi

    echo $value
}

loadBase()
{
    local basePath=$1
    local resultLogName=$(ls $basePath | grep -oE sweep.*_result\.log)
    local resultLog=$(cat $basePath/$resultLogName)
    local value=""

    for param in "${!flags[@]}"; do
        if [[ $param != "sp" ]]; then
            value=$(flagValueFromLog ${flags[$param]} "$resultLog")
            defaults[$param]=$value
            if [[ ${opts[debug]} == "true" ]]; then echo "loadBase $param = $value" > /dev/tty; fi
        fi
    done
}

loadOverrides()
{
    for param in "${!defaults[@]}"; do
        if [[ ${opts[$param]} != "" ]]; then
            defaults[$param]=${opts[$param]}
            if [[ ${opts[debug]} == "true" ]]; then
                echo "loadBase $flag = $value" > /dev/tty
            fi
        fi
    done
}

reload()
{
    local reloadPath=$1
    local resultLogName=$(ls $reloadPath | grep -oE sweep.*_result\.log)
    local resultLog=$(cat $reloadPath/$resultLogName)
    local param=""
    local params=""

    for flag in "${flags[@]}"; do
        param=$(flagFromLog $flag "$resultLog")

        if [[ $flag == ${flags[sp]} ]]; then
            param="$flag=$reloadPath"
        fi
        if [[ $params != "" ]]; then
            params+=" "$param
        else
            params=$param
        fi
    done

    local lookup_arg=""
    if [[ ${opts["lookup"]} != "false" ]]; then
        lookup_arg="${flags[lf]}=${opts["lookup"]}"
    fi

    execWord2Vec $params --interactive=True --reload_path=$reloadPath $lookup_arg
}

main()
{
    parseOptions $*

    starttime=$SECONDS

    if [[ ${opts["base"]} != "" ]]; then
        loadBase ${opts["base"]} > /dev/null
    fi

    if [[ ${opts["overrides"]} == "true" ]]; then
        loadOverrides
    fi

    if [[ ${opts["fixed"]} == "true" ]]; then
        echo "run default"
        runDefault
    elif [[ ${opts["sweep"]} != "false" ]]; then
        echo "sweep"
        sweep
    elif [[ ${opts["reload"]} != "false" ]]; then
        echo "reloading"
        reload ${opts["reload"]}
    else
        echo "  Error: sweeper requires -f or -s or -r"
        exit 1
    fi

    endtime=$SECONDS

    elapse=$(($endtime - $starttime))
    echo " "
    echo "Completed: $(($elapse / 60 / 60))hrs $(($elapse / 60))m $(($elapse % 60))s"

    exit 0
}


#########################################################
main $*
