#!/bin/bash

echo "starting..."
sleep 30 # gitve postgres docker time to init
while : ; do
    python3 /app/serien-and-movie-crawler.py
    sleep $((24*60*60))
done
