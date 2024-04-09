# Music Metadata Processing System with MusicBrainz

## Public API

### Base endpoint
http://34.123.189.132:60080


### Endpoints

#### `GET /search-track`

Searches a track by track title and returns track metadata if found.

Request parameters:
| Name | Type | Mandatory | Description |
| -------- | -------- | -------- | -------- |
| `q`   | STRING   | yes   | search query that is tested against the track titles in the database. If a track with similar name is present in the database, returns the best match. |

The only required response parameter is `status`, other response parameters depend on its value.

Response parameters for status code `200`:
| Name | Type | Description |
| -------- | -------- | -------- |
| `status`   | INTEGER   | HTTP status code (200) |
| `artist_name`   | STRING   | name of the artist |
| `duration`   | STRING   | time length of the track in the format 'mm:ss' |
| `mbid`   | STRING   | MusicBrainz UUID (a.k.a. mbid) of the track |
| `release_title`   | STRING   | name of the release that includes the track. The database only assigns one release per a track with a particular `track_title` |
| `track_title`   | STRING   | name of the track |


Response parameters for status codes `4xx`&`5xx`:
| Name | Type | Description |
| -------- | -------- | -------- |
| `status`   | INTEGER   | HTTP status code (4xx/5xx) |
| `error`   | STRING   | explanation |

---

Request example:

`curl http://34.123.189.132:60080/search-track?q=radeoactive`

Response example:

```json
{
  "artist_name": "Imagine Dragons",
  "duration": "3:06",
  "mbid": "4d28f3d7-6e11-317e-9085-407c931211b9",
  "release_title": "Night Visions",
  "track_title": "Radioactive",
  "status": 200
}
```

Request example:

`curl http://34.123.189.132:60080/search-track?q=radeeaeaoactive`

Response example:

```json
{
  "error": "No match found",
  "status": 404
}
```



## Build from source and run

### 1. create `set-env.sh` file with env variables
Use `set-env.sh.example` as an example

### (optionally) 2. test

The tests do not rely on the k8s environment. You can use your python installed on your system.

For the first run, I recommend creating a python venv and install the dependencies for both python pods:
```bash
python -m venv venv; # python 3.8 and 3.12 work
. venv/bin/activate

pip install -r populate_task/requirements.txt
pip install -r rest_api_service/requirements.txt
```

Then, run tests:
```bash
. venv/bin/activate
. set-env.sh

 #1 
python populate_task/test.py
 #2 
python rest_api_service/test.py 
```

### 3. build and run for your k8s environment
:grey_exclamation: Requires installed `docker` and `kubectl`

#### A) Locally (minikube)
:grey_exclamation: Requires installed `minikube`

`minikube` requires non-root docker access. You may need to execute `sudo usermod -aG docker $USER && newgrp docker` to add your user to docker group [[R]](https://github.com/kubernetes/minikube/issues/7903#issuecomment-802493269)

Run:

`bash build.sh`

if pods started successfully and services are running, check ip address of the service by running `minikube ip`. The address of the REST API service will be the ip address from its output with the `30080` port.

#### B) on Google Kubernetes Engine (GKE)
:grey_exclamation: Requires installed `gcloud` and logged in to `gcloud` [[R]](https://cloud.google.com/sdk/docs/install-sdk), and a k8s cluster created in [Google Kubernetes Engine console](https://console.cloud.google.com/kubernetes/list/overview) with corresponding credentials specified in `set-env.sh`.

Run:

`bash build-gpc-gke.sh`

if pods started successfully and services are running, check the external ip address of the REST API service by running `kubectl get services`. GCP GKE will automatically assign a `EXTERNAL-IP` field to `rest-api-service` shortly after pods start.

Use that `EXTERNAL-IP` with the port `60080` as an endpoint base for the REST API service. (In my case, `EXTERNAL-IP` is 34.123.189.132)

