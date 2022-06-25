WORK_DIR=$1
FHS_CONTAINER_NAME=$2
FHS_PORT=$3

docker run -tdi --name "$FHS_CONTAINER_NAME" \
	-p $FHS_PORT:8080 \
	-v "$WORK_DIR"/conf-files/private:/root/federation-hosting-service/src/main/resources/private \
	-v "$WORK_DIR"/conf-files/application.properties:/root/federation-hosting-service/application.properties \
	fogbow/federation-hosting-service:latest

docker exec "$FHS_CONTAINER_NAME" /bin/bash -c "./mvnw spring-boot:run -X > log.out 2> log.err" &