from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import text


class PostgresConnector:
    def __init__(self, db_cfg, environment):
        print(f"[DEBUG] Initializing PostgresConnector with environment: {environment}")
        self.db_cfg = db_cfg
        self.environment = environment.upper()
        self.ssh_tunnel = None

        ssh_cfg = self.db_cfg.get('ssh', {})
        print(f"[DEBUG] SSH config: {ssh_cfg}")
        use_ssh = ssh_cfg.get('enable', False) and (self.environment == "DEV")
        print(f"[DEBUG] use_ssh: {use_ssh}")
        if use_ssh:
            print(f"[DEBUG] Starting SSH tunnel to {ssh_cfg['ssh_host']}:{ssh_cfg.get('ssh_port', 272)} as {ssh_cfg['ssh_user']}")
            self.ssh_tunnel = SSHTunnelForwarder(
                (ssh_cfg['ssh_host'], int(ssh_cfg.get('ssh_port', 272))),
                ssh_username=ssh_cfg['ssh_user'],
                ssh_password=ssh_cfg.get('ssh_password'),
                ssh_pkey=ssh_cfg.get('ssh_pkey'),
                remote_bind_address=(self.db_cfg['host'], self.db_cfg['port']),
            )
            self.ssh_tunnel.start()
            local_host, local_port = self.ssh_tunnel.local_bind_host, self.ssh_tunnel.local_bind_port
            print(f"[DEBUG] SSH tunnel started. Local bind: {local_host}:{local_port}")
        else:
            local_host, local_port = self.db_cfg['host'], self.db_cfg['port']
            print(f"[DEBUG] Using direct DB connection to {local_host}:{local_port}")

        uri = f"postgresql+psycopg2://{db_cfg['user']}:{db_cfg['password']}@{local_host}:{local_port}/{db_cfg['database']}"
        print(f"[DEBUG] SQLAlchemy URI: {uri}")
        self.engine = create_engine(
            uri,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True
        )

    def get_conn(self):
        return self.engine.connect()

    def close(self):
        if self.ssh_tunnel:
            self.ssh_tunnel.stop()

def main():
    # Replace these values with your actual database/SSH configuration
 
    environment = 'DEV'  # or 'PROD' etc.

    connector = None
    try:
        connector = PostgresConnector(db_cfg, environment)
        with connector.get_conn() as conn:
            # Simple test query
            result = conn.execute(text('SELECT * from users_masteruser limit 10;'))
            for row in result:
                print(row)
        print("Connection and query successful.")
    except Exception as e:
        print("Error during DB connection/test:", e)
    finally:
        if connector:
            connector.close()
            print("Connection closed.")


if __name__ == '__main__':
    main()
