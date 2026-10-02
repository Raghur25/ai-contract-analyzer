from pymongo import MongoClient
from pymongo.errors import OperationFailure

from app.config import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client["mydb"]  # Get the default database from the URI

# Collections
contracts_collection = db["contracts"]
analysis_collection = db["analysis"]


def init_db():
    # Contracts have no "contract_id" field, so a unique index on it made every
    # insert after the first fail. Drop it if an earlier run created it.
    try:
        contracts_collection.drop_index("contract_id_1")
    except OperationFailure:
        pass  # index does not exist

    # Analyses reference their contract through "contract_id"
    analysis_collection.create_index("contract_id")