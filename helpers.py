from datetime import datetime, timezone
import sys
# if using older version of python, import backports.zoneinfo:
if sys.version_info.major <= 3 and sys.version_info.minor <= 8:
    from backports.zoneinfo import ZoneInfo
else:
    from zoneinfo import ZoneInfo
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, session
from functools import wraps
import re
from database import db
from sqlalchemy import text

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///ccdata.db")

def getAllBanks():
    try:
        result=db.session.execute(text("SELECT * FROM banks ORDER BY bank_name ASC"))
        banks = result.mappings().all()
        return (True, "Successfully retrieved banks", banks)
    except Exception as e:
        return (False, "Error loading banks! Please try again later.", None)

def getUserInfo(user_id):
    try:
        result = db.session.execute(
            text("""
                SELECT
                    user_id,
                    username,
                    first_name,
                    last_name,
                    email,
                    bank,
                    is_cc_admin
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )

        row = result.mappings().first()

        if not row:
            return (False, "User could not be found!", None)

        return (True, "Loaded user info successfully!", row)

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
    ]

def format_date_time(timestamp):
    """
    takes in timestamp like: 2025-11-20 16:59:28
    """
    # The original datetime string (assumed to be UTC)
    dt_string_utc = str(timestamp).split('.')[0]

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
    try:
        result = db.session.execute(
            text("""
                SELECT *
                FROM users
                WHERE username = :username
            """),
            {"username": username}
        )

        user = result.mappings().first()

        if not user:
            return (False, "Invalid username and/or password!", None)

        # Ensure password is correct
        if not check_password_hash(user["password"], password):
            return (False, "Invalid username and/or password!", None)

        return (True, "Successfully logged in user!", user)

    except:
        return (False, "Could not perform log in at this time. Please try again later.", None)


def isValidBank(bank_id, banks):
    """function will return false if bank is not valid"""
    for bank in banks:
        if bank['bank_id'] == bank_id:
            return True
    return False

def isValidUsername(username):
    # check to see if username is already taken
    try:
        result = db.session.execute(
            text("""
                SELECT 1
                FROM users
                WHERE username = :username
                LIMIT 1
            """),
            {"username": username}
        )

        exists = result.scalar()

        if exists:
            return (False, "Username already taken please select another!")

        # check to see valid username format (no spaces)
        if " " in username:
            return (False, "Username must not contain spaces!")

        # otherwise, return True
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
    password_hash = generate_password_hash(data.get("password"))
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    bank_id = int(data.get("bank_id"))
    username = data.get("username")

    try:
        result = db.session.execute(
            text("""
                INSERT INTO users (
                    username,
                    password,
                    first_name,
                    last_name,
                    email,
                    join_date,
                    is_admin,
                    is_cc_admin,
                    bank
                )
                VALUES (
                    :username,
                    :password,
                    :first_name,
                    :last_name,
                    :email,
                    CURRENT_TIMESTAMP,
                    FALSE,
                    FALSE,
                    :bank_id
                )
                RETURNING user_id
            """),
            {
                "username": username,
                "password": password_hash,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "bank_id": bank_id
            }
        )

        user_id = result.scalar()
        db.session.commit()

        # Remember which user has logged in
        session["user_id"] = user_id
        session["cart"] = {}
        session["is_cc_admin"] = False

        return (True, "User created successfully!")

    except:
        db.session.rollback()
        return (False, "Could not register at this time. Please try again later.")

def updateUserInfo(data):
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    bank = data.get("bank_id")
    
    # Build dynamic fields to update
    form_dict = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "bank": int(bank) if bank else None
    }

    set_clauses = []
    params = {}

    for key, value in form_dict.items():
        if value not in ("", None):
            set_clauses.append(f"{key} = :{key}")
            params[key] = value

    if not set_clauses:
        return (False, "No data provided!", None)

    params["user_id"] = session["user_id"]

    sql = f"""
        UPDATE users
        SET {', '.join(set_clauses)}
        WHERE user_id = :user_id
    """

    try:
        db.session.execute(text(sql), params)
        db.session.commit()

        # Fetch updated user info
        result = db.session.execute(
            text("""
                SELECT username, first_name, last_name, email, bank, join_date
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": session["user_id"]}
        )
        user_info = result.mappings().first()

        return (True, "Profile updated successfully!", user_info)

    except:
        db.session.rollback()
        return (False, "Error! Could not complete request - try again later!", None)

def updatePassword(password):
    password_hash = generate_password_hash(password)
    try:
        db.session.execute(
            text("""
                UPDATE users
                SET password = :password
                WHERE user_id = :user_id
            """),
            {"password": password_hash, "user_id": session["user_id"]}
        )
        db.session.commit()
        return (True, "Password updated successfully!")
    except:
        db.session.rollback()
        return (False, "Password could not be changed at this time, try again later!")


def createNewOrder(data):
    try:
        user_id = session['user_id']
        note = data.get('note')
        items = data.get('items', [])
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        address = data.get('address')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip')

        # Get the user's bank_id
        result = db.session.execute(
            text("SELECT bank FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        row = result.mappings().first()
        if not row:
            return (False, "Could not load bank info!", None)

        bank_id = row['bank']

        # Insert into orders table and get order_id
        insert_order = db.session.execute(
            text("""
                INSERT INTO orders (
                    user_id, order_date, order_status, bank_id, note, 
                    first_name, last_name, address, state, city, zip
                )
                VALUES (
                    :user_id, CURRENT_TIMESTAMP, 'received', :bank_id, :note, 
                    :first_name, :last_name, :address, :state, :city, :zip
                )
                RETURNING order_id
            """),
            {
                "user_id": user_id,
                "bank_id": bank_id,
                "note": note,
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "state": state,
                "city": city,
                "zip": zip_code
            }
        )
        order_id = insert_order.scalar()

        # Insert into order_items table
        for item in items:
            product_id, quantity = item[0], item[1]
            db.session.execute(
                text("""
                    INSERT INTO order_items (quantity, order_id, product_id)
                    VALUES (:quantity, :order_id, :product_id)
                """),
                {
                    "quantity": quantity,
                    "order_id": order_id,
                    "product_id": product_id
                }
            )

        db.session.commit()
        session['cart'] = {}

        return (True, "Order created successfully!", order_id)

    except:
        db.session.rollback()
        return (False, "Error creating order", None)

def getReceiptData(order_id):
    try:
        # Fetch order info with bank name
        order_result = db.session.execute(
            text("""
                SELECT 
                    o.order_id,
                    o.user_id,
                    o.order_date,
                    o.order_status,
                    o.bank_id,
                    b.bank_name AS bank_name,
                    o.note,
                    o.first_name,
                    o.last_name,
                    o.address,
                    o.state,
                    o.city,
                    o.zip
                FROM orders o
                JOIN banks b ON o.bank_id = b.bank_id
                WHERE o.order_id = :order_id
            """),
            {"order_id": order_id}
        )

        order = order_result.mappings().first()
        if not order:
            return (False, "Could not load order data at this time. Please try again later.", None)

        # Fetch order items with product info
        products_result = db.session.execute(
            text("""
                SELECT 
                    oi.order_item_id,
                    oi.quantity,
                    oi.order_id,
                    oi.product_id,
                    p.product_name AS product_name,
                    p.unit_price AS unit_price,
                    p.bundle_qty AS bundle_qty
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = :order_id
            """),
            {"order_id": order["order_id"]}
        )
        products = products_result.mappings().all()

        # Ensure user has permission
        if not session.get("is_cc_admin", False) and int(order["user_id"]) != int(session.get("user_id", 0)):
            return (False, "You do not have access to view this page!", None)

        # Grab user info
        user_result = db.session.execute(
            text("""
                SELECT user_id, username, first_name, last_name, email
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": session.get("user_id")}
        )
        user_info = user_result.mappings().first()
        if not user_info:
            return (False, "Could not load user information!", None)

        # Format date string
        date_str = format_date_time(order["order_date"])

        # Calculate total
        total = sum((item["quantity"] * item["bundle_qty"]) * item["unit_price"] for item in products)

        return (True, "Successfully retrieved order data", [user_info, date_str, products, total, order])

    except:
        db.session.rollback()
        return (False, "Could not load receipt at this time - please try again later!", None)

def getCartData():
    try:
        # Fetch user info with bank details
        user_result = db.session.execute(
            text("""
                SELECT 
                    u.username, u.first_name, u.last_name, u.email, u.join_date,
                    b.bank_name AS bank_name, b.website AS website, b.city AS city, 
                    b.state AS state, b.zip AS zip, b.address AS address
                FROM users u
                LEFT JOIN banks b ON u.bank = b.bank_id
                WHERE u.user_id = :user_id
            """),
            {"user_id": session.get("user_id")}
        )
        user_info = user_result.mappings().first()
        if not user_info:
            return (False, "Could not load user data. Please try again later!", None)

        # Fetch all products
        products_result = db.session.execute(
            text("SELECT * FROM products")
        )
        products = products_result.mappings().all()
        if not products:
            return (False, "Could not load products. Please try again later!", None)

        # Prepare cart product list
        product_list = []
        states = state_abbr()
        total = 0

        # Match products in cart
        for product_id, cart_item in session.get('cart', {}).items():
            for p in products:
                if p['product_id'] == int(product_id):
                    p_copy = dict(p)
                    p_copy['qty'] = cart_item.get('qty', 0)
                    product_list.append(p_copy)

        # Calculate total
        total = sum((item['qty'] * item['bundle_qty']) * item['unit_price'] for item in product_list)

        return (True, "Successfully loaded cart data", [user_info, product_list, total, states])

    except:
        db.session.rollback()
        return (False, "Could not load cart at this time, please try again later!", None)

def getProducts():
    try:
        result = db.session.execute(
            text("SELECT * FROM products")
        )
        products = result.mappings().all()

        if not products:
            return (False, "Failed to load products! Please try again later.", None)

        return (True, "Load products successful", products)

    except:
        db.session.rollback()
        return (False, "Could not load products! Please try again later.", None)

def getProduct(product_id):
    try:
        result = db.session.execute(
            text("SELECT * FROM products WHERE product_id = :product_id"),
            {"product_id": product_id}
        )
        product_info = result.mappings().first()

        if not product_info:
            return (False, "Product not found!", None)

        return (True, "Successfully loaded product!", product_info)

    except:
        db.session.rollback()
        return (False, "Could not load product at this time - try again later!", None)

def getOrderCount(user_id=None):
    try:
        if user_id:
            result = db.session.execute(
                text("SELECT COUNT(order_id) AS count FROM orders WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
        else:
            result = db.session.execute(
                text("SELECT COUNT(order_id) AS count FROM orders")
            )

        count = result.scalar()  # Returns the first column of the first row

        return (True, "Successfully loaded order count!", count)

    except Exception as e:
        print(e)
        db.session.rollback()
        return (False, "Could not load order count! Please try again later!", None)

def getOrderHistory(page, limit):
    try:
        offset = (int(page) - 1) * limit

        result = db.session.execute(
            text("""
                SELECT 
                    o.order_id,
                    o.order_date,
                    o.order_status,
                    o.note,
                    o.first_name,
                    o.last_name,
                    o.address,
                    o.state,
                    o.city,
                    o.zip,
                    b.bank_name,
                    COALESCE(
                        SUM(p.bundle_qty * oi.quantity * p.unit_price), 0
                    ) AS order_total
                FROM orders o
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                LEFT JOIN products p ON oi.product_id = p.product_id
                JOIN banks b ON o.bank_id = b.bank_id
                WHERE o.user_id = :user_id
                GROUP BY 
                    o.order_id, o.order_date, o.order_status, o.note, 
                    o.first_name, o.last_name, o.address,
                    o.state, o.city, o.zip, b.bank_name
                ORDER BY o.order_date DESC
                LIMIT :limit OFFSET :offset
            """),
            {
                "user_id": session["user_id"],
                "limit": int(limit),
                "offset": offset,
            }
        )

        orders = [dict(row) for row in result.mappings().all()]

        if not orders:
            return (False, "No orders placed!", [])

        bank = orders[0]["bank_name"]
        if "(" in bank:
            bank = bank.split("(")[0].strip()

        for order in orders:
            order["order_date"] = format_date_time(order["order_date"])

        return (True, "Successfully loaded card orders", [bank, orders, int(page)])

    except Exception as e:
        print("Order history error:", e)
        db.session.rollback()
        return (False, "Could not load orders at this time.", None)

    except Exception as e:
        print(e)
        db.session.rollback()
        return (False, "Could not load orders at this time. Please try again later!", None)

def getFilteredOrders(data, page, limit):
    try:
        # Extract filter arguments
        status_query = data.get("status")
        bank_query = data.get("bank")
        user_query = data.get("user")
        id_query = data.get("order_id")
        tracking_query = data.get("tracking")
        statuses = ["received", "processing", "delayed", "shipped"]
        page = int(data.get('page', page))
        offset = max((page - 1) * limit, 0)

        # Base SQL
        sql = """
            SELECT 
                o.order_id,
                o.order_date,
                o.order_status,
                o.note,
                o.first_name,
                o.last_name,
                o.address,
                o.state,
                o.city,
                o.zip,
                b.bank_name,
                SUM(p.bundle_qty * oi.quantity * p.unit_price) AS order_total,
                u.username AS username,
                o.tracking,
                o.shipped_date
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN banks b ON o.bank_id = b.bank_id
            LEFT JOIN users u ON o.user_id = u.user_id
        """

        where_clauses = []
        params = {}

        if bank_query:
            where_clauses.append("b.bank_name ILIKE :bank_query")
            params["bank_query"] = f"%{bank_query}%"
        if user_query:
            where_clauses.append("u.username = :user_query")
            params["user_query"] = user_query
        if status_query in statuses:
            where_clauses.append("o.order_status = :status_query")
            params["status_query"] = status_query
        if id_query:
            where_clauses.append("o.order_id = :id_query")
            params["id_query"] = id_query
        if tracking_query:
            where_clauses.append("o.tracking = :tracking_query")
            params["tracking_query"] = tracking_query

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += """
            GROUP BY o.order_id, o.order_date, o.order_status, o.note, 
                     o.first_name, o.last_name, o.address, o.state, o.city, o.zip, 
                     b.bank_name, u.username, o.tracking, o.shipped_date
            ORDER BY o.order_date DESC
            LIMIT :limit OFFSET :offset
        """
        params["limit"] = limit
        params["offset"] = offset

        # Execute query
        result = db.session.execute(text(sql), params)
        orders = [dict(row) for row in result.mappings().all()]

        # Format order dates
        for order in orders:
            order['order_date'] = format_date_time(str(order['order_date']))

        return (True, "Orders loaded successfully!", orders)
    except:
        db.session.rollback()
        return (False, "Could not load orders! Please try again later!", None)
    
def getOrderById(order_id):
    try:
        result = db.session.execute(
            text("""
                SELECT 
                    o.order_id,
                    u.user_id,
                    u.username AS username,
                    u.first_name AS ordered_by_first,
                    u.last_name AS ordered_by_last,
                    o.tracking,
                    o.order_date,
                    o.shipped_date,
                    o.admin_note,
                    o.order_status,
                    o.bank_id,
                    b.bank_name AS bank_name,
                    o.note,
                    o.first_name AS recipient_first,
                    o.last_name AS recipient_last,
                    o.address,
                    o.state,
                    o.city,
                    o.zip
                FROM orders o
                JOIN banks b ON o.bank_id = b.bank_id
                JOIN users u ON u.user_id = o.user_id
                WHERE o.order_id = :order_id
            """),
            {"order_id": order_id}
        )

        order = result.mappings().first()

        if not order:
            return (False, f"Order #CC{order_id} not found!", None)

        return (True, "Loaded card order successfully!", order)
    except Exception as e:
        print(e)
        db.session.rollback()
        return (False, "Failed to load card order - Please try again later!", None)

def editOrder(order_id, data, statuses):
    try:
        # Extract fields
        order_status = data.get('order_status')
        shipped_date = data.get('shipped_date')
        tracking = data.get('tracking')
        admin_note = data.get('admin_note')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        address = data.get('address')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip')

        # Validation
        if order_status not in statuses:
            return (False, f"Update denied - order status of {order_status} is not valid.", None)

        # Reset tracking and shipped_date if not shipped
        if order_status != "shipped":
            tracking = None
            shipped_date = None

        # Build SET clause dynamically
        form_data = {
            'order_status': order_status,
            'shipped_date': shipped_date,
            'tracking': tracking,
            'admin_note': admin_note,
            'first_name': first_name,
            'last_name': last_name,
            'address': address,
            'city': city,
            'state': state,
            'zip': zip_code
        }

        set_clauses = []
        params = {}

        for key, value in form_data.items():
            if value not in ("", None):
                set_clauses.append(f"{key} = :{key}")
                params[key] = value

        if not set_clauses:
            return (False, "No data provided to update!", None)

        params['order_id'] = order_id
        sql = f"UPDATE orders SET {', '.join(set_clauses)} WHERE order_id = :order_id"

        # Execute query
        db.session.execute(text(sql), params)
        db.session.commit()

        return (True, "Order updated successfully", None)

    except:
        db.session.rollback()
        return (False, "Could not update order at this time. Please try again later.")

def getUsersCount():
    try:
        result = db.session.execute(
            text("SELECT COUNT(*) FROM users WHERE user_id != :current_user_id"),
            {"current_user_id": session.get("user_id")}
        )
        count = result.scalar() 
        return (True, "Loaded users count successfully!", count)

    except Exception as e:
        db.session.rollback()
        return (False, "Could not load users count. Please try again later.", None)

def getUsers(data, page, limit):
    try:
        base_sql = """
            SELECT 
                u.user_id,
                u.username,
                u.first_name,
                u.last_name,
                u.email,
                u.join_date,
                u.is_cc_admin,
                b.bank_name
            FROM users u
            JOIN banks b ON u.bank = b.bank_id
        """

        filters = []
        params = {}

        # Extract filters from data
        username = data.get("username")
        user_id = data.get("user_id")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        join_date = data.get("join_date")
        bank_name = data.get("bank_name")

        if username:
            filters.append("u.username ILIKE :username")
            params["username"] = f"%{username}%"
        if user_id:
            filters.append("u.user_id::text ILIKE :user_id")  # cast to text for pattern match
            params["user_id"] = f"%{user_id}%"
        if first_name:
            filters.append("u.first_name ILIKE :first_name")
            params["first_name"] = f"%{first_name}%"
        if last_name:
            filters.append("u.last_name ILIKE :last_name")
            params["last_name"] = f"%{last_name}%"
        if email:
            filters.append("u.email ILIKE :email")
            params["email"] = f"%{email}%"
        if join_date:
            filters.append("u.join_date::text ILIKE :join_date")
            params["join_date"] = f"%{join_date}%"
        if bank_name:
            filters.append("b.bank_name ILIKE :bank_name")
            params["bank_name"] = f"%{bank_name}%"

        if filters:
            base_sql += " WHERE " + " AND ".join(filters)

        # Pagination
        offset = max((int(page) - 1) * limit, 0)
        base_sql += " ORDER BY u.username ASC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        # Execute query
        result = db.session.execute(text(base_sql), params)
        users = result.mappings().all()

        return (True, "Load users successfully!", users)
    except:
        db.session.rollback()
        return (False, "Could not load users! Please try again later.", None)
    
def getFirstName(user_id):
    try:
        result = db.session.execute(
            text("SELECT first_name FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        first_name = result.scalar()

        if not first_name:
            return (False, "Could not find user!", None)

        return (True, "User loaded successfully!", first_name)

    except:
        db.session.rollback()
        return (False, "Could not load user data - please try again later!", None)
    

def getBanksCount():
    try:
        result = db.session.execute(
            text("SELECT COUNT(*) FROM banks")
        )
        count = result.scalar()

        return (True, "Loaded bank count successfully!", count)

    except:
        db.session.rollback()
        return (False, "Could not load bank count. Please try again later.", None)

def getBanks(data, page, limit):
    try:
        base_sql = "SELECT * FROM banks"
        params = {}

        bank_name = data.get("bank_name")
        if bank_name:
            base_sql += " WHERE bank_name ILIKE :bank_name"
            params["bank_name"] = f"%{bank_name}%"

        # Pagination
        offset = (int(page) - 1) * limit
        base_sql += " ORDER BY bank_name ASC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        # Execute query
        result = db.session.execute(text(base_sql), params)
        banks = result.mappings().all()

        return (True, "Loaded banks successfully!", banks)

    except:
        db.session.rollback()
        return (False, "Failed to load banks - please try again later!", None)

def getBankById(bank_id):
    try:
        result = db.session.execute(
            text("SELECT * FROM banks WHERE bank_id = :bank_id"),
            {"bank_id": bank_id}
        )
        bank = result.mappings().first()

        if not bank:
            return (False, "Bank not found!", None)

        return (True, "Loaded bank successfully!", bank)

    except:
        db.session.rollback()
        return (False, "Failed to load bank - Please try again later!", None)

def editBank(bank_id, data):
    try:
        # Extract fields
        bank_name = data.get("bank_name")
        website = data.get("website")
        city = data.get("city")
        state = data.get("state")
        zip_code = data.get("zip")
        address = data.get("address")

        # Validate state
        states_arr = state_abbr()
        if state not in states_arr:
            return (False, "State is not valid!", None)

        # Build dynamic SET clause
        form_data = {
            "bank_name": bank_name,
            "website": website,
            "city": city,
            "state": state,
            "zip": zip_code,
            "address": address
        }

        set_clauses = []
        params = {}

        for key, value in form_data.items():
            if value not in ("", None):
                set_clauses.append(f"{key} = :{key}")
                params[key] = value

        if not set_clauses:
            return (False, "No data provided to update!", None)

        params["bank_id"] = bank_id
        sql = f"UPDATE banks SET {', '.join(set_clauses)} WHERE bank_id = :bank_id"

        # Execute query
        db.session.execute(text(sql), params)
        db.session.commit()

        return (True, "Bank updated successfully", None)

    except:
        db.session.rollback()
        return (False, "Could not update bank. Please try again later.", None)

def deleteBank(bank_id):
    try:
        db.session.execute(
            text("DELETE FROM banks WHERE bank_id = :bank_id"),
            {"bank_id": bank_id}
        )
        db.session.commit()
        return (True, "Bank deleted successfully!", None)

    except:
        db.session.rollback()
        return (False, "Bank deletion not successful. Please try again later.", None)

def createBank(data):
    try:
        # Validate that all required fields are filled
        required_fields = ["bank_name", "website", "address", "city", "state", "zip"]
        for field in required_fields:
            if not data.get(field):
                return (False, "Please fill out the form completely", None)

        # Insert new bank
        sql = """
            INSERT INTO banks (bank_name, website, address, city, state, zip)
            VALUES (:bank_name, :website, :address, :city, :state, :zip)
        """
        db.session.execute(text(sql), {
            "bank_name": data["bank_name"],
            "website": data["website"],
            "address": data["address"],
            "city": data["city"],
            "state": data["state"],
            "zip": data["zip"]
        })
        db.session.commit()

        # Confirm bank was inserted
        result = db.session.execute(
            text("SELECT bank_id FROM banks WHERE bank_name = :bank_name"),
            {"bank_name": data["bank_name"]}
        )
        bank = result.mappings().first()
        if not bank:
            return (False, "Could not load bank. Please try again later.", None)

        return (True, "Bank created successfully!", data["bank_name"])
    except:
        db.session.rollback()
        return (False, "Could not create bank. Please try again later.", None)

def adminUpdateUser(data, user_id):
    # Protect the "ccadmin" user
    if data.get('username') == "ccadmin":
        return (False, "You cannot edit this user!", None)

    # Check that logged-in user is a CC admin
    if not session.get("is_cc_admin", False):
        return (False, "You do not have the permission to perform this action!", None)

    try:
        # Build dynamic SET clause
        set_clauses = []
        params = {}

        for key, value in data.items():
            if value not in ("", None):
                if key == 'is_cc_admin':
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = 0  # force non-admin
                else:
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value

        if not set_clauses:
            return (False, "No data provided to edit!", None)

        params['user_id'] = user_id
        sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE user_id = :user_id"

        # Execute query
        db.session.execute(text(sql), params)
        db.session.commit()

        return (True, "User updated successfully!", None)

    except:
        db.session.rollback()
        return (False, "Could not update user at this time. Please try again later!", None)

def adminChangePassword(data, user_id):
    try:
        # Ensure logged-in user is a CC admin
        if not session.get("is_cc_admin", False):
            return (False, "You do not have the permissions to perform this action.", None)

        # Verify user exists
        result = db.session.execute(
            text("SELECT password FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        user = result.mappings().first()
        if not user:
            return (False, "Failed to load user, please try again later.", None)

        # Check password and confirmation
        password = data.get("password")
        confirm = data.get("confirm")
        if password != confirm:
            return (False, "Passwords do not match! Please try again.", None)

        # Hash the password and update
        hashed_password = generate_password_hash(password)
        db.session.execute(
            text("UPDATE users SET password = :password WHERE user_id = :user_id"),
            {"password": hashed_password, "user_id": user_id}
        )
        db.session.commit()

        return (True, "Successfully updated user password!", None)

    except:
        db.session.rollback()
        return (False, "Could not change password at this time. Please try again later.", None)

def adminCreateUser(data):
    try:
        # Admin permission check
        if not session.get("is_cc_admin", False):
            return (False, "You do not have permissions to perform this action!", None)

        # Password confirmation
        password = data.get("password")
        confirm = data.get("confirm")
        if password != confirm:
            return (False, "Passwords do not match! Please try again.", None)

        # Email validation
        if not is_valid_email_regex(data.get("email")):
            return (False, "Email address is not valid.", None)

        # Username validation
        user_check = isValidUsername(data.get("username"))
        if user_check[0] is False:
            return (False, "Username is already taken! Please select another.", None)

        # Prepare data
        data = data.copy()
        del data['confirm']
        data['password'] = generate_password_hash(password)
        data['bank'] = int(data['bank'])
        data['is_cc_admin'] = bool(data['is_cc_admin'])

        # Required fields
        required_fields = ["username", "password", "first_name", "last_name", "email", "bank", "is_cc_admin"]
        for field in required_fields:
            if field not in data or data[field] in ("", None):
                return (False, "Please fill out the form completely!", None)

        # Insert user
        sql = """
            INSERT INTO users
            (username, password, first_name, last_name, email, bank, is_cc_admin, join_date)
            VALUES
            (:username, :password, :first_name, :last_name, :email, :bank, :is_cc_admin, CURRENT_TIMESTAMP)
        """
        db.session.execute(text(sql), {k: data[k] for k in required_fields})
        db.session.commit()

        return (True, "User created successfully!", data.get("username"))

    except:
        db.session.rollback()
        return (False, "User could not be created at this time. Please try again later", None)

def deleteUser(user_id):
    try:
        # Check if user exists
        result = db.session.execute(
            text("SELECT username FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        user = result.mappings().first()
        if not user:
            return (False, "User not found!", None)

        # Prevent deletion of ccadmin
        if user['username'] == "ccadmin":
            return (False, "You cannot delete this user!", None)

        # Admin permission check
        if not session.get("is_cc_admin", False):
            return (False, "You do not have permissions to perform this action!", None)

        # Delete user
        db.session.execute(
            text("DELETE FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        db.session.commit()

        return (True, "User deleted successfully!", None)

    except:
        db.session.rollback()
        return (False, "Could not delete user at this time. Please try again later.", None)


















