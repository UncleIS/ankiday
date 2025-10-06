"""Tests for verbose functionality."""

import io
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from ankiday.backends.ankiconnect import AnkiConnectBackend
from ankiday.ops.apply import Planner, Applier


def test_backend_verbose_logging():
    """Test that verbose logging works in backend."""
    print("Testing backend verbose logging...")
    
    # Capture stdout
    captured_output = io.StringIO()
    
    with patch('sys.stdout', captured_output):
        # Create backend with verbose=True
        backend = AnkiConnectBackend(verbose=True)
        
        # Test verbose logging method
        backend._log_verbose("Test message")
        
    output = captured_output.getvalue()
    assert "[VERBOSE] Test message" in output
    print("✓ Backend verbose logging works")


def test_backend_no_verbose_logging():
    """Test that verbose logging is disabled by default."""
    print("Testing backend non-verbose mode...")
    
    # Capture stdout
    captured_output = io.StringIO()
    
    with patch('sys.stdout', captured_output):
        # Create backend with verbose=False (default)
        backend = AnkiConnectBackend(verbose=False)
        
        # Test verbose logging method
        backend._log_verbose("Test message")
        
    output = captured_output.getvalue()
    assert output == ""
    print("✓ Backend non-verbose mode works")


def test_planner_verbose_logging():
    """Test that verbose logging works in planner."""
    print("Testing planner verbose logging...")
    
    # Capture stdout
    captured_output = io.StringIO()
    
    with patch('sys.stdout', captured_output):
        # Create mock backend
        mock_backend = Mock()
        
        # Create planner with verbose=True
        planner = Planner(mock_backend, verbose=True)
        
        # Test verbose logging method
        planner._log_verbose("Test planner message")
        
    output = captured_output.getvalue()
    assert "[PLANNER] Test planner message" in output
    print("✓ Planner verbose logging works")


def test_applier_verbose_logging():
    """Test that verbose logging works in applier."""
    print("Testing applier verbose logging...")
    
    # Capture stdout
    captured_output = io.StringIO()
    
    with patch('sys.stdout', captured_output):
        # Create mock backend
        mock_backend = Mock()
        
        # Create applier with verbose=True
        applier = Applier(mock_backend, verbose=True)
        
        # Test verbose logging method
        applier._log_verbose("Test applier message")
        
    output = captured_output.getvalue()
    assert "[APPLIER] Test applier message" in output
    print("✓ Applier verbose logging works")


def test_verbose_flag_in_cli():
    """Test that CLI accepts verbose flag (basic import test)."""
    print("Testing CLI structure...")
    
    from ankiday.cli import app
    
    # If this imports without error, the CLI structure is valid
    assert app is not None
    print("✓ CLI structure is valid")


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_backend_verbose_logging,
        test_backend_no_verbose_logging,
        test_planner_verbose_logging,
        test_applier_verbose_logging,
        test_verbose_flag_in_cli,
    ]
    
    print("Running verbose flag tests...\n")
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\nTests completed: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
