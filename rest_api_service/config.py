import os

class Config():
    """
    Fields can overwrite in elements of `Flask::config`
        via `Flask::config::from_object(obj: Config)`
    """
    DB_NAME = os.getenv('POSTGRES_DB')
    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASS = os.getenv('POSTGRES_PASSWORD')
    # DB_HOST = os.getenv('POSTGRES_HOST')
    # DB_PORT = int(os.getenv('POSTGRES_PORT'))
    DB_HOST = "db-service"
    DB_PORT = 5432

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class ProdConfig(Config):
    pass

class DevConfig(Config):
    pass

