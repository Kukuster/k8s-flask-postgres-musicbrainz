# Music Metadata Processing System with MusicBrainz

## Public API

### Base endpoint
http://35.225.52.104:60080


### Endpoints

#### `GET /search-song`

Searches a song by song title and returns song metadata if found.

Request parameters:
| Name | Type | Mandatory | Description |
| -------- | -------- | -------- | -------- |
| `q`   | STRING   | yes   | search query that is tested against the song titles in the database. If a song with similar name is present in the database, returns the best match. |

The only required response parameter is `status`, other response parameters depend on its value.

Response parameters for status code `200`:
| Name | Type | Description |
| -------- | -------- | -------- |
| `status`   | INTEGER   | HTTP status code (200) |
| `artist_name`   | STRING   | name of the artist |
| `duration`   | STRING   | time length of the song in the format 'mm:ss' |
| `mbid`   | STRING   | MusicBrainz UUID (a.k.a. mbid) of the song |
| `release_title`   | STRING   | name of the release that includes the song. The database only assigns one release per a song with a particular `song_title` |
| `song_title`   | STRING   | name of the song |


Response parameters for status code `4xx`:
| Name | Type | Description |
| -------- | -------- | -------- |
| `status`   | INTEGER   | HTTP status code (4xx) |
| `error`   | STRING   | explanation |

---

Request example:

`curl http://35.225.52.104:60080/search-song?q=radeoactive`

Response example:

```json
{
  "artist_name": "Imagine Dragons",
  "duration": "3:07",
  "mbid": "bd61eda3-eb77-4634-ba66-4a084f7f8455",
  "release_title": "Night Visions",
  "song_title": "Radioactive",
  "status": 200
}
```

Request example:

`curl http://35.225.52.104:60080/search-song?q=radeeaeaoactive`

Response example:

```json
{
  "error": "No match found",
  "status": 404
}
```



## Build from source and run

### 1. create `set-env.sh` file with env variables, based on `set-env.sh.example`

### 2. build for your environment

#### A) Locally (minikube)
`bash build.sh`

if pods started successfully and services are running, check ip address of the service with `minikube ip`. Address of the REST API service will be the ip address from its output with the `30080` port.

#### B) on Google Kubernetes Engine (GKE)
`bash build-gpc-gke.sh`

