#!/bin/sh

cur_dir=`dirname  ${0}`

#检查log目录
log_dir=/data/log/interface
if [ ! -d $log_dir ]; then
    mkdir -p $log_dir
fi

#检查软链是否存在
ln_log_dir=$cur_dir/../log
if [ ! -L $ln_log_dir ]; then
    ln -s $log_dir $ln_log_dir
fi

for ini_file in `ls $cur_dir/../conf/*.ini`
do
    module=`echo $(basename $ini_file) | cut -d'.' -f1`
    master=uwsgi-$module-master
    worker=uwsgi-$module-worker

    count=`ps -ef | grep -w $master | grep -v "grep" | wc -l`
    #如果master进程不在了
    if [ $count -eq 0 ] ; then
        /usr/local/bin/uwsgi $cur_dir/../conf/$module.ini
    fi

done

time=`date "+%Y-%m-%d %H:%M:%S"`
echo $time > $cur_dir/../last_check
