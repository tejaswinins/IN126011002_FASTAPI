from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FastAPI working"}
from fastapi import FastAPI

app = FastAPI()

# Product list
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": False},

    # Q1 — Added products
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]


# Q1 — Get all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# Q2 — Filter products by category
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    result = [p for p in products if p["category"] == category_name]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }


# Q3 — Show only in-stock products
@app.get("/products/instock")
def get_instock_products():

    instock = [p for p in products if p["in_stock"]]

    return {
        "in_stock_products": instock,
        "count": len(instock)
    }


# Q4 — Store summary
@app.get("/store/summary")
def store_summary():

    in_stock = len([p for p in products if p["in_stock"]])
    out_of_stock = len(products) - in_stock
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "categories": categories
    }


# Q5 — Search products by name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }


#  Bonus — Cheapest and most expensive product
@app.get("/products/deals")
def get_deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

#Assignment2

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# Sample Products (from Day 1)

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

feedback = []
orders = []

# Q1 - Filter Products with Query Parameters

@app.get("/products/filter")
def filter_products(
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        category: Optional[str] = None):

    filtered = products

    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]

    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]

    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]

    return {"products": filtered, "count": len(filtered)}

# Q2 - Get Only Price of Product

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}

# Q3 - Customer Feedback (POST + Pydantic)

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data)

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

# Q4 - Product Summary Dashboard

@app.get("/products/summary")
def product_summary():

    total_products = len(products)
    in_stock = len([p for p in products if p["in_stock"]])
    out_stock = total_products - in_stock

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock,
        "out_of_stock_count": out_stock,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

# Q5 - Bulk Order (POST + Validation + Logic)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]


@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": total
    }

# ⭐ BONUS - Order Tracking

class SimpleOrder(BaseModel):
    product_id: int
    quantity: int


@app.post("/orders")
def place_order(order: SimpleOrder):

    new_order = {
        "order_id": len(orders) + 1,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(new_order)

    return new_order


@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}
    
#Assignment3
# Product Model
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


# GET all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# POST - Add Product
@app.post("/products", status_code=201)
def add_product(product: Product):

    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    new_product = {
        "id": len(products) + 1,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }


# DELETE Product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            products.remove(p)

            return {
                "message": f"Product '{p['name']}' deleted"
            }

    raise HTTPException(status_code=404, detail="Product not found")


# Q5 - Products Audit
@app.get("/products/audit")
def product_audit():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    out_stock_products = [p for p in products if not p["in_stock"]]

    in_stock_count = len(in_stock_products)

    out_of_stock_names = [p["name"] for p in out_stock_products]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


# BONUS - Category Discount
@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    updated = []

    for p in products:

        if p["category"].lower() == category.lower():

            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price

            updated.append({
                "name": p["name"],
                "new_price": new_price
            })

    if not updated:
        return {"message": "No products found in this category"}

    return {
        "updated_products": updated,
        "count": len(updated)
    }


# PUT - Update Product
@app.put("/products/{product_id}")
def update_product(product_id: int, price: int = None, in_stock: bool = None):

    for p in products:
        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {
                "message": "Product updated",
                "product": p
            }

    raise HTTPException(status_code=404, detail="Product not found")
# GET product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            return p

    raise HTTPException(status_code=404, detail="Product not found")

#Task4
products = {
    1: {"name": "Wireless Mouse", "price": 499, "stock": 10},
    2: {"name": "Notebook", "price": 99, "stock": 50},
    3: {"name": "USB Hub", "price": 299, "stock": 0},
    4: {"name": "Pen Set", "price": 49, "stock": 20},
}

cart = {}
orders = []
order_id_counter = 1


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]

    if product["stock"] == 0:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    if product_id in cart:
        cart[product_id]["quantity"] += quantity
        message = "Cart updated"
    else:
        cart[product_id] = {
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "unit_price": product["price"],
        }
        message = "Added to cart"

    cart[product_id]["subtotal"] = cart[product_id]["quantity"] * cart[product_id]["unit_price"]

    return {
        "message": message,
        "cart_item": cart[product_id]
    }


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    items = list(cart.values())
    grand_total = sum(item["subtotal"] for item in items)

    return {
        "items": items,
        "item_count": len(items),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")

    removed = cart.pop(product_id)

    return {"message": f"{removed['product_name']} removed from cart"}


@app.post("/cart/checkout")
def checkout(customer_name: str, delivery_address: str):
    global order_id_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    orders_placed = []

    for item in cart.values():
        order = {
            "order_id": order_id_counter,
            "customer_name": customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": delivery_address
        }

        orders.append(order)
        orders_placed.append(order)
        order_id_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": orders_placed,
        "grand_total": sum(o["total_price"] for o in orders_placed)
    }


@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }