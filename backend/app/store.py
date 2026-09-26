from collections import defaultdict
from threading import Lock
from datetime import datetime, timezone

from pymongo import MongoClient

from app.settings import settings


mem = defaultdict(list)
lock = Lock()
db = None
mongo_client = None


def init_db():
    global db
    global mongo_client

    if not settings.mongodb_uri:
        print("MongoDB URI not configured; using in-memory store")
        return

    try:
        mongo_client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=2500
        )

        mongo_client.admin.command("ping")

        db = mongo_client[settings.mongodb_db]

        print("MongoDB Atlas connected")

    except Exception as e:
        db = None
        mongo_client = None

        print(
            "MongoDB unavailable; using in-memory store:",
            e
        )


def save(collection, doc=None):
    """
    Save a document.

    Normal usage:
        save("chat_history", document)

    If only one argument is supplied, it is stored
    in the default 'chat_history' collection.
    """

    # Allow save(doc) as well as save(collection, doc)
    if doc is None:
        doc = collection
        collection = "chat_history"

    if doc is None:
        return None

    doc = dict(doc)

    doc.setdefault(
        "created_at",
        datetime.now(timezone.utc).isoformat()
    )

    with lock:
        mem[collection].insert(0, doc)

    # Save to MongoDB when configured
    if db is not None:

        try:
            db[collection].insert_one(doc)

        except Exception as e:

            print(
                f"MongoDB save failed for collection "
                f"'{collection}': {e}"
            )

    return doc


def all_items(collection):
    """
    Return all documents from a collection.
    """

    with lock:
        return list(mem[collection])


def find(collection, key, value):
    """
    Find the first matching document.
    """

    with lock:

        for item in mem[collection]:

            if item.get(key) == value:
                return item

    return None


def count(collection):
    """
    Return number of documents in a collection.
    """

    with lock:
        return len(mem[collection])


def clear_memory():
    """
    Clear the in-memory store.
    """

    with lock:
        mem.clear()