docker rm receiver-srt
docker build -f dockerfile-base -t base-srt:v2 . 
docker build -f dockerfile-receiver -t receiver-srt:v2 . 
docker run --network SRT-network --volume="$(pwd)/logs":/logs --name receiver-srt receiver-srt:v2