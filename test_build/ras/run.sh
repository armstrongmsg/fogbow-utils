WORK_DIR=$1
RAS_CONTAINER_NAME=$2
RAS_PORT=$3

docker run -tdi --name "$RAS_CONTAINER_NAME" \
	-p $RAS_PORT:8080 \
	-v "$WORK_DIR"/conf-files/private:/root/resource-allocation-service/src/main/resources/private \
	-v "$WORK_DIR"/conf-files/application.properties:/root/resource-allocation-service/application.properties \
	fogbow/resource-allocation-service:latest

docker exec "$RAS_CONTAINER_NAME" /bin/bash -c "./mvnw spring-boot:run -X > log.out 2> log.err" &