import os

DB_NAME = os.getenv('POSTGRES_DB', "")
DB_USER = os.getenv('POSTGRES_USER', "")
DB_PASS = os.getenv('POSTGRES_PASSWORD', "")
# DB_HOST = os.getenv('POSTGRES_HOST')
# DB_PORT = os.getenv('POSTGRES_PORT')
DB_HOST = "db-service"
DB_PORT = 5432

ARTIST_NAME = os.getenv('ARTIST_NAME', "")

MB_USERAGENT_APP_NAME = os.getenv('MB_USERAGENT_APP_NAME', "")
MB_USERAGENT_APP_VERSION = os.getenv('MB_USERAGENT_APP_VERSION', "")
MB_USERAGENT_APP_CONTACT = os.getenv('MB_USERAGENT_APP_CONTACT', "")
