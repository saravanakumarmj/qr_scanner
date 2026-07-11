from database.database import connect, close
from database.repository import Repository

connect()

repo = Repository()

record = repo.get_qr("250101S0001")

print(record)

close()
