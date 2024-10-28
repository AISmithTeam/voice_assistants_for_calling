import os

# Database url configuration
#DATABASE_URL = "mysql+pymysql://root:jhyfn2001@localhost:3306/VoiceAssistant"
SECRET_KEY = "test"
DATABASE_URL = "mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}".format(
    host=os.getenv("MYSQL_HOST"),
    port=os.getenv("MYSQL_PORT"),
    db_name=os.getenv("MYSQL_DB"),
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
)