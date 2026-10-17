import os

import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "exam"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
    )
    return connection