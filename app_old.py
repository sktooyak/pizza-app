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
        price REAL NOT NULL
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
        INSERT INTO menu_items (name, description, category, price)
        VALUES (?, ?, ?, ?)
        """, ("Cheese Pizza", "Fresh mozzarella and tomato sauce", "Pizza", 10.99))

        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price)
        VALUES (?, ?, ?, ?)
        """, ("Pepperoni Pizza", "Classic pepperoni and mozzarella cheese", "Pizza", 12.99))

        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price)
        VALUES (?, ?, ?, ?)
        """, ("Veggie Pizza", "Loaded with fresh vegetables", "Pizza", 11.99))

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

# Add to Cart route
# Handles form submission when user clicks "Add to Cart"
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
# Displays order form and handles order submission
@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        # Get customer order details from form
        customer_name = request.form["customer_name"]
        pizza_size = request.form["pizza_size"]
        pizza_type = request.form["pizza_type"]
        quantity = request.form["quantity"]
        address = request.form["address"]

        # Display order confirmation page
        return f"""
        <h1>Order Submitted!</h1>
        <p>Thank you, {customer_name}.</p>
        <p>Your {pizza_size} {pizza_type} pizza order has been placed.</p>
        <p>Quantity: {quantity}</p>
        <p>Delivery Address: {address}</p>
        """

    # Load order form page
    return render_template("order.html", cart_count=get_cart_count())

# Orders page route
# Displays previous orders page
@app.route("/orders")
def orders():
    return render_template("orders.html", cart_count=get_cart_count())

# -------------------------
# Run Application
# -------------------------
# Starts Flask development server
if __name__ == "__main__":
    init_db()
    seed_data()
    app.run(debug=True)
