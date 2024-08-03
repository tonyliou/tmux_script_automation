#!/bin/bash
echo "Running $(basename $0)"

sudo tcpdump -i any udp port 41001 -n -X -v
