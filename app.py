# Import Flask tools needed for page rendering, forms, redirects, and session cart storage
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
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
        payment_method TEXT NOT NULL,
        delivery_type TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
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
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, ("admin", generate_password_hash("admin123"), "admin"))

    conn.commit()
    conn.close()
# Ensure database/tables exist when the app starts, including on Render
init_db()
seed_data()

# -------------------------
# Database Connection
# -------------------------
def get_db_connection():
    conn = sqlite3.connect("pizzeria.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        conn = get_db_connection()
        g.user = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        conn.close()

# -------------------------
# Helper Functions
# -------------------------
def get_cart_count():
    cart = session.get("cart", [])
    return len(cart)


# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    return render_template("home.html", cart_count=get_cart_count())
# -------------------------
# AUTH ROUTES (LOGIN)
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
        else:
            session.clear()
            session["user_id"] = user["user_id"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("customer_dashboard"))

    return render_template("login.html", error=error, cart_count=get_cart_count())
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        role = request.form["role"]

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif role not in ["customer", "admin"]:
            error = "Invalid role."

        if error is None:
            try:
                conn = sqlite3.connect("pizzeria.db")
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
                """, (username, generate_password_hash(password), role))
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Username already exists."

    return render_template("register.html", error=error, cart_count=get_cart_count())

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/customer")
def customer_dashboard():
    if g.user is None or g.user["role"] != "customer":
        return redirect(url_for("login"))

    return render_template(
        "customer_dashboard.html",
        user=g.user,
        cart_count=get_cart_count()
    )
@app.route("/admin")
def admin_dashboard():
    if g.user is None or g.user["role"] != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        user=g.user,
        orders=orders,
        cart_count=get_cart_count()
    )

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


@app.route("/order", methods=["GET", "POST"])
def order():
    cart_items = session.get("cart", [])
    total = sum(item["price"] for item in cart_items)

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        address = request.form["address"]
        payment_method = request.form["payment_method"]
        delivery_type = request.form["delivery_type"]
        

        conn = sqlite3.connect("pizzeria.db")
        cursor = conn.cursor()

        # Save one order record for each item in the cart
        for item in cart_items:
            cursor.execute("""
            INSERT INTO orders (
                customer_name,
                phone,
                pizza_type,
                pizza_size,
                quantity,
                address,
                payment_method,
                delivery_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer_name,
                phone,
                item["pizza_name"],
                "Standard",
                1,
                address,
                payment_method,
                delivery_type
            ))

        conn.commit()
        conn.close()

        # Clear cart after checkout
        session["cart"] = []

        return render_template(
            "checkout_success.html",
            customer_name=customer_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total=total,
            delivery_type=delivery_type,
            cart_count=get_cart_count()
        )

    return render_template(
        "order.html",
        cart_items=cart_items,
        total=total,
        cart_count=get_cart_count()
    )


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    pizza_name = request.form["pizza_name"]
    price = float(request.form["price"])

    item = {
        "pizza_name": pizza_name,
        "price": price
    }

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]
    cart.append(item)
    session["cart"] = cart

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total = sum(item["price"] for item in cart_items)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cart_count=get_cart_count()
    )


@app.route("/remove_from_cart/<int:item_index>", methods=["POST"])
def remove_from_cart(item_index):
    cart = session.get("cart", [])

    if 0 <= item_index < len(cart):
        cart.pop(item_index)
        session["cart"] = cart

    return redirect(url_for("cart"))


@app.route("/orders")
def orders():
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()

    return render_template(
        "orders.html",
        orders=orders,
        cart_count=get_cart_count()
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", cart_count=get_cart_count())


# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)