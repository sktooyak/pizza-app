# Import Flask tools needed for page rendering, forms, redirects, and session cart storage
from flask import Flask, render_template, request, redirect, url_for, session 
import sqlite3

# Create Flask application
app = Flask(__name__)
app.secret_key = "pizza_secret_key"

# -------------------------
# Database Setup
# -------------------------
# Create required tables if they do not already exist
def init_db():
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        price REAL NOT NULL,
        image TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        pizza_type TEXT NOT NULL,
        pizza_size TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        address TEXT NOT NULL,
        payment_method TEXT NOT NULL
    )
    """)
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN order_type TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


# -------------------------
# Seed Sample Data
# -------------------------
# Seed initial menu data if the table is empty
def seed_data():
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Cheese Pizza", "Fresh mozzarella and tomato sauce", "Pizza", 10.99, "cheese.jpg"))

        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Pepperoni Pizza", "Classic pepperoni and mozzarella cheese", "Pizza", 12.99, "pepperoni.jpg"))

        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Veggie Pizza", "Loaded with fresh vegetables", "Pizza", 11.99, "veggie.jpg"))
        
         # Sides
        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Wings", "Crispy buffalo wings", "Sides", 6.99, "wings.jpg"))

        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Breadsticks", "Warm breadsticks with dipping sauce", "Sides", 5.49, "breadsticks.jpg"))

        # Drinks
        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Pepsi", "20 oz cold Pepsi", "Drinks", 2.49, "pepsi.jpg"))

        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Lemonade", "Fresh lemonade", "Drinks", 2.99, "lemonade.jpg"))

        # Desserts
        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Brownie", "Warm chocolate brownie", "Dessert", 3.99, "brownie.jpg"))

        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price, image)
        VALUES (?, ?, ?, ?, ?)
        """, ("Cinnamon Sticks", "Sweet cinnamon sticks with icing", "Dessert", 4.49, "cinnamon-sticks.jpg"))

    conn.commit()
    conn.close()


# -------------------------
# Database Connection
# -------------------------
# Create and return a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect("pizzeria.db")
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
# Helper Functions
# -------------------------
# Returns the number of items currently in the shopping cart
def get_cart_count():
    cart = session.get("cart", [])
    return len(cart)

# -------------------------
# Routes
# -------------------------

# Home page route
# Displays the main landing page and shows cart count in navigation
@app.route("/")
def home():
    return render_template("home.html", cart_count=get_cart_count())

# Menu page route
# Displays the pizza menu page
@app.route("/menu")
def menu():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM menu_items").fetchall()
    conn.close()

    return render_template(
        "menu.html",
        items=items,
        cart_count=get_cart_count()
    )

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    # Get pizza name and price from submitted form
    pizza_name = request.form["pizza_name"]
    price = float(request.form["price"])

    # Create dictionary object for cart item
    item = {
        "pizza_name": pizza_name,
        "price": price
    }

    # Create cart session if it does not already exist
    if "cart" not in session:
        session["cart"] = []

    # Add item to shopping cart
    cart = session["cart"]
    cart.append(item)
    session["cart"] = cart

    # Redirect user to cart page after adding item
    return redirect(url_for("cart"))

# Cart page route
# Displays all items currently in cart and calculates total price
@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])

    # Calculate total cart price
    total = sum(item["price"] for item in cart_items)
    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cart_count=get_cart_count()
    )

# Remove from Cart route
# Removes selected pizza from cart using its index
@app.route("/remove_from_cart/<int:item_index>", methods=["POST"])
def remove_from_cart(item_index):
    cart = session.get("cart", [])

    # Check that selected index exists before removing item
    if 0 <= item_index < len(cart):
        cart.pop(item_index)
        session["cart"] = cart

    return redirect(url_for("cart"))

# Order page route
# Displays checkout page and handles order submission
@app.route("/order", methods=["GET", "POST"])
def order():
    cart_items = session.get("cart", [])
    total = sum(item["price"] for item in cart_items)

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        address = request.form.get("address", "")
        payment_method = request.form["payment_method"]
        order_type = request.form["order_type"]

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO orders (
                customer_name, phone, pizza_type, pizza_size, quantity, address, payment_method, order_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_name,
                phone,
                "Cart Order",
                "N/A",
                len(cart_items),
                address,
                payment_method,
                order_type,
            ),
        )
        conn.commit()
        conn.close()

        session["cart"] = []

        return render_template(
            "checkout_success.html",
            customer_name=customer_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            order_type=order_type,
            total=total,
            cart_count=get_cart_count()
        )

    return render_template(
        "order.html",
        cart_items=cart_items,
        total=total,
        cart_count=get_cart_count()
    )

# Orders page route
# Displays previous orders page
@app.route("/orders")
def orders():
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return render_template("orders.html", orders=orders, cart_count=get_cart_count())

# Contact page route
# Displays contact information page
@app.route("/contact")
def contact():
    return render_template("contact.html", cart_count=get_cart_count())

# -------------------------
# Run Application
# -------------------------
# Starts Flask development server
if __name__ == "__main__":
    init_db()
    seed_data()
    app.run(debug=True)
