"""Authentication service for alLot."""
import bcrypt
from database.models import User
from database.db_manager import db_manager


class AuthService:
    """Handles user authentication."""
    
    @staticmethod
    def authenticate(username, password):
        """
        Authenticate user with username and password.
        
        Args:
            username: Username string
            password: Password string
            
        Returns:
            User object if authentication successful, None otherwise
        """
        session = db_manager.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return user
            return None
        finally:
            session.close()
    
    @staticmethod
    def change_password(username, old_password, new_password):
        """
        Change user password.
        
        Args:
            username: Username string
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple (success: bool, message: str)
        """
        session = db_manager.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            
            if not user:
                return False, "User not found"
            
            # Verify old password
            if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return False, "Current password is incorrect"
            
            # Hash and set new password
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.password_hash = new_hash.decode('utf-8')
            
            session.commit()
            return True, "Password changed successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error changing password: {str(e)}"
        finally:
            session.close()
