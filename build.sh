#!/bin/bash

envfile="set-env.sh"
. "$envfile"
ec="$?"
if [ "$ec" -ne 0 ]; then
    echo "BUILD ERROR: Could not set environment variables from '$envfile'"
    echo "Please fill in file '$envfile' using '$envfile.example' as a template,"
    echo "  and make sure you have read permissions for '$envfile'"
    exit 1
fi

echo POSTGRES_DB=$POSTGRES_DB
echo POSTGRES_USER=$POSTGRES_USER
echo ARTIST_NAME=$ARTIST_NAME

build_version="$1"

if [ -z "$build_version" ]; then
    build_version="latest"
fi


context="default"
context="minikube"

minikube start
eval $(minikube docker-env)

kubectl delete secret app-parameters
kubectl create secret generic app-parameters \
    "--from-literal=POSTGRES_DB=$POSTGRES_DB" \
    "--from-literal=POSTGRES_USER=$POSTGRES_USER" \
    "--from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD" \
    "--from-literal=ARTIST_NAME=$ARTIST_NAME" \
    "--from-literal=MB_USERAGENT_APP_NAME=$MB_USERAGENT_APP_NAME" \
    "--from-literal=MB_USERAGENT_APP_VERSION=$MB_USERAGENT_APP_VERSION" \
    "--from-literal=MB_USERAGENT_APP_CONTACT=$MB_USERAGENT_APP_CONTACT"

sleep 5


kubectl delete -n "$context" deployment db-service
kubectl delete deployment db-service
kubectl delete pvc postgredb-pvc
kubectl delete pv postgredb-pv
kubectl delete service db-service

# kubectl apply -f ./db_service/postgres-pv.yaml
# kubectl apply -f ./db_service/postgres-pvc.yaml
kubectl apply -f ./db_service/db-service.yaml

sleep 5

# # connect to the shell in the db-service pod:
# kubectl exec -it $(kubectl get pods | grep '^db-service' | awk 'FNR == 1 {print $1}') -- bash


kubectl delete -n "$context" job python-task-runner
kubectl delete job python-task-runner
sleep 3
img="python-task-runner-image:$build_version"
docker build -t "$img" -f ./populate_task/Dockerfile ./populate_task/

# Start the job and watch stdout:
kubectl apply -f ./populate_task/populate-task-job.yaml
sleep 5
pod_name=$(kubectl get pods --selector=job-name=python-task-runner --output=jsonpath='{.items[0].metadata.name}')
kubectl logs -f $pod_name

# # connect to the shell in the python-task-runner pod:
# kubectl exec -it $(kubectl get pods | grep '^python-task-runner' | awk 'FNR == 1 {print $1}') -- bash


sleep 1
kubectl delete -n "$context" deployment rest-api-service
kubectl delete deployment rest-api-service
kubectl delete service rest-api-service
sleep 2
img="rest-api-service-image:$build_version"
docker build -t "$img" -f ./rest_api_service/Dockerfile ./rest_api_service/

kubectl apply -f ./rest_api_service/rest-api-service.yaml

# sleep 10
# # read logs from the rest-api-service pod:
# kubectl logs -f $(kubectl get pods | grep '^rest-api-service' | awk 'FNR==1 {print $1}')

