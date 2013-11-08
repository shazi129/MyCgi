#!/bin/sh

cur_dir=`dirname  ${0}`

for ini_file in `ls $cur_dir/../conf/*.ini`
do
    module=`echo $(basename $ini_file) | cut -d'.' -f1`
    master=uwsgi-$module-master
    worker=uwsgi-$module-worker

    count=`ps -ef | grep -w $master | grep -v "grep" | wc -l`
    if [ $count -ne 0 ] ; then
         ps -ef | grep -w $master | grep -v grep | awk -F ' ' '{print $2}' | xargs kill -9
         ps -ef | grep -w $worker | grep -v grep | awk -F ' ' '{print $2}' | xargs kill -9
    fi

done
