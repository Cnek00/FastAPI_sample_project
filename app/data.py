# app/data.py

from typing import List, Dict, Any
from datetime import datetime
import uuid # Benzersiz ID'ler oluşturmak için

# Bellek içi ürün depolaması. Uygulama her yeniden başlatıldığında sıfırlanır.
# Başlangıçta boş bir liste olarak başlatıyoruz.
in_memory_products: List[Dict[str, Any]] = []

def generate_product_id() -> int:
    # Basit bir artan ID veya daha sağlam bir UUID kullanabiliriz.
    # Şimdilik basit bir sayıcı kullanalım.
    return len(in_memory_products) + 1

# UUID ile daha sağlam ID üretimi:
# def generate_product_uuid() -> str:
#     return str(uuid.uuid4())