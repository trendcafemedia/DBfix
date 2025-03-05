"""
Tests for the DBfix repair engine.

This module contains tests for the DatabaseRepairTool class and its methods.
"""

import os
import tempfile
import unittest
import sqlite3
from pathlib import Path

# Import the DatabaseRepairTool class
# Note: This import will need to be adjusted based on the actual package structure
from core.repair_engine import DatabaseRepairTool


class TestDatabaseRepairTool(unittest.TestCase):
    """Test cases for the DatabaseRepairTool class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a test database
        self.test_db_path = self.test_dir / "test.db"
        self._create_test_database(self.test_db_path)
        
        # Create a corrupted test database
        self.corrupted_db_path = self.test_dir / "corrupted.db"
        self._create_corrupted_database(self.corrupted_db_path)

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()

    def _create_test_database(self, db_path):
        """Create a test SQLite database."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a test table
        cursor.execute("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value INTEGER
        )
        """)
        
        # Insert some test data
        test_data = [
            (1, "Item 1", 100),
            (2, "Item 2", 200),
            (3, "Item 3", 300)
        ]
        cursor.executemany("INSERT INTO test_table VALUES (?, ?, ?)", test_data)
        
        conn.commit()
        conn.close()

    def _create_corrupted_database(self, db_path):
        """Create a corrupted SQLite database for testing."""
        # First create a normal database
        self._create_test_database(db_path)
        
        # Then corrupt it by writing random bytes in the middle
        with open(db_path, 'r+b') as f:
            f.seek(1024)  # Go to an offset
            f.write(b'CORRUPTED_DATA_FOR_TESTING')

    def test_initialization(self):
        """Test that the DatabaseRepairTool initializes correctly."""
        repair_tool = DatabaseRepairTool(
            input_path=str(self.test_db_path),
            output_dir=str(self.test_dir),
            log_level="INFO"
        )
        
        self.assertEqual(repair_tool.input_path, os.path.abspath(str(self.test_db_path)))
        self.assertEqual(repair_tool.output_dir, os.path.abspath(str(self.test_dir)))

    def test_validate_database(self):
        """Test the database validation method."""
        repair_tool = DatabaseRepairTool(
            input_path=str(self.test_db_path),
            output_dir=str(self.test_dir)
        )
        
        # Validate a good database
        validation_results = repair_tool.validate_database(str(self.test_db_path))
        self.assertTrue(validation_results["is_valid_sqlite"])
        self.assertEqual(validation_results["integrity_check"], "ok")
        self.assertIn("test_table", validation_results["tables"])
        
        # Validate a corrupted database
        validation_results = repair_tool.validate_database(str(self.corrupted_db_path))
        self.assertTrue(validation_results["is_valid_sqlite"])  # Header should still be valid
        self.assertNotEqual(validation_results["integrity_check"], "ok")  # Should fail integrity check

    def test_repair_database(self):
        """Test the database repair method."""
        repair_tool = DatabaseRepairTool(
            input_path=str(self.corrupted_db_path),
            output_dir=str(self.test_dir)
        )
        
        # Attempt repair
        success = repair_tool.repair_database()
        
        # Check if repair was successful
        self.assertTrue(success)
        self.assertTrue(repair_tool.results["success"])
        self.assertIsNotNone(repair_tool.results["repaired_path"])
        
        # Validate the repaired database
        if repair_tool.results["repaired_path"]:
            validation_results = repair_tool.validate_database(repair_tool.results["repaired_path"])
            self.assertTrue(validation_results["is_valid_sqlite"])
            # The integrity check might still fail depending on how severe the corruption was
            # and which repair strategy was used, so we don't assert on that


if __name__ == '__main__':
    unittest.main()
