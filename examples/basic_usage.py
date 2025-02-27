"""
Basic usage examples for the JackalPin Python SDK.
"""

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from jackalpin import JackalPinClient, JackalPinError, UnauthorizedError


async def main():
    """Run example operations using the JackalPin SDK."""
    print("🚀 JackalPin Python SDK Examples")

    # Load API key from .env file or environment
    load_dotenv()
    api_key = os.getenv("JACKALPIN_API_KEY")
    
    if not api_key:
        print("⚠️ No API key found. Please set the JACKALPIN_API_KEY environment variable.")
        print("You can continue with operations that don't require authentication.")
    
    # Initialize client
    client = JackalPinClient(api_key=api_key)
    
    try:
        # Test API key if available
        if api_key:
            print("\n🔑 Testing API key...")
            try:
                result = await client.test_key()
                print(f"✅ {result.message}")
            except UnauthorizedError:
                print("❌ API key is invalid or expired")
                return

            # List files (with pagination)
            print("\n📋 Listing files...")
            try:
                files = await client.list_files(limit=5)
                print(f"✅ Found {files.count} total files. Showing first {len(files.files)}:")
                for file in files.files:
                    # Format size as KB or MB
                    size = file.size / 1024
                    size_unit = "KB"
                    if size >= 1024:
                        size = size / 1024
                        size_unit = "MB"
                    
                    # Format creation date
                    try:
                        created_date = datetime.fromisoformat(file.created_at.replace('Z', '+00:00'))
                        created_str = created_date.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        created_str = file.created_at
                    
                    print(f"  - {file.file_name} ({file.cid})")
                    print(f"    Size: {size:.2f} {size_unit}, Created: {created_str}")
            except JackalPinError as e:
                print(f"❌ Error listing files: {e.message}")

            # List collections
            print("\n📁 Listing collections...")
            try:
                collections = await client.list_collections(limit=5)
                print(f"✅ Found {collections.count} total collections. Showing first {len(collections.collections)}:")
                for coll in collections.collections:
                    print(f"  - {coll.name} (ID: {coll.id})")
                    if coll.cid:
                        print(f"    CID: {coll.cid}")
            except JackalPinError as e:
                print(f"❌ Error listing collections: {e.message}")

            # Get usage stats
            print("\n📊 Getting usage stats...")
            try:
                usage = await client.get_usage()
                used_gb = usage.bytes_used / (1024**3)
                allowed_gb = usage.bytes_allowed / (1024**3)
                usage_percent = (usage.bytes_used / usage.bytes_allowed) * 100
                print(f"✅ Using {used_gb:.2f} GB of {allowed_gb:.2f} GB ({usage_percent:.2f}%)")
            except JackalPinError as e:
                print(f"❌ Error getting usage: {e.message}")

            # Get account ID
            print("\n🆔 Getting account ID...")
            try:
                account_id = await client.get_account_id()
                print(f"✅ Account ID: {account_id.id}")
            except JackalPinError as e:
                print(f"❌ Error getting account ID: {e.message}")

        # Get queue size (doesn't require authentication)
        print("\n⏱️ Getting queue size...")
        try:
            queue_size = await client.get_queue_size()
            print(f"✅ Current processing queue size: {queue_size.size}")
        except JackalPinError as e:
            print(f"❌ Error getting queue size: {e.message}")

    except JackalPinError as e:
        print(f"❌ Error: {e.message}")
        if hasattr(e, 'status_code') and e.status_code:
            print(f"   Status: {e.status_code}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
