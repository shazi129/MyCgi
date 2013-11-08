#!/bin/sh

cur_dir=`dirname  ${0}`
time=`date "+%Y-%m-%d %H:%M:%S"`
echo $time >> $cur_dir/../reload.trigger
