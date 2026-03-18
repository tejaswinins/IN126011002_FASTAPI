from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

feedback = []
orders = []

@app.get("/")
def home():
    return {"message": "FastAPI working"}

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    result = [p for p in products if p["category"].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found"}
    return {"category": category_name, "products": result}

@app.get("/products/instock")
def get_instock_products():
    return {"products": [p for p in products if p["in_stock"]]}

@app.get("/products/search/{keyword}")
def search_old(keyword: str):
    result = [p for p in products if keyword.lower() in p["name"].lower()]
    if not result:
        return {"message": "No products matched"}
    return {"results": result}

@app.get("/products/filter")
def filter_products(min_price: int = 0, max_price: int = 10000):
    result = [p for p in products if min_price <= p["price"] <= max_price]
    return {"products": result}

@app.get("/products/summary")
def product_summary():
    total = len(products)
    total_value = sum(p["price"] for p in products)
    return {"total_products": total, "total_value": total_value}

@app.get("/products/audit")
def product_audit():
    return {
        "in_stock": len([p for p in products if p["in_stock"]]),
        "out_of_stock": len([p for p in products if not p["in_stock"]])
    }

@app.put("/products/discount")
def apply_discount(percent: int):
    for p in products:
        p["price"] = int(p["price"] * (1 - percent / 100))
    return {"message": f"{percent}% discount applied", "products": products}

#DAY 6

@app.get("/products/search")
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p["name"].lower()]
    if not result:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(result), "products": result}

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):

    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = True if order == "desc" else False

    sorted_products = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }



@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    total = len(products)
    return {
        "page": page,
        "total_pages": (total + limit - 1) // limit,
        "products": products[start:end]
    }

@app.get("/products/sort-by-category")
def sort_by_category():
    return {"products": sorted(products, key=lambda x: (x["category"], x["price"]))}

@app.get("/products/browse")
def browse_products(keyword: Optional[str] = None, sort_by: str = "price", order: str = "asc", page: int = 1, limit: int = 2):
    result = products.copy()

    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    end = start + limit

    return {
        "products": result[start:end],
        "total": len(result)
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

#FEEDBACK 

class Feedback(BaseModel):
    customer_name: str
    product_id: int
    rating: int
    comment: Optional[str] = None

@app.post("/feedback")
def submit_feedback(data: Feedback):
    feedback.append(data)
    return {"message": "Feedback submitted"}

# ORDERS 

class Order(BaseModel):
    product_id: int
    quantity: int

@app.post("/orders")
def place_order(order: Order):
    new_order = {
        "order_id": len(orders) + 1,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "customer_name": "Guest"
    }
    orders.append(new_order)
    return new_order

@app.get("/orders")
def get_orders():
    return {"orders": orders}

@app.get("/orders/search")
def search_orders(customer_name: str):
    result = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    return {"orders": result}


@app.get("/orders/search")
def search_orders(customer_name: str):
    result = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    return {"orders": result}

@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):

    total = len(orders)
    total_pages = (total + limit - 1) // limit

    if page > total_pages:
        return {"message": "Page exceeds total pages"}

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "orders": orders[start:end]
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for o in orders:
        if o["order_id"] == order_id:
            return o
    raise HTTPException(status_code=404, detail="Order not found")

#cart

cart_products = {
    1: {"name": "Wireless Mouse", "price": 499, "stock": 10},
    2: {"name": "Notebook", "price": 99, "stock": 50},
    3: {"name": "USB Hub", "price": 299, "stock": 0},
    4: {"name": "Pen Set", "price": 49, "stock": 20},
}

cart = {}

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    if product_id not in cart_products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = cart_products[product_id]

    if product["stock"] == 0:
        raise HTTPException(status_code=400, detail="Out of stock")

    if product_id in cart:
        cart[product_id]["quantity"] += quantity
    else:
        cart[product_id] = {
            "product_name": product["name"],
            "quantity": quantity,
            "price": product["price"]
        }

    return {"cart": cart}

@app.get("/cart")
def view_cart():
    return cart

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")
    cart.pop(product_id)
    return {"message": "Item removed"}

@app.post("/cart/checkout")
def checkout(customer_name: str):
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = {
        "customer": customer_name,
        "items": list(cart.values())
    }

    orders.append(order)
    cart.clear()

    return {"message": "Order placed", "order": order}