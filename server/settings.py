import os

# Database url configuration
SECRET_KEY = "test"
DATABASE_URL = "mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}".format(
    host=os.getenv("MYSQL_HOST"),
    port=os.getenv("MYSQL_PORT"),
    db_name=os.getenv("MYSQL_DB"),
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
)