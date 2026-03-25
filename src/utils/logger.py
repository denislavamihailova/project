"""
Logging utility for Football AI Assistant
Handles structured logging to commands.log
"""

import os
from datetime import datetime
from pathlib import Path


class Logger:
    """Simple structured logger for commands and results"""
    
    def __init__(self, log_file="commands.log"):
        self.log_file = log_file
    
    def log_command(self, raw_input, intent, params, result, status="OK"):
        """
        Log a command execution
        
        Args:
            raw_input: The raw user input
            intent: Parsed intent
            params: Extracted parameters
            result: Result message from the handler
            status: "OK" or "ERROR"
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Safely serialize params for logging
        params_str = str(params) if params else "None"
        
        log_entry = (
            f"[{timestamp}] "
            f"INPUT: {raw_input} | "
            f"INTENT: {intent} | "
            f"PARAMS: {params_str} | "
            f"STATUS: {status} | "
            f"RESULT: {result}\n"
        )
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"❌ Failed to write to log: {e}")
    
    def log_error(self, raw_input, error_msg):
        """Log an error during command processing"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] ERROR: {raw_input} | {error_msg}\n"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"❌ Failed to write to log: {e}")


# Global logger instance
_logger = None


def get_logger():
    """Get or create the global logger instance"""
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger


def init_logger(log_file="commands.log"):
    """Initialize the logger with a specific log file"""
    global _logger
    _logger = Logger(log_file)
    return _logger

