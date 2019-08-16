from flask import Flask, render_template,redirect, url_for, request, flash, session, jsonify,send_from_directory
import pymysql.cursors
from datetime import datetime
import utilities
from collections import Counter
import ast
import csv
import os
import json
app = Flask(__name__)
app.secret_key = 'dot tell me again'

current_dir = str(os.getcwd())
app.config['UPLOAD_FOLDER'] = ''


def connect_to_db():
    if '127' in request.url:
        conn = pymysql.connect(host='localhost', user='root', password='root123', db='erp_web', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    else:
        conn = pymysql.connect(host='App01.mysql.pythonanywhere-services.com', user='App01', password='Data2019', db='App01$erp_web', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
    return conn


def product_manipulation(dict_product, amount):
    for i in dict_product:
        product = int(dict_product[i]) * int(amount)
        dict_product[i] = product
    return dict_product


def convertid2name(data):
    dict_data = ast.literal_eval(data)
    connection = connect_to_db()
    new_dict = dict_data.copy()
    try:
        with connection.cursor() as cursor:
            for i in list(dict_data.keys()):
                get_items = "SELECT material_name FROM material WHERE id=%s"
                cursor.execute(get_items, i)
                items_data = cursor.fetchone()
                new_dict[i] = items_data['material_name']
            new_dict2 = dict((new_dict[key], value) for (key, value) in dict_data.items())
            return new_dict2
    except Exception as e:
        return str(e)
    finally:
        connection.close()


@app.route('/index')
@app.route('/')
def default():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        url = request.url
        session['url'] = url
        if '127' in session.get('url'):
            app.config['UPLOAD_FOLDER'] = current_dir + '/out/'
        else:
            app.config['UPLOAD_FOLDER'] = current_dir + '/erp_web/out/'
        return render_template('blank.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/create_ledger')
def create_ledger():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        return render_template('new_ledger.html')


@app.route('/create_material')
def create_material():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate units from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT id, unit FROM units"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('new_material.html', items_data=items_data)
            except Exception as e:
                return str(e)


'''
                    Ledger Section starts....
'''


@app.route('/ledger_creation', methods=['POST', 'GET'])
def ledger_creation():
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
                return redirect(url_for('create_ledger'))
            else:
                connection = connect_to_db()
                with connection.cursor() as cursor:
                    try:
                        sql = "INSERT INTO ledger(ledger_name,date_time,added_by,comments,ip_address,mac_id) VALUES (%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, (ledger_name, date_time, str(session['username']), comments, ip, mac))
                        connection.commit()
                        flag = 'Successfully Added Ledger - {} at {}'.format(ledger_name, date_time)
                        flash(flag)
                        return redirect(url_for('create_ledger'))
                    except Exception as e:
                        flag = "Failure with %s" % e
                        flash(flag)
                        return redirect(url_for('create_ledger'))
                    finally:
                        connection.close()


@app.route('/delete_ledger')
def delete_ledger():
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
                    return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                return 'Exception'
            finally:
                connection.close()


@app.route('/ledger_deletion', methods=['POST', 'GET'])
def ledger_deletion():
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
                return redirect(url_for('delete_ledger'))
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    del_items = "DELETE FROM ledger WHERE ledger_name=%s"
                    cursor.execute(del_items, ledger_id)
                    connection.commit()
                    connection.close()
                    flag = "Successfully deleted - {} at - {}".format(ledger_id, datetime.now())
                    flash(flag)
                    return redirect(url_for('delete_ledger'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                return 'Exception'


@app.route('/modify_ledger')
def modify_ledger():
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


@app.route('/ledger_modification', methods=['POST', 'GET'])
def ledger_modification():
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
            return redirect(url_for('modify_ledger'))
        if connection.open == 1:
            # Populate ledger names from table
            if ledger_id == "0":
                flash("Please select Ledger")
                return redirect(url_for('modify_ledger'))
            try:
                with connection.cursor() as cursor:
                    if comments and ledger_id and ledger_name:
                        del_items = 'UPDATE ledger SET ledger_name="%s", comments="%s" WHERE id=%s' % (
                            ledger_name, comments, ledger_id)
                    elif ledger_name and ledger_id:
                        del_items = 'UPDATE ledger SET ledger_name="%s" WHERE id=%s' % (ledger_name, ledger_id)
                    else:
                        del_items = 'UPDATE ledger SET comments="%s" WHERE id=%s' % (comments, ledger_id)
                    cursor.execute(del_items)
                    connection.commit()
                    connection.close()
                    flag = "Successfully Updated - {} to - {} at {}".format(ledger_id, ledger_name, datetime.now())
                    flash(flag)
                    return redirect(url_for('modify_ledger'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                return 'Exception'


@app.route('/view_ledger')
def view_ledger():
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


@app.route('/material_creation', methods=['POST'])
def material_creation():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        mac = utilities.get_mac()
        ip = utilities.get_ip()
        if request.method == 'POST':
            material_name = request.form['materialname']
            unit = request.form['units']
            subunit = request.form['sub_units']
            comments = request.form['matcomments']
            if material_name == "":
                flag = "Please provide Material Name.."
                flash(flag)
                return redirect(url_for('create_material'))
            elif unit == "0"  or subunit == "0":
                flag = "Please provide Unit and Subunit.."
                flash(flag)
                return redirect(url_for('create_material'))
            else:
                with connection.cursor() as cursor:
                    try:
                        sql = "INSERT INTO material(material_name,unit,sub_unit,usage_flag,date_time,added_by,comments,ip_address,mac_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, (material_name, unit, subunit, '0', date_time, str(session['username']), comments, ip, mac))
                        connection.commit()
                        flag = 'Successfully Added Material - {} at {}' .format(material_name, date_time)
                        flash(flag)
                        return redirect(url_for('create_material'))
                    except Exception as e:
                        flag = "Failure with %s" % e
                        flash(flag)
                        return redirect(url_for('create_material'))
                    finally:
                        connection.close()


@app.route('/delete_material')
def delete_material():
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


@app.route('/material_deletion',  methods=['POST'])
def material_deletion():
    """
    Delete a Material
    :return: Success for Deletion and Failed for errors
    """
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        material_name = None
        connection = connect_to_db()
        if request.method == 'POST':
            material_name = request.form['materials']
            if material_name == "":
                flag = "Invalid Data"
                flash(flag)
                return redirect(url_for('delete_material'))
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    del_items = "DELETE FROM material WHERE material_name=%s AND usage_flag < 1"
                    cursor.execute(del_items, material_name)
                    connection.commit()
                    if connection.affected_rows() > 0:
                        flag = "Successfully deleted - {} at - {}" .format(material_name, datetime.now())
                    else:
                        flag = "Failed to delete - {} as it is linked to a Product in Component Master".format(material_name)
                    flash(flag)
                    return redirect(url_for('delete_material'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                return str(e)
            finally:
                connection.close()


@app.route('/material_modification', methods=['POST', 'GET'])
def material_modification():
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
            unit_list = request.form['unit_list']
            sub_unit_list = request.form['sub_unit_list']
        if material_name == "" and mat_comments == "":
            flash('Invalid Data. Please try again.')
            return redirect(url_for('modify_material'))
        elif unit_list == "0" or sub_unit_list == "0":
            flash('Please select the unit or sub-unit')
            return redirect(url_for('modify_material'))
        else:
            try:
                with connection.cursor() as cursor:
                    select_item = 'SELECT material_name FROM material WHERE id=%s'
                    cursor.execute(select_item, material_id)
                    item = cursor.fetchone()
                    if mat_comments and material_id and material_name == "":
                        upd_items = 'UPDATE material SET comments="%s",unit="%s", sub_unit="%s" WHERE id=%s' % (mat_comments,unit_list, sub_unit_list, material_id)
                    elif material_name and material_id:
                        upd_items = 'UPDATE material SET material_name="%s",unit="%s", sub_unit="%s" WHERE id=%s' % (material_name, unit_list, sub_unit_list, material_id)
                    else:
                        upd_items = 'UPDATE material SET material_name="%s", comments="%s", unit="%s", sub_unit="%s" WHERE id=%s' % (material_name, unit_list, sub_unit_list, mat_comments, material_id)
                    cursor.execute(upd_items)
                    connection.commit()
                    flag = "Successfully Updated - {} to {} at {}".format(item['material_name'], material_name, datetime.now())
                    flash(flag)
                    return redirect(url_for('modify_material'))
            except Exception as e:
                return str(e)
            finally:
                connection.close()


@app.route('/modify_material')
def modify_material():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_units = "SELECT unit FROM units"
                    cursor.execute(get_units)
                    units_data = cursor.fetchall()
                    get_items = "SELECT id, material_name, comments FROM material"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('alter_material.html', items_data=items_data, units_data=units_data)
            except Exception as e:
                return str(e)


@app.route('/view_material')
def view_material():
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
            return str(e)
        finally:
            cursor.close()
            connection.close()


@app.route('/alter_purchased_db')
def alter_purchased_db():
    connection = ''
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        try:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                get_items = "SELECT purchased_id from purchased"
                cursor.execute(get_items)
                items_pur_data = cursor.fetchall()
            with connection.cursor() as cursor:
                get_items = "SELECT id, ledger_name from ledger"
                cursor.execute(get_items)
                items_ledger_data = cursor.fetchall()
            with connection.cursor() as cursor:
                get_items = "SELECT id,material_name from material"
                cursor.execute(get_items)
                items_material_data = cursor.fetchall()
            return render_template('alter_purchased.html', purchase_data=items_pur_data, ledger_data=items_ledger_data, material_data=items_material_data)
        except Exception as e:
            return str(e)
        finally:
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
            qty_unit = int(request.form['qtykg'])
            unit = request.form['unit']
            subunit = request.form['subunit']
            material = request.form['materials_dat']
            qty_sub_unit = int(request.form['piece'])
            totamt = int(request.form['totamt']) if request.form['totamt'] != "" else 0
            rate = int(request.form['recamt']) if request.form['recamt'] != "" else 0


            if qty_unit == "" or pdate == "" or material == "" or qty_sub_unit == "":
                flag = "Invalid Data"
                flash(flag)
                return redirect(url_for('new_purchased_db'))
            else:
                connection = connect_to_db()
                with connection.cursor() as cursor:
                    try:
                        amount = -totamt
                        sql = "INSERT INTO purchased(purchased_date,ledger_id,unit,sub_unit," \
                              "quantity_unit, quantity_sub_unit,rate, total_amount, material_id, added_by,ip_address,mac_id) " \
                              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, (pdate, ledger_id, unit, subunit, qty_unit, qty_sub_unit, rate, totamt,
                                             material, str(session['username']), ip, mac))
                        connection.commit()
                        insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id, amount,comments) VALUES (%s, %s,%s,NULL,%s,'Money Spent on Raw Material Purchase')"
                        cursor.execute(insert_sql, (date_time, ledger_id, material, amount))
                        connection.commit()
                        get_material_purchased = "SELECT id FROM material_qty WHERE material_id=%s"
                        cursor.execute(get_material_purchased, material)
                        data = cursor.fetchone()
                        get_material_cdate = "SELECT closing_balance FROM material_movement WHERE txn_date = (SELECT MAX(txn_date) FROM material_movement WHERE mat_id=%s);"
                        cursor.execute(get_material_cdate, material)
                        cdate = cursor.fetchone()
                        if data is None:
                            sql_mat_mov = "INSERT INTO material_movement(mat_id,txn_date,opening_balance,closing_balance,txn_type) VALUES(%s,%s,%s,%s,%s)"
                            cursor.execute(sql_mat_mov, (material, date_time,"0",qty_sub_unit,'Purchase'))
                            sql_quantity = "INSERT INTO material_qty(material_id,quantity) VALUES(%s,%s)"
                            cursor.execute(sql_quantity, (material, qty_sub_unit))
                            connection.commit()
                        else:
                            final_closing = int(cdate['closing_balance']) + int(qty_sub_unit)
                            sql_quantity = "UPDATE material_qty SET quantity = quantity + %s WHERE material_id=%s and id=%s"
                            cursor.execute(sql_quantity, (qty_sub_unit, material, str(data['id'])))
                            sql_mat_mov = "INSERT INTO material_movement(mat_id,txn_date,opening_balance,closing_balance,txn_type) VALUES(%s,%s,%s,%s,%s)"
                            cursor.execute(sql_mat_mov, (material, date_time, cdate['closing_balance'], final_closing, 'Purchase'))
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
                    get_items = "SELECT purchased_id, purchased_date, l.ledger_name, quantity_unit, p.unit, p.sub_unit, total_amount, rate, quantity_sub_unit, m.material_name  FROM purchased p INNER JOIN ledger l ON p.ledger_id = l.id INNER JOIN material m ON p.material_id = m.id"
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
                    get_items = "SELECT purchased_id, purchased_date, l.ledger_name, quantity_unit, total_amount, quantity_sub_unit, m.material_name, p.added_by  FROM purchased p INNER JOIN ledger l ON p.ledger_id = l.id INNER JOIN material m ON p.material_id = m.id"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('delete_purchased.html', items_data=items_data)
            except Exception as e:
                return str(e)


@app.route('/del_purchased_data/<int:p_id>')
def del_purchased_data(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_material_qty = "SELECT material_id, quantity_sub_unit, total_amount,ledger_id FROM purchased WHERE purchased_id=%s"
                    cursor.execute(get_material_qty, p_id)
                    data = cursor.fetchone()
                    qty = data['quantity_sub_unit']
                    mat_id = data['material_id']
                    sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE material_id=%s"
                    cursor.execute(sql_quantity, (qty, mat_id))
                    connection.commit()
                    insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id, amount,comments) VALUES (%s, %s,%s,NULL,%s,'Money Received as Refund')"
                    cursor.execute(insert_sql, (date_time, data['ledger_id'], data['material_id'], data['total_amount']))
                    connection.commit()
                    del_items = "DELETE FROM purchased WHERE purchased_id=%s"
                    cursor.execute(del_items, p_id)
                    connection.commit()
                    connection.close()
                    return redirect(url_for('delete_purchased_db'))
            except Exception as e:
                return str(e)


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


# @app.route('/manufacture_process')
# def manufacture_process():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         connection = connect_to_db()
#         if connection.open == 1:
#             # Populate ledger names from table
#             try:
#                 with connection.cursor() as cursor:
#                     get_items = "SELECT id, product_name, comments FROM product"
#                     cursor.execute(get_items)
#                     items_data = cursor.fetchall()
#                     connection.close()
#                     return render_template('manufacture_process.html', items_data=items_data)
#             except Exception as e:
#                 return str(e)


@app.route('/component_master')
def component_master():
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
                    return render_template('component_master.html', items_data=items_data)
            except Exception as e:
                return str(e)


@app.route('/component_master_creation', methods=['POST'])
def component_master_creation():
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
            product_color = ''
            # product_date = request.form['pdate']
            product_qty = '0'

            item1_combo = int(request.form['item_text1'])
            item2_combo = int(request.form['item_text2'])
            item3_combo = int(request.form['item_text3'])
            item4_combo = int(request.form['item_text4'])
            item5_combo = int(request.form['item_text5'])
            item6_combo = int(request.form['item_text6'])
            item7_combo = int(request.form['item_text7'])
            item8_combo = int(request.form['item_text8'])
            item9_combo = int(request.form['item_text9'])
            item10_combo = int(request.form['item_text10'])

            item1 = int(request.form['item1'])
            item2 = int(request.form['item2'])
            item3 = int(request.form['item3'])
            item4 = int(request.form['item4'])
            item5 = int(request.form['item5'])
            item6 = int(request.form['item6'])
            item7 = int(request.form['item7'])
            item8 = int(request.form['item8'])
            item9 = int(request.form['item9'])
            item10 = int(request.form['item10'])
            # if item1 == 0 or item2 == 0: #  or item3==0 or item4==0 or item5==0 or item6==0 or item7==0 or item8==0:
            #     flag = "Minimum 2 Item's quantity is expected ..."
            #     flash(flag)
            #     return redirect(url_for('component_master'))
            if item1 == 0 and item2 == 0 and item3 == 0 and item4 == 0 and item5 == 0 and item6 == 0 and item7 == 0 \
                    and item8 == 0 and item9 == 0 and item10 == 0:
                flag = "Minimum 1 Item's quantity is expected ..."
                flash(flag)
                return redirect(url_for('component_master'))
            else:
                data = dict()
                list_handler = list()
                if product_name == "":
                    flag = "Product Name is expected."
                    flash(flag)
                    return redirect(url_for('component_master'))
                if item1 > 0 and item1_combo != 0:
                    list_handler.append(item1_combo)
                if item2 > 0 and item2_combo != 0:
                    list_handler.append(item2_combo)
                if item3 > 0 and item3_combo != 0:
                    list_handler.append(item3_combo)
                if item4 > 0 and item4_combo != 0:
                    list_handler.append(item4_combo)
                if item5 > 0 and item5_combo != 0:
                    list_handler.append(item5_combo)
                if item6 > 0 and item6_combo != 0:
                    list_handler.append(item6_combo)
                if item7 > 0 and item7_combo != 0:
                    list_handler.append(item7_combo)
                if item8 > 0 and item8_combo != 0:
                    list_handler.append(item8_combo)
                if item9 > 0 and item9_combo != 0:
                    list_handler.append(item9_combo)
                if item10 > 0 and item10_combo != 0:
                    list_handler.append(item10_combo)
                else:
                    pass
                dupes = [item for item, count in Counter(list_handler).items() if count > 1]
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
                        flash('You have provided duplicate item names - %s' % sum_of_dupes)
                        connection.close()
                    except Exception as e:
                        flash('Exception %s' % e)
                        redirect(url_for('component_master'))
                    return redirect(url_for('component_master'))
                else:
                    # list_of_ofs_items = list()
                    connection = connect_to_db()
                    with connection.cursor() as cursor:
                        try:
                            for i in range(1,9):
                                exec('data[item{}_combo] = item{}'.format(str(i), str(i)))
                            # print(data)
                            del data[0]
                            if not any(data):
                                flag = 'Items not provided'.format(product_name)
                                flash(flag)
                                return redirect(url_for('component_master'))
                            else:
                                sql = "INSERT INTO component_master(product_name,date_time,added_by,comments," \
                                      "product_spec,component_flag, product_rate,ip_address,mac_id) " \
                                      "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                cursor.execute(sql,
                                               (product_name, date_time, str(session['username']), product_comments,
                                                str(data), 'Y', product_rate, ip, mac))
                                # sql_product_qty = "INSERT INTO product_qty(product_name,quantity) VALUES (%s,%s)"
                                # cursor.execute(sql_product_qty,
                                #                (product_name, product_qty))
                                # connection.commit()

                                item_diction = ast.literal_eval(str(data))
                                for key in item_diction:
                                    get_material_usage_flag = "SELECT usage_flag FROM material WHERE id = %s"
                                    cursor.execute(get_material_usage_flag, key)
                                    data = cursor.fetchone()
                                    usage_counter = int(data['usage_flag']) + 1
                                    upd_items = 'UPDATE material SET usage_flag=%s WHERE id=%s' % (usage_counter, key)
                                    cursor.execute(upd_items)
                                    connection.commit()
                                flag = 'Successfully added the new component {}'.format(product_name)
                                flash(flag)
                                return redirect(url_for('component_master'))
                        except Exception as e:
                            flag = "Failure with %s" % e
                            flash(flag)
                            return redirect(url_for('component_master'))
                        finally:
                            connection.close()


# @app.route('/manufacture_process_creation', methods=['POST', 'GET'])
# def manufacture_process_creation():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
#         mac = utilities.get_mac()
#         ip = utilities.get_ip()
#         if request.method == 'POST':
#             product_name = request.form['pname']
#             product_rate = request.form['prate']
#             # product_color = request.form['pcolor']
#             # product_date = request.form['pdate']
#             product_qty = request.form['pqty']
#
#             item1_combo = request.form['item_cm1']
#             item2_combo = request.form['item_cm2']
#             item3_combo = request.form['item_cm3']
#             item4_combo = request.form['item_cm4']
#             item5_combo = request.form['item_cm5']
#             item6_combo = request.form['item_cm6']
#             item7_combo = request.form['item_cm7']
#             item8_combo = request.form['item_cm8']
#             item9_combo = request.form['item_cm9']
#             item10_combo = request.form['item_cm10']
#
#             item1 = int(request.form['item1'])
#             item2 = int(request.form['item2'])
#             item3 = int(request.form['item3'])
#             item4 = int(request.form['item4'])
#             item5 = int(request.form['item5'])
#             item6 = int(request.form['item6'])
#             item7 = int(request.form['item7'])
#             item8 = int(request.form['item8'])
#             item9 = int(request.form['item9'])
#             item10 = int(request.form['item10'])
#
#             data = dict()
#             list_handler = list()
#             if item1 > 0 and item1_combo != "":
#                 list_handler.append(item1_combo)
#             if item2 > 0 and item2_combo != "":
#                 list_handler.append(item2_combo)
#             if item3 > 0 and item3_combo != "":
#                 list_handler.append(item3_combo)
#             if item4 > 0 and item4_combo != "":
#                 list_handler.append(item4_combo)
#             if item5 > 0 and item5_combo != "":
#                 list_handler.append(item5_combo)
#             if item6 > 0 and item6_combo != "":
#                 list_handler.append(item6_combo)
#             if item7 > 0 and item7_combo != "":
#                 list_handler.append(item7_combo)
#             if item8 > 0 and item8_combo != "":
#                 list_handler.append(item8_combo)
#             if item9 > 0 and item9_combo != "":
#                 list_handler.append(item9_combo)
#             if item10 > 0 and item10_combo != "":
#                 list_handler.append(item10_combo)
#             else:
#                 pass
#             dupes = [item for item, count in Counter(list_handler).items() if count > 1]
#             if any(dupes):
#                 sum_of_dupes = ''
#                 counter = 0
#                 try:
#                     connection = connect_to_db()
#                     with connection.cursor() as cursor:
#                         for i in dupes:
#                             get_material_purchased = "SELECT material_name FROM material WHERE id = %s"
#                             cursor.execute(get_material_purchased, int(i))
#                             data = cursor.fetchone()
#                             if counter == 0:
#                                 sum_of_dupes = data['material_name']
#                             else:
#                                 sum_of_dupes = sum_of_dupes + " and " + data['material_name']
#                             counter += 1
#                     flash('Duplicate material - %s' % sum_of_dupes)
#                     connection.close()
#                 except Exception as e:
#                     flash('Exception %s' % e)
#                     redirect(url_for('manufacture_process'))
#                 return redirect(url_for('manufacture_process'))
#             else:
#                 list_of_ofs_items = list()
#                 connection = connect_to_db()
#                 with connection.cursor() as cursor:
#                     try:
#                         for i in range(1, 9):
#                             exec('data[item{}_combo] = item{}'.format(str(i), str(i)))
#                         print(data)
#                         new = {k: v for k, v in data.items() if v}
#                         data = new
#                         all_keys = data.keys()
#                         sql_quantity = "UPDATE product_qty SET quantity = quantity + %s WHERE product_name=%s"
#                         cursor.execute(sql_quantity, (product_qty, product_name))
#                         connection.commit()
#                         for item in all_keys:
#
#                             check_material = "SELECT quantity FROM material_qty WHERE material_id=(SELECT id from material WHERE material_name=%s)"
#                             cursor.execute(check_material, item)
#                             data_checked = cursor.fetchone()
#                             if data_checked is None:
#                                 flash("Material - {} not in inventory. Purchase Material.".format(item))
#                                 return redirect(url_for('manufacture_process'))
#                             if int(data_checked['quantity']) < int(data[item]):
#                                 list_of_ofs_items.append(item)
#                             sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE material_id=(SELECT id FROM material WHERE material_name=%s)"
#                             cursor.execute(sql_quantity, (data[item], item))
#                         connection.commit()
#                         sql = "INSERT INTO product(product_name,date_time,added_by,comments," \
#                               "product_spec,component_flag, product_rate,ip_address,mac_id) " \
#                               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#                         cursor.execute(sql,
#                                        (product_name, date_time, str(session['username']), '',
#                                         str(data), 'N', product_rate, ip, mac))
#                         connection.commit()
#                         flag = 'Successfully Added the new product {}'.format(product_name) if not any(list_of_ofs_items) else "Finished Product was created.. with Insufficient Materials - %s " % ','.join(str(n) for n in list_of_ofs_items)
#                         flash(flag)
#                         return redirect(url_for('manufacture_process'))
#                     except Exception as e:
#                         flag = "Failure with %s" % e
#                         flash(flag)
#                         return redirect(url_for('manufacture_process'))
#                     finally:
#                         connection.close()


@app.route('/view_component_details')
def view_component_details():
    try:
        connection = connect_to_db()
        list_data = list()
        with connection.cursor() as cursor:
            get_product_data = "SELECT id, product_name,product_rate,product_spec,added_by FROM component_master WHERE component_flag=%s"
            cursor.execute(get_product_data, 'Y')
            data = cursor.fetchall()
            # temp = data
            # for i in range(0, len(data)):
            #     a = ast.literal_eval(data[i]['product_spec'])
            #     # del a[0] if a[0] else a
            #     # b = a
            #     all_keys = a.keys()
            #     tempo = dict()
            #     for j in all_keys:
            #         get_material = "SELECT material_name FROM material WHERE id=%s"
            #         cursor.execute(get_material, j)
            #         material_name = cursor.fetchone()
            #         name = material_name['material_name']
            #         tempo[j] = name
            #     # print(tempo)
            #     c = {tempo[key]: value for key, value in a.items()}
            #     # print(c)
            #     temp[i]['product_spec'] = c
            # # print(temp)
            for items in data:
                named_item = convertid2name(items['product_spec'])
                named_item = str(json.dumps(named_item).replace('{', '[')).replace('}', ']').replace('\"', '').replace(
                    ':', ' -')
                items['product_spec'] = named_item
                list_data.append(items)
            return render_template('show_component_master.html', items_data=list_data)
    except Exception as e:
        return str(e)


@app.route('/view_manufactured_details')
def view_manufactured_details():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_product_data = "SELECT id, product_name,product_rate,product_spec,added_by FROM product WHERE component_flag=%s"
            cursor.execute(get_product_data, 'N')
            data = cursor.fetchall()
            # temp = data
            # for i in range(0, len(data)):
            #     a = ast.literal_eval(data[i]['product_spec'])
            #     # del a[0] if a[0] else a
            #     # b = a
            #     all_keys = a.keys()
            #     tempo = dict()
            #     for j in all_keys:
            #         get_material = "SELECT material_name FROM material WHERE id=%s"
            #         cursor.execute(get_material, j)
            #         material_name = cursor.fetchone()
            #         name = material_name['material_name']
            #         tempo[j] = name
            #     # print(tempo)
            #     c = {tempo[key]: value for key, value in a.items()}
            #     # print(c)
            #     temp[i]['product_spec'] = c
            # print(temp)
            return render_template('show_manufacture_details.html', items_data=data)
    except Exception as e:
        return str(e)




@app.route('/process_ledger/<int:p_id>', methods=['GET'])
def process_ledger(p_id):
    # p_id = 12
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_mat_comments = "SELECT comments FROM ledger where id=%s"
            cursor.execute(get_mat_comments, p_id)
            dat = cursor.fetchall()
            connection.close()
            return jsonify({'data': dat[0]['comments']})
    except Exception as e:
        return str(e)


@app.route('/process_material/<int:p_id>', methods=['GET'])
def process_material(p_id):
    # p_id = 12
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_mat_comments = "SELECT unit, sub_unit, comments FROM material where id=%s"
            cursor.execute(get_mat_comments, p_id)
            dat = cursor.fetchall()
            connection.close()
            return jsonify({'comments': dat[0]['comments'], 'unit': dat[0]['unit'], 'sub_unit': dat[0]['sub_unit']})
    except Exception as e:
        return str(e)


@app.route('/process_unit/<int:p_id>', methods=['GET'])
def process_unit(p_id):
    # p_id = 12
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_unit_comments = "SELECT unit,sub_unit FROM material where id=%s"
            cursor.execute(get_unit_comments, p_id)
            dat = cursor.fetchall()
            connection.close()
            return jsonify({'data': dat[0]['unit'], 'data2': dat[0]['sub_unit']})
    except Exception as e:
        return str(e)


@app.route('/process_alter_product/<int:p_id>', methods=['GET'])
def process_alter_product(p_id):
    # p_id = 12
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_unit_comments = "SELECT purchased_date,ledger_id,unit,sub_unit, quantity_unit,quantity_sub_unit,rate,total_amount,material_id FROM purchased where purchased_id=%s"
            cursor.execute(get_unit_comments, p_id)
            dat = cursor.fetchall()
            connection.close()
            return jsonify({'purchased_date': dat[0]['purchased_date'], 'ledger_id': dat[0]['ledger_id'], 'unit': dat[0]['unit'], 'sub_unit': dat[0]['sub_unit'], 'quantity_unit': dat[0]['quantity_unit'], 'rate': dat[0]['rate'], 'total_amount': dat[0]['total_amount'], 'material_id': dat[0]['material_id'], 'quantity_sub_unit': dat[0]['quantity_sub_unit']})
    except Exception as e:
        return str(e)


@app.route('/create_units')
def create_units():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        return render_template('new_units_add.html')


@app.route('/unit_creation', methods=['POST', 'GET'])
def unit_creation():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            connection = connect_to_db()
            unit = request.form['unitname']
            if connection.open == 1:
                # Add Unit to DB
                try:
                    with connection.cursor() as cursor:
                        get_items = "INSERT INTO units(unit) VALUES(%s)"
                        cursor.execute(get_items, unit)
                        connection.commit()
                        flag = 'Successfully Added the new {} unit'.format(unit)
                        flash(flag)
                        return redirect(url_for('create_units'))
                except Exception as e:
                    return str(e)


@app.route('/modify_units')
def modify_units():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT id, unit FROM units"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('alter_unit.html', items_data=items_data)
            except Exception as e:
                return str(e)


@app.route('/unit_modification', methods=['POST', 'GET'])
def unit_modification():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        unit_name = None
        unit_id = None
        connection = connect_to_db()
        if request.method == 'POST':
            unit_id = request.form['units_list']
            unit_name = request.form['new_name']
        if unit_id == "0" and unit_name == "":
            flash('Invalid Data. Please try again.')
            return redirect(url_for('modify_units'))
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    select_item = 'SELECT unit FROM units WHERE id=%s'
                    cursor.execute(select_item, unit_id)
                    item = cursor.fetchone()
                    if unit_name and unit_id != "0":
                        upd_items = 'UPDATE units SET unit="%s" WHERE id=%s' % (unit_name, unit_id)
                        cursor.execute(upd_items)
                        connection.commit()
                        connection.close()
                        flag = "Successfully Updated - {} to {} at {}".format(item['unit'], unit_name, datetime.now())
                        flash(flag)
                        return redirect(url_for('modify_units'))
            except Exception as e:
                return str(e)


@app.route('/delete_units')
def delete_units():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate unit names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT unit FROM units"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    return render_template('delete_units.html', items_data=items_data)
            except Exception as e:
                return str(e)
            finally:
                connection.close()


@app.route('/unit_deletion', methods=['POST', 'GET'])
def unit_deletion():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        unit = None
        connection = connect_to_db()
        if request.method == 'POST':
            unit = request.form['unit']
            if unit == "0":
                flag = "Invalid Data"
                flash(flag)
                return redirect(url_for('delete_units'))
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    del_items = "DELETE FROM units WHERE unit=%s"
                    cursor.execute(del_items, unit)
                    connection.commit()
                    connection.close()
                    flag = "Successfully deleted - {} at - {}".format(unit, datetime.now())
                    flash(flag)
                    return redirect(url_for('delete_units'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                return str(e)


@app.route('/view_units')
def view_units():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT id, unit FROM units"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('view_units.html', items_data=items_data)
            except Exception as e:
                return 'Exception'


@app.route('/show_finished_products/<int:p_id>', methods=['GET'])
def show_finished_products(p_id):
    # p_id = 12
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_unit_comments = "SELECT  product_name, comments, product_rate , product_spec FROM product where id=%s"
            cursor.execute(get_unit_comments, p_id)
            dat = cursor.fetchone()
            materials_used = dat['product_spec']
            materials_used = ast.literal_eval(materials_used)
            count = str(len(list(materials_used.keys())) * '%s,')[:-1]
            get_material_name = "SELECT id, material_name FROM material WHERE id IN " + "("+count+")"
            cursor.execute(get_material_name, tuple(materials_used.keys()))
            get_all = cursor.fetchall()
            connection.close()
            leng = len(get_all)
            for i in range(0, leng):
                id = get_all[i]['id']
                mat_quantity = materials_used[id]
                get_all[i]['quantity'] = mat_quantity
            return jsonify({'product_name': dat['product_name'], 'comments': dat['comments'], 'product_rate': dat['product_rate'], 'spec': get_all})
    except Exception as e:
        return str(e)


@app.route('/show_sell_products/<int:p_id>', methods=['GET'])
def show_sell_products(p_id):
    # p_id = 12
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_product_rate = "SELECT id, product_rate,product_name FROM component_master where id=%s"
            cursor.execute(get_product_rate, p_id)
            dat = cursor.fetchone()
            # get_product_qty = "SELECT quantity FROM product_qty WHERE product_name=%s"
            # cursor.execute(get_product_qty, dat['product_name'])
            # get_all = cursor.fetchone()
            connection.close()
            # return jsonify({'id': dat['id'], 'product_rate': dat['product_rate'], 'quantity': get_all['quantity']})
            return jsonify({'id': dat['id'], 'product_rate': dat['product_rate']})
    except Exception as e:
        return str(e)


@app.route('/add_billing')
def add_billing():
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
                get_products = "SELECT id,product_name FROM product where component_flag=%s"
                cursor.execute(get_products,'Y')
                product_data = cursor.fetchall()
                return render_template('add_billing.html', ledger_data=ledger_data, product_data=product_data)
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


@app.route('/direct_billing')
def direct_billing():
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
                get_products = "SELECT id,product_name FROM component_master where component_flag=%s"
                cursor.execute(get_products, 'Y')
                product_data = cursor.fetchall()
                return render_template('direct_billing.html', ledger_data=ledger_data, product_data=product_data)
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


@app.route('/billing_creation', methods=['POST', 'GET'])
def billing_creation():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        mac = utilities.get_mac()
        ip = utilities.get_ip()
        if request.method == 'POST':
            ledger_id = int(request.form['ledgers_dat'])
            pdate = request.form['pdate']
            qty_unit = int(request.form['qtykg']) if request.form['qtykg'] != "" else 0
            product_id = request.form['products_dat']
            totamt = int(request.form['totamt']) if request.form['totamt'] != "" else 0
            rate = int(request.form['recamt']) if request.form['recamt'] != "" else 0
            if ledger_id == 0:
                flag = "Ledger not selected."
                flash(flag)
                return redirect(url_for('add_billing'))
            elif qty_unit == 0 or pdate == "" or product_id == "" or totamt == 0:
                flag = "Invalid Data"
                flash(flag)
                return redirect(url_for('add_billing'))
            else:
                connection = connect_to_db()
                with connection.cursor() as cursor:
                    try:
                        get_product_name = "SELECT product_name FROM product WHERE id=%s"
                        cursor.execute(get_product_name, product_id)
                        names = cursor.fetchone()
                        get_ledger_name = "SELECT ledger_name FROM ledger WHERE id=%s"
                        cursor.execute(get_ledger_name, ledger_id)
                        ledger_name = cursor.fetchone()
                        sql = "INSERT INTO sell(sell_date,ledger_id,product_id,quantity," \
                              "rate, amount,added_by,ip_address,mac_id) " \
                              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, (pdate, ledger_id, product_id, qty_unit, rate, totamt, str(session['username']), ip, mac))
                        connection.commit()
                        check_products = "SELECT id,quantity FROM product_qty WHERE product_name=%s"
                        cursor.execute(check_products, names['product_name'])
                        data = cursor.fetchone()
                        if int(data['quantity']) < qty_unit:
                            flag = "Insufficient Quantity. Please manufacture..."
                            flash(flag)
                            return redirect(url_for('add_billing'))
                        else:
                            sql_quantity = "UPDATE product_qty SET quantity = quantity - %s WHERE product_name=%s and id=%s"
                            cursor.execute(sql_quantity, (qty_unit, names['product_name'], str(data['id'])))
                            connection.commit()
                        flag = 'Successfully Sold {} to {} on {}' .format(names['product_name'], ledger_name['ledger_name'], date_time)
                        flash(flag)
                        return redirect(url_for('add_billing'))
                    except Exception as e:
                        flag = "Failure with %s" % str(e)
                        flash(flag)
                        return redirect(url_for('add_billing'))
                    finally:
                        connection.close()


@app.route('/direct_billing_creation', methods=['POST'])
def direct_billing_creation():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        mac = utilities.get_mac()
        ip = utilities.get_ip()
        list_of_ofs_items = list()
        if request.method == 'POST':
            ledger_id = int(request.form['ledgers_dat'])
            pdate = request.form['pdate']
            qty_unit = int(request.form['qtykg']) if request.form['qtykg'] != "" else 0
            product_id = request.form['products_dat']
            totamt = int(request.form['totamt']) if request.form['totamt'] != "" else 0
            rate = int(request.form['recamt']) if request.form['recamt'] != "" else 0
            if ledger_id == 0:
                flag = "Ledger not selected."
                flash(flag)
                return redirect(url_for('direct_billing'))
            elif qty_unit == 0 or pdate == "" or product_id == "" or totamt == 0:
                flag = "Invalid Data"
                flash(flag)
                return redirect(url_for('direct_billing'))
            else:
                connection = connect_to_db()
                with connection.cursor() as cursor:
                    try:
                        flag = 'y'
                        get_product_name = "SELECT product_name,product_spec FROM component_master WHERE id=%s and component_flag=%s"
                        cursor.execute(get_product_name, (product_id, flag))
                        names = cursor.fetchone()
                        product_data = product_manipulation(convertid2name(names['product_spec']), qty_unit)

                        for item in product_data:
                            # Get Material Movement
                            get_material_cdate = "SELECT closing_balance,mat_id FROM material_movement WHERE txn_date = (SELECT MAX(txn_date) FROM material_movement WHERE mat_id=(SELECT id FROM material WHERE material_name=%s));"
                            cursor.execute(get_material_cdate, item)
                            cdate = cursor.fetchone()
                            # Add Material Movement
                            final_closing = int(cdate['closing_balance']) - int(product_data[item])
                            sql_mat_mov = "INSERT INTO material_movement(mat_id,txn_date,opening_balance,closing_balance,txn_type) VALUES(%s,%s,%s,%s,%s)"
                            cursor.execute(sql_mat_mov, (cdate['mat_id'], date_time, cdate['closing_balance'],
                                                         final_closing, 'Sale'))
                            sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE " \
                                           "material_id=(SELECT id FROM material WHERE material_name=%s)"
                            cursor.execute(sql_quantity, (product_data[item], item))
                            # cursor.execute(sql_update_flag, item)
                        connection.commit()
                        sql = "INSERT INTO product_master(product_name,date_time,added_by,comments," \
                              "product_spec,link_component_flag, product_rate,ip_address,mac_id) " \
                              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql,
                                       (names['product_name'], date_time, str(session['username']), 'Directly Added',
                                        str(product_data), product_id, rate, ip, mac))
                        connection.commit()
                        get_product_name = "SELECT MAX(id) as id FROM product_master"
                        cursor.execute(get_product_name,)
                        data_id = cursor.fetchone()
                        get_ledger_name = "SELECT ledger_name FROM ledger WHERE id=%s"
                        cursor.execute(get_ledger_name, ledger_id)
                        ledger_name = cursor.fetchone()
                        sql = "INSERT INTO sell(sell_date,ledger_id,product_id,quantity," \
                              "rate, amount,added_by,ip_address,mac_id) " \
                              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, (pdate, ledger_id, data_id['id'], qty_unit, rate, totamt, str(session['username']), ip, mac))
                        connection.commit()

                        insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id,amount,comments) VALUES (%s, %s,NULL,%s,%s,'Money Received on Sell')"
                        cursor.execute(insert_sql, (date_time, ledger_id, data_id['id'], totamt))
                        connection.commit()
                        for item in product_data:
                            check_material = "SELECT quantity FROM material_qty WHERE material_id=(SELECT id from material WHERE material_name=%s)"
                            cursor.execute(check_material, (item))
                            data_checked = cursor.fetchone()
                            if int(data_checked['quantity']) < int(product_data[item]):
                                list_of_ofs_items.append(item)
                        flag = 'Successfully Sold {} to {} on {}' .format(names['product_name'], ledger_name['ledger_name'], date_time) if not any(list_of_ofs_items) else 'Successfully Sold %s to %s on %s with Insufficient Materials - %s' % (names['product_name'],ledger_name['ledger_name'],date_time,','.join(str(n) for n in list_of_ofs_items))
                        flash(flag)
                        return redirect(url_for('direct_billing'))
                    except Exception as e:
                        flag = "Failure with %s" % str(e)
                        flash(flag)
                        return redirect(url_for('direct_billing'))
                    finally:
                        connection.close()


@app.route('/view_billings')
def view_billings():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate billing from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT sell_id,sell_date,l.ledger_name,p.product_name,quantity,rate,amount, s.added_by,s.ip_address,s.mac_id FROM sell s INNER join ledger l ON s.ledger_id = l.id INNER JOIN product_master p ON s.product_id=p.id"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('view_billings.html', items_data=items_data)
            except Exception as e:
                return str(e)


@app.route('/delete_billings')
def delete_billings():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate billing from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT sell_id,sell_date,l.ledger_name,p.product_name,quantity,rate,amount, s.added_by,s.ip_address,s.mac_id FROM sell s INNER join ledger l ON s.ledger_id = l.id INNER JOIN product p ON s.product_id=p.id"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('delete_sell_items.html', items_data=items_data)
            except Exception as e:
                return str(e)


# @app.route('/show_product_inventory')
# def show_product_inventory():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         connection = connect_to_db()
#         if connection.open == 1:
#             # Populate material names from table
#             try:
#                 with connection.cursor() as cursor:
#                     get_items = "select product_name, quantity from product_qty"
#                     cursor.execute(get_items)
#                     items_data = cursor.fetchall()
#                     connection.close()
#                     return render_template('show_product_inventory.html', items_data=items_data)
#             except Exception as e:
#                 return str(e)


@app.route('/pay_to_ledger')
def pay_to_ledger():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "select id,ledger_name from ledger"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('pay_to_ledger.html', ledger_data=items_data)
            except Exception as e:
                return str(e)


# @app.route('/paid_ledger')
# def paid_ledger():
#     ledger_id = int(request.form['ledgers_dat'])
#     payamount = request.form['payamount']
#     qty_unit = int(request.form['qtykg']) if request.form['qtykg'] != "" else 0
#     connection = connect_to_db()
#     if connection.open == 1:
#         # Populate ledger names from table
#         try:
#             with connection.cursor() as cursor:
#                 get_ledger_id = "SELECT ledger_id FROM cash WHERE ledger_id=%s"
#                 cursor.execute(get_ledger_id, ledger_id)
#                 check = cursor.fetchone()
#                 if check is None:
#                     insert_sql = "INSERT INTO cash(ledger_id, amount,comments) VALUES (%s,%s,'')"
#                     cursor.execute(insert_sql, (ledger_id, amount))
#                     connection.commit()
#                 else:
#                     update_sql = "UPDATE cash SET amount = amount - %s WHERE ledger_id=%s"
#                     cursor.execute(update_sql, (totamt, ledger_id))
#                     connection.commit()

@app.route('/show_cash_report')
def show_cash_report():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate material names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "select c.id, c.date_time, l.ledger_name, m.material_name, pr.product_name, amount from cash c INNER join ledger l ON c.ledger_id = l.id LEFT JOIN material m ON m.id=c.material_id LEFT JOIN product_master pr ON pr.id=c.product_id;"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('show_cash_report.html', items_data=items_data)
            except Exception as e:
                return str(e)


@app.route('/download_cash_report_as_csv')
def download_cash_report_as_csv():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        filename = 'Cash_Report_{}.csv' .format(str(datetime.now().strftime("%Y%m%d%H%M%S")))
        full_fname = app.config['UPLOAD_FOLDER'] + filename
        connection = connect_to_db()
        if connection.open == 1:
            # Populate material names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "select c.id as id, c.date_time as Entry_Time, l.ledger_name as Ledger_Name, m.material_name as Material_Name, pr.product_name as Product_Name, ABS(c.amount) as Amount, CASE WHEN amount > 0 THEN 'DEBIT' WHEN amount < 0 THEN 'CREDIT' END AS Transaction_Type from cash c INNER join ledger l ON c.ledger_id = l.id LEFT JOIN material m ON m.id=c.material_id LEFT JOIN product pr ON pr.id=c.product_id;"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                with open(full_fname, 'w', newline='') as csvFile:
                    fields = ['id', 'Entry_Time', 'Ledger_Name', 'Material_Name', 'Product_Name','Amount', 'Transaction_Type']
                    writer = csv.DictWriter(csvFile, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(items_data)
                csvFile.close()
                return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
            except Exception as e:
                return str(e)


@app.route('/del_sell_data/<int:p_id>')
def del_sell_data(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_product_qty = "SELECT pr.product_spec, s.quantity, s.amount,s.ledger_id FROM sell s INNER JOIN product pr ON s.product_id = pr.id WHERE sell_id=%s "
                    cursor.execute(get_product_qty, p_id)
                    data = cursor.fetchone()
                    new_data = product_manipulation(ast.literal_eval(data['product_spec']),1)
                    for item in new_data:
                        sql_quantity = "UPDATE material_qty SET quantity = quantity + %s WHERE material_id=(SELECT id FROM material WHERE material_name=%s)"
                        cursor.execute(sql_quantity, (new_data[item], item))
                    connection.commit()
                    del_items = "DELETE FROM sell WHERE sell_id=%s"
                    cursor.execute(del_items, p_id)
                    connection.commit()
                    insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id, amount,comments) VALUES (%s, %s,NULL,%s,%s,'Reversed')"
                    cursor.execute(insert_sql, (date_time, data['ledger_id'], p_id, -(data['amount'])))
                    connection.commit()
                    connection.close()
                    return redirect(url_for('delete_billings'))
            except Exception as e:
                return str(e)

# delete_component_details
@app.route('/delete_component_details')
def delete_component_details():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        list_data = []
        connection = connect_to_db()
        if connection.open == 1:
            # Populate material names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT id, product_name, date_time, product_spec, product_rate FROM component_master"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    for items in items_data:
                        named_item = convertid2name(items['product_spec'])
                        named_item = str(json.dumps(named_item).replace('{','[')).replace('}',']').replace('\"','')
                        items['product_spec'] = named_item
                        list_data.append(items)
                    return render_template('delete_component_master.html', items_data=list_data)
            except Exception as e:
                return str(e)


@app.route('/del_component_master_data/<int:p_id>')
def del_component_master_data(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        # date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    sel_product = "SELECT product_spec FROM component_master WHERE id=%s"
                    cursor.execute(sel_product, p_id)
                    fetched_data = cursor.fetchone()
                    del_items = "DELETE FROM component_master WHERE id=%s"
                    cursor.execute(del_items, p_id)

                    for key in ast.literal_eval(fetched_data['product_spec']):
                        get_usage_data = "SELECT usage_flag FROM material WHERE id=%s"
                        cursor.execute(get_usage_data, key)
                        fetched_usage_data = cursor.fetchone()
                        usage_add = int(fetched_usage_data['usage_flag']) - 1
                        upd_items = 'UPDATE material SET usage_flag=%s WHERE id=%s' % (usage_add, key)
                        cursor.execute(upd_items)
                    connection.commit()
                    connection.close()
                    return redirect(url_for('delete_component_details'))
            except Exception as e:
                return str(e)


@app.route('/show_mm_report')
def show_mm_report():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate material names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "select mv.id,m.material_name,mv.opening_balance, mv.closing_balance, mv.txn_type, DATE_FORMAT(mv.txn_date,'%d-%m-%Y %k:%i:%s') as date_and_time from material_movement mv LEFT JOIN material m ON m.id=mv.mat_id;"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('show_material_movement.html', items_data=items_data)
            except Exception as e:
                return str(e)


if __name__ == '__main__':
    app.run(debug=True)
