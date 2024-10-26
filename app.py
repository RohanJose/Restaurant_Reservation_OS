from flask import Flask, render_template, request, redirect, url_for,Response
from booking_manager import BookingManager
import threading
from flask_mail import Mail, Message
import  mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587

app.config['MAIL_USERNAME'] = 'rohanjose00@gmail.com'  
app.config['MAIL_PASSWORD'] = 'uajhtzdkzcqenibe'  
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

username = 'newuser'
password = 'newpassword'
host = 'localhost'
database = 'Orders'

cnx = mysql.connector.connect(
    user=username,
    password=password,
    host=host,
    database=database
)
cursor = cnx.cursor()
cursor.execute(''' CREATE TABLE IF NOT EXISTS details (
    id INT,
    date DATE,
    start TIME,
    stop TIME,
    guests INT,
    email VARCHAR(255)
);''')
print("Database Initailised")

booking_manager = BookingManager()
lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/available_seats', methods=['POST'])
def available_seats():
    date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    num_guests = int(request.form['num_guests'])
    algorithm = request.form['algorithm']

    chosen_table = booking_manager.get_available_seats(date, start_time, end_time, num_guests, algorithm)

 
    tables = booking_manager.tables

    if chosen_table:
        return render_template('booking_summary.html', chosen_table=chosen_table, tables=tables, date=date, start_time=start_time, end_time=end_time, num_guests=num_guests)
    else:
        return render_template('available_seats.html', error="No available seats.")


@app.route('/payment_page', methods=['GET'])
def payment_page():
    seat_id = request.args.get('seat_id')
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    num_guests = request.args.get('num_guests')
    
    return render_template('payment.html', seat_id=seat_id, date=date, start_time=start_time, end_time=end_time, num_guests=num_guests)

@app.route('/booking/<seat_id>', methods=['GET'])
def booking(seat_id):
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    num_guests = request.args.get('num_guests')
    
    return render_template('booking.html', seat_id=seat_id, date=date, start_time=start_time, end_time=end_time, num_guests=num_guests)



@app.route('/book_seat', methods=['POST'])
def book_seat():
    print(request.form)
    table_id = int(request.form['seat_id']) 
    date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    num_guests = int(request.form['num_guests'])
    email = request.form['email']  


    cursor.execute(" INSERT INTO details (id, date,start,stop, guests, email) VALUES (%s, %s, %s, %s,%s,%s)",
    (table_id, date,start_time,end_time, num_guests, email))
    cnx.commit()
    with lock:
        success = booking_manager.book_seat(table_id, date, start_time, end_time, num_guests)
        if success:
            send_confirmation_email(email, table_id, date, start_time, end_time, num_guests)
            return redirect(url_for('payment_success'))
        else:
            return redirect(url_for('payment_failure'))
def send_confirmation_email(email, seat_id, date, start_time, end_time, num_guests):
    msg = Message('Booking Confirmation', sender='rohanjose00@gmail.com', recipients=[email])
    msg.body = f'''
    Dear Customer,

    Thank you for your booking!

    Here are your booking details:
    Seat ID: {seat_id}
    Date: {date}
    Start Time: {start_time}
    End Time: {end_time}
    Number of Guests: {num_guests}

    We look forward to serving you!

    Best Regards,
    Restaurant Team
    '''
    
    mail.send(msg)

@app.route('/payment_success')
def payment_success():
    return render_template('success.html')

@app.route('/payment_failure')
def payment_failure():
    return render_template('failure.html')



@app.route('/admin')
def admin_view():
    auth = request.authorization
    if not auth or auth.password != "12345":
        return Response(
            'Could not verify your login!', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

    # Once authenticated, show the admin view
    bookings_summary = booking_manager.get_bookings_summary()
    not_chosen_tables = booking_manager.get_not_chosen_tables()  
    return render_template('admin.html', bookings_summary=bookings_summary, not_chosen_tables=not_chosen_tables)


if __name__ == '__main__':
    app.run(debug=True)
