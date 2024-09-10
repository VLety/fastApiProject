"""
Project name: REST API server solution based on FastAPI framework with RBAC model
Author: Volodymyr Letiahin
Contact: https://www.linkedin.com/in/volodymyr-letiahin-0208a5b2/
License: MIT
"""
from main import app, APP_CONFIG
import util

# FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/#testing
from pytest_assert_utils import util as pt_util
from fastapi.testclient import TestClient

TestApiServer = TestClient(app)
TestApiRootPath = APP_CONFIG["root_path"]
TestData = util.get_test_main()  # Project TEST data


def print_response(response):
    print("\n" + "Response:")
    util.print_json(response.json())


def test_create_valid_admin_header():
    response = TestApiServer.post(TestApiRootPath + "/token",
                                  data={
                                      "username": TestData["admin_user"]["username"],
                                      "password": TestData["admin_user"]["password"]
                                  })
    print_response(response)

    TestData["valid_admin_header"] = TestData["base_header"].copy()
    TestData["valid_admin_header"]["Authorization"] = (TestData["valid_admin_header"]["Authorization"] +
                                                       response.json()["access_token"])

    assert response.status_code == 200
    assert response.json() == {
        "access_token": pt_util.Any(str),
        "token_type": "bearer"
    }


def test_read_me_wrong_token():
    response = TestApiServer.get(TestApiRootPath + "/me", headers=TestData["wrong_header"])
    print_response(response)

    assert response.status_code == APP_CONFIG["raise_error"]["could_not_validate_credentials"]["status_code"]
    assert response.json() == {
        "detail": APP_CONFIG["raise_error"]["could_not_validate_credentials"]["detail"]
    }


def test_create_new_user():
    # Add password
    user_with_password = TestData["user"].copy()
    user_with_password["password"] = TestData["user_password"]

    response = TestApiServer.post(TestApiRootPath + "/user/",
                                  headers=TestData["valid_admin_header"],
                                  json=user_with_password)
    print_response(response)

    TestData["user"]["id"] = response.json()["id"]
    TestData["user"]["created"] = response.json()["created"]
    TestData["user"]["updated"] = response.json()["updated"]

    assert response.status_code == 200
    assert response.json() == TestData["user"]


def test_get_new_user_token():
    response = TestApiServer.post(TestApiRootPath + "/token",
                                  data={
                                      "username": TestData["user"]["username"],
                                      "password": TestData["user_password"]
                                  })
    print_response(response)

    TestData["user_header"] = TestData["base_header"].copy()
    TestData["user_header"]["Authorization"] = (TestData["user_header"]["Authorization"] +
                                                response.json()["access_token"])

    assert response.status_code == 200
    assert response.json() == {
        "access_token": pt_util.Any(str),
        "token_type": "bearer"
    }


def test_read_me_new_user():
    response = TestApiServer.get(TestApiRootPath + "/me",
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == 200
    assert response.json() == TestData["user"]


def test_read_status_new_user():
    response = TestApiServer.get(TestApiRootPath + "/status",
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_new_employee():
    response = TestApiServer.post(TestApiRootPath + "/employee",
                                  headers=TestData["user_header"],
                                  json=TestData["employee"])
    print_response(response)

    TestData["employee"]["id"] = response.json()["id"]
    TestData["employee"]["created"] = response.json()["created"]
    TestData["employee"]["updated"] = response.json()["updated"]
    TestData["employee"]["tickets"] = response.json()["tickets"]

    assert response.status_code == 200
    assert response.json() == TestData["employee"]


def test_read_new_employee():
    response = TestApiServer.get(TestApiRootPath + f'/employee/{TestData["employee"]["id"]}',
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == 200
    assert response.json() == TestData["employee"]


def test_update_new_employee():
    response = TestApiServer.put(TestApiRootPath + f'/employee/{TestData["employee"]["id"]}',
                                 headers=TestData["user_header"],
                                 json=TestData["employee_update"])
    print_response(response)

    # Safe old values
    old_id = TestData["employee"]["id"]
    old_created = TestData["employee"]["created"]
    old_tickets = TestData["employee"]["tickets"]

    # Update Employee with PUT data
    TestData["employee"] = TestData["employee_update"]

    # Set Employee additional data
    TestData["employee"]["id"] = old_id
    TestData["employee"]["created"] = old_created
    TestData["employee"]["updated"] = response.json()["updated"]
    TestData["employee"]["tickets"] = old_tickets

    assert response.status_code == 200
    assert response.json() == TestData["employee"]


def test_create_new_ticket_for_new_employee():
    response = TestApiServer.post(TestApiRootPath + f'/ticket/{TestData["employee"]["id"]}',
                                  headers=TestData["user_header"],
                                  json=TestData["ticket"])
    print_response(response)

    TestData["ticket"]["id"] = response.json()["id"]
    TestData["ticket"]["created"] = response.json()["created"]
    TestData["ticket"]["updated"] = response.json()["updated"]
    TestData["ticket"]["owner_id"] = TestData["user"]["id"]
    TestData["ticket"]["employee_id"] = TestData["employee"]["id"]

    assert response.status_code == 200
    assert response.json() == TestData["ticket"]


def test_read_new_ticket():
    response = TestApiServer.get(TestApiRootPath + f'/ticket/{TestData["ticket"]["id"]}',
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == 200
    assert response.json() == TestData["ticket"]


def test_read_new_employee_with_ticket():
    response = TestApiServer.get(TestApiRootPath + f'/employee/{TestData["employee"]["id"]}',
                                 headers=TestData["user_header"])
    print_response(response)

    TestData["employee"]["tickets"] = [TestData["ticket"]]

    assert response.status_code == 200
    assert response.json() == TestData["employee"]


def test_read_my_ticket():
    response = TestApiServer.get(TestApiRootPath + "/ticket/my/?skip=0&limit=100",
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == 200
    assert response.json() == [TestData["ticket"]]


def test_delete_new_ticket():
    response = TestApiServer.delete(TestApiRootPath + f'/ticket/{TestData["ticket"]["id"]}',
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == 200
    assert response.json() == {"message": APP_CONFIG["message"]["ticket_deleted_successfully"]}


def test_read_deleted_new_ticket():
    response = TestApiServer.get(TestApiRootPath + f'/ticket/{TestData["ticket"]["id"]}',
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == APP_CONFIG["raise_error"]["ticket_not_found"]["status_code"]
    assert response.json() == {"detail": APP_CONFIG["raise_error"]["ticket_not_found"]["detail"]}


def test_read_new_employee_without_ticket():
    response = TestApiServer.get(TestApiRootPath + f'/employee/{TestData["employee"]["id"]}',
                                 headers=TestData["user_header"])
    print_response(response)

    TestData["employee"]["tickets"] = []

    assert response.status_code == 200
    assert response.json() == TestData["employee"]


def test_delete_new_employee():
    response = TestApiServer.delete(TestApiRootPath + f'/employee/{TestData["employee"]["id"]}',
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == 200
    assert response.json() == {"message": APP_CONFIG["message"]["employee_deleted_successfully"]}


def test_read_deleted_new_employee():
    response = TestApiServer.get(TestApiRootPath + f'/employee/{TestData["employee"]["id"]}',
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == APP_CONFIG["raise_error"]["employee_not_found"]["status_code"]
    assert response.json() == {"detail": APP_CONFIG["raise_error"]["employee_not_found"]["detail"]}


def test_delete_new_user():
    response = TestApiServer.delete(TestApiRootPath + f'/user/{TestData["user"]["id"]}',
                                 headers=TestData["valid_admin_header"])
    print_response(response)

    assert response.status_code == 200
    assert response.json() == {"message": APP_CONFIG["message"]["user_deleted_successfully"]}


def test_read_deleted_new_user():
    response = TestApiServer.get(TestApiRootPath + f'/user/{TestData["user"]["id"]}',
                                 headers=TestData["valid_admin_header"])
    print_response(response)

    assert response.status_code == APP_CONFIG["raise_error"]["user_not_found"]["status_code"]
    assert response.json() == {"detail": APP_CONFIG["raise_error"]["user_not_found"]["detail"]}


def test_read_me_by_deleted_new_user():
    response = TestApiServer.get(TestApiRootPath + "/me",
                                 headers=TestData["user_header"])
    print_response(response)

    assert response.status_code == APP_CONFIG["raise_error"]["incorrect_user_name_or_password"]["status_code"]
    assert response.json() == {"detail": APP_CONFIG["raise_error"]["incorrect_user_name_or_password"]["detail"]}