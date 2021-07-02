#!/bin/bash
TODAY=$(date +%Y%m%d)
YEAR=$(date +%Y)

echo "$(date): Importing csv to db" | tee -a ./log/db.log

# import to temp table, deduplicate, drop temp table
sqlite3 hudomains.db <<EOF
.mode csv
.import unfiltered_csv/d_ido/$TODAY.csv hud_temp
INSERT OR IGNORE INTO hudomains(domain, igenylo, date) SELECT domain, igenylo, date FROM hud_temp;
DROP TABLE hud_temp;
--VACUUM;
EOF

echo "$(date): Exporting db to txt grouped by year" | tee -a ./log/db.log

# export to txt
# process last year on jan 1
if [ $(date +%m%d) -eq '0101' ]; then
	LASTYEAR=$((YEAR - 1))
	sqlite3 -header -list -separator ' ' hudomains.db "select domain, date from hudomains where date between '$LASTYEAR-01-01' and '$LASTYEAR-12-31' order by date, id;" > ./git/hudomains/$LASTYEAR.txt
fi

sqlite3 -header -list -separator ' ' hudomains.db "select domain, date from hudomains where date between '$YEAR-01-01' and '$YEAR-12-31' order by date, id;" > ./git/hudomains/$YEAR.txt
