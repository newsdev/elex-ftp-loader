function set_live_tables {e
    echo "Setting live results tables."
    cat fields/results.txt | psql -h localhost -U elex -d elex_$RACEDATE
}

function set_temp_tables {
    echo "Setting temp results tables."
    cat fields/results_temp.txt | psql -h localhost -U elex -d elex_$RACEDATE
}

function load_national_results {
    echo "Getting data."
    elex-ftp $RACEDATE | psql -h localhost -U elex -d elex_$RACEDATE -c "COPY results_temp FROM stdin DELIMITER ',' CSV HEADER;"
}

function copy_results {
    echo "Copying results."
    psql elex_$RACEDATE -c "TRUNCATE results CASCADE; INSERT INTO results SELECT * FROM results_temp;"
}