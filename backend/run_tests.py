"""
Test runner script for comprehensive testing.

Usage:
    python run_tests.py                  # Run all tests
    python run_tests.py --unit           # Run only unit tests
    python run_tests.py --integration    # Run only integration tests
    python run_tests.py --coverage       # Run with coverage report
    python run_tests.py --fast           # Skip slow tests
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle output."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ {description} FAILED")
        return False
    else:
        print(f"\n✅ {description} PASSED")
        return True


def main():
    parser = argparse.ArgumentParser(description="Run Event Scraper tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--file", type=str, help="Run specific test file")
    
    args = parser.parse_args()
    
    # Build pytest command
    pytest_cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-vv")
    else:
        pytest_cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        pytest_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])
    
    # Filter by test type
    if args.unit:
        pytest_cmd.extend(["-m", "not integration"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
    
    # Skip slow tests
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])
    
    # Specific file
    if args.file:
        pytest_cmd.append(f"tests/{args.file}")
    else:
        pytest_cmd.append("tests/")
    
    # Run tests
    cmd = " ".join(pytest_cmd)
    success = run_command(cmd, "Running Tests")
    
    if success and args.coverage:
        print("\n" + "="*60)
        print("Coverage report generated in htmlcov/index.html")
        print("="*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
