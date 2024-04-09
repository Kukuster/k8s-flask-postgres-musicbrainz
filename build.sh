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

echo "POSTGRES_DB=$POSTGRES_DB"
echo "POSTGRES_USER=$POSTGRES_USER"
echo "ARTIST_NAME=$ARTIST_NAME"

build_version="$1"

if [ -z "$build_version" ]; then
    build_version="latest"
fi


context="default"
context="minikube"

minikube start
eval $(minikube docker-env)

kubectl delete secret app-parameters 2>&1 | grep -iv "notfound\|not found"
kubectl create secret generic app-parameters \
    "--from-literal=POSTGRES_DB=$POSTGRES_DB" \
    "--from-literal=POSTGRES_USER=$POSTGRES_USER" \
    "--from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD" \
    "--from-literal=ARTIST_NAME=$ARTIST_NAME" \
    "--from-literal=MB_USERAGENT_APP_NAME=$MB_USERAGENT_APP_NAME" \
    "--from-literal=MB_USERAGENT_APP_VERSION=$MB_USERAGENT_APP_VERSION" \
    "--from-literal=MB_USERAGENT_APP_CONTACT=$MB_USERAGENT_APP_CONTACT"

sleep 5


kubectl delete -n "$context" deployment db-service 2>&1 | grep -iv "notfound\|not found"
kubectl delete deployment db-service 2>&1 | grep -iv "notfound\|not found"
# kubectl delete pvc postgredb-pvc 2>&1 | grep -iv "notfound\|not found"
# kubectl delete pv postgredb-pv 2>&1 | grep -iv "notfound\|not found"
kubectl delete service db-service 2>&1 | grep -iv "notfound\|not found"

sleep 5

# kubectl apply -f ./db_service/postgres-pv.yaml
# kubectl apply -f ./db_service/postgres-pvc.yaml
kubectl apply -f ./db_service/db-service.yaml

sleep 9

# # connect to the shell in the db-service pod:
# kubectl exec -it $(kubectl get pods | grep '^db-service' | awk 'FNR == 1 {print $1}') -- bash


kubectl delete -n "$context" job python-task-runner 2>&1 | grep -iv "notfound\|not found"
kubectl delete job python-task-runner 2>&1 | grep -iv "notfound\|not found"
sleep 5
img="python-task-runner-image:$build_version"
docker build -t "$img" -f ./populate_task/Dockerfile ./populate_task/

sleep 4
kubectl apply -f ./populate_task/populate-task-job.yaml

# wait until pod starts by checking if name is empty
pod_name=""
while [ -z "$pod_name" ]; do
    pod_name=$(kubectl get pods --selector=job-name=python-task-runner --output=jsonpath='{.items[0].metadata.name}')
    sleep 1
done

# watch job's stdout:
kubectl logs -f $pod_name


# # connect to the shell in the python-task-runner pod:
# kubectl exec -it $(kubectl get pods | grep '^python-task-runner' | awk 'FNR == 1 {print $1}') -- bash

# wait until job finishes by grepping for status (because querying by "-o jsonpath=..." does not work for some reason)
job_complete=""
while [ -z "$job_complete" ]; do
    job_complete=$(kubectl get jobs python-task-runner -o jsonpath='{.status.conditions}' | grep -i "complete\|failed\|finish")
    sleep 1
done


sleep 1
kubectl delete -n "$context" deployment rest-api-service 2>&1 | grep -iv "notfound\|not found"
kubectl delete deployment rest-api-service 2>&1 | grep -iv "notfound\|not found"
kubectl delete service rest-api-service 2>&1 | grep -iv "notfound\|not found"
sleep 4
img="rest-api-service-image:$build_version"
docker build -t "$img" -f ./rest_api_service/Dockerfile ./rest_api_service/

kubectl apply -f ./rest_api_service/rest-api-service.yaml

# sleep 10
# # read logs from the rest-api-service pod:
# kubectl logs -f $(kubectl get pods | grep '^rest-api-service' | awk 'FNR==1 {print $1}')

