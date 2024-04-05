import os
from typing import List

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import request
from Levenshtein import distance

from Songs import db, Song, search_by_title


# DB_NAME = os.getenv('DB_NAME')
# DB_USER = os.getenv('DB_USER')
# DB_PASS = os.getenv('DB_PASS')
# DB_HOST = os.getenv('DB_HOST')
# DB_PORT = os.getenv('DB_PORT')
DB_NAME = "songsdb"
DB_USER = "user12345user"
DB_PASS = "12345pass12345word12345"
DB_HOST = "db-service"
DB_PORT = 5432
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

db.init_app(app)

print(f"Flask app: {app}")
print(f"SQLAlchemy instance: {db}")

@app.route('/search-song', methods=['GET'])
def search_a_song():
    with app.app_context():
        print(f"Flask app: {app}")
        print(f"SQLAlchemy instance: {db}")
        q = request.args.get('q')
        if not q:
            return jsonify({'error': 'Missing query parameter "q"'}), 400

        Songs: List[Song] = Song.query.all()
        found = search_by_title(Songs, q)

        if found:
            return jsonify({
                'id': found.id,
                'mbid': found.mbid,
                'song_title': found.song_title,
                'release_id': found.release_id,
                'artist_id': found.artist_id,
                'duration': found.duration
            })
        else:
            return jsonify({'error': 'No match found'}), 404


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
