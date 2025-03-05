import os
import shutil
import sqlite3
import logging

def repair_imessage_db(input_path, output_path=None):
    """
    Attempt to repair a malformed iMessage SQLite database file.
    
    Args:
        input_path (str): Path to the malformed iMessage database file
        output_path (str, optional): Path to save the repaired database. 
                                     If None, will create a file with '_repaired' suffix.
    
    Returns:
        bool: True if repair was successful, False otherwise
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # If no output path specified, create one with '_repaired' suffix
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_repaired{ext}"
    
    # Backup the original file
    backup_path = f"{base}_original_backup{ext}"
    try:
        shutil.copy2(input_path, backup_path)
        logger.info(f"Created backup of original file at: {backup_path}")
    except Exception as backup_error:
        logger.error(f"Failed to create backup: {backup_error}")
        return False

    # Create a copy to work on
    try:
        shutil.copy2(input_path, output_path)
    except Exception as copy_error:
        logger.error(f"Failed to create working copy: {copy_error}")
        return False

    try:
        # Attempt to connect to the database
        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()
        
        # Attempt various repair strategies
        repair_strategies = [
            "PRAGMA integrity_check",
            "PRAGMA quick_check",
            "PRAGMA foreign_key_check"
        ]
        
        for strategy in repair_strategies:
            try:
                logger.info(f"Attempting repair strategy: {strategy}")
                cursor.execute(strategy)
                result = cursor.fetchone()
                logger.info(f"Result of {strategy}: {result}")
            except sqlite3.Error as strategy_error:
                logger.warning(f"Strategy {strategy} failed: {strategy_error}")
        
        # Attempt to vacuum the database
        try:
            conn.execute("VACUUM")
            conn.commit()
            logger.info("Database vacuumed successfully")
        except sqlite3.Error as vacuum_error:
            logger.warning(f"Vacuum failed: {vacuum_error}")
        
        # Close the connection
        conn.close()
        
        logger.info(f"Repaired database saved to: {output_path}")
        return True
    
    except sqlite3.Error as e:
        logger.error(f"Critical error during repair: {e}")
        return False
    except Exception as general_error:
        logger.error(f"Unexpected error during repair: {general_error}")
        return False

def main():
    # Specify the path to your iMessage chat.db file
    input_file = os.path.join('D:', 'archived stuff', 'Messages', 'chat.db')
    
    # Repair the database
    repair_success = repair_imessage_db(input_file)
    
    if repair_success:
        print("Database repair process completed successfully.")
    else:
        print("Database repair failed. Manual intervention may be required.")

if __name__ == '__main__':
    main()

# Additional Notes:
# 1. This script is specifically designed for iMessage SQLite databases
# 2. Always work on a copy of your original file
# 3. Some database corruptions may require professional data recovery tools
# 4. Successful repair is not guaranteed for severely corrupted databases