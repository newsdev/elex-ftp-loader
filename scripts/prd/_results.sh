function set_live_tables {
    cat fields/results.txt | psql -h localhost -U elex -d elex_$RACEDATE
}

function set_temp_tables {
    cat fields/results_temp.txt | psql -h localhost -U elex -d elex_$RACEDATE
}

function load_national_results {
    elex-ftp $RACEDATE | psql -h localhost -U elex -d elex_$RACEDATE -c "COPY results_temp FROM stdin DELIMITER ',' CSV HEADER;"
}

function copy_results {
    psql elex_$RACEDATE -c "TRUNCATE results CASCADE; INSERT INTO results SELECT * FROM results_temp;"
}