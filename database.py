import pymysql
import config

ssl_config = None
if config.MYSQL_SSL:
    ssl_config = {'ssl': {}}

connection = pymysql.connect(
    host=config.MYSQL_HOST,
    port=config.MYSQL_PORT,
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD,
    database=config.MYSQL_DB,
    ssl=ssl_config,
    cursorclass=pymysql.cursors.DictCursor
)

print("Database Connected Successfully!")