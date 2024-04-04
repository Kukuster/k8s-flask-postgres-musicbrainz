#!/bin/bash
# set -e # exit immediately if a command exits with a non-zero status.

build_version="$1"
# if [ -z "$build_version" ]; then
#     echo "Usage: $0 <build_version>"
#     echo " <build_version> has to be compatible with the docker tag format"
#     exit 1
# fi
if [ -z "$build_version" ]; then
    build_version="latest"
fi

# images=("db_service" "populate_task" "rest_api_service")

# # Build all the images in the project
# for image in ${images[@]}; do
#     docker build -t "coxittest_${image}":"$build_version" -f "${image}/Dockerfile" "${image}/"
# done


# docker build -t coxittest_populate_task:0.1 -f "populate_task/Dockerfile" "populate_task/"


context="default"
context="minikube"

minikube start
eval $(minikube docker-env)

sleep 5


kubectl delete -n "$context" deployment db-service
kubectl delete deployment db-service
kubectl delete pvc postgredb-pvc
kubectl delete pv postgredb-pv

kubectl apply -f ./db_service/postgres-pv.yaml
kubectl apply -f ./db_service/postgres-pvc.yaml
kubectl apply -f ./db_service/db-service.yaml

sleep 3

# kubectl exec -it $(kubectl get pods | grep '^db-service' | awk 'FNR == 1 {print $1}') -- bash


kubectl delete -n "$context" job python-task-runner
kubectl delete job python-task-runner
docker build -t python-task-runner-image:"$build_version" -f ./populate_task/Dockerfile ./populate_task/

# Start the job and watch stdout:
kubectl apply -f ./populate_task/populate-task-job.yaml
sleep 5
pod_name=$(kubectl get pods --selector=job-name=python-task-runner --output=jsonpath='{.items[0].metadata.name}')
kubectl logs -f $pod_name

# kubectl exec -it $(kubectl get pods | grep '^python-task-runner' | awk 'FNR == 1 {print $1}') -- bash
