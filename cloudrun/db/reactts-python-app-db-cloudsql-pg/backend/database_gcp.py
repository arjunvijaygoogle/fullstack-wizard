from typing import List
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from pydantic import BaseModel

class Account(BaseModel):
    id: int
    number: str
    userId: int


class AccountListResponse(BaseModel):
    accounts: List[Account]
    
def connect():
    # initialize Connector object
    connector = Connector()

    return connector

def get_all_accounts(connector: Connector):

    # initialize SQLAlchemy connection pool with Connector
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=lambda: connector.connect(
            "arjun-demo-123:us-central1:test-instance",
            "pg8000",
            user="admin",
            password="admin123",
            db="test"
        ),
    )

    accounts_data: List[Account] = []
    # connect to database
    with pool.connect() as db_conn:

        # query database
        result = db_conn.execute(sqlalchemy.text("SELECT * from account")).fetchall()

        # commit transaction (SQLAlchemy v2.X.X is commit as you go)
        db_conn.commit()

        # Do something with the results
        for row in result:
            print(row)
            accounts_data.append(
                Account(id=row[0], number=row[1], userId=float(row[2]))
            )

    connector.close()
    return AccountListResponse(accounts=accounts_data).model_dump_json(indent=4, by_alias=True)


# if __name__ == "__main__":
#     connector = connect()
#     get_all_accounts(connector)