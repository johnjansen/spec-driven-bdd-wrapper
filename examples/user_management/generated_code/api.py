"""
TODO: Implement UserAPI for spec-driven development test

This is a placeholder. The AI agent should implement:
1. MemoryUserStorage - in-memory user storage
2. UserAPI - REST-like API for user management

Requirements from spec:
- Create user with email and password
- Fetch user by ID
- Update user (e.g., email)
- Delete user
- Passwords must be hashed (use bcrypt or similar)
- Duplicate emails should be rejected
- Return JSON-like responses with success/error status

Run tests with: python behave_wrapper_v2.py (includes satisfaction scoring!)
"""


class MemoryUserStorage:
    """
    In-memory storage for users.
    Implement this class to store users with hashed passwords.
    """

    def __init__(self):
        self.users = {}  # Store users: id -> user_data
        self.next_id = 1

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
            del self.users[user_id]
            return True
        return False


class UserAPI:
    """
    User management API.
    Implementation should:
    - Hash passwords before storage
    - Validate inputs
    - Return appropriate success/error responses
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
        # TODO: Implement password hashing (e.g., bcrypt)
        # TODO: Check for duplicate emails
        # TODO: Return appropriate response
        raise NotImplementedError("TODO: Implement create_user")

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
        raise NotImplementedError("TODO: Implement get_user")

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
        raise NotImplementedError("TODO: Implement update_user")

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
        raise NotImplementedError("TODO: Implement delete_user")


# For testing
if __name__ == "__main__":
    storage = MemoryUserStorage()
    api = UserAPI(storage)

    # Stub implementation for initial testing
    print("API stub loaded. Implement the methods to pass tests!")
    print("\nTo run tests with satisfaction scoring:")
    print("  python behave_wrapper_v2.py --ollama-model glm-4.7:cloud")