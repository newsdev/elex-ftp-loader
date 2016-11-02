#!/bin/bash
. scripts/dev/_results.sh
. scripts/dev/_views.sh

if [[ ! -z $1 ]] ; then 
    RACEDATE=$1 
fi

if [ -f /tmp/elex_loader_timeout.sh ]; then
    . /tmp/elex_loader_timeout.sh
fi

if [[ -z $ELEX_LOADER_TIMEOUT ]] ; then
    ELEX_LOADER_TIMEOUT=60
fi

for (( i=1; i<100000; i+=1 )); do

    if [ -f /tmp/elex_loader_timeout.sh ]; then
        . /tmp/elex_loader_timeout.sh
    fi

    echo "Timeout:" $ELEX_LOADER_TIMEOUT"s"
    
    SECONDS=0

    TIMESTAMP=$(date +"%s")

    set_temp_tables

    load_national_results

    copy_results
    views

    echo "Results time elapsed:" $SECONDS"s"

    echo "Total time elapsed:" $SECONDS"s"

    sleep $ELEX_LOADER_TIMEOUT

done