#!/bin/bash

PORT=$1
ADDRESS=$2

NMAP_OUTPUT=`nmap -sV -p$PORT $ADDRESS | grep $PORT/`

if [ "$NMAP_OUTPUT" != "" ]; then
	echo $NMAP_OUTPUT
else
	echo ""
fi
