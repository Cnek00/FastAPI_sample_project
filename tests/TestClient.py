from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_product():
    response = client.post(
        "/products/",
        json={
            "name": "Test Ürün",
            "description": "Açıklama",
            "price": 100.0,
            "sku": "TESTSKU1",
            "category": "TestKategori",
            "stock_quantity": 10
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Ürün"
    assert data["sku"] == "TESTSKU1"
    assert data["stock_quantity"] == 10

def test_get_products():
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_product_by_id():
    # Önce bir ürün oluştur
    create_resp = client.post(
        "/products/",
        json={
            "name": "ID Test",
            "description": "Açıklama",
            "price": 50.0,
            "sku": "IDSKU",
            "category": "TestKategori",
            "stock_quantity": 5
        }
    )
    product_id = create_resp.json()["id"]
    # Şimdi ürünü getir
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id

def test_delete_product():
    # Önce bir ürün oluştur
    create_resp = client.post(
        "/products/",
        json={
            "name": "Silinecek",
            "description": "Açıklama",
            "price": 30.0,
            "sku": "DELETESKU",
            "category": "TestKategori",
            "stock_quantity": 3
        }
    )
    product_id = create_resp.json()["id"]
    # Şimdi ürünü sil
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204