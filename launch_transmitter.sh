docker build -f dockerfile-base -t base-srt:v1 . 
docker build -f dockerfile-transmitter -t transmitter-srt:v1 . 
docker run --volume="$(pwd)/stream":/stream --volume="$(pwd)/logs":/logs --device=/dev/video0:/dev/video0 -p 5000:5000 --name transmitter-srt transmitter-srt:v1