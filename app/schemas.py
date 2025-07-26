from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Ürün oluşturma veya güncelleme için kullanılan temel şema
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Ürünün adı.")
    description: Optional[str] = Field(None, max_length=1000, description="Ürünün açıklaması.")
    price: float = Field(..., gt=0, description="Ürünün birim fiyatı (sıfırdan büyük olmalı).")
    sku: str = Field(..., min_length=3, max_length=100, description="Ürünün stok kodu (SKU), benzersiz olmalı.")
    category: Optional[str] = Field(None, max_length=100, description="Ürünün kategorisi.")

# Ürün oluşturmak için kullanılan şema
class ProductCreate(ProductBase):
    stock_quantity: int = Field(0, ge=0, description="Ürünün başlangıç stok miktarı (sıfır veya pozitif).")

# API yanıtlarında kullanılacak ürün şeması (tüm alanları içerir)
class Product(ProductBase):
    id: int = Field(..., description="Ürünün benzersiz ID'si.")
    stock_quantity: int = Field(..., ge=0, description="Ürünün mevcut stok miktarı (sıfır veya pozitif).")
    created_at: datetime = Field(..., description="Ürünün oluşturulma zamanı.")
    updated_at: Optional[datetime] = Field(None, description="Ürünün son güncellenme zamanı.")

# Stok güncellemek için kullanılacak şema
class ProductUpdateStock(BaseModel):
    quantity: int = Field(..., description="Stok miktarındaki değişiklik (pozitif veya negatif olabilir).")

# Ürün güncellemek için kullanılacak şema (kısmi güncellemeye izin verir)
class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = Field(None, min_length=3, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    stock_quantity: Optional[int] = Field(None, ge=0) # Stok miktarı da güncellenebilir