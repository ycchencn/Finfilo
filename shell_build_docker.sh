#rm -r ./job/df_cache/*
#rm -r ./service/cache/*
docker build -t finfilo-service --file ./install/Dockerfile .
docker compose up -d
# docker rmi $(docker images -aq)
