#! /bin/bash

# dnnotion engineering
# by: mark r. cass
# date: mar/1/2018
# description: functions and data for hyperparamter data

hparamdata_get_value()
{
   local name="$1"; local hparams="$2"

   local pvalue="$(echo "$hparams" | grep "$name")"

   if [[ "$pvalue" != "" ]]; then
      pvalue="$(echo $pvalue | awk '{print $2}')"
   fi
   echo "$pvalue"
}

hparamdata_lines_above()
{
   local name="$1"

   local -A hparamdata_table_lines_above=(
   [da]=1
   [db]=2
   [dc]=3
   [de]=4
   [df]=5
   [di]=6
   [dl]=7
   [dm]=8
   [dn]=9
   [do]=10
   [dr]=11
   [ds]=12
   [dw]=13
   [dx]=14
   [fa]=15
   [fb]=16
   [fd]=17
   [ff]=18
   [fm]=19
   [fu]=20
   [fw]=21
   [ld]=22
   [le]=23
   [li]=24
   [lp]=25
   [lr]=26
   [ls]=27
   [ma]=28
   [md]=29
   [mt]=30
   [o1]=31
   [o2]=32
   [oa]=33
   [ob]=34
   [of]=35
   [om]=36
   [on]=37
   [ou]=38
   [pd]=39
   [pn]=40
   [ra]=41
   [rb]=42
   [rc]=43
   [rd]=44
   [ro]=45
   [rp]=46
   [rr]=47
   [rt]=48
   [rw]=49
   [sg]=50
   [sp]=51
   [st]=52
   [tb]=53
   [tc]=54
   [td]=55
   [te]=56
   [tf]=57
   [tg]=58
   [th]=59
   [ti]=60
   [tj]=61
   [tk]=62
   [tl]=63
   [tm]=64
   [to]=65
   [tr]=66
   [ts]=67
   [tt]=68
   [tv]=69
   [wa]=70
   [wc]=71
   [wd]=72
   [we]=73
   [wl]=74
   [wn]=75
   [ws]=76
   [wv]=77
   [wy]=78
)

   echo "${hparamdata_table_lines_above[$name]}"
}

hparamdata_lines_below()
{
   local name="$1"
   local -A hparamdata_table_lines_below=(
   [da]=77
   [db]=76
   [dc]=75
   [de]=74
   [df]=73
   [di]=72
   [dl]=71
   [dm]=70
   [dn]=69
   [do]=68
   [dr]=67
   [ds]=66
   [dw]=65
   [dx]=64
   [fa]=63
   [fb]=62
   [fd]=61
   [ff]=60
   [fm]=59
   [fu]=58
   [fw]=57
   [ld]=56
   [le]=55
   [li]=54
   [lp]=53
   [lr]=52
   [ls]=51
   [ma]=50
   [md]=49
   [mt]=48
   [o1]=47
   [o2]=46
   [oa]=45
   [ob]=44
   [of]=43
   [om]=42
   [on]=41
   [ou]=40
   [pd]=39
   [pn]=38
   [ra]=37
   [rb]=36
   [rc]=35
   [rd]=34
   [ro]=33
   [rp]=32
   [rr]=31
   [rt]=30
   [rw]=29
   [sg]=28
   [sp]=27
   [st]=26
   [tb]=25
   [tc]=24
   [td]=23
   [te]=22
   [tf]=21
   [tg]=20
   [th]=19
   [ti]=18
   [tj]=17
   [tk]=16
   [tl]=15
   [tm]=14
   [to]=13
   [tr]=12
   [ts]=11
   [tt]=10
   [tv]=9
   [wa]=8
   [wc]=7
   [wd]=6
   [we]=5
   [wl]=4
   [wn]=3
   [ws]=2
   [wv]=1
   [wy]=0
)
   echo "${hparamdata_table_lines_below[$name]}"
}