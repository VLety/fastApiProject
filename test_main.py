"""
Project name: REST API server solution based on FastAPI framework with RBAC model
Author: Volodymyr Letiahin
Contact: https://www.linkedin.com/in/volodymyr-letiahin-0208a5b2/
License: MIT
"""
from pytest_assert_utils import util as pt_util
from fastapi.testclient import TestClient
from main import app
import util

client = TestClient(app)

valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInNjb3BlcyI6W10sImV4cCI6MTcyNTg3NzY5OX0.V6apnF1O_aT1ct_WoCanzWZSnncJGmTcnfKl7HZJTK4"
expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInNjb3BlcyI6W10sImV4cCI6MTcyNTg3MzIyNX0.BnQ0CRDKkKUzvlkkeF_J3_QeipIIR9BkuAQpoz7ZJ0Y"
valid_headers = {"Authorization": "Bearer " + valid_token}
expired_headers = {"Authorization": "Bearer " + expired_token}
current_user = {
    "username": "admin",
    "first_name": "David",
    "last_name": "Bauer",
    "phone": "+431279843271",
    "email": "admin@fastapi.com",
    "role": [
        "admin"
    ],
    "disabled": False,
    "login_denied": False,
    "id": 1,
    "created": "",
    "updated": ""
}


def test_read_me_expired_token():
    response = client.get("/api/v1/me", headers=expired_headers)
    print("\n" + "Response:")
    util.print_json(response.json())

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Token has expired"
    }


def test_read_me():
    response = client.get("/api/v1/me", headers=valid_headers)
    print("\n" + "Response:")
    util.print_json(response.json())

    try:
        current_user["id"] = response.json()["id"]
        current_user["created"] = response.json()["created"]
        current_user["updated"] = response.json()["updated"]
    except Exception:
        pass

    assert response.status_code == 200
    assert response.json() == current_user


def test_read_status():
    response = client.get("/api/v1/status", headers=valid_headers)
    print("\n" + "Response:")
    util.print_json(response.json())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
