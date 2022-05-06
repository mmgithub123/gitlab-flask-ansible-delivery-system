#!/bin/bash

date_week_ago=`date -d '-7 day' +%F`
date_week_ago_cmp=${date_week_ago//-/}
date_week_ago_timestamp=`date -d "$date_week_ago_cmp" +%s`

message_arr=$(ls -lah /var/log/ |grep message  |awk '{print $9}' |grep -)
arr=($message_arr)
for s in ${arr[@]}
do
log_date=${s#*-}
log_date_timestamp=`date -d "$log_date" +%s`
if [ $date_week_ago_timestamp -gt $log_date_timestamp ];then
   echo "cd /var/log && rm -f messages-$log_date"
   cd /var/log && rm -f messages-$log_date
fi
done
