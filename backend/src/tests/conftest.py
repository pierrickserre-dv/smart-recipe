from unittest.mock import MagicMock, patch

patcher_auth = patch(
    "google.auth.default", return_value=(MagicMock(), "mock-project-id")
)
patcher_firestore = patch("google.cloud.firestore.Client")
patcher_firebase = patch("firebase_admin.initialize_app")

patcher_auth.start()
patcher_firestore.start()
patcher_firebase.start()


def pytest_sessionfinish(session, exitstatus):
    patcher_auth.stop()
    patcher_firestore.stop()
    patcher_firebase.stop()
