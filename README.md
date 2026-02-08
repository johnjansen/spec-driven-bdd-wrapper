# Spec-Driven BDD Wrapper

[![StrongDM Software Factory](https://img.shields.io/badge/StrongDM-Software%20Factory-blue)](https://factory.strongdm.ai/)

A production-ready implementation of StrongDM's **Software Factory** pattern for spec-driven development with AI agents.

## 🎯 What It Does

Runs BDD tests against AI-generated code, obfuscates technical details with an LLM, and returns behavioral feedback with satisfaction scoring (0.0-1.00).

### Key Features

- ✅ **BDD test execution** with Behave/Gherkin
- ✅ **Obfuscation layer** translates technical errors to behavioral feedback
- ✅ **Satisfaction scoring** (0.0-1.00) with LLM-as-judge evaluation
- ✅ **Config file** auto-discovery (`.spec-driven.toml`)
- ✅ **Two test interface patterns** (direct import or HTTP API)
- ✅ **Deployment thresholds** (production: 95%, staging: 80%)
- ✅ **Reward-hack resistant** - agent can't see test implementation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/spec-driven-bdd-wrapper.git
cd spec-driven-bdd-wrapper

# Install dependencies
pip install -r requirements.txt

# Or with uv
uv sync
```

### 2. Initialize a Project

```bash
# Create example config
spec-driven init

# Edit .spec-driven.toml for your project
```

### 3. Run Tests

```bash
# Auto-discover .spec-driven.toml and run tests
spec-driven test
```

## 📖 How It Works

### Architecture

```
Agent → generates code → Tests run (agent can't see)
         ↓
    Wrapper runs tests
         ↓
    Phase 1: Obfuscation (technical → behavioral feedback)
         ↓
    Phase 2: Scoring (0.0-1.00 satisfaction)
         ↓
    Agent receives: score + reasoning + feedback
```

### Obfuscation Example

**Technical error (what wrapper sees):**
```
AssertionError at user_steps.py:63: stored_password == 'secure123'
```

**Behavioral feedback (what agent receives):**
```
Passwords must be hashed before storage, not stored in plaintext.
```

### Satisfaction Scoring

**Boolean pass/fail:**
```
5 tests failed (no context)
```

**Probabilistic scoring:**
```
🔴 Satisfaction: 0.00/1.00 (Poor)

Reasoning: 0% of scenarios passed. All failures are critical,
affecting core CRUD operations. The application is completely non-functional.
```

## 🔧 Configuration

### .spec-driven.toml

```toml
[project]
name = "my-user-api"

[paths]
# Where agent writes code
generated_code_dir = "generated_code"

# Where tests live (agent can't see)
test_dir = "tests"

[test]
runner = "behave"

# How tests exercise code:
# - "direct_import": Import and call methods directly
# - "http_test_client": Use HTTP client (Flask, FastAPI, etc.)
interface.type = "http_test_client"

[llm]
model = "llama3.1"
url = "http://localhost:11434"
timeout = 20

[scoring]
# Thresholds for deployment decisions
production_threshold = 0.95
staging_threshold = 0.80
dev_threshold = 0.70
```

## 📚 Examples

See `examples/user_management/` for a complete working example:

```bash
cd examples/user_management

# View stub implementation (will fail)
cat generated_code/api.py

# Run tests - see 0.00/1.00 score
spec-driven test

# Copy working implementation
cp example_implementation.py generated_code/api.py

# Run tests - see 0.85+/1.00 score
spec-driven test
```

## 🌐 Test Interface Patterns

### Option A: Direct Import

```python
# Tests import generated code directly
from generated_code.api import UserAPI

api = UserAPI()
response = api.create_user(email, password)
```

**Pros:** Simple, fast, test internals

### Option B: HTTP Integration

```python
# Tests exercise HTTP endpoints
from generated_code.api import create_app

app = create_app()
client = app.test_client()
response = client.post("/users", json={...})
```

**Pros:** Production parity, tests contract, decoupled

See `docs/TEST_INTERFACE.md` for details.

## 📊 Wrapper Versions

| Version | Config | Scoring | Best For |
|---------|--------|---------|----------|
| **V1** | ❌ | ❌ | Learning, simple projects |
| **V2** | ❌ | ✅ | Single project, iterative development |
| **V3** | ✅ | ✅ | Production, teams, CI/CD |

**Recommendation:** Use V3 for production.

## 🤖 API Usage

```python
from spec_driven import BDDWrapperV3, SpecDrivenConfig

# Load config (auto-discovered)
config = SpecDrivenConfig()
wrapper = BDDWrapperV3(config)

# Run tests with scoring
feedback = wrapper.run()

# Check deployment readiness
if extract_score(feedback) >= config.production_threshold:
    deploy()
```

## 📖 Documentation

- **[Quick Start](docs/QUICK_START.md)** - 5-minute demo
- **[Architecture](docs/ARCHITECTURE.md)** - Complete architecture guide
- **[Test Interface](docs/TEST_INTERFACE.md)** - Import patterns explained
- **[Full Flow](docs/FULL_FLOW.md)** - Complete flow diagrams
- **[Wrapper Versions](docs/WRAPPER_VERSIONS.md)** - V1/V2/V3 comparison
- **[Index](docs/INDEX.md)** - Complete documentation index

## 🧪 Requirements

- Python 3.10+
- [Behave](https://behave.readthedocs.io/) (BDD framework)
- [Ollama](https://ollama.com/) (local LLM)
- [requests](https://requests.readthedocs.io/) (HTTP client)
- [toml](https://pypi.org/project/toml/) (config parsing)

## 🔧 Setting Up Ollama

```bash
# Install Ollama
brew install ollama  # macOS
# Or visit https://ollama.com/downloads

# Start Ollama
ollama serve

# Pull a model
ollama pull llama3.1
# OR
ollama pull mistral
```

## 🌟 Why This Matters

### The Problem

 traditional testing with AI agents:

```
Agent sees: "assert stored_password != 'secure123'"
Agent writes: stored_password = "hashed_password"  # Passes test, but wrong!
```

### Our Solution

```
Agent sees: "Passwords must be hashed before storage"
Agent writes: bcrypt.hashpw(password, salt)  # Correct!
```

### Key Insights

1. **Separation**: Tests live outside agent's accessible directories
2. **Obfuscation**: Agent sees behavioral problems, not technical details
3. **Scoring**: Probabilistic feedback guides iteration (0.85 = close vs 0.00 = restart)
4. **Standard Tools**: Uses Behave/Gherkin, no custom framework

## 📚 Reference

This implementation is based on [StrongDM's Software Factory](https://factory.strongdm.ai/):

> "The three golden rules:
> 1. Code must not be written by humans
> 2. Code must not be reviewed by humans
> 3. Target: $1,000/day in tokens per human engineer"

The Software Factory demonstrates how spec-driven development with AI agents can:
- Humans write specifications and scenarios
- Agents write all code without human review
- LLM-as-judge validates behavior (0.0-1.00 satisfaction)

## 🤝 Contributing

Contributions welcome! Please read the documentation in `docs/` first.

## 📄 License

MIT License - feel free to use in your projects!

## 🙏 Credits

- **Concept**: [StrongDM Software Factory](https://factory.strongdm.ai/)
- **BDD Framework**: [Behave](https://behave.readthedocs.io/)
- **LLM**: [Ollama](https://ollama.com/)

---

*A production-ready implementation of spec-driven development for AI agents.*