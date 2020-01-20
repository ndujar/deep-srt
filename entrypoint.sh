#!/bin/bash

./srt/build/srt-live-transmit udp://localhost:1234 "$MEDIUM://$RECEIVER_ADDRESS:$RECEIVER_PORT?latency=$LATENCY" -v -stats-report-frequency $REPORT_FREQUENCY -statsout -pf csv &
exec ffmpeg -f lavfi -i testsrc=duration=300:size=1280x720:rate=30 -c:v mpeg2video -b:v $FFMPEG_BITRATE -f mpegts "udp://127.0.0.1:1234?pkt_size=1316"

