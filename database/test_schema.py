from database.database import connect, close
from database.schema import initialize_database

connect()

initialize_database()

close()
