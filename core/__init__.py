"""
DBfix Core Module

This package contains the core functionality of the DBfix SQLite Database Repair Tool.
It provides multiple repair strategies for corrupted SQLite databases.
"""

__version__ = '0.1.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'
__license__ = 'MIT'

from .repair_engine import DatabaseRepairTool

__all__ = ['DatabaseRepairTool']
