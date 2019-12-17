docker rm transmitter-srt
docker build -f dockerfile-base -t base-srt:v1 . 
docker build -f dockerfile-transmitter -t transmitter-srt:v1 . 
docker run --volume="$(pwd)/stream":/stream --volume="$(pwd)/logs":/logs -p 1234:1234 --name transmitter-srt transmitter-srt:v1