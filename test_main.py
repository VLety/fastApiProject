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

TestApiServer = TestClient(app)

valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInNjb3BlcyI6W10sImV4cCI6MTcyNTg3NzY5OX0.V6apnF1O_aT1ct_WoCanzWZSnncJGmTcnfKl7HZJTK4"
expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInNjb3BlcyI6W10sImV4cCI6MTcyNTg3MzIyNX0.BnQ0CRDKkKUzvlkkeF_J3_QeipIIR9BkuAQpoz7ZJ0Y"
wrong_token = "Wrong Token!"

valid_headers = {"Authorization": "Bearer " + valid_token}
expired_headers = {"Authorization": "Bearer " + expired_token}
wrong_headers = {"Authorization": "Bearer " + wrong_token}

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
    "id": 0,
    "created": "string",
    "updated": "string"
}

new_employee = {
    "first_name": "Jones",
    "last_name": "Smith",
    "nick_name": "Bravo",
    "phone": "+380504430000",
    "email": "user@gmail.com",
    "birthday": "2024-06-01",
    "country": "Ukraine",
    "city": "Kyiv",
    "address": "Khreschatyk St, 14, UA 01001",
    "id": 0,
    "created": "string",
    "updated": "string",
    "tickets": []
}


def test_read_me_wrong_token():
    response = TestApiServer.get("/api/v1/me", headers=wrong_headers)
    print("\n" + "Response:")
    util.print_json(response.json())

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials"
    }


def test_read_me_expired_token():
    response = TestApiServer.get("/api/v1/me", headers=expired_headers)
    print("\n" + "Response:")
    util.print_json(response.json())

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Token has expired"
    }


def test_read_me():
    response = TestApiServer.get("/api/v1/me", headers=valid_headers)
    print("\n" + "Response:")
    util.print_json(response.json())

    current_user["id"] = response.json()["id"]
    current_user["created"] = response.json()["created"]
    current_user["updated"] = response.json()["updated"]

    assert response.status_code == 200
    assert response.json() == current_user


def test_read_status():
    response = TestApiServer.get("/api/v1/status", headers=valid_headers)
    print("\n" + "Response:")
    util.print_json(response.json())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_employee():
    response = TestApiServer.post("/api/v1/employee", headers=valid_headers, json=new_employee)
    print("\n" + "Response:")
    util.print_json(response.json())

    new_employee["id"] = response.json()["id"]
    new_employee["created"] = response.json()["created"]
    new_employee["updated"] = response.json()["updated"]
    new_employee["tickets"] = response.json()["tickets"]

    assert response.status_code == 200
    assert response.json() == new_employee
