#!/bin/bash
tshark -i eth0 -f "port $RECEIVER_PORT" -s 1500 -w rc-vSRT.pcapng &
exec ./bin/srt-xtransmit generate "srt://$RECEIVER_ADDRESS:$RECEIVER_PORT?transtype=live&rcvbuf=1000000000&sndbuf=1000000000" --msgsize 1316 --sendrate $SENDRATE --duration 10s --statsfile /logs/stats-snd.csv --statsfreq $REPORT_FREQUENCY


