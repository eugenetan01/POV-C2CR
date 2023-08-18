#!/usr/bin/env python3
##
# Script to continuously inserts new documents into the MongoDB database/
# collection 'AUTO_HA.records'
#
# Prerequisite: Install latest PyMongo driver and other libraries, e.g:
#   $ sudo pip3 install pymongo dnspython
#
# For usage details, run with no params (first ensure script is executable):
#   $ ./continuous-insert.py
##
import sys
from random import randint
import time
import datetime
import pymongo

USER = "TBD"
PASSWORD = "TBD"
CLUSTER_URL = "TBD.mongodb.net"
DB_NAME = "sample_analytics"
TTL_INDEX_NAME = "date_created_ttl_index"

####
# Main start function
####


def main():
    peform_inserts()


####
# Perform the continuous database insert workload, sleeping for 10 milliseconds
# between each insert operation
####


def peform_inserts():
    mongodb_url = (
        f"mongodb+srv://{USER}:{PASSWORD}@{CLUSTER_URL}/?retryWrites=true&w=majority"
    )
    print(f"Connecting to:\n {mongodb_url}\n")
    connection = pymongo.MongoClient(mongodb_url, retryWrites=True, retryReads=True)
    db = connection[DB_NAME]
    connect_problem = False
    count = 0

    while True:
        try:
            count += 1
            account_id = randint(100000, 999999)
            timestamp = datetime.datetime.utcnow()

            res_account = db.accounts.insert_one(
                {
                    "account_id": account_id,
                    "date_created": timestamp,
                    "limit": randint(1000, 10000),
                    "products": ["InvestmentFund"],
                }
            )

            res_transactions = db.transactions.insert_one(
                {
                    "account_id": randint(100000, 999999),
                    "date_created": timestamp,
                    "bucket_start_date": timestamp,
                    "bucket_end_date": datetime.datetime.utcnow(),
                    "transactions": [
                        {
                            "date": timestamp,
                            "amount": 1,
                            "transaction_code": "buy",
                            "symbol": "goog",
                            "price": "876.12345",
                            "total": "876.12345",
                        }
                    ],
                }
            )

            print("Inserted Account:" + str(res_account.inserted_id))
            print("Inserted transaction:" + str(res_transactions.inserted_id))
        except KeyboardInterrupt:
            print
            sys.exit(0)
        except Exception as e:
            print(f"{datetime.datetime.now()} - DB-CONNECTION-PROBLEM: " f"{str(e)}")
            connect_problem = True


# Constants


####
# Main
####
if __name__ == "__main__":
    main()
