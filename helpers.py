from cs50 import SQL
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from flask import redirect, session
from functools import wraps
import re

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ccdata.db")

def getAllBanks():
    try:
        banks=db.execute("SELECT * FROM banks ORDER BY bank_name ASC")
        return (True, "Successfully retrieved banks", banks)
    except:
        return (False, "Error loading banks! Please try again later.", None)

def getUserInfo(id):
        try:
            rows=db.execute("SELECT user_id, username, first_name, last_name, email, bank, is_cc_admin FROM users WHERE user_id=?", id)
            if not rows:
                return (False, "User could not be found!", None)
            return (True, "Loaded user info successfully!", rows[0])
        except:
            return (False, "Could not load user info. Please try again later!", None)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def cc_admin_required(f):
    """
    Decorate routes to require cc_admin.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        if session.get("is_cc_admin") is False:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def is_valid_email_regex(email):
    """
    Checks if the email has a valid format using a regular expression.
    """
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def state_abbr():
    """
    Just returns a list of state abbreviations to pass into jinja templates
    """
    return [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "GU",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI",
    "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND",
    "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VI", "VA", "WA", "WV", "WI", "WY"
    ];

def format_date_time(timestamp):
    """
    takes in timestamp like: 2025-11-20 16:59:28
    """

    # The original datetime string (assumed to be UTC)
    dt_string_utc = timestamp

    # 1. Parse the string into a naive datetime object
    dt_object_naive = datetime.strptime(dt_string_utc, "%Y-%m-%d %H:%M:%S")

    # 2. Make the datetime object timezone-aware (localize it to UTC)
    dt_object_utc = dt_object_naive.replace(tzinfo=timezone.utc)

    # 3. Define the target time zone ('America/New_York' handles both EST and EDT)
    est_timezone = ZoneInfo('America/New_York')

    # 4. Convert the time to the target time zone
    dt_object_est = dt_object_utc.astimezone(est_timezone)

    utc_timestamp = dt_object_est

    months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    [date, time] = str(utc_timestamp).split(" ")
    d=date.split("-")
    year=d[0]
    month=months[int(d[1])-1]
    day=d[2]
    #format time
    t=time.split(":")
    hour=t[0]
    minute=t[1]
    std_time = military_to_standard((hour+minute)).split(":")
    return f"{month} {day}, {year}, {std_time[0]}:{std_time[1]}"

def military_to_standard(military_time_str):
    """
    Converts a military time string (e.g., "1430" or "0900") to standard time (e.g., "02:30 PM" or "09:00 AM").
    """
    # Parse the military time string into a datetime object
    # We use a dummy date because we only care about the time
    time_obj = datetime.strptime(military_time_str, "%H%M")

    # Format the datetime object into standard time
    standard_time_str = time_obj.strftime("%I:%M %p")
    if (standard_time_str[0] == "0"):
        standard_time_str=standard_time_str[1:]
    return standard_time_str

def doLogin(username, password):
    """
    Logs in user
    """
    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    if len(rows) != 1:
        return (False, "Invalid username and/or password!", None)
    # Ensure username exists and password is correct
    pw_check = check_password_hash(rows[0]["password"], password)
    if pw_check == False:
        return (False, "Invalid username and/or password!", None)

    return (True, "Successfully logged in user!", rows[0])
    # try:

    # except:
    #     return (False, "Could not perform log in at this time. Please try again later.", None)


def isValidBank(bank_id, banks):
    """function will return false if bank is not valid"""
    for bank in banks:
        if bank['bank_id'] == bank_id:
            return True
    return False

def isValidUsername(username):
    #check to see if username is already taken
    try:
        user_check = db.execute("SELECT username FROM users WHERE username=?;", username)
        if (len(user_check) != 0):
            return (False, "Username already taken please select another!")

        #check to see valid username format (no spaces)
        if " " in username:
            return (False, "Username must not contain spaces!")
        #otherwise, return True
        return (True, "Username is valid!")
    except:
        return (False, "Request could not be completed at this time, please try again later.")


def isValidPassword(password, confirm):
    # check if password matches confirm password
    if (password != confirm):
        return (False, "Passwords do not match!")

    # check if valid password format (no spaces)
    if " "  in password:
        return (False, "Password must not contain spaces!")

    # check if password length is at least 8!
    if len(password) < 8:
        return (False, "Password must be at least 8 characters!")

    return (True, "Password is valid.")

def doRegister(data):
    hash = generate_password_hash(data.get("password"))
    first_name =  data.get("first_name")
    last_name =  data.get("last_name")
    email = data.get("email")
    bank_id = int(data.get("bank_id"))
    username = data.get("username")
    try:
        db.execute("INSERT INTO users (username, password, first_name, last_name, email, join_date, is_admin, is_cc_admin, bank) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, FALSE, FALSE, ?)", username, hash, first_name, last_name, email, bank_id)
        # Remember which user has logged in
        rows = db.execute("SELECT user_id FROM users WHERE username=?", username)
        session['user_id'] = rows[0]['user_id']
        session['cart'] = {}
        session['is_cc_admin'] = False
        # Redirect user to home page
        return (True, "User created successfully!")
    except:
        return (False, "Could not register at this time. Please try again later.")

def updateUserInfo(data):
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        bank = int(data.get("bank_id"))
        form_dict = {'first_name': first_name, 'last_name': last_name, 'email': email, 'bank':bank}
        sql_set = ""
        values = []
        for key in form_dict:
            if form_dict[key] != "":
                if key == "bank":
                    sql_set += f' {key}=?'
                else:
                    sql_set += f' {key}=?,'
                values.append(form_dict[key])
        sql = "UPDATE users SET" + sql_set + " WHERE user_id=?"
        if len(values) == 0:
            return (False, "No data provided!", None)
        values.append(session["user_id"])
        try:
            db.execute(sql, *values)
            user_info=db.execute("SELECT username, first_name, last_name, email, bank, join_date FROM users WHERE user_id=?", session["user_id"])
            return [True, "Profile updated successfully!", user_info[0]]
        except:
            return [False, "Error! Could not complete request - try again later!", None]

def updatePassword(password):
    hash = generate_password_hash(password)
    try:
        db.execute("UPDATE users SET password=? WHERE user_id=?", hash, session["user_id"])
        return (True, "Password updated successfully!")
    except:
        return (False, "Password could not be changed at this time, try again later!")

def createNewOrder(data):
    try:
        user_id = session['user_id']
        note = data['note']
        items = data['items']
        first_name = data['first_name']
        last_name = data['last_name']
        address = data['address']
        city = data['city']
        state = data['state']
        zip = data['zip']
        rows=db.execute('SELECT bank FROM users WHERE user_id=?', user_id)
        if not rows:
            return (False, "Could not load banks!")
        bank_id=rows[0]['bank']
        #INSERT INTO ORDERS TABLE
        db.execute("INSERT INTO orders (user_id, order_date, order_status, bank_id, note, first_name, last_name, address, state, city, zip) VALUES (?, CURRENT_TIMESTAMP, 'received', ?, ?, ?, ?, ?, ?, ?, ?)", user_id, bank_id, note, first_name, last_name, address, state, city, zip)
        new_order = db.execute("SELECT last_insert_rowid() AS id")
        order_id = new_order[0]['id']
        #INSERT into order_items table
        for item in items:
            #insert each item
            db.execute("INSERT INTO order_items (quantity, order_id, product_id) VALUES (?, ?, ?)", item[1], order_id, item[0])
        session['cart'] = {}
        return (True, "Order created successfully!", order_id)
    except:
        return (False, "Error creating order", None)

def getReceiptData(order_id):
    try:
        rows = db.execute("SELECT order_id, user_id, order_date, order_status, orders.bank_id, banks.bank_name AS 'bank_name', note, first_name, last_name, orders.address, orders.state, orders.city, orders.zip FROM orders JOIN banks ON orders.bank_id=banks.bank_id WHERE order_id=?", order_id)
        if len(rows) == 0:
            return (False, "Could not load order data at this time. Please try again later.", None)
        order = rows[0]
        products = db.execute("SELECT order_item_id, quantity, order_id, order_items.product_id, products.product_name AS 'product_name', products.unit_price AS 'unit_price', products.bundle_qty AS 'bundle_qty' FROM order_items JOIN products on order_items.product_id=products.product_id WHERE order_id=?", order['order_id'])

        #ensure that user id in session matches the user id that placed the order
        if session['is_cc_admin'] == False and int(order['user_id']) != int(session['user_id']):
            return (False, "You do not have access to view this page!", None)

        #grab user data
        user_info = db.execute("SELECT user_id, username, first_name, last_name, email FROM users WHERE user_id=?", session["user_id"])
        if not user_info:
            return (False, "Could not load user information!", None)
        date_str=format_date_time(order['order_date'])

        #calculate item $ total
        total = 0;
        for i in products:
            total = total + (i['quantity'] * i['bundle_qty']) * i['unit_price']
        return (True, "Successfully retrieved order data", [user_info[0], date_str, products, total])
    except:
        return (False, "Could not load receipt at this time - please try again later!", None)

def getCartData():
    try:
        user_info=db.execute("SELECT username, first_name, last_name, email, join_date, banks.bank_name AS 'bank_name', banks.website AS 'website', banks.city AS 'city', banks.state AS 'state', banks.zip AS 'zip', banks.address AS 'address' FROM users LEFT JOIN banks ON bank=banks.bank_id WHERE user_id=?", session["user_id"])
        if not user_info:
            return (False, "Could not load user data. Please try again later!", None)
        products=db.execute("SELECT * FROM products")
        if not products:
            return (False, "Could not load products. Please try again later!", None)
        product_list = []
        states = state_abbr()
        total = 0
        # generate list for each product including the QTY in cart
        for k in session['cart'].keys():
            for p in products:
                if p['product_id'] == k:
                    p['qty'] = session['cart'][k]['qty']
                    product_list.append(p)
        for i in product_list:
            total = total + (i['qty'] * i['bundle_qty']) * i['unit_price']
        return (True, "Successfully loaded cart data", [user_info[0], product_list, total, states])
    except:
        return (False, "Could not load cart at this time, please try again later!", None)

def getProduct(product_id):
    try:
        rows=db.execute("SELECT * FROM products WHERE product_id=?", product_id)
        product_info=rows[0]
        return (True, "Successfully loaded product!", product_info)
    except:
        return (False, "Could not load product at this time - try again later!", None)

def getOrderCount(user_id=None):
    try:
        rows = []
        sql = "SELECT COUNT(order_id) AS 'count' FROM orders"
        if user_id:
            sql += " WHERE user_id=?"
            rows = db.execute(sql, user_id)
        else:
            rows = db.execute(sql)
        return (True, "Successfully loaded order count!", rows[0]['count'])
    except:
        return (False, "Could not load order count! Please try again later!", None)

def getOrderHistory(page, limit):
    try:
        endpage =  0
        orders = None
        bank = None
        offset = (int(page)-1) * limit

        orders=db.execute("SELECT o.order_id, o.order_date, o.order_status, o.note, o.first_name, o.last_name, o.address, o.state, o.city, o.zip, b.bank_name, SUM(p.bundle_qty * oi.quantity * p.unit_price) AS order_total FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id JOIN banks b ON o.bank_id = b.bank_id WHERE o.user_id = ? GROUP BY o.order_id, o.order_date, o.order_status, o.note, o.first_name, o.last_name, o.address, o.state, o.city, o.zip, b.bank_name ORDER BY o.order_date DESC LIMIT ? OFFSET ?", session['user_id'], limit, offset)
        if len(orders) == 0:
            return (False, "No orders placed!", orders)
        bank = orders[0]['bank_name']
        idx = bank.find('(')
        if idx != -1:
            bank=bank[:idx-1]
        for order in orders:
            order['order_date'] = format_date_time(order['order_date'])
            return (True, "Successfully loaded card orders", [bank, orders, int(page)])
    except:
        return (False, "Could not load orders at this time. Please try again later!", None)

def getFilteredOrders(data, page, limit):
    try:
        #data is the request.args from /orders route
        status_query = data.get("status")
        bank_query = data.get("bank")
        user_query = data.get("user")
        id_query = data.get("order_id")
        tracking_query = data.get("tracking")
        statuses = ["received", "processing", "delayed", "shipped"]
        arg_count = 0;
        values = []
        page = data.get('page', '1',)

        offset = (int(page)-1) * limit
        sql = "SELECT tracking, o.order_id, o.order_date, o.order_status, o.note, o.first_name, o.last_name, o.address, o.state, o.city, o.zip, b.bank_name, SUM(p.bundle_qty * oi.quantity * p.unit_price) AS order_total, u.username AS username, tracking, shipped_date FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id JOIN banks b ON o.bank_id = b.bank_id LEFT JOIN users u ON o.user_id=u.user_id "

        if status_query or bank_query or user_query or id_query or tracking_query:
            sql += "WHERE "
        if bank_query:
            bank_search = f'%{bank_query}%'
            sql += f"b.bank_name LIKE ? "
            values.append(bank_search)
            arg_count += 1;
        if user_query:
            if arg_count > 0:
                sql += "AND "
            sql += f"username=? "
            values.append(user_query)
            arg_count +=1;
        if status_query in statuses:
            if arg_count > 0:
                sql += "AND "
            sql += f"o.order_status=? "
            values.append(status_query)
            arg_count += 1
        if id_query and id_query != "":
            if arg_count > 0:
                sql += "AND "
            sql += f"o.order_id=? "
            values.append(id_query)
            arg_count += 1
        if tracking_query:
            if arg_count > 0:
                sql += "AND "
            sql += f"tracking=? "
            values.append(tracking_query)
            arg_count += 1

        sql += "GROUP BY o.order_id, o.order_date, o.order_status, o.note, o.first_name, o.last_name, o.address, o.state, o.city, o.zip, b.bank_name ORDER BY o.order_date DESC LIMIT ? OFFSET ?"
        values.append(limit)
        values.append(offset)
        orders=db.execute(sql, *values)
        for order in orders:
            order['order_date'] = format_date_time(order['order_date'])
        return (True, "Orders loaded successfully!", orders)
    except:
        return (False, "Could not load orders! Please try again later!", None)

def getOrderById(id):
    try:
        rows = db.execute("SELECT order_id, users.user_id, users.username AS 'username', users.first_name AS 'ordered_by_first', users.last_name AS 'ordered_by_last', tracking, order_date, shipped_date, admin_note, order_status, orders.bank_id, banks.bank_name AS 'bank_name', note, orders.first_name AS 'recipient_first', orders.last_name AS 'recipient_last', orders.address, orders.state, orders.city, orders.zip FROM orders JOIN banks ON orders.bank_id=banks.bank_id JOIN users ON users.user_id=orders.user_id WHERE order_id=?", id)
        if len(rows) == 0:
            return (False, f"Order #CC{id} not found!", None)
        return (True, "Loaded card order successfully!", rows[0])
    except:
        return (False, "Failed to load card order - Please try again later!", None)

def editOrder(id, data, statuses):
    try:
        order_status = data.get('order_status')
        shipped_date = data.get('shipped_date')
        tracking = data.get('tracking')
        admin_note = data.get('admin_note')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        address = data.get('address')
        city = data.get('city')
        state = data.get('state')
        zip = data.get('zip')

        #Validation
        # If order status is not in statuses:
        if order_status not in statuses:
            flash(f"Update denied - order status of {order_status} is not valid.")
            return (False, f"/orders/edit/{id}", None)
        # If order is set from "shipped" or another status, delete any tracking number and shipped date.
        if order_status != "shipped":
            tracking = "NULL"
            shipped_date = "NULL"
        # build SQL string
        form_data = [('order_status', order_status), ('shipped_date', shipped_date), ('tracking', tracking), ('admin_note', admin_note), ('first_name', first_name), ('last_name', last_name), ('address', address), ('city', city), ('state', state), ('zip', zip)]
        values = []
        sql = "UPDATE orders SET"
        for f in form_data:
            if f[1] != "":
                sql += f" {f[0]}=?,"
                values.append(f[1])
        sql = sql[:-1]
        values.append(id)
        sql += " WHERE order_id=?"
        db.execute(sql, *values)
        return (True, "Order updated successfully", None)
    except:
        return (False, "Could not update order at this time. Please try again later.")

def getUsersCount():
    try:
        rows = db.execute("SELECT COUNT(*) AS 'count' FROM users WHERE user_id != ?", session["user_id"])
        return (True, "Loaded card orders successfully!", rows[0]["count"])
    except:
        return (False, "Could not load users count. Please try again later.", None)

def getUsers(data, page, limit):
    try:
        sql = "SELECT user_id, username, first_name, last_name, email, join_date, is_cc_admin, banks.bank_name FROM users JOIN banks ON users.bank=banks.bank_id"
        values = []
        username = data.get("username")
        user_id = data.get("user_id")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        join_date = data.get("join_date")
        bank_name = data.get("bank_name")
        if username or user_id or first_name or last_name or email or join_date or bank_name:
            sql += " WHERE"
        data_dict = {"username" : username, "user_id": user_id, "first_name": first_name, "last_name": last_name, "email": email, "join_date": join_date, "bank_name": bank_name}
        for k, v in data_dict.items():
            if v:
                if len(values) > 2:
                    sql += " AND"
                vQuery = f"%{v}%"
                values.append(vQuery)
                sql+= f" {k} LIKE ?"
        sql+=  " ORDER BY username ASC LIMIT ? OFFSET ?"
        offset = (int(page)-1) * limit
        #query the database for all users:
        users = db.execute(sql, *values, limit, offset)
        return (True, "Load users successfully!", users)
    except:
        return (False, "Could not load users! Please try again later.", None)

def getBanksCount():
    try:
        rows = db.execute("SELECT COUNT(*) AS 'count' FROM banks")
        return (True, "Loaded bank count successfully!", rows[0]["count"])
    except:
        return (False, "Could not bank count. Please try again later.", None)

def getBanks(data, page, limit):
    try:
        sql = "SELECT * FROM banks"
        values = []
        bank_name = data.get("bank_name")
        if bank_name:
            bank_query = f"%{bank_name}%"
            sql+= " WHERE bank_name LIKE ?"
            values.append(bank_query)
        sql += " ORDER BY bank_name ASC LIMIT ? OFFSET ?"
        offset = (int(page)-1) * limit
        banks = db.execute(sql, *values, limit, offset)
        return (True, "Loaded banks successfully!", banks)
    except:
        return (False, "Failed to load banks - please try again later!", None)

def getBankById(id):
    try:
        rows = db.execute("SELECT * FROM banks WHERE bank_id=?", id)
        if len(rows) == 0:
            return (False, f"Bank not found!", None)
        return (True, "Loaded card order successfully!", rows[0])
    except:
        return (False, "Failed to load bank - Please try again later!", None)

def editBank(id, data):
    try:
        bank_name = data.get("bank_name")
        website = data.get("website")
        city = data.get("city")
        state = data.get("state")
        zip = data.get("zip")
        address = data.get("address")
        # is valid state?
        states_arr = state_abbr()
        if state not in states_arr:
            return (False, "State is not valid!", None)
        # build SQL string
        form_data = [('bank_name', bank_name), ('website', website), ('city', city), ('state', state), ('zip', zip), ('address', address), ('address', address)]
        values = []
        sql = "UPDATE banks SET"
        for f in form_data:
            if f[1] != "":
                sql += f" {f[0]}=?,"
                values.append(f[1])
        sql = sql[:-1]
        values.append(id)
        sql += " WHERE bank_id=?"
        db.execute(sql, *values)
        return (True, "Bank updated successfully", None)
    except:
        return (False, "Could not update bank. Please try again later.", None)

def deleteBank(id):
    try:
        db.execute("DELETE FROM banks WHERE bank_id=?", id)
        return (True, "Bank deleted successfully!", None)
    except:
        return (False, "Bank deletion not successful. Please try again later.", None)

def createBank(data):
    try:
        values = []
        sql="INSERT INTO banks (bank_name, website, address, city, state, zip) VALUES (?, ?, ?, ?, ?, ?)"
        isValidData = True
        for d in data:
            if data[d] == "":
                isValidData = False
                break
            values.append(data[d])
        if not isValidData:
            return (False, "Please fill out the form completely", None)
        newBank = db.execute(sql, *values)
        #check to see if sql added the bank:
        name = db.execute("SELECT bank_id FROM banks WHERE bank_name=?", data['bank_name'])
        if len(name) != 1:
            return (False, "Could not load bank. Please try again later.", None)
        return (True, "Bank created successfully!", data['bank_name'])
    except:
        return (False, "Could not create bank. Please try again later.", None)

def adminUpdateUser(data, id):
    if data.get('username') == "ccadmin":
        return (False, "You cannot edit this user!", None)
    try:
        values = []
        sql = "UPDATE users SET"
        sqlvalues = ""
        for d in data:
            if data[d] != "":
                if sqlvalues != "":
                    sqlvalues += ","
                if d == 'is_cc_admin':
                    print(data[d])
                    sqlvalues += f" {d}=?"
                    values.append(0)
                else:
                    sqlvalues += f" {d}=?"
                    values.append(data[d])
        if len(values) == 0:
            return (False, "No data provided to edit!", None)
        values.append(id)
        sql += sqlvalues + " WHERE user_id=?"
        #be sure that the logged in user is an admin!
        if session.get("is_cc_admin") == False or session.get("is_cc_admin") == None:
            return (False, "You do not have the permission to perform this action!", None)
        db.execute(sql, *values)
        return (True, "User updated successfully!", None)
    except:
        return (False, "Could not update user at this time. Please try again later!", None)

def adminChangePassword(data, id):
    try:
        # get user info
        userhash = db.execute("SELECT password FROM users WHERE user_id=?", id)
        if len(userhash) == 0:
            return (False, "Failed to load user, please try again later.", None)
        # data will have password and confirm - make sure these match!
        password = data.get("password")
        confirm = data.get("confirm")
        if password != confirm:
            return (False, "Passwords do not match! Please try again.", None)
        if session.get("is_cc_admin") is False:
            return (False, "You do not have the permissions to perform this action.", None)
        # hash the password
        hash = generate_password_hash(password)
        db.execute("UPDATE users SET password=? WHERE user_id=?", hash, id)
        return (True, "Successfully updated user password!", None)
    except:
        return (False, "Could not change password at this time. Please try again later.", None)

def adminCreateUser(data):
    try:
        if session['is_cc_admin'] == False or session['is_cc_admin'] == None:
            return (False, "You do not have permissions to perform this action!", None)
        # data will have password and confirm - make sure these match!
        password = data.get("password")
        confirm = data.get("confirm")
        if password != confirm:
            return (False, "Passwords do not match! Please try again.", None)
        if not is_valid_email_regex(data.get("email")):
            return (False, "Email address is not valid.", None)
        user_check = isValidUsername(data.get("username"))
        if user_check[0] == False:
            return (False, "Username is already taken! Please select another.", None)
        del data['confirm']
        data['password'] = generate_password_hash(password)
        sql = "INSERT INTO users (username, password, first_name, last_name, email, bank, is_cc_admin, join_date) VALUES ("
        sqlvalues = ""
        values = []
        data['bank'] = int(data['bank'])
        data['is_cc_admin'] = bool(data['is_cc_admin'])
        for d in data:
            if data[d] == "":
                break
            if len(values) > 0:
                sqlvalues += ", "
            sqlvalues += "?"
            values.append(data[d])
        if len(values) != 7:
            return (False, "Please fill out the form completely!", None)
        sql += sqlvalues + ", CURRENT_TIMESTAMP)"
        db.execute(sql, *values)
        return (True, "User created successfully!", data.get("username"))
    except:
        return (True, "User could not be created at this time. Please try again later", None)

def deleteUser(id):
    user = db.execute("SELECT username FROM users WHERE user_id=?", id)
    if len(user) < 1:
        return (False, "User not found!", None)
    if user[0]['username'] == "ccadmin":
        return (False, "You cannot delete this user!", None)
    try:
        if session['is_cc_admin'] == False or session['is_cc_admin'] == None:
            return (False, "You do not have permissions to perform this action!", None)
        db.execute("DELETE FROM users WHERE user_id=?", id)
        return (True, "User deleted successfully!", None)
    except:
        return (False, "Could not delete user at this time. Please try again later.", None)


















