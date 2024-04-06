import os
from typing import List

from flask import Flask, jsonify, make_response
from flask import request

from config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT
from db import db, Song, get_artist, get_release, search_by_title


app = Flask(__name__)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

db.init_app(app)

@app.route('/search-song', methods=['GET'])
def search_a_song():
    with app.app_context():
        print(f"Flask app: {app}")
        print(f"SQLAlchemy instance: {db}")
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

        Songs: List[Song] = Song.query.all()
        found = search_by_title(Songs, q)

        if found:
            status = 200
            return jsonify({
                'status': status,
                # 'id': found.id,
                'mbid': found.mbid,
                'song_title': found.song_title,
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

@app.route('/songs/<int:song_id>', methods=['GET'])
def get_song(song_id: int):
    with app.app_context():
        song = Song.query.get(song_id)
        if song is None:
            return jsonify({'error': 'Song not found'}), 404

        return jsonify({
            'id': song.id,
            'mbid': song.mbid,
            'song_title': song.song_title,
            'release_id': song.release_id,
            'artist_id': song.artist_id,
            'duration': song.duration
        })

@app.route('/are-you-up', methods=['GET'])
def are_you_up():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
