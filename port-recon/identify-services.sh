#!/bin/bash

#this script accepts stdin from port-recon and checks each address to see if the port is opened.

while read line; do
	PORT=`echo $line | awk -F" " '{print $1}'`
	ADDR=`echo $line | awk -F" " '{print $2}'`
	STATUS=`port-confirm.sh $PORT $ADDR`
        if [ "$STATUS" != "" ]; then
            echo "$ADDR $STATUS"
        fi
done
