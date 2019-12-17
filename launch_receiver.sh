docker rm receiver-srt
docker build -f dockerfile-base -t base-srt:v1 . 
docker build -f dockerfile-receiver -t receiver-srt:v1 . 
docker run --volume="$(pwd)/stream":/stream --volume="$(pwd)/logs":/logs --name receiver-srt -p 4201:4201 receiver-srt:v1