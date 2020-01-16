#/bin/bash
exec ./srt/build/srt-live-transmit udp://localhost:1234 $MEDIUM://$RECEIVER_ADDRESS:$RECEIVER_PORT -v -stats-report-frequency $REPORT_FREQUENCY -statsout -pf csv

