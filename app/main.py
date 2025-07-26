# app/main.py

from fastapi import FastAPI, HTTPException, status
from typing import List, Optional
from datetime import datetime
from . import schemas
from .data import in_memory_products, generate_product_id # Bellek içi depolamayı import ediyoruz

# FastAPI uygulamasını başlat
app = FastAPI(
    title="Envanter Yönetim Sistemi API (Bellek İçi Veri)",
    description="Şirketlerin ürün envanterini yönetmek için bir RESTful API. Veriler uygulama belleğinde tutulur ve her yeniden başlatmada sıfırlanır.",
    version="1.0.0",
)

# Temel bir "Merhaba Dünya" endpoint'i
@app.get("/")
def read_root():
    return {"message": "Envanter Yönetim Sistemi API'sine Hoş Geldiniz! (Bellek İçi Veri Modu)"}



# Yeni bir ürün oluştur
@app.post("/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate):
    # SKU'nun benzersizliğini kontrol et
    if any(p["sku"] == product.sku for p in in_memory_products):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu SKU'ya sahip bir ürün zaten mevcut.")

    db_product = product.dict()
    db_product["id"] = generate_product_id()
    db_product["created_at"] = datetime.now()
    db_product["updated_at"] = None # İlk oluşturulduğunda güncellenme tarihi yok

    in_memory_products.append(db_product)
    return db_product

# Tüm ürünleri listele
@app.get("/products/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    filtered = in_memory_products

    if name:
        filtered = [p for p in filtered if name.lower() in p["name"].lower()]
    if category:
        filtered = [p for p in filtered if p.get("category") and category.lower() in p["category"].lower()]
    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]
    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]

    return filtered[skip : skip + limit]

# Belirli bir ürünü ID'ye göre getir
@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int):
    for product in in_memory_products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün bulunamadı")

# Bir ürünü güncelle (PUT metodu ile tüm alanlar güncellenir)
@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate):
    for idx, existing_product in enumerate(in_memory_products):
        if existing_product["id"] == product_id:
            # SKU benzersizliğini kontrol et (güncellenen ürünün SKU'su dışındaki ürünler için)
            if any(p["sku"] == product.sku and p["id"] != product_id for p in in_memory_products):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu SKU'ya sahip başka bir ürün zaten mevcut.")

            updated_product = product.dict()
            updated_product["id"] = product_id # ID'yi koru
            updated_product["created_at"] = existing_product["created_at"] # Oluşturulma tarihini koru
            updated_product["updated_at"] = datetime.now()

            in_memory_products[idx] = updated_product
            return updated_product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün bulunamadı")

# Bir ürünü kısmen güncelle (PATCH metodu)
@app.patch("/products/{product_id}", response_model=schemas.Product)
def patch_product(product_id: int, product_update: schemas.ProductUpdate):
    for idx, existing_product in enumerate(in_memory_products):
        if existing_product["id"] == product_id:
            update_data = product_update.dict(exclude_unset=True) # Sadece gelen alanları al
            
            # Eğer SKU güncelleniyorsa, benzersizliğini kontrol et
            if "sku" in update_data and any(p["sku"] == update_data["sku"] and p["id"] != product_id for p in in_memory_products):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu SKU'ya sahip başka bir ürün zaten mevcut.")

            existing_product.update(update_data)
            existing_product["updated_at"] = datetime.now() # Güncellenme tarihini ayarla
            in_memory_products[idx] = existing_product # Listeyi güncelle
            return existing_product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün bulunamadı")


# Bir ürünün stok miktarını güncelle (PATCH'e özel bir durum)
@app.patch("/products/{product_id}/stock", response_model=schemas.Product)
def update_product_stock(product_id: int, stock_update: schemas.ProductUpdateStock):
    for idx, product in enumerate(in_memory_products):
        if product["id"] == product_id:
            new_quantity = product["stock_quantity"] + stock_update.quantity
            if new_quantity < 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stok miktarı negatif olamaz.")
            
            product["stock_quantity"] = new_quantity
            product["updated_at"] = datetime.now()
            in_memory_products[idx] = product
            return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün bulunamadı")


# Bir ürünü sil
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    global in_memory_products # Listeyi değiştireceğimiz için global anahtar kelimesi kullanıyoruz
    initial_len = len(in_memory_products)
    in_memory_products = [p for p in in_memory_products if p["id"] != product_id]
    if len(in_memory_products) == initial_len:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün bulunamadı")
    # 204 No Content durum kodu döndürdüğümüzde yanıt gövdesi boş olmalıdır.
    return # FastAPI otomatik olarak 204 yanıtını döndürür