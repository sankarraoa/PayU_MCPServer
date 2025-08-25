import os
from db.base_connector import load_db_config
from db.postgres_connector import PostgresConnector
from sqlalchemy import text
from repository.user_repository import get_users



os.environ['APP_ENV'] = 'DEV'
os.environ['DB_PASSWORD'] = 'your_postgres_pwd'
os.environ['SSH_USER'] = 'your_ssh_user'
os.environ['SSH_PASSWORD'] = 'your_ssh_pwd'
os.environ['MYSQL_PASSWORD'] = 'your_mysql_pwd'

env, db_conns = load_db_config()

# For Postgres connection with SSH
pg_cfg = db_conns['pscore_postgres']
pg_db = PostgresConnector(pg_cfg, environment=env) 


with pg_db.get_conn() as conn:
    #rows = conn.execute(text("SELECT * from users_masteruser limit 10;")).fetchall()
    #print(f"Rows: {len(rows)}")
    users = get_users(conn, "9845267602")
    #print(f"Rows: {len(rows)}")

    for user in users:
        print(user)

pg_db.close()
