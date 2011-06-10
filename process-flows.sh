#!/bin/bash

ARGII_DIR='/nsm/nfscripts/argii'
PORTFILE='/nsm/nfscripts/ports.lst'

#check to make sure today's report directory works
TDATE=`date +%Y-%m-%d`
NFDD='/opt/flows'

#make sure the daily directory is built
if [ ! -e "$NFDD/data/$TDATE" ]; then
	mkdir $NFDD/data/$TDATE
	mkdir $NFDD/data/$TDATE/feeds
	mkdir $NFDD/data/$TDATE/reports
	mkdir $NFDD/data/$TDATE/lts
	echo "Creating daily dir $NFDD/data/$TDATE"
fi

#process files
for file in `ls /opt/flows/incoming/`; do

	echo "Processing $file"
	TARGET_DIR=`echo $file | awk -F"_" '{print $2 "-" $3 "-" $4}'`
	
	#if dir does not exist for TARGET_DIR, create it:
	if [ ! -e "$NFDD/data/$TARGET_DIR" ]; then
		mkdir $NFDD/data/$TARGET_DIR
		mkdir $NFDD/data/$TARGET_DIR/feeds
		mkdir $NFDD/data/$TARGET_DIR/reports
		mkdir $NFDD/data/$TARGET_DIR/lts
	fi


	#cofile="$file.co"

	#first, do geoip location and append .co
	#/usr/local/bin/ralabel -f /etc/ralabel.conf -r /netflow/argus/raw-feeds/$file -w /netflow/argus/raw-feeds/$cofile

	#delete original file to save space
	#rm /netflow/argus/raw-feeds/$file
	
	#monitor ports
	#for port in $(cat $PORTFILE); do
	#	$ARGII_DIR/port-filter.sh /netflow/argus/raw-feeds/$cofile $port $NFDD/$TDATE/feeds/dport-$port.ar
	#done

	#for ip-range monitoring
	#$ARGII_DIR/range-filter.sh /netflow/argus/raw-feeds/$cofile /nsm/nfscripts/bannerwatch/prod.acl $NFDD/$TDATE/feeds/banner-prod.ar

	#finally, delete the original ra file
	cat $NFDD/incoming/$file | gzip > $NFDD/data/$TARGET_DIR/lts/$file.gz
	rm $NFDD/incoming/$file
done
