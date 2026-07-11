from database.database import connect, is_connected, close

connect()

print(is_connected())

close()

print(is_connected())
