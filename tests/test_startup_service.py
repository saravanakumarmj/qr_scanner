from database.database import connect, close
from services.startup_service import StartupService


connect()

startup = StartupService()

startup.start()

close()
