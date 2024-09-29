from flask import Flask, render_template, request, redirect, url_for, jsonify
import razorpay
from razorpay.errors import BadRequestError, SignatureVerificationError
import hmac
import os
import hashlib

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

@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_secret = 'https://webhook.site/28a6cca3-a655-4970-a879-3cd822e6d01f'  # Replace with your actual webhook secret from Razorpay dashboard
    request_data = request.data.decode('utf-8')
    received_signature = request.headers.get('X-Razorpay-Signature')

    # Validate the webhook signature
    generated_signature = hmac.new(key_secret.encode('utf-8'), request_data.encode('utf-8'), hashlib.sha256).hexdigest()

    if hmac.compare_digest(generated_signature, received_signature):
        # The signature is valid, process the event
        webhook_event = request.get_json()
        event_type = webhook_event['event']

        if event_type == 'payment.captured':
            # Payment was successful
            payment_id = webhook_event['payload']['payment']['entity']['id']
            amount = webhook_event['payload']['payment']['entity']['amount']
            print(f"Payment captured successfully: {payment_id}, Amount: {amount}")
            # Here, you can update your database or perform other actions as necessary
            return jsonify({"status": "success", "message": "Payment captured successfully"}), 200
        else:
            print(f"Unhandled event type: {event_type}")
            return jsonify({"status": "success", "message": "Unhandled event type"}), 200
    else:
        # The signature does not match
        print("Invalid signature")
        return jsonify({"status": "error", "message": "Invalid signature"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
