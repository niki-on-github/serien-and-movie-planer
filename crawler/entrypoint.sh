#!/bin/bash

echo "starting..."
sleep 2
while : ; do
    python3 /app/serien-and-movie-crawler.py
    sleep $((24*60*60))
done
