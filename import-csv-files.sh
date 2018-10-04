#!/bin/bash -e -x

for year in 2016 2017 2018; do
    ~/lib/icsv2ledger/icsv2ledger.py -q -a absa-checking transaction-history/absa-checking-$year.csv generated/absa-checking-$year.ledger
    ~/lib/icsv2ledger/icsv2ledger.py -q -a absa-saving transaction-history/absa-saving-$year.csv generated/absa-saving-$year.ledger
    ~/lib/icsv2ledger/icsv2ledger.py -q -a absa-creditcard transaction-history/absa-creditcard-$year.csv generated/absa-creditcard-$year.ledger
    ~/lib/icsv2ledger/icsv2ledger.py -q -a dkb-giro transaction-history/dkb-giro-$year.csv generated/dkb-giro-$year.ledger
    ~/lib/icsv2ledger/icsv2ledger.py -q -a dkb-creditcard transaction-history/dkb-creditcard-$year.csv generated/dkb-creditcard-$year.ledger
done
