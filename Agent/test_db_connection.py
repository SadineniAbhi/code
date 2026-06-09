from pymongo import MongoClient

conn_string = ""

try:
    client = MongoClient(conn_string)
    # The 'ping' command is cheap and does not require a specific database
    client.admin.command("ping")
    print("✅ Ping successful! Connected to MongoDB.")
except Exception as e:
    print("❌ Connection failed:", e)
