from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
from datetime import datetime
import secrets
import string
import sqlite3

app = FastAPI()

# Mount the directory containing your HTML files
app.mount("/static/css", StaticFiles(directory="static/css"), name="static_css")
app.mount("/static/js", StaticFiles(directory="static/js"), name="static_js")
app.mount("/static/images", StaticFiles(directory="static/images"), name="static_images")

templates = Jinja2Templates(directory="templates")

# Initialize the cursor as a global variable
conn = sqlite3.connect('order_id.db')
c = conn.cursor()

# Create a table to store order data if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                order_key TEXT,
                order_date TEXT,
                payment_method TEXT,
                license_key TEXT
            )''')
conn.commit()


def generate_current_date():
    current_date = datetime.now()
    formatted_date = current_date.strftime("%B %d, %Y")
    return formatted_date


def generate_payment_method():
    card_networks = ["Visa", "MasterCard", "American Express", "Discover"]
    card_network = random.choice(card_networks)
    ending_digits = "".join([str(random.randint(0, 9)) for _ in range(4)])
    result = f"{card_network} ending in {ending_digits}"
    return result


def generate_license_key(length=32):
    hex_string = secrets.token_hex(length//2)
    return hex_string


def generate_order_key(prefix="wc_order_", length=13):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    order_id = prefix + random_string
    return order_id


def generate_order_id():
    while True:
        # Generate a random 6-digit number greater than 420000 but less than 500000
        random_number = random.randint(420001, 499999)
        # Check if the number already exists in the database
        c.execute("SELECT COUNT(*) FROM order_id WHERE number=?", (random_number,))
        if c.fetchone()[0] == 0:
            # If the number is unique, insert it into the database and return it
            c.execute("INSERT INTO order_id VALUES (?)", (random_number,))
            conn.commit()
            return random_number


@app.get("/")
async def home():
    return RedirectResponse(url="https://ezmod.vip/")


@app.get("/receipts/{number_of_receipts}")
async def generate_receipts(number_of_receipts: int):
    # Generate receipts
    receipts = []
    for _ in range(number_of_receipts):
        order_id = generate_order_id()
        order_key = generate_order_key()
        order_date = generate_current_date()
        payment_method = generate_payment_method()
        license_key = generate_license_key()
        # Insert order data into the database
        c.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", (order_id, order_key, order_date, payment_method, license_key))
        conn.commit()
        # Generate receipt URL
        receipt = f"https://ezmod.org/checkout/order-received/{order_id}/?key={order_key}"
        receipts.append(receipt)

    receipts = "\n".join(receipts)
    return Response(content=receipts, media_type="text/plain")


@app.get("/checkout/order-received/{order_id}/", response_class=HTMLResponse)
async def checkout_order_received(request: Request, order_id: str, order_key: str = Query(None, alias="key")):
    # Retrieve order data from the database
    c.execute("SELECT * FROM orders WHERE order_id=?", (order_id,))
    order_data = c.fetchone()

    if order_data and order_key == order_data[0]:
        _, order_key, order_date, payment_method, license_key = order_data
        # Render the template with the retrieved order data
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "order_id": order_id,
                "order_date": order_date,
                "payment_method": payment_method,
                "license_key": license_key
            }
        )

    else:
        # Render the "cobalt-thank-you.html" template
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "order_id": order_id,
                "order_date": None,
                "payment_method": None,
                "license_key": None
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)