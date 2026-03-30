from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "pizza_secret_key"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

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
    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        customer_name = request.form["customer_name"]
        pizza_size = request.form["pizza_size"]
        pizza_type = request.form["pizza_type"]
        quantity = request.form["quantity"]
        address = request.form["address"]

        return f"""
        <h1>Order Submitted!</h1>
        <p>Thank you, {customer_name}.</p>
        <p>Your {pizza_size} {pizza_type} pizza order has been placed.</p>
        <p>Quantity: {quantity}</p>
        <p>Delivery Address: {address}</p>
        """

    return render_template("order.html")

@app.route("/orders")
def orders():
    return render_template("orders.html")

if __name__ == "__main__":
    app.run(debug=True)
