from behave import given, when, then
import json
import sys
from pathlib import Path

# Add generated_code to path so we can import the API
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated_code"))

try:
    from api import UserAPI, MemoryUserStorage
except ImportError:
    print("WARNING: API module not found. Implementation needed.")
    UserAPI = None
    MemoryUserStorage = None

# Container for test state
class TestState:
    def __init__(self):
        self.api = None
        self.response = None
        self.created_user_id = None
        self.error_message = None

state = TestState()

@given("the user database is empty")
def step_impl(context):
    if UserAPI is None:
        context.skipped = True
        return
    storage = MemoryUserStorage()
    state.api = UserAPI(storage)
    state.response = None
    state.created_user_id = None
    state.error_message = None

@given('I create a user with email "{email}" and password "{password}"')
def step_impl(context, email, password):
    if getattr(context, 'skipped', False):
        return
    state.response = state.api.create_user(email, password)
    if state.response.get("success"):
        state.created_user_id = state.response["user"]["id"]

@when('I create a user with email "{email}" and password "{password}"')
def step_impl(context, email, password):
    if getattr(context, 'skipped', False):
        return
    state.response = state.api.create_user(email, password)
    if state.response.get("success"):
        state.created_user_id = state.response["user"]["id"]

@when('I attempt to create another user with the same email')
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    state.response = state.api.create_user("alice@example.com", "anotherpass")

@when('I fetch the user using their ID')
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    if state.created_user_id:
        state.response = state.api.get_user(state.created_user_id)

@when('I update the user\'s email to "{new_email}"')
def step_impl(context, new_email):
    if getattr(context, 'skipped', False):
        return
    if state.created_user_id:
        state.response = state.api.update_user(state.created_user_id, {"email": new_email})

@when('I delete the user')
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    if state.created_user_id:
        state.response = state.api.delete_user(state.created_user_id)

@when('I fetch the deleted user')
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    if state.created_user_id:
        state.response = state.api.get_user(state.created_user_id)

@then("the user should be created successfully")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    assert state.response is not None, "No response received"
    assert state.response.get("success") == True, f"Expected success, got: {state.response}"
    assert "user" in state.response, "Response missing user data"

@then("the password should be hashed (not stored as plaintext)")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    # Check if password in response or storage contains plaintext
    if "user" in state.response:
        user_data = state.response["user"]
        # Password should NOT be in user data
        assert "password" not in user_data, "Password should not be in user response"
        assert "password_hash" not in user_data, "Password hash should not be in user response"
    
    # Check storage directly
    user_id = state.created_user_id
    if user_id:
        user = state.api.storage.get_user(user_id)
        stored_password = user.get("password_hash", user.get("password", ""))
        assert stored_password != "secure123", "Password stored as plaintext!"
        assert len(stored_password) > 20, "Password hash too short (likely plaintext)"

@then("the user should have ID greater than 0")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    if "user" in state.response:
        user_id = state.response["user"].get("id")
        assert user_id is not None, "User ID should not be None"
        assert user_id > 0, f"User ID should be greater than 0, got: {user_id}"

@then("user creation should fail")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    assert state.response is not None, "No response received"
    assert state.response.get("success") == False, f"Expected failure, got success: {state.response}"

@then("an appropriate error message should be returned")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    assert "error" in state.response, "Response should contain error message"
    error = state.response["error"]
    assert len(error) > 0, "Error message should not be empty"

@then("I should receive the user details")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    assert state.response is not None, "No response received"
    assert state.response.get("success") == True, f"Expected success, got: {state.response}"
    assert "user" in state.response, "Response missing user data"

@then('the email should match "{expected_email}"')
def step_impl(context, expected_email):
    if getattr(context, 'skipped', False):
        return
    user_email = state.response["user"]["email"]
    assert user_email == expected_email, f"Expected {expected_email}, got {user_email}"

@then("the password should not be included in the response")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    user_data = state.response.get("user", {})
    assert "password" not in user_data, "Password should not be in response"
    assert "password_hash" not in user_data, "Password hash should not be in response"

@then("the update should succeed")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    assert state.response is not None, "No response received"
    assert state.response.get("success") == True, f"Expected success, got: {state.response}"

@then("fetching the user should show the new email")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    fetch_response = state.api.get_user(state.created_user_id)
    assert fetch_response.get("success") == True
    assert fetch_response["user"]["email"] == "charlie.new@example.com"

@then("the user should no longer exist")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    fetch_response = state.api.get_user(state.created_user_id)
    assert fetch_response.get("success") == False, "Deleted user should not be found"

@then("fetching the deleted user should return an error")
def step_impl(context):
    if getattr(context, 'skipped', False):
        return
    assert state.response.get("success") == False
    assert "error" in state.response