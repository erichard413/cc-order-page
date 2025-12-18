import os
from redis import Redis
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
import math
from helpers import login_required, getProducts, getFirstName, is_valid_email_regex, cc_admin_required, doLogin, isValidBank, isValidUsername, isValidPassword, doRegister, updateUserInfo, getUserInfo, updatePassword, createNewOrder, getReceiptData, getCartData, getProduct, getOrderCount, getOrderHistory, getFilteredOrders, getOrderById, editOrder, getUsersCount, getUsers, getBanks, getBanksCount, getBankById, editBank, deleteBank, getAllBanks, state_abbr, createBank, adminUpdateUser, adminChangePassword, adminCreateUser, deleteUser
from flask_sqlalchemy import SQLAlchemy
from database import db

# Configure application
app = Flask(__name__, static_folder='./static')
# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = Redis.from_url(os.environ["REDIS_URL"])
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///ccdata.db")

db.init_app(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    user = session.get('user_id')
    if (user):
        first_name = getFirstName(user)
        if first_name[0] == False:
            flash(first_name[1])
            return render_template("index.html")
        return render_template("index.html", name=first_name[2])
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    if "cart" not in session:
        session["cart"] = {}

    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!", 'error')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return render_template("login.html")

        user = doLogin(username, password)
        if user[0] == False:
            flash(user[1])
            return render_template("login.html")
        # Remember which user has logged in
        session["user_id"] = user[2]['user_id']
        # Is admin?
        session['is_cc_admin'] = user[2]["is_cc_admin"]
        # Redirect user to home page
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """function to log out a user"""
    # Forget any user_id
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """function to register a user"""
    #Forget any user_id
    session.clear()
    banks = getAllBanks()
    if banks[0] == False:
        flash(banks[1])
        return redirect("/")
    if request.method == "POST":
        #get data from form
        username = request.form.get("username")
        user_check = isValidUsername(username)
        if user_check[0] == False:
            flash(user_check[1])
            return render_template("register.html", banks=banks[2])

        bank_id = int(request.form.get("bank_id"))
        # is bank id in the list of banks?
        if not isValidBank(bank_id, banks[2]):
            flash("Invalid Bank!")
            return render_template("register.html", banks=banks[2])
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        password_check = isValidPassword(password, confirm)
        if password_check[0] == False:
            flash(password_check[1])
            return render_template("register.html", banks=banks[2])

        #is email valid?
        if not is_valid_email_regex(request.form.get('email')):
            flash("Email address is not valid email address!", 'error')
            return render_template("register.html", banks=banks[2])

        #if passed validation: do db insert here
        isRegistered = doRegister(request.form)
        if isRegistered[0] == False:
            flash(isRegistered[1])
        return redirect("/")

    return render_template("/register.html", banks=banks[2])

@app.route("/myinfo", methods=["GET", "POST"])
@login_required
def myinfo():
    banks = getAllBanks()
    if banks[0] == False:
        flash(banks[1])
        return redirect("/")
    if request.method == "POST":
        update = updateUserInfo(request.form)
        flash(update[1])
        return redirect("/myinfo")
    user_info = getUserInfo(session['user_id'])
    if user_info[0] == False:
        flash(user_info[1])
        return redirect("/")
    return render_template("/myinfo.html", banks=banks[2], user_info=user_info[2])

@app.route("/password", methods=["GET", "POST"])
@login_required
def mypassword():
    if request.method == "POST":
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        # check if password matches confirm password
        password_check = isValidPassword(password, confirm)
        if password_check[0] == False:
            flash(password_check[1])
            return redirect("/password")

        # do DB query
        update_pw = updatePassword(password)
        if update_pw[0] == False:
            flash(update_pw[1])
            return render_template("password.html")
        flash(update_pw[1])
        return redirect("/myinfo")
    return render_template("password.html")

@app.route("/order", methods=["GET", "POST"])
@login_required
def order():
    rows=getProducts()
    if rows[0] == False:
        flash(rows[1])
        return redirect("/")
    products = [dict(row) for row in rows[2]]
    if request.method == "POST":
        data = request.json
        if 'id' not in data or 'qty' not in data:
            flash("Invalid request!")
            return redirect("/order", products=products)
        id = int(data.get('id'))
        qty = int(data.get('qty'))
        if id in session['cart']:
            session['cart'][id]['qty'] = session['cart'][id]['qty'] + qty
        else:
            session['cart'][id] = {'id': id, 'qty': qty}
        found_product = [p for p in products if p.get('product_id') == id][0]
        flash(f"Added {qty} bundle{'s' if qty != 1 else ''} of {found_product['bundle_qty']} of {found_product['product_name']}s to cart!")
        return jsonify(success=True)
    return render_template("/order.html", products=products)

@app.route("/order/new", methods=["POST"])
@login_required
def do_order():
    data = request.json
    make_order = createNewOrder(data)
    if make_order[0] == False:
        flash("Card order could not be processed. Please try again later.")
        return jsonify({
            "success": False,
            "error": "Card order could not be processed. Please try again later.",
            "redirect_url": url_for("order")
        }), 500
    return jsonify({
        'success': True,
        'redirect_url': url_for("order_receipt", order_id=make_order[2])
    })

@app.route("/order/<int:order_id>/receipt")
@login_required
def order_receipt(order_id):
    receipt_data = getReceiptData(order_id)
    if receipt_data[0] == False:
        flash(receipt_data[1])
        return redirect("/")
    return render_template("/receipt.html", order=receipt_data[2][4], user_info=receipt_data[2][0], date=receipt_data[2][1], products=receipt_data[2][2], total=receipt_data[2][3], is_admin=session['is_cc_admin'])

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    data = getCartData()
    if data[0] == False:
        flash(data[1])
        return redirect("/")
    return render_template("/cart.html", cart=session['cart'], user_info=data[2][0], products=data[2][1], total=data[2][2], states=data[2][3])

@app.route("/cart/<int:product_id>", methods=["DELETE", "POST"])
@login_required
def deleteFromCart(product_id):
    """
    this route will remove items from CART
    """
    product = getProduct(product_id)
    if product[0] == False:
        flash(product[1])
        return redirect("/cart")

    if request.method == "DELETE":
        del session['cart'][product_id]
        flash(f"Removed {product[2]['product_name']}s from cart!")
        return redirect("/cart")

@app.route("/error", methods=["DELETE"])
def error(e):
    """
    Catch all page for errors
    """
    return render_template("error.html")

@app.route("/history")
@login_required
def history_page():
    limit = 30
    endpage = 0
    page = request.args.get('page', '1',)
    count = getOrderCount(session["user_id"])
    order_count = count[2]
    if order_count == 0:
        return render_template("history.html", bank=None, orders=None)
    if order_count > 0:
        page = request.args.get('page', '1',)
        endpage = math.ceil(int(order_count)/limit)
        if page.isdigit() == False:
            return redirect("/history?page=1")
        if int(page) > endpage:
            return redirect("/history?page=1")
    if count[0] == False:
        flash(count[1])
        return redirect("/")
    orders = getOrderHistory(page, limit)
    if orders[0] == False:
        flash(orders[1])
        return redirect("/")
    return render_template("history.html", bank=orders[2][0], orders=orders[2][1], page=int(page), endpage=endpage)

@app.route("/orders", methods=["GET"])
@cc_admin_required
def orders():
    limit = 30
    page = 0
    endpage =  0
    count_query = getOrderCount()
    if count_query[0] == False:
        flash(count_query[1])
        return redirect("/")

    if count_query[2] > 0:
        page = request.args.get('page', '1',)
        endpage = math.ceil(int(count_query[2])/limit)

        if page.isdigit() == False:
            return redirect("/orders?page=1")
        if int(page) > endpage:
            return redirect("/orders?page=1")
    orders_query = getFilteredOrders(request.args, page, limit)
    if orders_query[0]==False:
        flash(orders_query[1])
        return redirect("/")
    return render_template("orders.html", orders=orders_query[2], page=int(page), endpage=endpage)


@app.route("/orders/edit/<int:id>", methods=["GET", "POST"])
@cc_admin_required
def edit_orders(id):
    order_query = getOrderById(id)
    order = dict(order_query[2])
    formatted_date = str(order['shipped_date']).split(" ")[0]
    order['shipped_date'] = formatted_date
    if order_query[0] ==  False:
        flash(order_query[1])
        return redirect("/orders")
    statuses = ["received", "processing", "delayed", "shipped"]
    if request.method == "POST":
        response = editOrder(id, request.form, statuses)
        if response[0] == False:
            flash(response[1])
            return redirect(f'/orders/edit/{id}')
        flash("Order updated successfully!")
        return redirect(f'/orders/edit/{id}')
    return render_template("editorder.html", order=order, statuses=statuses)

@app.route("/users", methods=["GET"])
@cc_admin_required
def get_orders():
    limit = 30
    page = 0
    endpage =  0
    count_query = getUsersCount()
    if count_query[0] == False:
        flash(count_query[1])
        return redirect("/")
    if count_query[2] > 0:
        page = request.args.get('page', '1',)
        endpage = math.ceil(int(count_query[2])/limit)
        if page.isdigit() == False:
            return redirect("/users?page=1")
        if int(page) > endpage:
            return redirect("/users?page=1")
    users = getUsers(request.args, page, limit)
    if users[0] == False:
        flash(users[1])
        return redirect("/")
    return render_template("users.html", users=users[2], page=int(page), endpage=endpage)

@app.route("/banks", methods=["GET"])
@cc_admin_required
def get_banks():
    limit = 30
    page = 0
    endpage = 0
    count_query = getBanksCount()
    if count_query[0] == False:
        flash(count_query[1])
        return redirect("/")
    if count_query[2] > 0:
        page = request.args.get('page', '1',)
        endpage = math.ceil(int(count_query[2])/limit)
        if page.isdigit() == False:
            return redirect("/banks?page=1")
        if int(page) > endpage:
            return redirect("/banks?page=1")
    banks_query = getBanks(request.args, page, limit)
    if banks_query[0] ==  False:
        flash(banks_query[1])
        return redirect("/")
    return render_template("banks.html", banks=banks_query[2], page=int(page), endpage=endpage)

@app.route("/banks/edit/<int:id>", methods=["GET", "POST"])
@cc_admin_required
def edit_banks(id):
    states = state_abbr()
    bank_query = getBankById(id)
    if bank_query[0] ==  False:
        flash(bank_query[1])
        return redirect("/banks")
    bank = bank_query[2]
    if request.method == "POST":
        response = editBank(id, request.form)
        if response[0] == False:
            flash(response[1])
            return redirect(f'/banks/edit/{id}')
        flash(response[1])
        return redirect(f'/banks/edit/{id}')
    return render_template("editbank.html", bank=bank, states=states)

@app.route("/banks/delete/<int:id>", methods=["POST"])
@cc_admin_required
def delete_bank(id):
    if request.method == "POST":
        response = deleteBank(id)
        flash(response[1])
        return redirect("/banks")

@app.route("/banks/create", methods=["GET", "POST"])
@cc_admin_required
def create_bank():
    states = state_abbr()
    if request.method == "POST":
        response = createBank(request.form)
        if response[0] == False:
            flash(response[1])
            return redirect("/banks/create")
        flash(response[1])
        return redirect(f"/banks?bank_name={response[2]}")
    return render_template("newbank.html", states=states)

@app.route("/users/edit/<int:id>", methods=["GET", "POST"])
@cc_admin_required
def edit_user(id):
    if request.method=="POST":
        update = adminUpdateUser(request.form, id)
        if update[0] == False:
            flash(update[1])
            return redirect(f"/users/edit/{id}")
        flash(update[1])
        return redirect(f"/users/edit/{id}")
    user = getUserInfo(id)
    if user[0] == False:
        flash(user[1])
        return redirect("/users")
    banks = getAllBanks()
    if banks[0] == False:
        flash(banks[1])
        return redirect("/users")
    return render_template("edituser.html", user=user[2], banks=banks[2])

@app.route("/users/password/<int:id>", methods=["GET", "POST"])
@cc_admin_required
def change_password(id):
    if request.method=="POST":
        res = adminChangePassword(request.form, id)
        flash(res[1])
        return redirect(f"/users/edit/{id}")
    return render_template("changepw.html", id=id)

@app.route("/users/new", methods=["GET", "POST"])
@cc_admin_required
def create_user():
    banks = getAllBanks()
    if banks[0] == False:
        flash(banks[1])
        return redirect("/users")
    if request.method == "POST":
        res = adminCreateUser(request.form.to_dict())
        if res[0] == False:
            flash(res[1])
            return redirect("/users/new")
        flash(res[1])
        return redirect(f"/users?username={res[2]}")
    return render_template("createuser.html", banks=banks[2])

@app.route("/users/delete/<int:id>", methods=["POST"])
@cc_admin_required
def delete_user(id):
    res = deleteUser(id)
    flash(res[1])
    return redirect("/users")

# Run the app if this file is executed directly
if __name__ == "__main__":
    app.run()



