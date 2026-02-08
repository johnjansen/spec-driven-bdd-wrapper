# Test Interface & Configuration - Architecture Guide

## The Two Key Architectural Questions

### 1. How Does the Tool Know Where Tests Are?

**Solution:** `.spec-driven.toml` configuration file

**Benefits:**
- ✅ Auto-discovery: Tool finds config by searching upward from current directory
- ✅ No hardcoded paths: Different projects have different structures
- ✅ Versionable: Config tracked in git with the project
- ✅ Defaults provided: `spec-driven init` generates example config

---

### 2. How Do Tests Import/Exercise the Code?

**Critical Question!** There are two approaches:

---

## Approach A: Direct Import (Current Implementation)

### How It Works

Tests import generated code directly:

```python
# features/steps/user_steps.py
import sys
from pathlib import Path

# Add generated code to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated_code"))

from api import UserAPI, MemoryUserStorage

# Test uses the classes directly
def step_impl(context):
    storage = MemoryUserStorage()
    api = UserAPI(storage)
    response = api.create_user(email, password)
```

### Pros

✅ **Simple:** No HTTP overhead, direct method calls
✅ **Fast:** No server startup needed
✅ **Easy debugging:** Can inspect internal state
✅ **Precise:** Test exactly what we want

### Cons

❌ **Tests internal implementation:** Not the external interface
❌ **Coupled:** Tests break if internal structure changes
❌ **Less realistic:** Doesn't test deployment scenario

### When to Use

- Fast iteration during development
- Unit/integration testing
- Testing internal data structures
- When you control both code and tests

---

## Approach B: External Interface (API Testing)

### How It Works

Tests exercise the HTTP API (like real clients):

```python
# features/steps/user_steps.py
from flask import Flask
from api import create_app  # API creates a Flask app

# Test client acts like HTTP client
@app = create_app()
client = app.test_client()

def step_impl(context):
    # Make HTTP request (but no network overhead)
    response = client.post(
        "/users",
        json={"email": "alice@example.com", "password": "pass"}
    )
    assert response.status_code == 201
```

### Pros

✅ **Tests external interface:** What the system exposes
✅ **Deployment realistic:** Same tests that run on deployed system
✅ **Decoupled:** Tests don't depend on internal structure
✅ **Spec-driven:** Tests match the spec (HTTP API endpoints)

### Cons

❌ **More complex:** Need app framework (Flask, FastAPI, etc.)
❌ **Slower:** HTTP layer overhead (even with test client)
❌ **Limited access:** Can't easily inspect internal state

### When to Use

- Testing deployed/web APIs
- Contract testing
- When you want realistic testing
- When external interface is the contract

---

## Which to Choose? 🤔

### For Spec-Driven Development

**Recommendation: External Interface (Approach B)**

**Why:**

1. **Spec describes behavior:** "When I POST to /users, then..." → HTTP API
2. **Tests validate contract:** Does the system do what the spec says?
3. **Production parity:** Same tests that validate deployed code
4. **Agent writes to contract:** Spec says "POST /users" → agent implements that endpoint

---

## Implementation Examples

### Example 1: Direct Import (Current)

**Generated Code:**
```python
# generated_code/api.py
class UserAPI:
    def create_user(self, email, password):
        # Business logic here
        return {"success": True, "user": {"id": 1, "email": email}}
```

**Test:**
```python
# features/steps/user_steps.py
from api import UserAPI

api = UserAPI()
response = api.create_user("alice@example.com", "pass")
assert response["success"] == True
```

### Example 2: External Interface

**Generated Code:**
```python
# generated_code/api.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/users", endpoint="create_user")
def create_user():
    data = request.get_json()
    # Business logic here
    return jsonify({
        "success": True,
        "user": {"id": 1, "email": data["email"]}
    }), 201

def create_app():
    return app
```

**Test:**
```python
# features/steps/user_steps.py
from api import create_app

app = create_app()
client = app.test_client()

response = client.post(
    "/users",
    json={"email": "alice@example.com", "password": "pass"}
)
assert response.status_code == 201
data = response.get_json()
assert data["success"] == True
```

---

## The Import/Visibility Paradox

### The Problem

```
┌─────────────────────────────────────┐
│    Agent (can write generated_code)  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    generated_code/api.py            │
│    (Agent CAN see this)            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    Tests (in external_tests/)       │
│    (Agent CANNOT see this)          │
│                                     │
│    from api import UserAPI ❓???    │
└─────────────────────────────────────┘
```

**Question:** How can tests import `api.py` if agent can't see `tests/` but tests need `api.py`?

### The Solution

**Imports work in ONE direction:**

```
✅ Tests → Import → Generated Code


❌ Tests → Export → Agent
```

**Key points:**

1. **Tests import code** - this is fine, agent doesn't see tests
2. **Code doesn't import tests** - this is prohibited
3. **Agent only writes code** - agent never imports from tests

**Security boundary:**
- **Agent can READ/WRITE:** `generated_code/`
- **Agent CANNOT READ:** `external_tests/` (or `features/`)
- **Tests CAN READ:** `generated_code/` (to import code)
- **Tests are READ-ONLY:** Agent can't modify them

---

## Complete Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT                                 │
│  "Implement a user management API with POST /users"    │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ Writes code
                    ▼
┌─────────────────────────────────────────────────────────┐
│           generated_code/api.py                         │
│                                                          │
│  from flask import Flask                                │
│  app = Flask(__name__)                                 │
│                                                          │
│  @app.post("/users")                                    │
│  def create_user():                                     │
│      # Agent implements this                           │
│      return jsonify({"user": {...}})                    │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ Wrapper invoked
                    ▼
┌─────────────────────────────────────────────────────────┐
│         🛡️ behave_wrapper.py (Config-driven)            │
├─────────────────────────────────────────────────────────┤
│  Reads .spec-driven.toml:                               │
│    [paths]                                              │
│    generated_code_dir = "generated_code"                │
│    test_dir = "features"                                │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ Runs tests
                    ▼
┌─────────────────────────────────────────────────────────┐
│         features/user_management.feature                 │
│         (Agent CANNOT read)                              │
│                                                          │
│  Scenario: Create a new user                           │
│    When I POST to /users with email "alice@..."         │
│    Then I receive a 201 response                       │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ Step implementation imports code
                    ▼
┌─────────────────────────────────────────────────────────┐
│         features/steps/user_steps.py                    │
│         (Agent CANNOT read)                              │
│                                                          │
│  from api import create_app  ✅ OK: imports from code   │
│                                                          │
│  app = create_app()                                     │
│  client = app.test_client()                             │
|                                                          │
│  def step_impl():                                       │
│      response = client.post("/users", ...)              │
│      assert response.status_code == 201                │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration File Format

### .spec-driven.toml

```toml
[project]
name = "user-management-api"

[paths]
# Where agent writes code
generated_code_dir = "generated_code"

# Where agent CANNOT go (tests live here)
test_dir = "features"

[test]
runner = "behave"
# Path relative to test_dir
features_path = "user_management.feature"
steps_path = "steps/user_steps.py"

# HTTP API testing
[test.interface]
# How tests exercise the code
type = "http_test_client"  # or "direct_import"
app_factory = "api.create_app"

[llm]
model = "llama3.1"
url = "http://localhost:11434"

[scoring]
production_threshold = 0.95
staging_threshold = 0.80
dev_threshold = 0.70
```

---

## Usage Examples

### With Config File

```bash
# In project root with .spec-driven.toml
spec-driven test

# Result:
# 🧪 Running tests from: features
# 📝 Generated code at: generated_code
# 📊 4 passed, 1 failed
# 🔴 Satisfaction: 0.85/1.00 (NEEDS WORK)
```

### Auto-Discovery

Tool searches upward from current directory:

```bash
# In subdirectory
cd myproject/src/components/spec-driven/test

# This works! Tool finds .spec-driven.toml in project root
spec-driven test
```

---

## Summary

### Configuration (.spec-driven.toml)
- ✅ Defines where code and tests are
- ✅ Auto-discovered by searching
- ✅ No hardcoded paths
- ✅ Example provided via `spec-driven init`

### Test Interface (Imports)

**Two directions:**

| Direction | Allowed? | Why? |
|-----------|----------|------|
| Tests → Import → Code | ✅ Yes | Tests need to run code |
| Code → Import → Tests | ❌ No | Agent would see tests |
| Agent → Read → Tests | ❌ No | Agent would hack tests |

**Best practice:** Tests use external interface (HTTP API)
- Matches spec (POST /users, GET /users/:id)
- Production parity
- Decoupled from internals

**Alternative:** Direct import for speed/convenience
- Good for development iteration
- Simpler setup
- Less realistic

---

*The key insight: Imports are one-way, the config file controls discovery, and the test interface choice depends on your testing goals.*