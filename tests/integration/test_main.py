import logging

from fastapi import status
from fastapi.testclient import TestClient
from src.main import app


def test_welcome(caplog):
    # WHEN
    client = TestClient(app)
    with caplog.at_level(logging.INFO):
        response = client.get("/")

    # THEN
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to NebulaPicker"}
    assert False
