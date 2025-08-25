import os
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables from .env file
load_dotenv()

# Import your existing modules
from db.base_connector import load_db_config  
from db.postgres_connector import PostgresConnector
from repository.user_repository import get_users

def main():
    """Test your existing database setup"""
    print("🧪 Testing PayU Finance Database Connection...")
    
    # Set environment variables (now loaded from .env)
    os.environ['APP_ENV'] = os.getenv('APP_ENV', 'DEV')
    os.environ['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '')
    os.environ['SSH_USER'] = os.getenv('SSH_USER', '')
    os.environ['SSH_PASSWORD'] = os.getenv('SSH_PASSWORD', '')
    os.environ['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
    
    try:
        # Load database configuration
        print("📋 Loading database configuration...")
        env, db_conns = load_db_config()
        print(f"✅ Environment: {env}")
        
        # Get PostgreSQL configuration
        pg_cfg = db_conns['pscore_postgres']
        print("✅ PostgreSQL configuration loaded")
        
        # Create database connector
        print("🔌 Connecting to database...")
        pg_db = PostgresConnector(pg_cfg, environment=env)
        
        # Test the connection
        print("🧪 Testing database connection...")
        with pg_db.get_conn() as conn:
            # Test with a simple query first
            print("📊 Testing simple query...")
            result = conn.execute(text("SELECT 1 as test")).fetchone()
            print(f"✅ Simple query successful: {result}")
            
            # Test your repository function
            print("👥 Testing user search...")
            users = get_users(conn, "9845267602")
            print(f"✅ Found {len(users)} users")
            
            # Print first user (if any) 
            if users:
                print("📝 Sample user data:")
                for key, value in users[0].items():
                    # Truncate long values for display
                    display_value = str(value)[:50] + "..." if len(str(value)) > 50 else value
                    print(f"   {key}: {display_value}")
            else:
                print("⚠️  No users found with that search term")
        
        # Close connection
        pg_db.close()
        print("✅ Connection closed successfully")
        print("\n🎉 Your database setup is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your .env file has correct credentials")
        print("2. Ensure your database is accessible")
        print("3. Verify SSH connection if using tunneling")
        print("4. Check config/databases.yaml exists and is correct")

if __name__ == "__main__":
    main()
