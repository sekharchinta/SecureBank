from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
import mysql.connector as db
import re
from datetime import datetime
import random
import os
from decimal import Decimal, InvalidOperation
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key")

# ----------------------- DATABASE CONNECTION -----------------------

def get_db_connection():
    return db.connect(
        user='root',
        password='lxfZBhpPmwhSjirNyORmdhlhkoaipNyU',
        host='containers-us-west-123.railway.app',
        database='railway',
        port=12345
    )

@app.before_request
def before_request():
    g.db = get_db_connection()
    g.cur = g.db.cursor(buffered=True)

@app.teardown_appcontext
def teardown_db(exception):
    db_conn = getattr(g, 'db', None)
    if db_conn is not None:
        db_conn.close()

# ----------------------- HELPERS -----------------------

def is_valid_email(email):
    return re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email)

def is_valid_mobile(mobile):
    return re.fullmatch(r'^[6-9][0-9]{9}$', mobile)

def generate_account_number():
    accno_prefix = '10032051'
    cur = g.cur
    while True:
        num = random.randint(1000, 9999)
        accnum = accno_prefix + str(num)
        cur.execute('SELECT accountno FROM user_accounts WHERE accountno=%s', (accnum,))
        if cur.fetchone() is None:
            return int(accnum)

def verify_pin(stored_pin, entered_pin):
    if stored_pin is None:
        return False
    if isinstance(stored_pin, (bytes, bytearray)):
        stored_pin = stored_pin.decode("utf-8", "ignore")
    stored_pin = str(stored_pin).strip()
    entered_pin = (entered_pin or "").strip()

    # Debug print
    print(f"[DEBUG] Stored PIN: {stored_pin[:25]}...  Entered PIN: {entered_pin}")

    try:
        if stored_pin.startswith(("pbkdf2:", "scrypt:")):
            return check_password_hash(stored_pin, entered_pin)
    except Exception as e:
        print(f"[DEBUG] Hash verification error: {e}")
    return stored_pin == entered_pin

# ----------------------- ROUTES -----------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_pin/<int:acc>/<pin>')
def test_pin(acc, pin):
    cur = g.cur
    cur.execute("SELECT pin FROM logins WHERE id=%s", (acc,))
    row = cur.fetchone()
    if not row:
        return "❌ No account found"
    result = verify_pin(row[0], pin)
    return f"✅ PIN Match: {result}"

# ----------------------- CREATE ACCOUNT -----------------------

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    cur = g.cur
    db_conn = g.db

    if request.method == 'POST':
        account_type = request.form.get('account_type')

        # -------- USER ACCOUNT --------
        if account_type == 'user':
            name = request.form.get('name')
            mobile = request.form.get('mobile')
            email = request.form.get('email')
            acc_type = request.form.get('acc_type')
            pin = request.form.get('pin')
            confirm_pin = request.form.get('confirm_pin')

            if not name or name.isdigit():
                flash('Please enter a valid name', 'error')
                return redirect(url_for('create_account'))

            if not is_valid_mobile(mobile):
                flash('Invalid mobile number', 'error')
                return redirect(url_for('create_account'))

            cur.execute('SELECT phnno FROM user_accounts WHERE phnno=%s', (mobile,))
            if cur.fetchone():
                flash('Mobile number already exists', 'error')
                return redirect(url_for('create_account'))

            if not is_valid_email(email):
                flash('Invalid email format', 'error')
                return redirect(url_for('create_account'))

            cur.execute('SELECT email FROM user_accounts WHERE email=%s', (email,))
            if cur.fetchone():
                flash('Email already exists', 'error')
                return redirect(url_for('create_account'))

            if acc_type and acc_type.lower() not in ['savings', 'current']:
                flash('Invalid account type', 'error')
                return redirect(url_for('create_account'))

            if pin != confirm_pin or len(pin) != 4 or not pin.isdigit():
                flash('PIN must be 4 digits and match confirmation', 'error')
                return redirect(url_for('create_account'))

            account_no = generate_account_number()
            hashed_pin = generate_password_hash(pin, method='pbkdf2:sha256', salt_length=16)

            cur.execute(
                'INSERT INTO user_accounts(username, phnno, email, accounttype, accountno, balance) VALUES (%s,%s,%s,%s,%s,%s)',
                (name, mobile, email, acc_type, account_no, Decimal('0.00'))
            )
            cur.execute('INSERT INTO logins(id, pin, usertype) VALUES (%s,%s,%s)',
                        (account_no, hashed_pin, 'Account Holder'))
            db_conn.commit()
            flash(f'Account created successfully! Your Account No: {account_no}', 'success')
            return redirect(url_for('user_login'))

        # -------- ADMIN ACCOUNT --------
        elif account_type == 'admin':
            name = request.form.get('name')
            mobile = request.form.get('mobile')
            email = request.form.get('email')
            emp_id = request.form.get('emp_id')
            pin = request.form.get('pin')
            confirm_pin = request.form.get('confirm_pin')

            if not name or name.isdigit():
                flash('Please enter a valid name', 'error')
                return redirect(url_for('create_account'))

            if not is_valid_mobile(mobile):
                flash('Invalid mobile number', 'error')
                return redirect(url_for('create_account'))

            cur.execute('SELECT phnno FROM admin_accounts WHERE phnno=%s', (mobile,))
            if cur.fetchone():
                flash('Mobile number already exists', 'error')
                return redirect(url_for('create_account'))

            if not is_valid_email(email):
                flash('Invalid email format', 'error')
                return redirect(url_for('create_account'))

            cur.execute('SELECT email FROM admin_accounts WHERE email=%s', (email,))
            if cur.fetchone():
                flash('Email already exists', 'error')
                return redirect(url_for('create_account'))

            if not emp_id or not emp_id.isdigit():
                flash('Employee ID must be numeric', 'error')
                return redirect(url_for('create_account'))

            cur.execute('SELECT empid FROM bankemployees WHERE empid=%s', (int(emp_id),))
            if not cur.fetchone():
                flash('Employee ID not found', 'error')
                return redirect(url_for('create_account'))

            cur.execute('SELECT employeeid FROM admin_accounts WHERE employeeid=%s', (emp_id,))
            if cur.fetchone():
                flash('Admin account already exists for this employee', 'error')
                return redirect(url_for('create_account'))

            if pin != confirm_pin or len(pin) != 4 or not pin.isdigit():
                flash('PIN must be 4 digits and match confirmation', 'error')
                return redirect(url_for('create_account'))

            hashed_pin = generate_password_hash(pin, method='pbkdf2:sha256', salt_length=16)
            cur.execute('INSERT INTO admin_accounts(adminname, phnno, email, employeeid) VALUES (%s,%s,%s,%s)',
                        (name, mobile, email, emp_id))
            cur.execute('INSERT INTO logins(id, pin, usertype) VALUES (%s,%s,%s)',
                        (emp_id, hashed_pin, 'Admin'))
            db_conn.commit()

            flash('Admin account created successfully!', 'success')
            return redirect(url_for('admin_login'))

    return render_template('create_account.html')

# ----------------------- LOGIN ROUTES -----------------------

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    cur = g.cur
    if request.method == 'POST':
        account_id = (request.form.get('account_id') or "").strip()
        pin = (request.form.get('pin') or "").strip()
        if not account_id or not pin:
            flash('Please fill all fields', 'error')
            return redirect(url_for('user_login'))

        cur.execute('SELECT pin FROM logins WHERE id=%s AND usertype="Account Holder"', (account_id,))
        data = cur.fetchone()
        if not data:
            flash('Account not found', 'error')
            return redirect(url_for('user_login'))

        stored_pin = data[0]
        print(f"[DEBUG] Stored PIN: {stored_pin}")
        print(f"[DEBUG] Entered PIN: {pin}")

        if not verify_pin(stored_pin, pin):
            flash('Incorret PIN', 'error')
            return redirect(url_for('user_login'))

        session['user_id'] = account_id
        session['user_type'] = 'user'
        return redirect(url_for('user_dashboard'))

    return render_template('user_login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    cur = g.cur
    if request.method == 'POST':
        emp_id = (request.form.get('account_id') or "").strip()
        pin = (request.form.get('pin') or "").strip()
        if not emp_id or not pin:
            flash('Please fill all fields', 'error')
            return redirect(url_for('admin_login'))

        cur.execute('SELECT pin FROM logins WHERE id=%s AND usertype="Admin"', (emp_id,))
        data = cur.fetchone()
        if not data:
            flash('Invalid credentials', 'error')
            return redirect(url_for('admin_login'))

        stored_pin = data[0]
        if not verify_pin(stored_pin, pin):
            flash('Invalid PIN', 'error')
            return redirect(url_for('admin_login'))

        session['user_id'] = emp_id
        session['user_type'] = 'admin'
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')

# ----------------------- DASHBOARDS -----------------------

# ----------------------- USER DASHBOARD  -----------------------

# ----------------------- USER DASHBOARD (FIXED & OPTIMIZED) -----------------------

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    """Displays user dashboard and handles deposit/withdraw actions."""
    if 'user_id' not in session or session.get('user_type') != 'user':
        return redirect(url_for('user_login'))

    cur = g.cur
    db_conn = g.db
    db_conn.autocommit = False  # ensure we manage transactions manually
    account_no = int(session['user_id'])

    # Fetch current user data
    cur.execute(
        'SELECT username, accountno, accounttype, balance FROM user_accounts WHERE accountno=%s',
        (account_no,)
    )
    user_data = cur.fetchone()

    if not user_data:
        flash("User account not found!", "danger")
        return redirect(url_for('logout'))

    # Handle Deposit or Withdraw actions
    if request.method == 'POST' and 'action' in request.form:
        action = request.form.get('action')
        amount_str = request.form.get('amount', '').strip()

        # Input validation
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                flash("Amount must be greater than 0", "danger")
                return redirect(url_for('user_dashboard'))
        except (InvalidOperation, TypeError):
            flash("Invalid amount entered.", "danger")
            return redirect(url_for('user_dashboard'))

        try:
            # Lock the user row for update to prevent race conditions
            cur.execute("SELECT balance FROM user_accounts WHERE accountno=%s FOR UPDATE", (account_no,))
            row = cur.fetchone()
            if not row:
                flash("Account not found!", "danger")
                db_conn.rollback()
                return redirect(url_for('user_dashboard'))

            current_balance = Decimal(row[0])

            # Perform credit or debit
            if action == 'credit':
                new_balance = current_balance + amount
                cur.execute(
                    "UPDATE user_accounts SET balance=%s WHERE accountno=%s",
                    (new_balance, account_no)
                )
                cur.execute(
                    "INSERT INTO transactions (accountno, transactiontype, amount, Event_date, Event_time) VALUES (%s,%s,%s,CURDATE(),CURTIME())",
                    (account_no, 'credit', amount)
                )
                flash(f"₹{amount:.2f} credited successfully!", "success")

            elif action == 'debit':
                if current_balance < amount:
                    flash("Insufficient balance!", "warning")
                    db_conn.rollback()
                    return redirect(url_for('user_dashboard'))

                new_balance = current_balance - amount
                cur.execute(
                    "UPDATE user_accounts SET balance=%s WHERE accountno=%s",
                    (new_balance, account_no)
                )
                cur.execute(
                    "INSERT INTO transactions (accountno, transactiontype, amount, Event_date, Event_time) VALUES (%s,%s,%s,CURDATE(),CURTIME())",
                    (account_no, 'debit', amount)
                )
                flash(f"₹{amount:.2f} debited successfully!", "success")

            # Commit both balance update and transaction record
            db_conn.commit()

        except Exception as e:
            db_conn.rollback()
            print(f"[ERROR] Transaction failed: {e}")
            flash("Transaction failed. Please try again.", "danger")

    # Fetch updated user data (after transaction)
    cur.execute(
        'SELECT username, accountno, accounttype, balance FROM user_accounts WHERE accountno=%s',
        (account_no,)
    )
    user_data = cur.fetchone()

    # Fetch recent transactions (limit 10)
    cur.execute("""
        SELECT transactiontype, amount, Event_date, Event_time 
        FROM transactions WHERE accountno=%s
        ORDER BY Event_date DESC, Event_time DESC LIMIT 10
    """, (account_no,))
    transactions = cur.fetchall()

    return render_template('user_dashboard.html', user_data=user_data, transactions=transactions)


# ----------------------- VIEW ALL TRANSACTIONS -----------------------

@app.route('/user_all_transactions')
def user_all_transactions():
    """Displays all transactions of the logged-in user."""
    if 'user_id' not in session or session.get('user_type') != 'user':
        return redirect(url_for('user_login'))

    cur = g.cur
    account_no = int(session['user_id'])

    cur.execute("""
        SELECT transactiontype, amount, Event_date, Event_time 
        FROM transactions 
        WHERE accountno=%s
        ORDER BY Event_date DESC, Event_time DESC
    """, (account_no,))
    transactions = cur.fetchall()

    return render_template('user_all_transactions.html', transactions=transactions)


# ----------------------- CHANGE PIN -----------------------

@app.route('/change_pin', methods=['GET', 'POST'])
def change_pin():
    """Flask-based PIN change page."""
    if 'user_id' not in session or session.get('user_type') != 'user':
        return redirect(url_for('user_login'))

    cur = g.cur
    db_conn = g.db
    account_no = int(session['user_id'])

    if request.method == 'POST':
        current_pin = request.form.get('current_pin')
        new_pin = request.form.get('new_pin')
        confirm_pin = request.form.get('confirm_pin')

        # Input validation
        if not all([current_pin, new_pin, confirm_pin]):
            flash('All fields are required.', 'warning')
            return redirect(url_for('change_pin'))

        if len(new_pin) != 4 or not new_pin.isdigit():
            flash('New PIN must be a 4-digit number.', 'warning')
            return redirect(url_for('change_pin'))

        if new_pin != confirm_pin:
            flash('New PIN and Confirm PIN do not match.', 'danger')
            return redirect(url_for('change_pin'))

        # Fetch stored PIN
        cur.execute('SELECT pin FROM logins WHERE id=%s AND usertype="Account Holder"', (account_no,))
        data = cur.fetchone()

        if not data:
            flash('User not found.', 'danger')
            return redirect(url_for('change_pin'))

        stored_pin = data[0]

        if not verify_pin(stored_pin, current_pin):
            flash('Incorrect current PIN.', 'danger')
            return redirect(url_for('change_pin'))

        # Update PIN
        new_hashed = generate_password_hash(new_pin)
        try:
            cur.execute('UPDATE logins SET pin=%s WHERE id=%s', (new_hashed, account_no))
            db_conn.commit()
            flash('PIN changed successfully!', 'success')
        except Exception as e:
            db_conn.rollback()
            flash('Failed to change PIN. Please try again.', 'danger')
            print(f"[ERROR] Change PIN: {e}")
            return redirect(url_for('change_pin'))

        return redirect(url_for('user_dashboard'))

    return render_template('change_pin.html')




# ----------------------- ADMIN DASHBOARD -----------------------

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    """Displays the Admin Dashboard with user search and date-based transaction search."""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))

    cur = g.cur
    context = {
        "user_result": None,
        "transactions": None,
        "search_date": None
    }

    # --- Search User by Account Number ---
    if request.method == 'POST' and 'search_account' in request.form:
        acc_no = request.form.get('search_account', '').strip()
        if not acc_no.isdigit():
            flash("Please enter a valid account number!", "warning")
        else:
            cur.execute("""
                SELECT username, accountno, accounttype, phnno, email, balance
                FROM user_accounts
                WHERE accountno = %s
            """, (acc_no,))
            user = cur.fetchone()
            if user:
                context["user_result"] = user
            else:
                flash("No user found with that account number.", "danger")

    # --- Search Transactions by Date ---
    if request.method == 'POST' and 'search_date' in request.form:
        search_date = request.form.get('search_date', '').strip()
        try:
            datetime.strptime(search_date, "%Y-%m-%d")  # validate date format
            cur.execute("""
                SELECT accountno, transactiontype, amount, Event_date, Event_time
                FROM transactions
                WHERE Event_date = %s
                ORDER BY Event_time DESC
            """, (search_date,))
            tx = cur.fetchall()
            if tx:
                context["transactions"] = tx
                context["search_date"] = search_date
            else:
                flash("No transactions found for that date.", "info")
        except ValueError:
            flash("Invalid date format! Use YYYY-MM-DD.", "danger")

    # --- Dashboard Summary ---
    cur.execute("SELECT COUNT(*) FROM user_accounts")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transactions")
    total_transactions = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT Event_date) FROM transactions WHERE Event_date = CURDATE()")
    today_transactions = cur.fetchone()[0]

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_transactions=total_transactions,
        today_transactions=today_transactions,
        user_result=context["user_result"],
        transactions=context["transactions"],
        search_date=context["search_date"]
    )

@app.route('/admin_all_users')
def admin_all_users():
    """Displays all users in the system for admin view."""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))

    cur = g.cur
    cur.execute("""
        SELECT username, accountno, accounttype, phnno, email, balance
        FROM user_accounts
        ORDER BY username ASC
    """)
    users = cur.fetchall()

    return render_template('admin_all_users.html', users=users)


# ----------------------- LOGOUT -----------------------

@app.route('/logout')
def logout():
    session.clear()
    #flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

# ----------------------- MAIN -----------------------

from datetime import datetime

@app.context_processor
def inject_now():
    """Makes current_year available in every Jinja2 template"""
    return {'current_year': datetime.now().year}


if __name__ == '__main__':
    app.run(debug=True)
