#!/usr/bin/env python3
"""
Test clear session with persistent storage (JSON and SQLite)
"""

from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager
import os
import tempfile
import shutil

def test_clear_session_with_persistent_storage():
    """Test clear session with both JSON and SQLite storage"""
    
    print("🧪 TESTING CLEAR SESSION WITH PERSISTENT STORAGE")
    print("=" * 60)
    
    # Test with both storage types
    storage_types = ["json", "sqlite"]
    
    for storage_type in storage_types:
        print(f"\n📁 Testing with {storage_type.upper()} storage")
        print("-" * 40)
        
        # Create temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        storage_path = os.path.join(temp_dir, "test_sessions")
        
        try:
            # Initialize components with persistent storage
            human_conversation_manager = HumanConversationManager()
            session_manager = SessionManager(storage_type=storage_type, storage_path=storage_path)
            
            session_id = "test_persistent_clear"
            
            # Build up context
            print("📝 Building context...")
            session = session_manager.get_session(session_id)
            
            # Add some context
            result = human_conversation_manager.process_human_conversation("track order 9999", session)
            session_manager.update_session(session)
            
            # Verify storage file exists
            if storage_type == "json":
                storage_file = os.path.join(storage_path, f"{session_id}.json")
                file_exists_before = os.path.exists(storage_file)
                print(f"  JSON file exists before clear: {file_exists_before}")
            elif storage_type == "sqlite":
                storage_file = f"{storage_path}.db"
                file_exists_before = os.path.exists(storage_file)
                print(f"  SQLite file exists before clear: {file_exists_before}")
            
            # Verify session exists in memory
            session_in_memory_before = session_id in session_manager.sessions
            print(f"  Session in memory before clear: {session_in_memory_before}")
            
            # Clear the session
            print("🧹 Clearing session...")
            session_manager.clear_session(session_id)
            
            # Check that session is removed from memory
            session_in_memory_after = session_id in session_manager.sessions
            print(f"  Session in memory after clear: {session_in_memory_after}")
            
            # Check storage file handling
            if storage_type == "json":
                file_exists_after = os.path.exists(storage_file)
                print(f"  JSON file exists after clear: {file_exists_after}")
            elif storage_type == "sqlite":
                # For SQLite, check if record was deleted (file still exists but record is gone)
                file_exists_after = os.path.exists(storage_file)
                print(f"  SQLite file exists after clear: {file_exists_after}")
                
                # Check if record was actually deleted
                if file_exists_after:
                    import sqlite3
                    with sqlite3.connect(storage_file) as conn:
                        cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE session_id = ?", (session_id,))
                        record_count = cursor.fetchone()[0]
                        print(f"  SQLite records for session: {record_count}")
            
            # Test fresh session
            print("🔍 Testing fresh session...")
            fresh_session = session_manager.get_session(session_id)
            
            # Verify it's completely fresh
            is_fresh = (
                len(fresh_session.conversation_history) == 0 and
                len(fresh_session.order_states) == 0 and
                fresh_session.active_order_id is None
            )
            
            print(f"  Fresh session state: {is_fresh}")
            
            # Validation
            if storage_type == "json":
                success = (
                    file_exists_before and
                    not session_in_memory_after and
                    not file_exists_after and
                    is_fresh
                )
            else:  # sqlite
                success = (
                    file_exists_before and
                    not session_in_memory_after and
                    record_count == 0 and
                    is_fresh
                )
            
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  {status}: {storage_type.upper()} storage clear test")
            
        except Exception as e:
            print(f"❌ ERROR testing {storage_type}: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    print(f"\n🎯 PERSISTENT STORAGE TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_clear_session_with_persistent_storage()