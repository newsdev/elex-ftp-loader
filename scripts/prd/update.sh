#!/bin/bash
. /home/ubuntu/elex-ftp-loader/scripts/prd/_results.sh
. /home/ubuntu/elex-ftp-loader/scripts/prd/_views.sh

if [[ ! -z $1 ]] ; then 
    RACEDATE=$1 
fi

set_temp_tables

load_national_results

copy_results
views