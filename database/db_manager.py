"""Database manager for alLot application."""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base, User
import bcrypt


class DatabaseManager:
    """Manages database connection and initialization."""
    
    def __init__(self):
        """Initialize database manager."""
        self.db_path = self._get_db_path()
        self.engine = None
        self.Session = None
        self._initialize()
    
    def _get_db_path(self):
        """Get database file path."""
        # Store DB in AppData for Windows
        app_data = os.getenv('APPDATA')
        if app_data:
            db_dir = Path(app_data) / 'alLot'
            db_dir.mkdir(parents=True, exist_ok=True)
            return db_dir / 'allot.db'
        else:
            # Fallback to current directory
            return Path('allot.db')
    
    def _initialize(self):
        """Initialize database connection and create tables."""
        db_url = f'sqlite:///{self.db_path}'
        self.engine = create_engine(db_url, echo=False)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        
        # Create default admin user if not exists
        self._create_default_user()
    
    def _create_default_user(self):
        """Create default admin user."""
        session = self.Session()
        try:
            # Check if admin user exists
            existing_user = session.query(User).filter_by(username='admin').first()
            if not existing_user:
                # Hash default password
                password_hash = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
                
                # Create admin user
                admin_user = User(
                    username='admin',
                    password_hash=password_hash.decode('utf-8')
                )
                session.add(admin_user)
                session.commit()
                print("Default admin user created (username: admin, password: admin)")
        except Exception as e:
            session.rollback()
            print(f"Error creating default user: {e}")
        finally:
            session.close()
    
    def get_session(self):
        """Get a new database session."""
        return self.Session()
    
    def close(self):
        """Close database connection."""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()
