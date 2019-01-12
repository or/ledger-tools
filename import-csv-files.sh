#!/bin/bash -e

for year in $(seq 2016 $(date +%Y)); do
    for t in absa-checking absa-saving absa-creditcard dkb-giro dkb-creditcard; do
        echo "importing ${t}-${year}..."
        in_file="transaction-history/${t}-${year}.csv"
        out_file="generated/${t}-${year}.ledger"
        if [ -f "$in_file" ]; then
            ~/lib/icsv2ledger/icsv2ledger.py -q -a $t $in_file $out_file
        fi
    done
done
