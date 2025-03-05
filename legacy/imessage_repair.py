import os
import shutil
import sqlite3
import subprocess
import sys

def get_sqlite_version():
    """Check the installed SQLite version."""
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('SELECT sqlite_version()')
        version = cursor.fetchone()[0]
        conn.close()
        return version
    except Exception as e:
        print(f"Could not determine SQLite version: {e}")
        return None

def advanced_db_repair(input_path):
    """
    Advanced repair strategy for severely corrupted SQLite databases
    """
    # Create paths
    base, ext = os.path.splitext(input_path)
    backup_path = f"{base}_original_backup{ext}"
    repaired_path = f"{base}_advanced_repaired{ext}"
    
    # Create backup
    shutil.copy2(input_path, backup_path)
    print(f"Created backup: {backup_path}")
    
    # Repair strategies
    repair_strategies = [
        # Strategy 1: Simple copy and vacuum
        lambda path: simple_vacuum_repair(path),
        
        # Strategy 2: SQLite .recover command (if available)
        lambda path: sqlite_recover_repair(path),
        
        # Strategy 3: Attempt to extract as much data as possible
        lambda path: salvage_data_repair(path)
    ]
    
    # Try each repair strategy
    for strategy in repair_strategies:
        try:
            # Create a fresh copy for each strategy
            shutil.copy2(input_path, repaired_path)
            
            print(f"Attempting repair with: {strategy.__name__}")
            if strategy(repaired_path):
                print(f"Repair successful using {strategy.__name__}")
                return repaired_path
        except Exception as e:
            print(f"Strategy {strategy.__name__} failed: {e}")
    
    print("All repair strategies failed.")
    return None

def simple_vacuum_repair(db_path):
    """
    Attempt a simple vacuum repair
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA integrity_check")
        conn.execute("VACUUM")
        conn.close()
        return True
    except sqlite3.DatabaseError as e:
        print(f"Simple vacuum repair failed: {e}")
        return False

def sqlite_recover_repair(db_path):
    """
    Use SQLite's .recover command if available
    """
    try:
        # Attempt to use sqlite3 command-line tool to recover
        output_path = f"{db_path}_recovered{os.path.splitext(db_path)[1]}"
        
        # Construct recover command
        command = [
            'sqlite3', 
            db_path, 
            f'.recover {output_path}'
        ]
        
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Check if recovery was successful
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"Recovered database saved to: {output_path}")
            return True
        
        return False
    except Exception as e:
        print(f"SQLite recover command failed: {e}")
        return False

def salvage_data_repair(db_path):
    """
    Attempt to salvage as much data as possible
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Print out table names and try to count rows
        print("Attempting to salvage data from tables:")
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"Table: {table_name}, Rows: {count}")
            except sqlite3.Error:
                print(f"Could not access table: {table_name}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Data salvage attempt failed: {e}")
        return False

def main():
    # Paths
    input_file = r"D:\archived stuff\Messages\chat.db"
    
    # Check file exists
    if not os.path.exists(input_file):
        print(f"Error: File not found at {input_file}")
        return
    
    # Check SQLite version
    sqlite_version = get_sqlite_version()
    print(f"SQLite Version: {sqlite_version}")
    
    # Attempt advanced repair
    repaired_file = advanced_db_repair(input_file)
    
    if repaired_file:
        print(f"Repair process completed. Check: {repaired_file}")
    else:
        print("Comprehensive repair failed. Consider professional data recovery.")

if __name__ == '__main__':
    main()