from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import random
import string

app = Flask(__name__)
# Medicine dictionary
medicine_dict = {
    'azithral': {'price': 120.00,
                 'uses': 'Treatment of Bacterial infections',
                 'manufacturer': 'Pfizer',
                 'dosage_form': 'Tablet',
                 'quantity': 52},
    'avil': {'price': 10.00,
             'quantity': 102,
             'manufacturer': 'Sanofi',
             'dosage_form': 'Tablet',
             'uses': 'Treatment of Allergic conditions'},
    'atarax': {'price': 78.00,
               'uses': 'Treatment of Anxiety, Treatment of Skin conditions with inflammation & itching',
               'manufacturer': 'UCB Pharma',
               'dosage_form': 'Syrup',
               'quantity': 70},
    'aciloc': {'price': 38.00,
               'uses': 'Treatment of Gastroesophageal reflux disease (Acid reflux), Treatment of Peptic ulcer disease',
               'manufacturer': 'Cadila Healthcare',
               'dosage_form': 'Capsule',
               'quantity': 30},
    'nicip': {'price': 23.00,
              'uses': 'Treatment of Allergic conditions',
              'manufacturer': 'Cipla',
              'dosage_form': 'Tablet',
              'quantity': 80},
    'crocin': {'price': 18.00,
              'uses': 'Relief of pain and fever',
              'quantity': 90,
              'manufacturer': 'GlaxoSmithKline',
              'dosage_form': 'Tablet'},
    'augmentin': {'price': 250.00,
              'uses': 'Treatment of bacterial infections',
              'quantity': 20,
              'manufacturer': 'GlaxoSmithKline',
              'dosage_form': 'Tablet'},
    'neurobion': {'price': 45.00,
              'uses': 'Treatment of nerve pain and inflammation',
              'quantity': 60,
              'manufacturer': 'Merck KGaA',
              'dosage_form': 'Tablet'},
    'omnacortil': {'price': 95.00,
              'uses': 'Treatment of various inflammatory and autoimmune diseases',
              'quantity': 30,
              'manufacturer': 'Macleods Pharmaceuticals Ltd.',
              'dosage_form': 'Tablet'},
    'lactocalamine': {'price': 65.00,
              'uses': 'Treatment of skin irritation and itching',
              'quantity': 45,
              'manufacturer': 'Piramal Healthcare',
              'dosage_form': 'Lotion'},
    'sporlac': {'price': 55.00,
              'uses': 'Treatment of diarrhea and gut-related infections',
              'quantity': 40,
              'manufacturer': 'Sanofi India Limited',
              'dosage_form': 'Capsule'},
}


user_cart = []

#home route for the chatbot
@app.route("/")
def home():
    return "Welcome to the WhatsApp chatbot!"

#main route for the Twilio webhook
@app.route('/sms', methods=['POST'])
def sms():
    # Get the incoming message from user
    incoming_message = request.values.get('Body', '').lower()
    
    #Twilio response object
    response = MessagingResponse()
    
    # Check if the user wants to order medicine
    if 'search' in incoming_message:
        try:
            medicine_name = incoming_message.split('search ')[1].strip()
        except:
            message = 'Invalid format. Please enter the name of the medicine you would like to search after "search".'
            response.message(message)
            return str(response)
        
        if medicine_name in medicine_dict:
            #details of the medicine from the dictionary
            medicine_details = medicine_dict[medicine_name]
            message = f'Here are the details of {medicine_name}:\nPrice: Rs.{medicine_details["price"]:.2f}\nStock: {medicine_details["quantity"]}\nUses: {medicine_details["uses"]}\nManufacturer: {medicine_details["manufacturer"]}\nDosage Form: {medicine_details["dosage_form"]}'
        else:
            message = f'Sorry, {medicine_name} is not available.'
        response.message(message)
    elif 'hi' in incoming_message:
        message = 'Welcome to the medicine ordering chatbot!\n'
        msg1='\n 1. To add medicine to your cart or to order, \nEnter "add [medicine name]".\n2. To remove medicine \nEnter "Remove [medicine name]".\n3. To search for medicine, \nEnter "search [medicine name]".\n4. Enter "cart" to view your cart.\n5. Enter "Checkout" to place your order.'
        response.message(message)
        response.message(msg1)
        return str(response)

    elif 'remove' in incoming_message:
        # Get the name and quantity
        try:
            medicine_name, quantity = incoming_message.split('remove ')[1].strip().split()
            quantity = int(quantity)
        except:
            message = 'Invalid format. Please enter the name of the medicine followed by the quantity (separated by a space). Example: "Remove Medicine1 2" to remove 2 units of Medicine1 from your cart.'
            response.message(message)
            return str(response)

        # Check if the medicine is in the user's cart
        for item in user_cart:
            if item['medicine'] == medicine_name:
                if item['quantity'] >= quantity:
                    # Reduce the quantity of the medicine in the user's cart
                    item['quantity'] -= quantity
                    # Increase the quantity of the medicine in the medicine dictionary
                    medicine_dict[medicine_name]['quantity'] += quantity
                    message = f'{quantity} unit(s) of {medicine_name} has been removed from your cart.'
                else:
                    message = f'Invalid quantity. You have only {item["quantity"]} unit(s) of {medicine_name} in your cart.'
                response.message(message)
                return str(response)

        message = f'Sorry, {medicine_name} is not in your cart.'
        response.message(message)
        message = f'Sorry, {medicine_name} is not in your cart.'
        response.message(message)

        # Check if the user wants to order medicine
    elif 'checkout' in incoming_message:
        if len(user_cart) == 0:
            message = 'Your cart is empty. Please add some medicine before placing your order.'
        else:
            # Calculate the total cost
            total_cost = sum([medicine_dict[medicine['medicine']]['price'] * medicine['quantity'] for medicine in user_cart])

            order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # Generate the bill
            bill = f"-----------------------------------\n"
            bill += f"                MEDICINE BILL\n"
            bill += f"-----------------------------------\n"
            bill += f"Date: {datetime.datetime.now()}\n"
            bill += f"Order ID: {order_id}\n\n"
            bill += f"MEDICINE PRICE QTY TOTAL\n"
            bill += f"-----------------------------------\n"

            for item in user_cart:
                medicine_name = item['medicine']
                medicine_price = medicine_dict[medicine_name]['price']
                quantity = item['quantity']
                total = medicine_price * quantity
                bill += f"{medicine_name.ljust(16)} {medicine_price:.2f}  {quantity}    {total:.2f}\n"
            
            bill += f"-----------------------------------\n"
            bill += f"TOTAL COST: {total_cost:.2f}\n"
            bill += f"-----------------------------------\n\n"
            bill += f"Thank you for your order! Your order will be shipped to you within 2-3 business days."

            # Send the bill as a response
            response.message(bill)

            # Clear the user's cart
            user_cart.clear()  

    # Check if the user wants to add medicine to their cart
    elif 'add' in incoming_message:
        # Get the name and quantity
        try:
            medicine_name, quantity = incoming_message.split('add ')[1].strip().split()
            quantity = int(quantity)
        except:
            message = 'Invalid format. Please enter the name of the medicine followed by the quantity (separated by a space). Example: "Add Medicine1 2" to add 2 units of medicine1 to your cart.'
            response.message(message)
            return str(response)
        
       
        if medicine_name in medicine_dict and medicine_dict[medicine_name]['quantity'] >= quantity:
            
            user_cart.append({'medicine': medicine_name, 'quantity': quantity})
        
            medicine_dict[medicine_name]['quantity'] -= quantity
            message = f'{quantity} unit(s) of {medicine_name} has been added to your cart.'
        elif medicine_name in medicine_dict and medicine_dict[medicine_name]['quantity'] < quantity:
            message = f'Sorry, only {medicine_dict[medicine_name]["quantity"]} unit(s) of {medicine_name} are available.'
        else:
            message = f'Sorry, {medicine_name} is not available.'
        response.message(message)
    

    elif 'cart' in incoming_message:
       
        if len(user_cart) == 0:
            message = 'Your cart is empty.'
        else:
         
            total_cost = sum([medicine_dict[medicine['medicine']]['price'] * medicine['quantity'] for medicine in user_cart])
            message = 'Here is the contents of your cart:\n'
            for medicine in user_cart:
                message += f'{medicine["medicine"]} - Rs.{medicine_dict[medicine["medicine"]]["price"]:.2f} x {medicine["quantity"]} = Rs.{medicine_dict[medicine["medicine"]]["price"] * medicine["quantity"]:.2f}\n'
                message += f'\nTotal cost: Rs.{total_cost:.2f}'
        response.message(message)
        
    return str(response)  

    
# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)

