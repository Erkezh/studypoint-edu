
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Add the current directory to sys.path to make sure we can import app
sys.path.append(os.getcwd())

async def check_db():
    from app.core import config
    
    # Reload config to ensure we get the latest env vars
    import importlib
    importlib.reload(config)
    
    db_url = config.settings.database_url
    print(f"Checking database connection to: {db_url}")
    
    try:
        # Try connecting to the specific database
        engine = create_async_engine(str(db_url))
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Successfully connected to the database 'ixl'.")
        return True
    except Exception as e:
        print(f"Failed to connect to 'ixl': {e}")
        
    print("Attempting to connect to default 'postgres' database to check if 'ixl' exists...")
    
    # Try connecting to default 'postgres' db to create 'ixl'
    # We need to modify the URL to point to 'postgres' database instead of 'ixl'
    from sqlalchemy.engine.url import make_url
    url_obj = make_url(str(db_url))
    postgres_db_url = url_obj.set(database='postgres')
    
    try:
        engine = create_async_engine(postgres_db_url, isolation_level="AUTOCOMMIT")
        async with engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{url_obj.database}'"))
            if result.scalar():
                print(f"Database '{url_obj.database}' exists but connection failed earlier. Check permissions.")
                return False
            else:
                print(f"Database '{url_obj.database}' does not exist. Creating it...")
                await conn.execute(text(f"CREATE DATABASE {url_obj.database}"))
                print(f"Database '{url_obj.database}' created successfully.")
                return True
    except Exception as e:
        print(f"Failed to connect to 'postgres' database: {e}")
        return False

if __name__ == "__main__":
    try:
        if asyncio.run(check_db()):
            sys.exit(0)
        else:
            sys.exit(1)
    except ImportError:
        # custom logic in case app.core.config isn't easily importable, 
        # but since we are in backend dir it should be fine if we set pythonpath
        print("Could not import app.config. Please ensure you are running this from the backend directory.")
        sys.exit(1)
