from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Siddhi126@",
    database="siddhi_resort"
)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        if user:
            return jsonify({'success': True, 'redirect': url_for('admin')})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials!'})
    return render_template('Login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        try:
            query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            db.commit()
            return jsonify({'success': True})
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'message': 'Failed to sign up. Please try again.'})
    return render_template('Signup.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/gallery')
def gallery():
    return render_template('Gallery.html')

@app.route('/room')
def room():
    return render_template('Room.html')

@app.route('/admin')
def admin():
    return render_template('Admin.html')

@app.route('/addroom', methods=['GET', 'POST'])
def addroom():
    if request.method == 'POST':
        data = request.get_json()
        room_number = data.get('roomNumber')
        room_type = data.get('roomType')
        price = data.get('price')
        
        try:
            query = "INSERT INTO rooms (room_number, room_type, price) VALUES (%s, %s, %s)"
            cursor.execute(query, (room_number, room_type, price))
            db.commit()
            return jsonify({'success': True})
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'message': 'Failed to add room. Please try again.'})
    return render_template('AddRoom.html')

@app.route('/roomlist')
def roomlist():
    return render_template('RoomList.html')

@app.route('/rooms', methods=['GET'])
def get_rooms():
    try:
        query = "SELECT room_number, room_type, price FROM rooms"
        cursor.execute(query)
        rooms = cursor.fetchall()
        room_list = [{'room_number': room[0], 'room_type': room[1], 'price': room[2]} for room in rooms]
        return jsonify(room_list)
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Failed to retrieve rooms.'})


@app.route('/addguest', methods=['GET', 'POST'])
def addguest():
    if request.method == 'POST':
        guest_name = request.form['guestName']
        guest_email = request.form['guestEmail']
        guest_phone = request.form['guestPhone']
        check_in_date = request.form['checkInDate']
        check_out_date = request.form['checkOutDate']
        
        query = """
            INSERT INTO guests (guest_name, guest_email, guest_phone, check_in_date, check_out_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (guest_name, guest_email, guest_phone, check_in_date, check_out_date))
        db.commit()
        
        return redirect(url_for('guestlist'))
    return render_template('AddGuest.html')


@app.route('/guestlist')
def guestlist():
    query = "SELECT * FROM guests"
    cursor.execute(query)
    guests = cursor.fetchall()
    return render_template('GuestList.html', guests=guests)

@app.route('/delete_guest/<int:guest_id>', methods=['POST'])
def delete_guest(guest_id):
    query = "DELETE FROM guests WHERE id = %s"
    cursor.execute(query, (guest_id,))
    db.commit()
    return redirect(url_for('guestlist'))

@app.route('/update_guest/<int:guest_id>', methods=['GET', 'POST'])
def update_guest(guest_id):
    if request.method == 'POST':
        guest_name = request.form['guestName']
        guest_email = request.form['guestEmail']  # Ensure this matches your table column
        guest_phone = request.form['guestPhone']
        check_in_date = request.form['checkInDate']
        check_out_date = request.form['checkOutDate']
        
        query = """
            UPDATE guests
            SET guest_name = %s, guest_email = %s, guest_phone = %s, check_in_date = %s, check_out_date = %s
            WHERE id = %s
        """
        cursor.execute(query, (guest_name, guest_email, guest_phone, check_in_date, check_out_date, guest_id))
        db.commit()
        
        return redirect(url_for('guestlist'))
    
    query = "SELECT * FROM guests WHERE id = %s"
    cursor.execute(query, (guest_id,))
    guest = cursor.fetchone()
    
    return render_template('UpdateGuest.html', guest=guest)


@app.route('/addpayment', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        amount = request.form['amount']
        payment_method = request.form['payment-method']

        # Insert the payment data into the database
        query = """
            INSERT INTO payments (name, email, amount, payment_method)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, amount, payment_method))
        db.commit()

        return redirect(url_for('paymentlist'))
    
    # Render the payment form
    return render_template('AddPayment.html')

@app.route('/paymentlist')
def paymentlist():
    # Fetch all payment records from the database
    query = "SELECT name, email, amount, payment_method, payment_date FROM payments"
    cursor.execute(query)
    payments = cursor.fetchall()

    return render_template('PaymentList.html', payments=payments)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        site_title = request.form['siteTitle']
        site_desc = request.form['siteDescription']
        
        try:
            # Begin transaction
            db.start_transaction()
            
            # Call the stored procedure
            query = "CALL SaveSettings(%s, %s)"
            cursor.execute(query, (site_title, site_desc))
            
            # Commit the transaction
            db.commit()
            
            return jsonify({'success': True, 'message': 'Settings saved successfully'})
        except Exception as e:
            # Rollback in case of error
            db.rollback()
            print(e)
            return jsonify({'success': False, 'message': 'Failed to save settings. Please try again.'})
    return render_template('Settings.html')

@app.route('/logout')
def logout():
    # Redirect to the login page or home page
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)


