#!/bin/bash

./srt/build/srt-live-transmit udp://localhost:1234 "$MEDIUM://$RECEIVER_ADDRESS:$RECEIVER_PORT?latency=$LATENCY" -v -stats-report-frequency $REPORT_FREQUENCY -statsout -pf csv &
exec ffmpeg -f rawvideo -video_size 1280x720 -pixel_format yuv420p -framerate $FFMPEG_BITRATE -i /dev/urandom -codec:a copy -f mpegts "udp://127.0.0.1:1234?pkt_size=1316"

