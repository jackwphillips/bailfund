#!/usr/bin/env bash


DIR=/home/jackwphillips/projects/bailfund/bailfund_scrapy
cd $DIR
source "../venv/bin/activate"

ERROR=log_count/ERROR
LOG=/tmp/spiderlog.log
if test -f "$LOG"; then
    rm $LOG
fi

echo
echo Initiating scrapy

scrapy crawl docketspider &> $LOG
sleep 5

while grep $ERROR $LOG; do
    echo Unsuccessful. Trying again.
    scrapy crawl docketspider &> $LOG
    sleep 5 
done

echo
echo
echo Processing downloaded files
python3 scripts/file_processer.py ./pdfs

