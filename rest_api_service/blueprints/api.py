import os
from typing import List

from flask import jsonify, make_response, Blueprint
from flask import request

from db import db, Track, get_artist, get_release, search_by_title


blueprint = Blueprint('api', __name__)

@blueprint.route('/search-track', methods=['GET'])
def search_a_track():
    q = request.args.get('q')
    if not q:
        status = 400
        return jsonify({
            'status': status,
            'error': 'Missing query parameter "q"'
        }), 400
        # response = make_response('Missing query parameter "q"', 400)
        # response.mimetype = "text/plain"
        # return response

    Tracks: List[Track] = Track.query.all()
    if len(Tracks) == 0:
        status = 500
        return jsonify({
            'status': status,
            'error': 'No tracks found in the database'
        }), 500
        # response = make_response('No tracks found in the database', 500)
        # response.mimetype = "text/plain"
        # return response
    found = search_by_title(Tracks, q)

    if found:
        status = 200
        return jsonify({
            'status': status,
            # 'id': found.id,
            'mbid': found.mbid,
            'track_title': found.track_title,
            # 'release_id': found.release_id,
            # 'artist_id': found.artist_id,
            'release_title': get_release(found.release_id).release_title,
            'artist_name': get_artist(found.artist_id).artist_name,
            'duration': found.duration
        })
        # response = make_response('', 200)
        # response.mimetype = "text/plain"
        # return response
    else:
        status = 404
        return jsonify({
            'status': status,
            'error': 'No match found'
        }), 404
        # response = make_response('No results', 404)
        # response.mimetype = "text/plain"
        # return response

@blueprint.route('/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id: int):
    track = Track.query.get(track_id)
    if track is None:
        return jsonify({'error': 'Track not found'}), 404

    return jsonify({
        'id': track.id,
        'mbid': track.mbid,
        'track_title': track.track_title,
        'release_id': track.release_id,
        'artist_id': track.artist_id,
        'duration': track.duration
    })

@blueprint.route('/are-you-up', methods=['GET'])
def are_you_up():
    return jsonify({'status': 'ok'})

