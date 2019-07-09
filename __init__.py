from flask import Flask, render_template,redirect, url_for, request, flash
import pymysql.cursors
from datetime import datetime
import utilities
app = Flask(__name__)
app.secret_key = 'dont tell me again'


def connect_to_db():
    conn = pymysql.connect(host='localhost', user='root', password='root123', db='erp_web', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    return conn


@app.route('/index')
@app.route('/')
def default():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('blank.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/new_ledger')
def new_ledger():
    return render_template('new_ledger.html')


@app.route('/new_ledger_add', methods =['POST', 'GET'])
def new_ledger_add():
    date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    mac = utilities.get_mac()
    ip = utilities.get_ip()
    if request.method == 'POST':
        ledger_name = request.form['ledgername']
        comments = request.form['comments']
        if ledger_name == "":
            flag = "Invalid Data"
            flash(flag)
            return redirect(url_for('new_ledger'))
        else:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                try:
                    sql = "INSERT INTO ledger(ledger_name,date_time,added_by,comments,ip_address,mac_id) VALUES (%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (ledger_name, date_time, 'SSP', comments, ip, mac))
                    connection.commit()
                    flag = 'Successfully Added Ledger - {} at {}' .format(ledger_name, date_time)
                    flash(flag)
                    return redirect(url_for('new_ledger'))
                except Exception as e:
                    flag = "Failure with %s" % e
                    flash(flag)
                    return redirect(url_for('new_ledger'))
                finally:
                    connection.close()


@app.route('/del_ledger_db')
def del_ledger_db():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                get_items = "SELECT id, ledger_name FROM ledger"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('delete_ledger.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/delete_ledger',  methods=['POST', 'GET'])
def delete_ledger():
    ledger_id = None
    connection = connect_to_db()
    if request.method == 'POST':
        ledger_id = request.form['ledgers']
        if ledger_id == "":
            flag = "Invalid Data"
            flash(flag)
            return redirect(url_for('del_ledger_db'))
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                del_items = "DELETE FROM ledger WHERE id=%s"
                cursor.execute(del_items, ledger_id)
                connection.commit()
                connection.close()
                flag = "Successfully deleted - {} at - {}" .format(ledger_id, datetime.now())
                flash(flag)
                return redirect(url_for('del_ledger_db'))
                # return render_template('delete_ledger.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/alter_ledger_db')
def alter_ledger_db():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                get_items = "SELECT id, ledger_name, comments FROM ledger"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('alter_ledger.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/alter_ledger', methods=['POST', 'GET'])
def alter_ledger():
    ledger_name = None
    ledger_id = None
    comments = None
    connection = connect_to_db()
    if request.method == 'POST':
        ledger_id = request.form['ledgers_list']
        ledger_name = request.form['new_name']
        comments = request.form['new_comments']
        # if ledger_name == "" or ledger_id == "":
        #     flag = "Invalid Data"
        #     flash(flag)
        #     return redirect(url_for('alter_ledger_db'))
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                if comments and ledger_id:
                    del_items = 'UPDATE ledger SET comments="%s" WHERE id=%s' % (comments, ledger_id)
                elif ledger_name and ledger_id:
                    del_items = 'UPDATE ledger SET ledger_name="%s" WHERE id=%s' % (ledger_name, ledger_id)
                else:
                    del_items = 'UPDATE ledger SET ledger_name="%s", comments="%s" WHERE id=%s' % (ledger_name, comments, ledger_id)
                cursor.execute(del_items)
                connection.commit()
                connection.close()
                flag = "Successfully Updated - {} to - {} at {}".format(ledger_id, ledger_name, datetime.now())
                flash(flag)
                return redirect(url_for('alter_ledger_db'))
                # return render_template('delete_ledger.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


# @app.route('/view_ledger')
# def view_ledger():
#     return render_template('view_ledger.html')

@app.route('/view_ledger_db')
def view_ledger_db():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                get_items = "SELECT id, ledger_name, date_time, added_by, comments FROM ledger"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('view_ledger.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/authenticate_login', methods=['POST', 'GET'])
def authenticate_login():
    error = None
    if request.method == 'POST':
        id = request.form['username']
        password = request.form['password']
        if id == 'Admin@ssp.com' and password == 'Pass':
            flash('Successfully logged in')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials. Please try again.')
            error = 'Invalid Credentials'
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)