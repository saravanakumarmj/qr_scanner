from services.upload_service import UploadService

service = UploadService()

success, message = service.run()

print()

print(success)

print(message)