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


@app.route('/new_material')
def new_material():
    return render_template('new_material.html')


'''
                    Ledger Section starts....
'''


@app.route('/new_ledger_add', methods=['POST', 'GET'])
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
                    flag = 'Successfully Added Ledger - {} at {}'.format(ledger_name, date_time)
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


@app.route('/delete_ledger', methods=['POST', 'GET'])
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
                flag = "Successfully deleted - {} at - {}".format(ledger_id, datetime.now())
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
    if ledger_name == "" and comments == "":
        flash('Invalid Data. Please try again.')
        return redirect(url_for('alter_ledger_db'))
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                if comments and ledger_id:
                    del_items = 'UPDATE ledger SET comments="%s" WHERE id=%s' % (comments, ledger_id)
                elif ledger_name and ledger_id:
                    del_items = 'UPDATE ledger SET ledger_name="%s" WHERE id=%s' % (ledger_name, ledger_id)
                else:
                    del_items = 'UPDATE ledger SET ledger_name="%s", comments="%s" WHERE id=%s' % (
                    ledger_name, comments, ledger_id)
                cursor.execute(del_items)
                connection.commit()
                connection.close()
                flag = "Successfully Updated - {} to - {} at {}".format(ledger_id, ledger_name, datetime.now())
                flash(flag)
                return redirect(url_for('alter_ledger_db'))
                # return render_template('delete_ledger.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


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


'''
        Material Section starts
'''


@app.route('/new_material_add', methods =['POST', 'GET'])
def new_material_add():
    date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    mac = utilities.get_mac()
    ip = utilities.get_ip()
    if request.method == 'POST':
        material_name = request.form['materialname']
        comments = request.form['matcomments']
        if material_name == "":
            flag = "Invalid Data"
            flash(flag)
            return redirect(url_for('new_material'))
        else:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                try:
                    sql = "INSERT INTO material(material_name,date_time,added_by,comments,ip_address,mac_id) VALUES (%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (material_name, date_time, 'SSP', comments, ip, mac))
                    connection.commit()
                    flag = 'Successfully Added Material - {} at {}' .format(material_name, date_time)
                    flash(flag)
                    return redirect(url_for('new_material'))
                except Exception as e:
                    flag = "Failure with %s" % e
                    flash(flag)
                    return redirect(url_for('new_material'))
                finally:
                    connection.close()


@app.route('/del_material_db')
def del_material_db():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                get_items = "SELECT id, material_name FROM material"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('delete_material.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/delete_material',  methods=['POST', 'GET'])
def delete_material():
    material_id = None
    connection = connect_to_db()
    if request.method == 'POST':
        material_id = request.form['materials']
        if material_id == "":
            flag = "Invalid Data"
            flash(flag)
            return redirect(url_for('del_material_db'))
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                del_items = "DELETE FROM material WHERE id=%s"
                cursor.execute(del_items, material_id)
                connection.commit()
                connection.close()
                flag = "Successfully deleted - {} at - {}" .format(material_id, datetime.now())
                flash(flag)
                return redirect(url_for('del_material_db'))
                # return render_template('delete_ledger.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/alter_material', methods=['POST', 'GET'])
def alter_material():
    material_name = None
    material_id = None
    mat_comments = None
    connection = connect_to_db()
    if request.method == 'POST':
        material_id = request.form['materials_list']
        material_name = request.form['new_name']
        mat_comments = request.form['new_comments']
    if material_name == "" and mat_comments == "":
        flash('Invalid Data. Please try again.')
        return redirect(url_for('alter_material_db'))
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                if mat_comments and material_id:
                    del_items = 'UPDATE material SET comments="%s" WHERE id=%s' % (mat_comments, material_id)
                elif material_name and material_id:
                    del_items = 'UPDATE material SET material_name="%s" WHERE id=%s' % (material_name, material_id)
                else:
                    del_items = 'UPDATE material SET material_name="%s", comments="%s" WHERE id=%s' % (material_name, mat_comments, material_id)
                cursor.execute(del_items)
                connection.commit()
                connection.close()
                flag = "Successfully Updated - {} to - {} at {}".format(material_id, material_name, datetime.now())
                flash(flag)
                return redirect(url_for('alter_material_db'))
                # return render_template('delete_ledger.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/alter_material_db')
def alter_material_db():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                get_items = "SELECT id, material_name, comments FROM material"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('alter_material.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/view_material_db')
def view_material_db():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate material names from table
        try:
            with connection.cursor() as cursor:
                get_items = "SELECT id, material_name, date_time, added_by, comments FROM material"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('view_material.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


'''
            General Section starts
'''


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

'''
        Purchase section starts
'''


# @app.route('/new_purchased')
# def new_purchased():
#     return render_template('new_purchased.html')

@app.route('/new_purchased_db')
def new_purchased_db():
    cursor = None
    connection = None
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_items = "SELECT id,ledger_name FROM ledger"
            cursor.execute(get_items)
            ledger_data = cursor.fetchall()
        with connection.cursor() as cursor:
            get_materials = "SELECT id,material_name FROM material"
            cursor.execute(get_materials)
            material_data = cursor.fetchall()
            return render_template('new_purchased.html', ledger_data=ledger_data, material_data=material_data)
    except Exception as e:
        return 'Exception'
    finally:
        cursor.close()
        connection.close()


@app.route('/new_purchased', methods =['POST', 'GET'])
def new_purchased():
    date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    mac = utilities.get_mac()
    ip = utilities.get_ip()
    if request.method == 'POST':
        ledger_id = int(request.form['ledgers_dat'])
        pdate = request.form['pdate']
        qtykg = int(request.form['qtykg'])
        totamt = int(request.form['totamt'])
        recamt = int(request.form['recamt'])
        material = int(request.form['materials_dat'])
        piece = int(request.form['piece'])

        if pdate == "" or qtykg == "" or totamt == "" or recamt == "" or piece == "":
            flag = "Invalid Data"
            flash(flag)
            return redirect(url_for('new_purchased_db'))
        else:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                try:
                    sql = "INSERT INTO purchased(purchased_date,ledger_id,quantity_KG,total_amount," \
                          "receive_amount,no_of_piece, material_id, added_by,ip_address,mac_id) " \
                          "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (pdate, ledger_id, qtykg, totamt, recamt, piece, material, 'SSP', ip, mac))
                    connection.commit()
                    get_material_purchased = "SELECT id FROM material_qty WHERE material_id=%s"
                    cursor.execute(get_material_purchased, material)
                    data = cursor.fetchone()
                    if data is None:
                        sql_quantity = "INSERT INTO material_qty(material_id,quantity) VALUES(%s,%s)"
                        cursor.execute(sql_quantity, (material, piece))
                        connection.commit()
                    else:
                        sql_quantity = "UPDATE material_qty SET quantity = quantity + %s WHERE material_id=%s and id=%s"
                        cursor.execute(sql_quantity, (piece, material, str(data['id'])))
                        connection.commit()
                    flag = 'Successfully Added the Purchased data on {}' .format(date_time)
                    flash(flag)
                    return redirect(url_for('new_purchased_db'))
                except Exception as e:
                    flag = "Failure with %s" % e
                    flash(flag)
                    return redirect(url_for('new_purchased_db'))
                finally:
                    connection.close()


@app.route('/view_purchased_db')
def view_purchased_db():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate material names from table
        try:
            with connection.cursor() as cursor:
                get_items = "SELECT purchased_id, purchased_date, l.ledger_name, quantity_KG, total_amount, receive_amount, no_of_piece, m.material_name, p.added_by  FROM purchased p INNER JOIN ledger l ON p.ledger_id = l.id INNER JOIN material m ON p.material_id = m.id"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('view_purchased.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/delete_purchased_db')
def delete_purchased_db():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate material names from table
        try:
            with connection.cursor() as cursor:
                get_items = "SELECT purchased_id, purchased_date, l.ledger_name, quantity_KG, total_amount, receive_amount, no_of_piece, m.material_name, p.added_by  FROM purchased p INNER JOIN ledger l ON p.ledger_id = l.id INNER JOIN material m ON p.material_id = m.id"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('delete_purchased.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


@app.route('/del_purchased_data/<int:p_id>')
def del_purchased_data(p_id):
    connection = connect_to_db()
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                get_material_qty = "SELECT material_id, no_of_piece FROM purchased WHERE purchased_id=%s"
                cursor.execute(get_material_qty, p_id)
                data = cursor.fetchone()
                qty = data['no_of_piece']
                mat_id = data['material_id']
                sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE material_id=%s"
                cursor.execute(sql_quantity, (qty, mat_id))
                connection.commit()
                del_items = "DELETE FROM purchased WHERE purchased_id=%s"
                cursor.execute(del_items, p_id)
                connection.commit()
                connection.close()
                return redirect(url_for('delete_purchased_db'))
        except Exception as e:
            return 'Exception'


@app.route('/show_material_inventory')
def show_material_inventory():
    connection = connect_to_db()
    if connection.open == 1:
        # Populate material names from table
        try:
            with connection.cursor() as cursor:
                get_items = "select m.material_name, q.quantity from material_qty q INNER JOIN material m ON q.material_id = m.id;"
                cursor.execute(get_items)
                items_data = cursor.fetchall()
                connection.close()
                return render_template('show_material_inventory.html', items_data=items_data)
        except Exception as e:
            return 'Exception'


if __name__ == '__main__':
    app.run(debug=True)