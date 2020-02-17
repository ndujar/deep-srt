docker rm transmitter-srt
docker build -f dockerfile-base -t base-srt:v2 . 
docker build -f dockerfile-transmitter -t transmitter-srt:v2 . 
docker run --privileged --network SRT-network --volume="$(pwd)/logs":/logs --name transmitter-srt transmitter-srt:v2