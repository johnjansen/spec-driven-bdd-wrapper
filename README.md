# Spec-Driven BDD Wrapper

[![StrongDM Software Factory](https://img.shields.io/badge/StrongDM-Software%20Factory-blue)](https://factory.strongdm.ai/)
[![Prototype](https://img.shields.io/badge/Status-Prototype-orange)](https://github.com/johnjansen/spec-driven-bdd-wrapper)
[![Use at your own risk](https://img.shields.io/badge/Warning-Use%20at%20your%20own%20risk-red)](https://github.com/johnjansen/spec-driven-bdd-wrapper)

**⚠️ Prototype - Use at your own risk**

A prototype implementation exploring StrongDM's **Software Factory** pattern for spec-driven development with AI agents. Written by OpenClaw (GLM-4.7) as a proof-of-concept for research and exploration.

## 🎯 What It Does

A **pipe-filter** prototype that reads test output from ANY test framework, obfuscates technical details with an LLM, and returns behavioral feedback with satisfaction scoring (0.0-1.00).

**What this is:** A working prototype showing the pattern in action
**What this isn't:** Production-ready software (see warnings below)

### How It Works

**Universal pipe filter:**
```bash
# ANY test framework → pipe → spec-driven-evaluate
pytest -v | python spec-driven-evaluate
npm test | python spec-driven-evaluate
go test ./... | python spec-driven-evaluate
cargo test | python spec-driven-evaluate
```

**Key breakthrough:** Framework-agnostic! Works with ANY test runner, not just Behave.

### Key Features (Prototype)

- ✅ **Universal** - Works with pytest, Jest, go test, cargo test, etc.
- ✅ **Auto-detects framework** - Parses output format automatically
- ✅ **Obfuscation layer** - Translates technical errors to behavioral feedback
- ✅ **Satisfaction scoring** (0.0-1.00) with LLM-as-judge evaluation
- ✅ **Simple integration** - Just pipe output to script
- ✅ **Reward-hack resistant** - Agent can't see technical details

## ⚠️ Warnings & Limitations

**Please read this before using:**

1. **This is a prototype** - created as a proof-of-concept to explore the StrongDM Software Factory ideas
2. **Not production-ready** - hasn't been tested in real scenarios, may have bugs, incomplete features
3. **Use at your own risk** - intended for research and exploration only
4. **No formal testing** - not a battle-tested library
5. **Ollama dependency** - requires local LLM setup, may be flaky
6. **Single project focus** - designed for exploration, not general-purpose use
7. **Learning tool** - best for understanding the pattern, not for production deployment

**What it's good for:**
- Understanding the spec-driven development pattern
- Seeing how LLM obfuscation works
- Experimenting with satisfaction scoring
- Kicking the tires of the ideas

**What it's not good for:**
- Production deployments
- Critical systems
- Large-scale use cases
- Real-world automation

## 🚀 Quick Start (For Exploration)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/johnjansen/spec-driven-bdd-wrapper.git
cd spec-driven-bdd-wrapper

# Install dependencies
pip install -r requirements.txt
```

### 2. Use with ANY Test Framework

```bash
# Python/pytest
pytest -v | python spec_driven_evaluate

# JavaScript/Jest
npm test | python spec_driven_evaluate

# Go
go test ./... -v | python spec_driven_evaluate

# Rust
cargo test | python spec_driven_evaluate
```

That's it! The wrapper auto-detects the framework format and obfuscates failures.

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

**No configuration needed!** The wrapper:

1. Reads test output from stdin (piped)
2. Auto-detects framework format (pytest, Jest, go, cargo, etc.)
3. Parses failures automatically
4. Obfuscates with LLM
5. Returns scored feedback

Optional: **Environment variables** for Ollama:
```bash
export OLLAMA_MODEL=llama3.1
export OLLAMA_URL=http://localhost:11434
```

## 📚 Example Workflow

```bash
# 1. Agent generates code (your_project/src/api.py)
# 2. Run your existing tests
pytest your_project/tests/ -v | python spec_driven_evaluate

# Output:
# 🔴 TEST RESULTS - Satisfaction: 0.65/1.00 (Moderate)
#
# Reasoning: 65% pass rate. Most core functionality works but
# there are several edge case failures that need attention.
#
# BEHAVIORAL FEEDBACK:
# 1. The user deletion operation fails to clean up reference tracking.
# 2. Authentication timeouts are not handled correctly under load.
# 3. Data validation is missing for negative number inputs.

# 3. Agent improves code
# 4. Run again
pytest your_project/tests/ -v | python spec_driven_evaluate

# Output:
# 🟢 TEST RESULTS - Satisfaction: 0.95/1.00 (Excellent)
#
# Reasoning: 95% pass rate. All core functionality working correctly.

# 5. Deploy when ready
```

### See Legacy Example

The original Behave-based approach is preserved in `examples/user_management/`:
```bash
cd examples/user_management
behave features/ | python ../spec_driven-evaluate
```

## 🌐 Usage Pattern

The wrapper is a **universal pipe filter** - read any test output, parse it, obfuscate, score.

### Supported Frameworks

**Python:**
```bash
pytest -v | python spec_driven_evaluate
unittest discover -v | python spec_driven_evaluate
```

**JavaScript/TypeScript:**
```bash
npm test | python spec_driven_evaluate
npm run test | python spec_driven_evaluate
```

**Go:**
```bash
go test ./... -v | python spec_driven_evaluate
```

**Rust:**
```bash
cargo test | python spec_driven_evaluate
```

**Custom:**
```bash
your_test_runner | python spec_driven_evaluate
```

### Why This Architecture Works

**Problems with framework-specific:**
- ❌ Tied to one ecosystem (e.g., Python/Behave only)
- ❌ Can't use existing tests
- ❌ Complex setup

**Benefits of pipe-filter:**
- ✅ Universal - works with any language/framework
- ✅ Simple - just pipe output
- ✅ Uses your existing tests
- ✅ No migration needed

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

## 🎓 Why This Prototype Matters

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

**⚠️ Prototype written by OpenClaw (GLM-4.7) to explore StrongDM's Software Factory concepts**

Use for research and exploration only. Not suitable for production use.