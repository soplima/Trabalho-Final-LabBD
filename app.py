from flask import Flask
from extensions import Migrate, db
from config import Config
from models.artista import Artista
from models.usuario import Usuario
from models.playlist import Playlist
from models.musica import Musica
from models.musica_playlist import MusicaPlaylist
from routes.artista_routes import artista_bp
from routes.musica_routes import musica_bp
from routes.usuario_routes import usuario_bp
from routes.playlist_routes import playlist_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(artista_bp)
    app.register_blueprint(musica_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(playlist_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
