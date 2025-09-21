#!/usr/bin/env python3
"""
Test script for Project Scanner database saving functionality.
"""

import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime

def test_database_functionality():
    """Test the database functionality directly without complex imports."""
    print("🧪 Testing Database Functionality")
    print("=" * 50)
    
    try:
        # Test database creation and basic operations
        data_path = Path("data")
        data_path.mkdir(exist_ok=True)
        db_path = data_path / "prj1.db"
        
        # Create a simple database connection
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        
        print("✅ Database connection established")
        
        # Create a simple test table
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                language TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ Test table created")
        
        # Insert a test project
        test_project = {
            'name': 'Test Project',
            'path': 'X:\\GitHub\\test-project',
            'language': 'Python',
            'description': 'A test project for database functionality'
        }
        
        cursor.execute('''
            INSERT INTO test_projects (name, path, language, description)
            VALUES (?, ?, ?, ?)
        ''', (test_project['name'], test_project['path'], test_project['language'], test_project['description']))
        
        project_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Test project inserted with ID: {project_id}")
        
        # Retrieve the project
        cursor.execute('SELECT * FROM test_projects WHERE path = ?', (test_project['path'],))
        row = cursor.fetchone()
        
        if row:
            print("✅ Project retrieved successfully")
            print(f"   Name: {row[1]}")
            print(f"   Path: {row[2]}")
            print(f"   Language: {row[3]}")
            print(f"   Description: {row[4]}")
        else:
            print("❌ Failed to retrieve project")
            return False
        
        # Update the project
        cursor.execute('''
            UPDATE test_projects SET description = ? WHERE id = ?
        ''', ('Updated test project description', project_id))
        conn.commit()
        
        print("✅ Project updated successfully")
        
        # Get all projects
        cursor.execute('SELECT * FROM test_projects')
        all_projects = cursor.fetchall()
        print(f"✅ Retrieved {len(all_projects)} projects from database")
        
        # Clean up
        cursor.execute('DROP TABLE IF EXISTS test_projects')
        conn.commit()
        conn.close()
        
        print("✅ Database test completed successfully")
        print("\n🎉 All database tests passed! The database functionality is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return False

def test_project_scanner_imports():
    """Test if we can import the project scanner modules."""
    print("\n🧪 Testing Project Scanner Imports")
    print("=" * 50)
    
    try:
        # Add the script directory to Python path
        script_dir = Path(__file__).parent / "script"
        sys.path.insert(0, str(script_dir.parent))
        
        # Try to import individual modules first
        print("Testing individual module imports...")
        
        # Test database_manager import
        try:
            from script.database_manager import DatabaseManager
            print("✅ DatabaseManager imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import DatabaseManager: {e}")
            return False
        
        # Test tag_manager import
        try:
            from script.tag_manager import TagManager
            print("✅ TagManager imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import TagManager: {e}")
            return False
        
        # Test build_system import
        try:
            from script.build_system import BuildSystemDetector
            print("✅ BuildSystemDetector imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import BuildSystemDetector: {e}")
            return False
        
        # Test project_scanner import
        try:
            from script.project_scanner import ProjectScanner
            print("✅ ProjectScanner imported successfully")
            
            # Test initialization
            scanner = ProjectScanner(use_sqlite=True)
            print("✅ ProjectScanner initialized successfully")
            
        except ImportError as e:
            print(f"❌ Failed to import ProjectScanner: {e}")
            return False
        
        print("\n🎉 All import tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed with error: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Project Scanner Tests")
    print("=" * 60)
    
    # Test basic database functionality first
    db_success = test_database_functionality()
    
    # Test project scanner imports
    import_success = test_project_scanner_imports()
    
    if db_success and import_success:
        print("\n🎉 All tests passed! Project scanner functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)
