from flask import Flask, render_template, request, redirect, url_for
import razorpay
from razorpay.errors import BadRequestError

app = Flask(__name__)

# Razorpay credentials
key_id = 
key_secret = 
client = razorpay.Client(auth=(key_id, key_secret))

# Dummy data for items and prices
items = {"item1": 10, "item2": 20, "item3": 30}
selected_items = []

@app.route('/')
def index():
    total_amount = sum(items[item] for item in selected_items)
    return render_template('index.html', items=items, selected_items=selected_items, total_amount=total_amount)

@app.route('/add_item', methods=['POST'])
def add_item():
    item = request.form['item']
    selected_items.append(item)
    return redirect(url_for('index'))

@app.route('/remove_item', methods=['POST'])
def remove_item():
    item = request.form['item']
    selected_items.remove(item)
    return redirect(url_for('index'))

@app.route('/buy')
def buy():
    try:
        total_amount = sum(items[item] for item in selected_items) * 100  # Razorpay requires amount in paise
        order = client.order.create(dict(amount=total_amount, currency='INR', payment_capture=1))
        order_id = order['id']
        return render_template('buy.html', key_id=key_id, amount=total_amount, order_id=order_id)
    except BadRequestError as e:
        # Log the error for debugging purposes
        print(f"Razorpay BadRequestError: {str(e)}")
        return "Error processing payment. Please try again later."

if __name__ == '__main__':
    app.run(debug=True)
