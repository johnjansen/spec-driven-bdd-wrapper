"""
Example partial implementation showing one method working.

Copy this into generated_code/api.py to see the wrapper in action.
"""

import bcrypt
import hashlib


class MemoryUserStorage:
    """
    In-memory storage for users.
    """
    
    def __init__(self):
        self.users = {}  # Store users: id -> user_data
        self.next_id = 1
        self.emails = set()  # Track emails for duplicate checking
    
    def create_user(self, email: str, password_hash: str) -> int:
        """
        Create a new user.
        
        Args:
            email: User's email address
            password_hash: Hashed password (not plaintext!)
        
        Returns:
            User ID
        """
        user_id = self.next_id
        self.next_id += 1
        self.users[user_id] = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash
        }
        self.emails.add(email)
        return user_id
    
    def get_user(self, user_id: int) -> dict:
        """
        Get user by ID.
        
        Returns:
            User dict or None if not found
        """
        return self.users.get(user_id)
    
    def update_user(self, user_id: int, updates: dict) -> bool:
        """
        Update user fields.
        
        Returns:
            True if updated, False if not found
        """
        if user_id in self.users:
            self.users[user_id].update(updates)
            return True
        return False
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete user by ID.
        
        Returns:
            True if deleted, False if not found
        """
        if user_id in self.users:
            user = self.users[user_id]
            self.emails.remove(user["email"])
            del self.users[user_id]
            return True
        return False
    
    def email_exists(self, email: str) -> bool:
        """Check if email is already in use."""
        return email in self.emails


class UserAPI:
    """
    User management API.
    """
    
    def __init__(self, storage: MemoryUserStorage):
        self.storage = storage
    
    def create_user(self, email: str, password: str) -> dict:
        """
        Create a new user with email and password.
        
        MUST hash password before storage!
        
        Returns:
            {
                "success": True,
                "user": {"id": 123, "email": "user@example.com"}
            }
            OR
            {
                "success": False,
                "error": "Error message"
            }
        """
        # Input validation
        if not email or not password:
            return {
                "success": False,
                "error": "Email and password are required"
            }
        
        # Check for duplicate email
        if self.storage.email_exists(email):
            return {
                "success": False,
                "error": "Email already exists"
            }
        
        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user
        user_id = self.storage.create_user(email, password_hash)
        
        user = self.storage.get_user(user_id)
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"]
                # Don't include password_hash in response!
            }
        }
    
    def get_user(self, user_id: int) -> dict:
        """
        Get user by ID.
        
        Returns:
            {
                "success": True,
                "user": {"id": 123, "email": "user@example.com"}
            }
            OR
            {
                "success": False,
                "error": "User not found"
            }
        
        NOTE: Password should NOT be in the response!
        """
        user = self.storage.get_user(user_id)
        
        if user is None:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Return user without password
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"]
            }
        }
    
    def update_user(self, user_id: int, updates: dict) -> dict:
        """
        Update user fields (e.g., email).
        
        Returns:
            {
                "success": True,
                "user": {...}
            }
            OR
            {
                "success": False,
                "error": "Error message"
            }
        """
        user = self.storage.get_user(user_id)
        
        if user is None:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # If updating email, check for duplicates (excluding current user)
        if "email" in updates and updates["email"] != user["email"]:
            if self.storage.email_exists(updates["email"]):
                return {
                    "success": False,
                    "error": "Email already exists"
                }
        
        # Update user
        if self.storage.update_user(user_id, updates):
            updated_user = self.storage.get_user(user_id)
            return {
                "success": True,
                "user": {
                    "id": updated_user["id"],
                    "email": updated_user["email"]
                }
            }
        
        return {
            "success": False,
            "error": "Failed to update user"
        }
    
    def delete_user(self, user_id: int) -> dict:
        """
        Delete user by ID.
        
        Returns:
            {
                "success": True
            }
            OR
            {
                "success": False,
                "error": "Error message"
            }
        """
        if self.storage.delete_user(user_id):
            return {
                "success": True
            }
        
        return {
            "success": False,
            "error": "User not found"
        }


# For testing
if __name__ == "__main__":
    storage = MemoryUserStorage()
    api = UserAPI(storage)
    
    # Test create
    result = api.create_user("alice@example.com", "password123")
    print("Create user:", result)
    
    # Test get
    if result["success"]:
        user_id = result["user"]["id"]
        get_result = api.get_user(user_id)
        print("Get user:", get_result)
    
    # Test duplicate
    duplicate = api.create_user("alice@example.com", "anotherpass")
    print("Duplicate email:", duplicate)
    
    print("\n✅ All methods implemented!")
    print("\nTo run tests:")
    print("  python ../behave_wrapper.py --ollama-model llama3.1")