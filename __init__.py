from flask import Flask, render_template,redirect, url_for, request, flash, session
import pymysql.cursors
from datetime import datetime
import utilities
import collections
import ast
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        return render_template('blank.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/new_ledger')
def new_ledger():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        return render_template('new_ledger.html')


@app.route('/new_material')
def new_material():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        return render_template('new_material.html')


'''
                    Ledger Section starts....
'''


@app.route('/new_ledger_add', methods=['POST', 'GET'])
def new_ledger_add():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
                        cursor.execute(sql, (ledger_name, date_time, str(session['username']), comments, ip, mac))
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
                        cursor.execute(sql, (material_name, date_time, str(session['username']), comments, ip, mac))
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
            # flash('Successfully logged in')
            session['username'] = id.split('@')[0]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials. Please try again.')
            error = 'Invalid Credentials'
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


'''
        Purchase section starts
'''


# @app.route('/new_purchased')
# def new_purchased():
#     return render_template('new_purchased.html')

@app.route('/new_purchased_db')
def new_purchased_db():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
                        cursor.execute(sql, (pdate, ledger_id, qtykg, totamt, recamt, piece, material, str(session['username']), ip, mac))
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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

'''
 New Buildout starts here
'''


@app.route('/new_buildout')
def new_buildout():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT id, material_name, comments FROM material"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('new_buildout.html', items_data=items_data)
            except Exception as e:
                return 'Exception'


@app.route('/new_buildout_add', methods=['POST', 'GET'])
def new_buildout_add():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        mac = utilities.get_mac()
        ip = utilities.get_ip()
        if request.method == 'POST':
            product_name = request.form['pname']
            product_rate = request.form['prate']
            product_comments = request.form['pcomments']
            product_color = request.form['pcolor']
            product_date = request.form['pdate']
            product_qty = request.form['pqty']

            item1_combo = int(request.form['item_cm1'])
            item2_combo = int(request.form['item_cm2'])
            item3_combo = int(request.form['item_cm3'])
            item4_combo = int(request.form['item_cm4'])
            item5_combo = int(request.form['item_cm5'])
            item6_combo = int(request.form['item_cm6'])
            item7_combo = int(request.form['item_cm7'])
            item8_combo = int(request.form['item_cm8'])

            item1 = int(request.form['item1'])
            item2 = int(request.form['item2'])
            item3 = int(request.form['item3'])
            item4 = int(request.form['item4'])
            item5 = int(request.form['item5'])
            item6 = int(request.form['item6'])
            item7 = int(request.form['item7'])
            item8 = int(request.form['item8'])
            if item1==0 or item2==0: #  or item3==0 or item4==0 or item5==0 or item6==0 or item7==0 or item8==0:
                flag = "Items missing ..."
                flash(flag)
                return redirect(url_for('new_buildout'))
            else:
                data = dict()
                list_handler = list()
                if product_name == "" or product_color == "" or product_qty == "" or product_rate == "" or product_comments == "" or product_date == "":
                    flag = "Invalid Data"
                    flash(flag)
                    return redirect(url_for('new_buildout'))
                if item1 > 0 and item1_combo !=0:
                    list_handler.append(item1_combo)
                if item2 > 0 and item2_combo !=0:
                    list_handler.append(item2_combo)
                if item3 > 0 and item3_combo !=0:
                    list_handler.append(item3_combo)
                if item4 > 0 and item4_combo !=0:
                    list_handler.append(item4_combo)
                if item5 > 0 and item5_combo !=0:
                    list_handler.append(item5_combo)
                if item6 > 0 and item6_combo !=0:
                    list_handler.append(item6_combo)
                if item7 > 0 and item7_combo !=0:
                    list_handler.append(item7_combo)
                if item8 > 0 and item8_combo !=0:
                    list_handler.append(item8_combo)
                else:
                    pass
                dupes = [item for item, count in collections.Counter(list_handler).items() if count > 1]
                if any(dupes):
                    sum_of_dupes = ''
                    counter = 0
                    try:
                        connection = connect_to_db()
                        with connection.cursor() as cursor:
                            for i in dupes:
                                get_material_purchased = "SELECT material_name FROM material WHERE id = %s"
                                cursor.execute(get_material_purchased, int(i))
                                data = cursor.fetchone()
                                if counter == 0:
                                    sum_of_dupes = data['material_name']
                                else:
                                    sum_of_dupes = sum_of_dupes + " and " + data['material_name']
                                counter += 1
                        flash('Duplicate material - %s' %(sum_of_dupes))
                        connection.close()
                    except Exception as e:
                        flash('Exception %s' %(e))
                        redirect(url_for('new_buildout'))
                    return redirect(url_for('new_buildout'))
                else:
                    concat_errors = ''
                    counter = 0
                    list_of_ofs_items = list()
                    connection = connect_to_db()
                    with connection.cursor() as cursor:
                        try:
                            for i in range(1,9):
                                exec('data[item{}_combo] = item{}'.format(str(i), str(i)))
                            print(data)
                            del data[0]
                            all_keys = data.keys()
                            for item in all_keys:
                                check_material = "SELECT quantity FROM material_qty WHERE material_id=%s"
                                cursor.execute(check_material, item)
                                data_checked = cursor.fetchone()
                                if int(data_checked['quantity']) <= int(data[item]):
                                    get_material_purchased = "SELECT material_name FROM material WHERE id = %s"
                                    cursor.execute(get_material_purchased, item)
                                    get_data = cursor.fetchone()
                                    list_of_ofs_items.append(get_data['material_name'])
                                else:

                                    sql = "INSERT INTO product(product_name,date_time,added_by,comments," \
                                          "product_color,build_date, product_spec, product_rate,ip_address,mac_id) " \
                                          "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                    cursor.execute(sql,
                                                   (product_name, date_time, str(session['username']), product_comments,
                                                    product_color, product_date, str(data), product_rate, ip, mac))
                                    connection.commit()
                                    get_product_data = "SELECT quantity FROM product_qty WHERE product_name=%s AND product_color=%s"
                                    cursor.execute(get_product_data, (product_name, product_color))
                                    product_data = cursor.fetchone()
                                    if product_data is None:
                                        sql_quantity = "INSERT INTO product_qty(product_name, product_color, quantity) VALUES(%s,%s,%s)"
                                        cursor.execute(sql_quantity, (product_name, product_color, product_qty))
                                        connection.commit()
                                    else:
                                        sql_quantity = "UPDATE product_qty SET quantity = quantity + %s WHERE product_name=%s AND product_color=%s"
                                        cursor.execute(sql_quantity, (product_qty, product_name, product_color))
                                        connection.commit()
                                    for item in all_keys:
                                        print(item)
                                        sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE material_id=%s"
                                        cursor.execute(sql_quantity, (data[item], item))
                                        connection.commit()
                                    flag = 'Successfully Added the new product {}'.format(product_name)
                                    flash(flag)
                                    return redirect(url_for('new_buildout'))
                        except Exception as e:
                            flag = "Failure with %s" % e
                            flash(flag)
                            return redirect(url_for('new_buildout'))
                        finally:
                            connection.close()
                        if any(list_of_ofs_items):
                            flag = "Insufficient Materials - %s " % str(list_of_ofs_items)
                            flash(flag)
                            return redirect(url_for('new_buildout'))


@app.route('/view_product_details')
def view_product_details():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_product_data = "SELECT id, product_name,comments,product_color,build_date,added_by,product_rate,product_spec FROM product"
            cursor.execute(get_product_data)
            data = cursor.fetchall()
            temp = data
            for i in range(0,len(data)):
                a = ast.literal_eval(data[i]['product_spec'])
                b = a
                all_keys = a.keys()
                tempo = dict()
                for j in all_keys:
                    get_material = "SELECT material_name FROM material WHERE id=%s"
                    cursor.execute(get_material, j)
                    material_name = cursor.fetchone()
                    name = material_name['material_name']
                    tempo[j] = name
                print(tempo)
                c = {tempo[key]: value for key, value in a.items()}
                # print(c)
                temp[i]['product_spec'] = c
            # print(temp)
            return render_template('show_product_details.html', items_data=temp)
    except Exception as e:
        return 'Exception'



if __name__ == '__main__':
    app.run(debug=True)