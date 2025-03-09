import pytest
from httpx import AsyncClient
from main import app
from fastapi.testclient import TestClient
client = TestClient(app)

def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello world!'}


def test_register_user():
    """Тест регистрации нового пользователя"""
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser323",
        "password": "testpassword323"
    })
    assert response.status_code == 200
    assert "id" in response.json()


def test_register_duplicate_user():
    """Тест регистрации уже существующего пользователя"""
    client.post("/auth/register", json={
        "username": "duplicateuser",
        "password": "password123"
    })
    response = client.post("/auth/register", json={
        "username": "duplicateuser",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"

def test_login_success():
    """Тест успешного входа в систему"""
    client.post("/auth/register", json={
        "username": "loginuser",
        "password": "securepass"
    })
    response = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "securepass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    """Тест неудачного входа с неверными учетными данными"""
    response =client.post("/auth/login", json={
        "username": "unknownuser",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_get_student_not_found():
    """Тест получения несуществующего студента"""
    response = client.get("/students/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"

def test_create_student():
    """Тест создания студента"""
    response = client.post("/students", json={
        "first_name": "John",
        "last_name": "Doe",
        "faculty": "Engineering",
        "course": 3,
        "grade": 4.5
    })
    assert response.status_code == 200
    assert response.json()["first_name"] == "John"


def test_delete_student():
    """Тест удаления студента"""
    create_response = client.post("/students", json={
        "first_name": "Jane",
        "last_name": "Doe",
        "faculty": "Physics",
        "course": 2,
        "grade": 4.2
    })
    student_id = create_response.json()["id"]
    delete_response = client.delete(f"/students/{student_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Student was deleted."

def test_delete_nonexistent_student():
    """Тест удаления несуществующего студента"""
    response = client.delete("/students/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"
