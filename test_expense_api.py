import pytest
from fastapi.testclient import TestClient
from expense_api import app, expenses_db, next_id

client = TestClient(app)

# перед каждым тестом БД очищается, счётчик ID сброс
@pytest.fixture(autouse=True)
def reset_db():
    expenses_db.clear()
    # сбросв next_id через модуль
    import expense_api
    expense_api.next_id = 1

def test_health_check(): # 1. проверка доступности API
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("[УСПЕХ] test_health_check")

def test_create_expense_should_succeed(): # 2. создание расхода
    response = client.post("/expenses", json={
        "amount": 1500.0,
        "category": "Продукты",
        "description": "Пятёрочка"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 1500.0
    assert data["category"] == "Продукты"
    assert data["id"] == 1
    print("[УСПЕХ] test_create_expense_should_succeed")

def test_get_expenses_should_return_list(): # 3. получение списка расходов
    # Сначала добавим два расхода
    client.post("/expenses", json={
        "amount": 500.0, "category": "Транспорт", "description": "Автобус"
    })
    client.post("/expenses", json={
        "amount": 2000.0, "category": "Продукты", "description": "Магнит"
    })

    response = client.get("/expenses")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["expenses"]) == 2
    print("[УСПЕХ] test_get_expenses_should_return_list")

def test_get_expense_by_id_should_return_expense(): # 4. получение расхода по ID
    client.post("/expenses", json={
        "amount": 750.0, "category": "Кафе", "description": "Обед"
    })

    response = client.get("/expenses/1")
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Обед"
    assert data["amount"] == 750.0
    print("[УСПЕХ] test_get_expense_by_id_should_return_expense")

def test_get_expense_by_id_should_return_404(): # 5. ошибка 404 при несуществующем ID
    response = client.get("/expenses/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Расход не найден"
    print("[УСПЕХ] test_get_expense_by_id_should_return_404")

def test_update_expense_should_succeed(): # 6. обновление расхода
    client.post("/expenses", json={
        "amount": 300.0, "category": "Транспорт", "description": "Метро"
    })

    response = client.put("/expenses/1", json={
        "amount": 350.0, "category": "Транспорт", "description": "Такси"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 350.0
    assert data["description"] == "Такси"
    print("[УСПЕХ] test_update_expense_should_succeed")

def test_update_expense_should_return_404(): # 7. ошибка 404 при обновлении несуществующего
    response = client.put("/expenses/999", json={
        "amount": 100.0, "category": "Другое", "description": "Тест"
    })
    assert response.status_code == 404
    print("[УСПЕХ] test_update_expense_should_return_404")

def test_delete_expense_should_remove(): # 8. удаление расхода
    client.post("/expenses", json={
        "amount": 100.0, "category": "Развлечения", "description": "Кино"
    })

    response = client.delete("/expenses/1")
    assert response.status_code == 200
    assert "удалён" in response.json()["message"]

    # проверка что расход действительно удалён
    get_resp = client.get("/expenses/1")
    assert get_resp.status_code == 404
    print("[УСПЕХ] test_delete_expense_should_remove")

def test_get_expenses_by_category(): # 9. фильтрация по категории
    client.post("/expenses", json={
        "amount": 500.0, "category": "Продукты", "description": "Хлеб"
    })
    client.post("/expenses", json={
        "amount": 300.0, "category": "Транспорт", "description": "Метро"
    })
    client.post("/expenses", json={
        "amount": 700.0, "category": "Продукты", "description": "Молоко"
    })

    response = client.get("/expenses/category/Продукты")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["category"] == "Продукты"
    print("[УСПЕХ] test_get_expenses_by_category")

def test_filter_category_empty(): # 10. фильтр по категории без результатов
    response = client.get("/expenses/category/Несуществующая")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["expenses"] == []
    print("[УСПЕХ] test_filter_category_empty")