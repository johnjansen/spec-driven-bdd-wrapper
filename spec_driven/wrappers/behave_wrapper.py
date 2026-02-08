#!/usr/bin/env python3
"""
BDD Obfuscation Wrapper for Spec-Driven Development

Runs BDD tests and returns obfuscated feedback to AI agents.
Agent sees behavioral feedback, not implementation details.
"""

import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Any
import sys


class BDDObfuscationWrapper:
    """
    Wrapper that:
    1. Runs Behave tests against generated code
    2. Captures raw test results
    3. Obfuscates implementation details using Ollama LLM
    4. Returns behavioral feedback suitable for agents
    """

    def __init__(
        self,
        code_dir: str = "generated_code",
        test_dir: str = "external_tests",
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.1"
    ):
        self.code_dir = Path(code_dir)
        self.test_dir = Path(test_dir)
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model

    def run_tests_and_obfuscate(self) -> str:
        """
        Main entry point:
        1. Run Behave tests
        2. Collect results
        3. Obfuscate with Ollama
        4. Return feedback for agent
        """
        print("🧪 Running BDD tests...")
        raw_results = self._run_behave()
        
        print(f"📊 Tests completed. Status: {raw_results['status']}")
        
        if raw_results['status'] == 'passed':
            return "✅ All tests passed! Implementation is correct."
        
        print("🔍 Obfuscating test failures with Ollama...")
        feedback = self._obfuscate_results(raw_results)
        
        return feedback

    def _run_behave(self) -> Dict[str, Any]:
        """
        Run Behave and return structured results.
        Tests are run from agent cannot see the implementation.
        """
        results_path = self.test_dir / "test_results.json"
        
        # Clean up previous results
        if results_path.exists():
            results_path.unlink()
        
        # Run behave against external tests directory
        # The tests import from generated_code, but the test files themselves
        # are in external_tests (which agent can't see)
        cmd = [
            sys.executable, "-m", "behave",
            str(self.test_dir / "features"),
            "--format=json.pretty",
            f"--outfile={results_path}"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Tests timed out after 30 seconds"
            }
        
        # Parse the JSON output
        if results_path.exists():
            with open(results_path, 'r') as f:
                test_data = json.load(f)
        else:
            test_data = []
        
        return self._parse_test_results(test_data, result)

    def _parse_test_results(self, test_data: List[Dict], command_result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """
        Parse Behave JSON output and extract failures.
        """
        failures = []
        passed = 0
        failed = 0
        skipped = 0
        
        for feature in test_data:
            feature_name = feature.get("name", "Unknown Feature")
            
            for scenario in feature.get("elements", []):
                scenario_name = scenario.get("name", "Unknown Scenario")
                status = scenario.get("status", "unknown")
                
                if status == "passed":
                    passed += 1
                elif status in ("failed", "error"):
                    failed += 1
                    # Extract failure details
                    failure_details = {
                        "feature": feature_name,
                        "scenario": scenario_name,
                        "steps": [],
                        "error": None
                    }
                    
                    for step in scenario.get("steps", []):
                        step_info = {
                            "keyword": step.get("keyword", ""),
                            "name": step.get("name", ""),
                            "status": step.get("status", "")
                        }
                        if step.get("status") == "failed":
                            error_match = step.get("match", {})
                            if error_match:
                                step_info["error_message"] = error_match.get("message", "")
                                failure_details["error"] = error_match.get("message", "")
                        failure_details["steps"].append(step_info)
                    
                    failures.append(failure_details)
                elif status == "skipped":
                    skipped += 1
        
        return {
            "status": "passed" if failed == 0 else "failed",
            "summary": {
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "total": passed + failed + skipped
            },
            "failures": failures,
            "raw_output": command_result.stdout,
            "stderr": command_result.stderr
        }

    def _obfuscate_results(self, raw_results: Dict[str, Any]) -> str:
        """
        Use Ollama LLM to translate code-level failures into behavioral feedback.

        Agent sees:
            "Password should be hashed but appears to be stored in plaintext"

        Not:
            "AssertionError at user_steps.py:42: stored_password != 'secure123'"
        """
        prompt = self._build_obfuscation_prompt(raw_results)

        try:
            print(f"  Calling {self.ollama_model} (this may take a moment)...")
            response = self._call_ollama(prompt)
            if not response.strip():
                raise ValueError("Empty response from Ollama")
            return self._clean_and_format_response(response)
        except Exception as e:
            # Fallback if Ollama fails
            error_msg = f"Failed to call Ollama: {e}"
            print(f"⚠️  {error_msg}")
            return self._fallback_obfuscation(raw_results)

    def _build_obfuscation_prompt(self, results: Dict[str, Any]) -> str:
        """Build a prompt that instructs the LLM to obfuscate technical details."""
        prompt = """You are translating test failures into behavioral feedback for an AI developer.

Your job: Convert code-level failures into business/specification-level problems.
- HIDE: File names, line numbers, function names, stack traces
- SHOW: What behavior failed, what was expected vs. actual
- BE CONCISE: Each failure should be 1-3 sentences
- USE CLARITY: Focus on what the spec expects, not how it's implemented

Examples translation:
  ❌ "AssertionError at user_steps.py:42: expected password_hash != None\n     Actual: stored_password == 'secure123'"
  ✅ "The password should be hashed before storage, but it appears to be stored in plaintext."

  ❌ "KeyError: 'email' in api.py line 15"
  ✅ "The user email field is missing from the user response."

Here are the test failures to translate:

"""
        
        for failure in results["failures"]:
            prompt += f"\n📍 Feature: {failure['feature']}\n"
            prompt += f"   Scenario: {failure['scenario']}\n"
            
            # Add details about the failure
            if failure["error"]:
                prompt += f"   Error: {failure['error']}\n"
            
            # Find the failing step
            for step in failure["steps"]:
                if step["status"] == "failed":
                    prompt += f"   Failed Step: {step['keyword']} {step['name']}\n"
                    if "error_message" in step:
                        prompt += f"   Technical Error: {step['error_message']}\n"
            
            prompt += "\n"
        
        prompt += """
Translate each failure into behavioral feedback. Format as a numbered list:
1. [Behavior problem description]
2. [Behavior problem description]

Return ONLY the translated feedback, nothing else.
"""
        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API for obfuscation."""
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 2000
            }
        }
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=20
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Handle different response formats (some models use "thinking" or "response")
        result = data.get("response", "") or data.get("thinking", "")
        return result

    def _clean_and_format_response(self, response: str) -> str:
        """Clean up LLM response and format nicely."""
        # Remove markdown if present
        cleaned = response.strip()
        
        # Add summary header
        return f"""
================================================================================
Test Results: Implementation Needed
================================================================================

{cleaned}

================================================================================
"""
    
    def _fallback_obfuscation(self, results: Dict[str, Any]) -> str:
        """Fallback if Ollama is unavailable: simple summary without technical details."""
        failures = results["failures"]
        summary = [
            f"Implementation issues detected ({results['summary']['failed']} test(s) failed)\n"
        ]

        # Group by common patterns
        patterns = {
            "create_user": [],
            "get_user": [],
            "update_user": [],
            "delete_user": [],
            "authentication": [],
            "storage": []
        }

        for failure in failures:
            scenario = failure['scenario']
            error = failure.get("error", "")

            # Try to categorize
            if "create" in scenario.lower():
                if "NotImplementedError" in str(error):
                    patterns["create_user"].append("the create_user method is not implemented yet.")
                elif "hash" in scenario.lower() or "password" in scenario.lower():
                    patterns["authentication"].append("passwords need to be hashed, not stored in plaintext.")
                elif "duplicate" in scenario.lower():
                    patterns["create_user"].append("duplicate emails should be rejected.")
                else:
                    patterns["create_user"].append("user creation has issues.")
            elif "fetch" in scenario.lower() or "get" in scenario.lower():
                patterns["get_user"].append("user retrieval is not working correctly.")
            elif "update" in scenario.lower():
                patterns["update_user"].append("user updates are not functioning.")
            elif "delete" in scenario.lower():
                patterns["delete_user"].append("user deletion has issues.")

        # Build summary
        for category, messages in patterns.items():
            if messages:
                unique_messages = list(set(messages))
                summary.append(f"{category.upper()}:")
                for msg in unique_messages:
                    summary.append(f"  - {msg}")

        return "\n".join(summary)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="BDD Obfuscation Wrapper")
    parser.add_argument("--code-dir", default="generated_code", help="Directory containing generated code")
    parser.add_argument("--test-dir", default="external_tests", help="Directory containing BDD tests")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--ollama-model", default="llama3.1", help="Ollama model to use")
    
    args = parser.parse_args()
    
    wrapper = BDDObfuscationWrapper(
        code_dir=args.code_dir,
        test_dir=args.test_dir,
        ollama_url=args.ollama_url,
        ollama_model=args.ollama_model
    )
    
    feedback = wrapper.run_tests_and_obfuscate()
    print(feedback)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())