"""
Test complete cloud -> local SQLite refresh.
"""

from services.refresh_local_service import RefreshLocalService


def test_full_refresh():

    service = RefreshLocalService()

    success, message = service.run()

    print()
    print("=" * 60)
    print("FULL LOCAL REFRESH TEST")
    print("=" * 60)
    print()
    print(f"Success : {success}")
    print(f"Message : {message}")
    print()
    print("=" * 60)

    assert success is True


if __name__ == "__main__":
    test_full_refresh()