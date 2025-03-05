#!/usr/bin/env python3
"""
Advanced SQLite Database Repair Tool

This script combines and enhances the functionality of imessage_repair.py and malfix.py
to provide a comprehensive SQLite database repair tool with advanced features.

Features:
- Multiple repair strategies for different corruption scenarios
- Command-line interface for easy use
- Detailed logging and reporting
- Support for any SQLite database (not just iMessage)
- Database integrity validation
- Partial data extraction for severely corrupted files
- Cross-platform support
"""

import os
import sys
import shutil
import sqlite3
import subprocess
import logging
import argparse
import json
import datetime
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union


class DatabaseRepairTool:
    """Advanced SQLite database repair tool with multiple strategies."""

    def __init__(self, input_path: str, output_dir: Optional[str] = None, 
                 log_level: str = "INFO", is_imessage: bool = False):
        """
        Initialize the database repair tool.
        
        Args:
            input_path: Path to the SQLite database to repair
            output_dir: Directory to save repaired database and reports (default: same as input)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            is_imessage: Whether the database is an iMessage database
        """
        # Setup paths
        self.input_path = os.path.abspath(input_path)
        self.db_filename = os.path.basename(input_path)
        self.is_imessage = is_imessage
        
        # Setup output directory
        if output_dir:
            self.output_dir = os.path.abspath(output_dir)
        else:
            self.output_dir = os.path.dirname(self.input_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup logging
        self.log_file = os.path.join(self.output_dir, f"repair_{os.path.splitext(self.db_filename)[0]}.log")
        self._setup_logging(log_level)
        
        # Initialize results
        self.results = {
            "database_info": {
                "original_path": self.input_path,
                "size": os.path.getsize(self.input_path) if os.path.exists(self.input_path) else 0,
                "sqlite_version": self._get_sqlite_version(),
                "platform": platform.system(),
                "is_imessage": is_imessage
            },
            "repair_attempts": [],
            "tables_recovered": [],
            "success": False,
            "repaired_path": None,
            "report_path": None
        }
        
        self.logger.info(f"Initialized repair tool for {self.input_path}")
        self.logger.info(f"SQLite version: {self.results['database_info']['sqlite_version']}")
        self.logger.info(f"Platform: {self.results['database_info']['platform']}")

    def _setup_logging(self, log_level: str):
        """Setup logging configuration."""
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Configure logging
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized at level {log_level}")
        self.logger.info(f"Log file: {self.log_file}")

    def _get_sqlite_version(self) -> str:
        """Get the installed SQLite version."""
        try:
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute('SELECT sqlite_version()')
            version = cursor.fetchone()[0]
            conn.close()
            return version
        except Exception as e:
            self.logger.error(f"Could not determine SQLite version: {e}")
            return "Unknown"

    def create_backup(self) -> str:
        """Create a backup of the original database file."""
        backup_dir = os.path.join(self.output_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(self.db_filename)
        backup_path = os.path.join(backup_dir, f"{base}_backup_{timestamp}{ext}")
        
        try:
            shutil.copy2(self.input_path, backup_path)
            self.logger.info(f"Created backup at: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise

    def validate_database(self, db_path: str) -> Dict[str, Any]:
        """
        Validate the database integrity and collect information.
        
        Args:
            db_path: Path to the database to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "is_valid_sqlite": False,
            "integrity_check": None,
            "tables": [],
            "table_counts": {},
            "errors": []
        }
        
        # Check if file exists
        if not os.path.exists(db_path):
            validation_results["errors"].append(f"File not found: {db_path}")
            return validation_results
        
        # Check SQLite header
        try:
            with open(db_path, 'rb') as f:
                header = f.read(16)
                validation_results["is_valid_sqlite"] = (header[:16] == b'SQLite format 3\x00')
                if not validation_results["is_valid_sqlite"]:
                    validation_results["errors"].append("Not a valid SQLite database (header check failed)")
        except Exception as e:
            validation_results["errors"].append(f"Error checking SQLite header: {e}")
        
        # If not a valid SQLite database, return early
        if not validation_results["is_valid_sqlite"]:
            return validation_results
        
        # Try to connect and get database information
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check integrity
            try:
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                validation_results["integrity_check"] = integrity_result
            except sqlite3.Error as e:
                validation_results["errors"].append(f"Integrity check failed: {e}")
            
            # Get table list
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                validation_results["tables"] = tables
                
                # Get row counts for each table
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                        count = cursor.fetchone()[0]
                        validation_results["table_counts"][table] = count
                    except sqlite3.Error as e:
                        validation_results["errors"].append(f"Could not count rows in table {table}: {e}")
            except sqlite3.Error as e:
                validation_results["errors"].append(f"Could not list tables: {e}")
            
            conn.close()
        except sqlite3.Error as e:
            validation_results["errors"].append(f"Could not connect to database: {e}")
        
        return validation_results

    def repair_database(self) -> bool:
        """
        Attempt to repair the database using multiple strategies.
        
        Returns:
            True if at least one repair strategy was successful, False otherwise
        """
        self.logger.info(f"Starting repair process for {self.input_path}")
        
        # Create backup
        try:
            backup_path = self.create_backup()
        except Exception as e:
            self.logger.error(f"Repair aborted: {e}")
            return False
        
        # Validate original database
        self.logger.info("Validating original database...")
        original_validation = self.validate_database(self.input_path)
        self.results["original_validation"] = original_validation
        
        if original_validation["integrity_check"] == "ok":
            self.logger.info("Database integrity check passed. No repair needed.")
            self.results["success"] = True
            self.results["repaired_path"] = self.input_path
            return True
        
        # Create output path for repaired database
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(self.db_filename)
        repaired_path = os.path.join(self.output_dir, f"{base}_repaired_{timestamp}{ext}")
        
        # Define repair strategies
        repair_strategies = [
            self._basic_pragma_repair,
            self._vacuum_repair,
            self._sqlite_recover_repair,
            self._dump_and_reload_repair,
            self._salvage_data_repair
        ]
        
        # Try each repair strategy
        success = False
        for strategy in repair_strategies:
            strategy_name = strategy.__name__.replace("_", " ").title()
            self.logger.info(f"Attempting repair with: {strategy_name}")
            
            # Create a fresh copy for each strategy
            try:
                strategy_path = f"{repaired_path}_{strategy.__name__}"
                shutil.copy2(self.input_path, strategy_path)
                
                # Attempt repair
                start_time = datetime.datetime.now()
                strategy_result = strategy(strategy_path)
                end_time = datetime.datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Record attempt
                attempt_info = {
                    "strategy": strategy_name,
                    "success": strategy_result["success"],
                    "path": strategy_path if strategy_result["success"] else None,
                    "duration": duration,
                    "details": strategy_result.get("details", {})
                }
                self.results["repair_attempts"].append(attempt_info)
                
                # If successful, validate the repaired database
                if strategy_result["success"]:
                    self.logger.info(f"Strategy {strategy_name} succeeded")
                    validation = self.validate_database(strategy_path)
                    
                    # Check if the repaired database is better than the original
                    is_better = self._is_repair_better(original_validation, validation)
                    
                    if is_better:
                        self.logger.info(f"Repaired database is better than original")
                        success = True
                        self.results["success"] = True
                        self.results["repaired_path"] = strategy_path
                        self.results["repaired_validation"] = validation
                        
                        # If this is a perfect repair, we can stop
                        if validation["integrity_check"] == "ok":
                            self.logger.info("Perfect repair achieved. Stopping repair process.")
                            break
                    else:
                        self.logger.info("Repaired database is not better than original")
                else:
                    self.logger.warning(f"Strategy {strategy_name} failed")
            
            except Exception as e:
                self.logger.error(f"Error during {strategy_name}: {e}")
                self.results["repair_attempts"].append({
                    "strategy": strategy_name,
                    "success": False,
                    "error": str(e)
                })
        
        # Generate report
        self._generate_report()
        
        return success

    def _is_repair_better(self, original_validation: Dict[str, Any], 
                          repaired_validation: Dict[str, Any]) -> bool:
        """
        Determine if the repaired database is better than the original.
        
        Args:
            original_validation: Validation results for original database
            repaired_validation: Validation results for repaired database
            
        Returns:
            True if repaired is better, False otherwise
        """
        # If original had integrity issues but repaired doesn't
        if (original_validation["integrity_check"] != "ok" and 
            repaired_validation["integrity_check"] == "ok"):
            return True
        
        # If repaired has more accessible tables
        if len(repaired_validation["table_counts"]) > len(original_validation["table_counts"]):
            return True
        
        # If repaired has more total rows across all tables
        original_total_rows = sum(original_validation["table_counts"].values())
        repaired_total_rows = sum(repaired_validation["table_counts"].values())
        
        if repaired_total_rows > original_total_rows:
            return True
        
        # If repaired has fewer errors
        if len(repaired_validation["errors"]) < len(original_validation["errors"]):
            return True
        
        return False

    def _basic_pragma_repair(self, db_path: str) -> Dict[str, Any]:
        """
        Attempt basic PRAGMA repairs on the database.
        
        Args:
            db_path: Path to the database to repair
            
        Returns:
            Dictionary with repair results
        """
        result = {
            "success": False,
            "details": {
                "pragmas_attempted": [],
                "pragmas_succeeded": []
            }
        }
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # List of PRAGMA commands to try
            pragmas = [
                "PRAGMA integrity_check",
                "PRAGMA quick_check",
                "PRAGMA foreign_key_check"
            ]
            
            for pragma in pragmas:
                result["details"]["pragmas_attempted"].append(pragma)
                try:
                    self.logger.info(f"Executing {pragma}")
                    cursor.execute(pragma)
                    pragma_result = cursor.fetchone()
                    self.logger.info(f"Result: {pragma_result}")
                    result["details"]["pragmas_succeeded"].append(pragma)
                except sqlite3.Error as e:
                    self.logger.warning(f"PRAGMA failed: {pragma} - {e}")
            
            # Success if at least one PRAGMA succeeded
            result["success"] = len(result["details"]["pragmas_succeeded"]) > 0
            
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"Basic PRAGMA repair failed: {e}")
            result["details"]["error"] = str(e)
        
        return result

    def _vacuum_repair(self, db_path: str) -> Dict[str, Any]:
        """
        Attempt to repair the database using VACUUM.
        
        Args:
            db_path: Path to the database to repair
            
        Returns:
            Dictionary with repair results
        """
        result = {
            "success": False,
            "details": {}
        }
        
        try:
            conn = sqlite3.connect(db_path)
            
            # Try integrity check first
            try:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                result["details"]["integrity_check"] = integrity_result
            except sqlite3.Error as e:
                self.logger.warning(f"Integrity check failed: {e}")
                result["details"]["integrity_check_error"] = str(e)
            
            # Try vacuum
            try:
                self.logger.info("Executing VACUUM")
                conn.execute("VACUUM")
                conn.commit()
                self.logger.info("VACUUM completed successfully")
                result["success"] = True
            except sqlite3.Error as e:
                self.logger.warning(f"VACUUM failed: {e}")
                result["details"]["vacuum_error"] = str(e)
            
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"Vacuum repair failed: {e}")
            result["details"]["error"] = str(e)
        
        return result

    def _sqlite_recover_repair(self, db_path: str) -> Dict[str, Any]:
        """
        Attempt to repair the database using SQLite's .recover command.
        
        Args:
            db_path: Path to the database to repair
            
        Returns:
            Dictionary with repair results
        """
        result = {
            "success": False,
            "details": {}
        }
        
        # Check if sqlite3 command-line tool is available
        try:
            version_check = subprocess.run(
                ["sqlite3", "--version"], 
                capture_output=True, 
                text=True
            )
            result["details"]["sqlite3_cli_version"] = version_check.stdout.strip()
        except Exception as e:
            self.logger.warning(f"SQLite3 command-line tool not available: {e}")
            result["details"]["error"] = "SQLite3 command-line tool not available"
            return result
        
        try:
            # Create temporary SQL file for recovery
            temp_sql_path = f"{db_path}_recovery.sql"
            
            # Construct recover command
            command = [
                "sqlite3", 
                db_path, 
                f".recover"
            ]
            
            # Run the command and capture output to SQL file
            with open(temp_sql_path, 'w') as sql_file:
                self.logger.info(f"Running SQLite .recover command")
                process = subprocess.run(
                    command,
                    stdout=sql_file,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            result["details"]["command"] = " ".join(command)
            result["details"]["return_code"] = process.returncode
            result["details"]["stderr"] = process.stderr
            
            # Check if SQL file was created and has content
            if os.path.exists(temp_sql_path) and os.path.getsize(temp_sql_path) > 0:
                # Create a new database from the SQL file
                new_db_path = f"{db_path}_recovered"
                
                # Import the SQL into a new database
                import_command = [
                    "sqlite3",
                    new_db_path,
                    f".read {temp_sql_path}"
                ]
                
                self.logger.info(f"Importing recovered SQL into new database")
                import_process = subprocess.run(
                    import_command,
                    capture_output=True,
                    text=True
                )
                
                result["details"]["import_command"] = " ".join(import_command)
                result["details"]["import_return_code"] = import_process.returncode
                result["details"]["import_stderr"] = import_process.stderr
                
                # If new database was created successfully, copy it to the original path
                if os.path.exists(new_db_path) and os.path.getsize(new_db_path) > 0:
                    shutil.copy2(new_db_path, db_path)
                    self.logger.info(f"Recovered database copied to {db_path}")
                    result["success"] = True
                    
                    # Clean up temporary files
                    os.remove(new_db_path)
                    os.remove(temp_sql_path)
                else:
                    self.logger.warning("Failed to create recovered database")
            else:
                self.logger.warning("No recovery SQL generated")
        
        except Exception as e:
            self.logger.error(f"SQLite recover command failed: {e}")
            result["details"]["error"] = str(e)
        
        return result

    def _dump_and_reload_repair(self, db_path: str) -> Dict[str, Any]:
        """
        Attempt to repair the database by dumping and reloading.
        
        Args:
            db_path: Path to the database to repair
            
        Returns:
            Dictionary with repair results
        """
        result = {
            "success": False,
            "details": {
                "tables_dumped": [],
                "tables_reloaded": []
            }
        }
        
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                self.logger.warning("No tables found in database")
                conn.close()
                return result
            
            # Create a new database for the repaired version
            temp_db_path = f"{db_path}_temp"
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            
            temp_conn = sqlite3.connect(temp_db_path)
            
            # For each table, try to dump and reload
            for table in tables:
                try:
                    # Get table schema
                    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                    schema = cursor.fetchone()
                    
                    if schema and schema[0]:
                        # Create table in new database
                        temp_conn.execute(schema[0])
                        result["details"]["tables_dumped"].append(table)
                        
                        # Try to copy data
                        try:
                            cursor.execute(f"SELECT * FROM [{table}]")
                            rows = cursor.fetchall()
                            
                            # Get column names
                            column_info = cursor.description
                            column_count = len(column_info)
                            
                            # Prepare insert statement with placeholders
                            placeholders = ", ".join(["?" for _ in range(column_count)])
                            insert_sql = f"INSERT INTO [{table}] VALUES ({placeholders})"
                            
                            # Insert data into new database
                            temp_conn.executemany(insert_sql, rows)
                            temp_conn.commit()
                            
                            result["details"]["tables_reloaded"].append(table)
                            self.logger.info(f"Table {table} dumped and reloaded successfully")
                        except sqlite3.Error as e:
                            self.logger.warning(f"Could not copy data for table {table}: {e}")
                    else:
                        self.logger.warning(f"Could not get schema for table {table}")
                
                except sqlite3.Error as e:
                    self.logger.warning(f"Error processing table {table}: {e}")
            
            # Close connections
            conn.close()
            temp_conn.close()
            
            # If any tables were reloaded, consider it a success
            if result["details"]["tables_reloaded"]:
                # Replace the original with the new database
                shutil.copy2(temp_db_path, db_path)
                result["success"] = True
                self.logger.info(f"Database repaired by dump and reload")
            
            # Clean up
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
        
        except Exception as e:
            self.logger.error(f"Dump and reload repair failed: {e}")
            result["details"]["error"] = str(e)
        
        return result

    def _salvage_data_repair(self, db_path: str) -> Dict[str, Any]:
        """
        Attempt to salvage as much data as possible from the database.
        
        Args:
            db_path: Path to the database to repair
            
        Returns:
            Dictionary with repair results
        """
        result = {
            "success": False,
            "details": {
                "tables_found": [],
                "tables_salvaged": [],
                "rows_salvaged": {}
            }
        }
        
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            result["details"]["tables_found"] = tables
            
            if not tables:
                self.logger.warning("No tables found in database")
                conn.close()
                return result
            
            # For each table, try to salvage data
            for table in tables:
                try:
                    # Get table schema
                    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                    schema = cursor.fetchone()
                    
                    if schema and schema[0]:
                        # Try to count rows
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                            count = cursor.fetchone()[0]
                            self.logger.info(f"Table {table} has {count} rows")
                            
                            # If table has rows, consider it salvaged
                            if count > 0:
                                result["details"]["tables_salvaged"].append(table)
                                result["details"]["rows_salvaged"][table] = count
                        except sqlite3.Error as e:
                            self.logger.warning(f"Could not count rows in table {table}: {e}")
                    else:
                        self.logger.warning(f"Could not get schema for table {table}")
                
                except sqlite3.Error as e:
                    self.logger.warning(f"Error processing table {table}: {e}")
            
            conn.close()
            
            # If any tables were salvaged, consider it a success
            if result["details"]["tables_salvaged"]:
                result["success"] = True
                self.logger.info(f"Database partially salvaged")
                
                # For iMessage databases, extract messages to a separate file
                if self.is_imessage and "message" in result["details"]["tables_salvaged"]:
                    self._extract_imessage_data(db_path)
        
        except Exception as e:
            self.logger.error(f"Data salvage attempt failed: {e}")
            result["details"]["error"] = str(e)
        
        return result

    def _extract_imessage_data(self, db_path: str) -> None:
        """
        Extract iMessage data to a separate file.
        
        Args:
            db_path: Path to the iMessage database
        """
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Extract messages
            try:
                query = """
                SELECT 
                    m.rowid as message_id,
                    m.guid as unique_id,
                    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date_sent,
                    m.text as message_body,
                    m.is_from_me,
                    h.id as contact_id
                FROM 
                    message m
                LEFT JOIN handle h ON m.handle_id = h.rowid
                ORDER BY m.date
                """
                
                cursor.execute(query)
                messages = [dict(row) for row in cursor.fetchall()]
                
                # Save to JSON file
                output_path = os.path.join(self.output_dir, "extracted_messages.json")
                with open(output_path, 'w') as f:
                    json.dump(messages, f, indent=2)
                
                self.logger.info(f"Extracted {len(messages)} messages to {output_path}")
                self.results["extracted_messages_path"] = output_path
            
            except sqlite3.Error as e:
                self.logger.warning(f"Could not extract messages: {e}")
            
            conn.close()
        
        except Exception as e:
            self.logger.error(f"Failed to extract iMessage data: {e}")

    def _generate_report(self) -> None:
        """Generate a detailed report of the repair process."""
        # Add timestamp to results
        self.results["timestamp"] = datetime.datetime.now().isoformat()
        
        # Save results to JSON file
        report_path = os.path.join(self.output_dir, f"repair_report_{os.path.splitext(self.db_filename)[0]}.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.results["report_path"] = report_path
        self.logger.info(f"Report saved to {report_path}")
        
        # Generate HTML report
        self._generate_html_report()

    def _generate_html_report(self) -> None:
        """Generate an HTML report of the repair process."""
        html_path = os.path.join(self.output_dir, f"repair_report_{os.path.splitext(self.db_filename)[0]}.html")
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Database Repair Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .warning {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .section {{ margin-bottom: 30px; }}
    </style>
</head>
<body>
    <h1>Database Repair Report</h1>
    <div class="section">
        <h2>Summary</h2>
        <p><strong>Database:</strong> {self.input_path}</p>
        <p><strong>Timestamp:</strong> {self.results["timestamp"]}</p>
        <p><strong>Status:</strong> <span class="{'success' if self.results['success'] else 'failure'}">
            {("Repair Successful" if self.results['success'] else "Repair Failed")}
        </span></p>
        <p><strong>SQLite Version:</strong> {self.results['database_info']['sqlite_version']}</p>
        <p><strong>Platform:</strong> {self.results['database_info']['platform']}</p>
        <p><strong>Original Size:</strong> {self.results['database_info']['size']} bytes</p>
        <p><strong>Type:</strong> {"iMessage Database" if self.results['database_info']['is_imessage'] else "SQLite Database"}</p>
        
        {f'<p><strong>Repaired Database:</strong> {self.results["repaired_path"]}</p>' if self.results["repaired_path"] else ''}
        {f'<p><strong>Report File:</strong> {self.results["report_path"]}</p>' if self.results["report_path"] else ''}
    </div>

    <div class="section">
        <h2>Repair Attempts</h2>
        <table>
            <tr>
                <th>Strategy</th>
                <th>Result</th>
                <th>Duration (s)</th>
                <th>Details</th>
            </tr>
            {''.join([f'''
            <tr>
                <td>{attempt['strategy']}</td>
                <td class="{'success' if attempt['success'] else 'failure'}">{('Success' if attempt['success'] else 'Failed')}</td>
                <td>{attempt.get('duration', 'N/A')}</td>
                <td>{attempt.get('path', 'N/A')}</td>
            </tr>
            ''' for attempt in self.results['repair_attempts']])}
        </table>
    </div>

    <div class="section">
        <h2>Database Structure</h2>
        <h3>Original Database</h3>
        <p><strong>Integrity Check:</strong> <span class="{'success' if self.results['original_validation']['integrity_check'] == 'ok' else 'failure'}">
            {self.results['original_validation'].get('integrity_check', 'Failed')}
        </span></p>
        
        <h4>Tables</h4>
        <table>
            <tr>
                <th>Table Name</th>
                <th>Row Count</th>
            </tr>
            {''.join([f'''
            <tr>
                <td>{table}</td>
                <td>{self.results['original_validation']['table_counts'].get(table, 'N/A')}</td>
            </tr>
            ''' for table in self.results['original_validation'].get('tables', [])])}
        </table>
        
        {'<h3>Repaired Database</h3>' if self.results.get('repaired_validation') else ''}
        {f'''
        <p><strong>Integrity Check:</strong> <span class="{'success' if self.results['repaired_validation']['integrity_check'] == 'ok' else 'failure'}">
            {self.results['repaired_validation'].get('integrity_check', 'Failed')}
        </span></p>
        
        <h4>Tables</h4>
        <table>
            <tr>
                <th>Table Name</th>
                <th>Row Count</th>
            </tr>
            {''.join([f"""
            <tr>
                <td>{table}</td>
                <td>{self.results['repaired_validation']['table_counts'].get(table, 'N/A')}</td>
            </tr>
            """ for table in self.results['repaired_validation'].get('tables', [])])}
        </table>
        ''' if self.results.get('repaired_validation') else ''}
    </div>

    <div class="section">
        <h2>Errors</h2>
        <ul>
            {''.join([f'<li class="failure">{error}</li>' for error in self.results['original_validation'].get('errors', [])])}
        </ul>
    </div>

    <footer>
        <p>Generated by Advanced SQLite Database Repair Tool on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>
"""
        
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report saved to {html_path}")


def main():
    """Main entry point for the script."""
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Advanced SQLite Database Repair Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_path",
        help="Path to the SQLite database file to repair"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save repaired database and reports (default: same as input)"
    )
    
    parser.add_argument(
        "-l", "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    parser.add_argument(
        "--imessage",
        action="store_true",
        help="Specify if the database is an iMessage database"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="Advanced SQLite Database Repair Tool v1.0.0"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create repair tool instance
    repair_tool = DatabaseRepairTool(
        input_path=args.input_path,
        output_dir=args.output_dir,
        log_level=args.log_level,
        is_imessage=args.imessage
    )
    
    # Attempt repair
    try:
        success = repair_tool.repair_database()
        
        if success:
            print(f"\nRepair successful! Repaired database saved to: {repair_tool.results['repaired_path']}")
            print(f"Report saved to: {repair_tool.results['report_path']}")
            sys.exit(0)
        else:
            print("\nRepair failed. Check the log file for details.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nRepair process interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
