import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING shares > 0 ORDER BY symbol",
        user_id,
    )
    # Get user's cash balance
    user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    total = user_cash
    for stock in stocks:
        stock["price"] = lookup(stock["symbol"])["price"]
        stock["amount"] = stock["price"] * stock["shares"]
        total += stock["amount"]
    return render_template("index.html", stocks=stocks, total=total, cash=user_cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    user_id = session["user_id"]
    # Check user's balance
    user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0][
        "cash"
    ]
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        # Ensure symbol exists
        if not quote:
            return apology("Wrong symbol", 403)
        # Ensure valid shares
        shares = request.form.get("shares")
        if not shares:
            return apology("Invalid shares", 403)
        try:
            shares = int(shares)
            if shares < 0:
                return apology("Invalid shares", 403)
        except ValueError:
            return apology("Invalid shares", 403)

        name = quote["name"]
        price = quote["price"]
        symbol = quote["symbol"]

        amount = price * shares
        if amount > user_cash:
            return apology("Insufficient cash", 403)

        type = 'Buy'
        #  Add transaction to transactions table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, price, shares, amount, type) VALUES (?, ?, ?, ?, ?, ?)",
            user_id,
            symbol,
            price,
            shares,
            amount,
            type,
        )

        # Update user cash
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?", user_cash - amount, user_id
        )
        flash(f"Bought!")

        # Redirect to homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html", user_cash=user_cash)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    stocks = db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", user_id
    )
    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not quote:
            return apology("Wrong symbol", 403)
        name = quote["name"]
        price = quote["price"]
        symbol = quote["symbol"]
        return render_template("quoted.html", name=name, price=price, symbol=symbol)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password or not confirmation:
            return apology("must provide password and/or confirmation", 403)

        # Ensure password matches confirmation
        elif password != confirmation:
            return apology("password must match confirmation", 403)

        if not re.fullmatch(r"[A-Za-z0-9!@#$%^&*()+=]{8,}", password):
            return apology("invalid password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Check if username exists
        if len(rows) == 1:
            return apology("username already exists", 403)

        # Add username + pw to db
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            generate_password_hash(password),
        )

        new_user = db.execute("SELECT * FROM users WHERE username = ?", username)[0][
            "id"
        ]
        # Remember which user has logged in
        session["user_id"] = new_user

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        stocks = db.execute(
            "SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING shares > 0 ORDER BY symbol",
            user_id,
        )
        # Get user's cash balance
        for stock in stocks:
            stock["price"] = lookup(stock["symbol"])["price"]
            stock["amount"] = stock["price"] * stock["shares"]

        return render_template("sell.html", stocks=stocks)
    # User reached route via POST (as by submitting a form via POST)
    else:
        # Get symbol & shares
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 403)

        shares = request.form.get("shares")

        # Get user's shares for given symbol
        user_shares = db.execute(
            "SELECT SUM(shares) as shares FROM transactions WHERE user_id = ? AND symbol = ?",
            user_id,
            symbol,
        )[0]["shares"]

        if not shares:
            return apology("must provide shares", 403)
        try:
            shares = int(shares)
            if shares > user_shares:
                return apology("not enough shares", 403)
        except ValueError:
            return apology("shares must be integer greater than 0", 403)

        price = lookup(symbol)["price"]
        amount = price * shares
        type = 'Sell'
        # Add sell to the transactions table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, price, shares, amount, type) VALUES (?, ?, ?, ?, ?, ?)",
            user_id,
            symbol,
            price,
            -shares,
            amount,
            type,
        )

        # Update user cash
        cash = (
            db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
            + amount
        )
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user_id)
        flash(f"Sold!")
        return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("password.html")

    else:
        old_pw = request.form.get("old")
        if not old_pw:
            return apology("must provide old password", 403)

        current_pw = db.execute("SELECT hash FROM users WHERE id = ?", user_id)[0][
            "hash"
        ]
        if not check_password_hash(current_pw, old_pw):
            return apology("wrong old password", 403)

        # Ensure password was submitted
        new_pw = request.form.get("new")
        confirmation = request.form.get("confirmation")
        if not new_pw or not confirmation:
            return apology("must provide new password and/or confirmation", 403)

        # Ensure password matches confirmation
        elif new_pw != confirmation:
            return apology("new password must match confirmation", 403)

        elif not re.fullmatch(r"[A-Za-z0-9!@#$%^&*()+=]{8,}", new_pw):
            return apology("invalid password", 403)

        db.execute(
            "UPDATE users SET hash = ? WHERE id= ?",
            generate_password_hash(new_pw),
            user_id,
        )
        flash(f"Password updated sucessfully!")
        return redirect("/")


@app.route("/addcash", methods=["GET", "POST"])
@login_required
def addcash():
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("addcash.html")

    else:
        # Ensure valid amount
        amount = request.form.get("amount")
        if not amount:
            return apology("must provide amount", 403)

        # Query user cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0][
            "cash"
        ]

        # Add amount to user cash
        new_cash = float(amount) + user_cash

        # Update database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, user_id)

        flash(f"Cash added successfully!")
        return redirect("/")


@app.route("/buysell", methods=["POST"])
@login_required
def buysell():
    user_id = session["user_id"]
    userchoice = request.form.get("userchoice")
    symbol = request.form.get("symbol")
    shares = request.form.get("shares")

    # Lookup current price
    price = lookup(symbol)["price"]
    if not userchoice:
        return apology("must provide option", 403)

    if not shares:
        return apology("must provide shares", 403)
    try:
        shares = int(shares)
    except ValueError:
        return apology("shares must be integer greater than 0", 403)

    if userchoice == "sell":
        # Get availale shares
        user_shares = int(request.form.get("user_shares"))

        # Ensure shares not exceed available shares
        if shares > user_shares:
            return apology("not enough shares", 403)

        # Amount = shares * current price
        amount = float(shares) * price
        type = 'Sell'
        # Add amount to user_cash in user table

        # Add sell to the transactions table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, price, shares, amount, type) VALUES (?, ?, ?, ?, ?, ?)",
            user_id,
            symbol,
            price,
            -shares,
            amount,
            type,
        )

        # Update user cash
        cash = (
            db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
            + amount
        )
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user_id)
        flash(f"Sold!")
        return redirect("/")

    else:  # userchoice == "buy"
        # Amount = shares * current price
        amount = shares * price

        # Query available cash from users table
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0][
            "cash"
        ]
        # ensure amount <= cash
        if amount > user_cash:
            return apology("insufficient cash", 403)

        type = 'Buy'
        # Add buy to the transactions table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, price, shares, amount, type) VALUES (?, ?, ?, ?, ?, ?)",
            user_id,
            symbol,
            price,
            shares,
            amount,
            type,
        )

        # Subtract amount from cash in user table
        cash = user_cash - amount
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user_id)
        flash(f"Bought!")
        return redirect("/")
