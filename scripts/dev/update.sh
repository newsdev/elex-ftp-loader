#!/bin/bash
. scripts/dev/_results.sh
. scripts/dev/_views.sh

if [[ ! -z $1 ]] ; then 
    RACEDATE=$1 
fi

set_temp_tables

load_national_results

copy_results
views