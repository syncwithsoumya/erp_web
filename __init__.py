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


def write_to_log_data(txn_date=None, txn_msg=None, added_by=None, ip_address=None, mac_id=None):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        try:
            sql = "INSERT INTO log_data(txn_date,txn_msg,added_by,ip_address,mac_id) VALUES (%s,%s,%s,%s,%s)"
            cursor.execute(sql, (txn_date, txn_msg, added_by, ip_address, mac_id))
            connection.commit()
            return True
        except Exception as e:
            return False
        finally:
            connection.close()


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


@app.route('/change_password')
def change_password():
    return render_template('change_password.html')


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


@app.route('/super_admin_panel')
def super_admin_panel():
    return render_template('super_admin/super_admin_base.html')


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
                write_to_log_data(date_time, flag + 'create_ledger', str(session['username']), ip, mac)
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
                        write_to_log_data(date_time, flag, str(session['username']), ip, mac)
                        return redirect(url_for('create_ledger'))
                    except Exception as e:
                        flag = "Failure with %s" % e
                        flash(flag)
                        write_to_log_data(date_time, flag, str(session['username']), ip, mac)
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
                return str(e)
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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'delete_ledger', str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    return redirect(url_for('delete_ledger'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                return str(e)


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
                return str(e)


@app.route('/ledger_modification', methods=['POST'])
def ledger_modification():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if request.method == 'POST':
            # ledger_id = request.form['ledgers_list']
            ledger_id = request.form['Ledgerid']
            ledger_oldname = request.form['Ledgername']
            ledger_name = request.form['Ledgernewname']
            # comments = request.form['new_comments']
            if ledger_name == "":
                flag = 'Invalid Data. Please try again.'
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'modify_ledger', str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('modify_ledgers'))
            if connection.open == 1:
                # Populate ledger names from table
                try:
                    with connection.cursor() as cursor:
                        del_items = 'UPDATE ledger SET ledger_name="%s", comments="%s" WHERE id=%s' % (
                                ledger_name, 'New Ledger', ledger_id)
                        cursor.execute(del_items)
                        connection.commit()
                        connection.close()
                        flag = "Successfully Updated - {} to - {} at {}".format(ledger_oldname, ledger_name, datetime.now())
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('modify_ledgers'))
                        # return render_template('delete_ledger.html', items_data=items_data)
                except Exception as e:
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    return str(e)


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
                    get_items = "SELECT id, ledger_name, DATE_FORMAT(date_time,'%d-%m-%Y') as date_time, added_by, comments FROM ledger"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('view_ledger.html', items_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


@app.route('/modify_ledgers')
def modify_ledgers():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "SELECT id, ledger_name, DATE_FORMAT(date_time,'%d-%m-%Y') as date_time, added_by, comments FROM ledger"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('delete_ledgers.html', items_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


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
                        get_material_id = "SELECT MAX(id) as material_id FROM material"
                        cursor.execute(get_material_id)
                        mat_id = cursor.fetchone()
                        sql_insert_mat_qty = "INSERT INTO material_qty(material_id,quantity) VALUES (%s,%s)"
                        cursor.execute(sql_insert_mat_qty, (mat_id['material_id'],'0'))
                        connection.commit()
                        flag = 'Successfully Added Material - {} at {}' .format(material_name, date_time)
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag,
                                          str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('create_material'))
                    except Exception as e:
                        flag = "Failure with %s" % e
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag,
                                          str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('create_material'))
                    finally:
                        connection.close()


# @app.route('/delete_material')
# def delete_material():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         connection = connect_to_db()
#         if connection.open == 1:
#             # Populate ledger names from table
#             try:
#                 with connection.cursor() as cursor:
#                     get_items = "SELECT id, material_name FROM material"
#                     cursor.execute(get_items)
#                     items_data = cursor.fetchall()
#                     connection.close()
#                     return render_template('delete_material.html', items_data=items_data)
#             except Exception as e:
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return str(e)


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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'delete_material', str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('delete_material'))
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    del_items = "DELETE FROM material WHERE material_name=%s AND usage_flag < 1"
                    cursor.execute(del_items, material_name)
                    connection.commit()
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")),
                                      'Deleted Material Name-{}'.format(material_name),
                                      str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    if connection.affected_rows() > 0:
                        flag = "Successfully deleted - {} at - {}" .format(material_name, datetime.now())
                    else:
                        flag = "Failed to delete - {} as it is linked to a Product in Component Master".format(material_name)
                    flash(flag)
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    return redirect(url_for('delete_material'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


@app.route('/material_modification', methods=['POST'])
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
                flag = 'Invalid Data. Please try again.'
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'modify_material', str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('modify_material'))
            elif unit_list == "0" or sub_unit_list == "0":
                flag = 'Please select the unit or sub-unit'
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('modify_material'))
                except Exception as e:
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                    get_items = "SELECT id, material_name, DATE_FORMAT(date_time,'%d-%m-%Y') as date_time, added_by, comments FROM material"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('view_material.html', items_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


'''
            General Section starts
'''


@app.route('/authenticate_login', methods=['POST'])
def authenticate_login():
    error = None
    if request.method == 'POST':
        id = request.form['username']
        password = request.form['password']
        if id == 'Admin@ssp.com' and password == 'Pass1234':
            # flash('Successfully logged in')
            session['username'] = id.split('@')[0]
            return redirect(url_for('dashboard'))
        elif id == 'Luna@ssp.com' and password == 'Pass':
            # flash('Successfully logged in')
            session['username'] = id.split('@')[0]
            return redirect(url_for('dashboard'))
        elif id == 'superadmin@ssp.com' and password == 'Pass':
            # flash('Successfully logged in')
            session['username'] = id.split('@')[0]
            return redirect(url_for('super_admin_panel'))
        elif id == 'Babloo@ssp.com' and password == 'Pass':
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
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)
        finally:
            cursor.close()
            connection.close()


# @app.route('/alter_purchased_db')
# def alter_purchased_db():
#     connection = ''
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         try:
#             connection = connect_to_db()
#             with connection.cursor() as cursor:
#                 get_items = "SELECT purchased_id from purchased"
#                 cursor.execute(get_items)
#                 items_pur_data = cursor.fetchall()
#             with connection.cursor() as cursor:
#                 get_items = "SELECT id, ledger_name from ledger"
#                 cursor.execute(get_items)
#                 items_ledger_data = cursor.fetchall()
#             with connection.cursor() as cursor:
#                 get_items = "SELECT id,material_name from material"
#                 cursor.execute(get_items)
#                 items_material_data = cursor.fetchall()
#             return render_template('alter_purchased.html', purchase_data=items_pur_data, ledger_data=items_ledger_data, material_data=items_material_data)
#         except Exception as e:
#             write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
#                               utilities.get_ip(), utilities.get_mac())
#             return str(e)
#         finally:
#             connection.close()


@app.route('/new_purchased', methods=['POST'])
def new_purchased():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        mac = utilities.get_mac()
        ip = utilities.get_ip()
        if request.method == 'POST':
            ledger_id = int(request.form['ledgers_dat'])
            pdate = datetime.strptime(request.form['pdate'],'%d-%m-%Y').strftime('%d-%m-%Y') if str(request.form['pdate']) != "" else ""
            qty_unit = int(request.form['qtykg']) if str(request.form['qtykg']) != "" else ""
            unit = request.form['unit']
            subunit = request.form['subunit']
            material = request.form['materials_dat']
            qty_sub_unit = int(request.form['piece']) if str(request.form['piece']) != "" else ""
            totamt = int(request.form['totamt']) if request.form['totamt'] != "" else 0
            rate = int(request.form['recamt']) if request.form['recamt'] != "" else 0
            mv_date = datetime.strptime(request.form['pdate'],'%d-%m-%Y').strftime('%Y%m%d') + str(datetime.now().strftime('%H%M%S'))
            if qty_unit == "" or pdate == "" or int(material) == 0 or qty_sub_unit == "" or pdate == "" or ledger_id == 0:
                flag = "Invalid Data"
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'new_purchased_db', str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('new_purchased_db'))
            elif rate < 0:
                flag = "Rate is negative.. Try again!"
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'new_purchased_db',
                                  str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                        get_purchased_id = "SELECT MAX(purchased_id) as purchase_id FROM purchased"
                        cursor.execute(get_purchased_id)
                        purchased_data = cursor.fetchone()
                        insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id, amount,comments,purchased_id) VALUES (%s, %s,%s,NULL,%s,'Money Spent on Raw Material Purchase',%s)"
                        cursor.execute(insert_sql, (mv_date, ledger_id, material, amount, purchased_data['purchase_id']))
                        connection.commit()
                        # get_material_purchased = "SELECT id FROM material_qty WHERE material_id=%s"
                        # cursor.execute(get_material_purchased, material)
                        # data = cursor.fetchone()
                        # get_material_cdate = "SELECT diff FROM material_movement WHERE txn_date = (SELECT MAX(txn_date) FROM material_movement WHERE mat_id=%s) AND txn_type not in (%s,%s);"
                        # cursor.execute(get_material_cdate, (material,'Deleted','Altered'))
                        # cdate = cursor.fetchone()
                        # if data is None:
                        sql_mat_mov = "INSERT INTO material_movement(mat_id,txn_date,amount,txn_type,purchase_id,sell_id) VALUES(%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql_mat_mov, (material, mv_date, qty_sub_unit, 'Purchase', purchased_data['purchase_id'], 0))
                        sql_quantity = "UPDATE material_qty SET quantity=quantity + %s WHERE material_id=%s"
                        cursor.execute(sql_quantity, (qty_sub_unit, material))
                        connection.commit()
                        # else:
                        #     # final_closing = int(cdate['diff']) + int(qty_sub_unit)
                        #     sql_quantity = "UPDATE material_qty SET quantity = quantity + %s WHERE material_id=%s and id=%s"
                        #     cursor.execute(sql_quantity, (qty_sub_unit, material, str(data['id'])))
                        #     sql_mat_mov = "INSERT INTO material_movement(mat_id,txn_date,opening_balance,closing_balance,txn_type,diff,purchase_id,sell_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
                        #     cursor.execute(sql_mat_mov, (material, date_time, cdate['diff'], int(qty_sub_unit), 'Purchase', int(final_closing), purchased_data['purchase_id'],0))
                        #     connection.commit()
                        flag = 'Successfully Added the Purchased data on {}' .format(date_time)
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('new_purchased_db'))
                    except Exception as e:
                        flag = "Failure with %s" % e
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('new_purchased_db'))
                    finally:
                        connection.close()


@app.route('/alter_purchased', methods=['POST'])
def alter_purchased():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        mac = utilities.get_mac()
        ip = utilities.get_ip()
        if request.method == 'POST':
            purchased_id = request.form['purchaseid']
            # pdate = datetime.strptime(request.form['pdate'], '%d-%m-%Y').strftime('%d-%m-%Y') if str(
            #     request.form['pdate']) != "" else ""
            ledger_id = int(request.form['ledger_data'])
            material_id = int(request.form['material_data'])
            qty_unit = int(request.form['quantity']) if str(request.form['quantity']) != "" else ""
            unit = request.form['quantityunit']
            subunit = request.form['subquantityunit']
            qty_sub_unit = int(request.form['subquantity']) if str(request.form['subquantity']) != "" else ""
            totamt = int(request.form['amount']) if request.form['amount'] != "" else 0
            rate = int(request.form['rate'])
            if rate < 0:
                flag = "Rate is negative.. Try again!"
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'new_purchased_db',
                                  str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for(''))
            else:
                connection = connect_to_db()
                with connection.cursor() as cursor:
                    try:
                        amount = -totamt
                        sql = "UPDATE purchased SET ledger_id=%s,unit=%s,sub_unit=%s,quantity_unit=%s,quantity_sub_unit=%s,rate=%s,total_amount=%s,material_id=%s,added_by=%s WHERE purchased_id=%s"
                        cursor.execute(sql, (ledger_id, unit, subunit, qty_unit, qty_sub_unit, rate, totamt,
                                             material_id, str(session['username']), purchased_id))
                        connection.commit()
                        insert_sql = "UPDATE cash SET ledger_id=%s, material_id=%s, amount=%s WHERE purchased_id=%s"
                        cursor.execute(insert_sql, (ledger_id, material_id, amount, purchased_id))
                        connection.commit()
                        sql_mat_mov = "UPDATE material_movement SET mat_id=%s,amount=%s WHERE purchase_id=%s"
                        cursor.execute(sql_mat_mov, (material_id, qty_sub_unit, purchased_id))
                        sql_quantity = "UPDATE material_qty SET quantity=quantity + %s WHERE material_id=%s"
                        cursor.execute(sql_quantity, (qty_sub_unit, material_id))
                        connection.commit()
                        flag = 'Successfully Added the Purchased data on {}' .format(date_time)
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('delete_purchased_db'))
                    except Exception as e:
                        flag = "Failure with %s" % e
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('delete_purchased_db'))
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
                    return render_template('view_purchased.html', items_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


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
                    get_items = "SELECT p.purchased_id, p.purchased_date, l.ledger_name, p.quantity_unit, p.total_amount, p.quantity_sub_unit, p.sub_unit,p.unit, m.material_name FROM purchased p INNER JOIN ledger l ON p.ledger_id = l.id INNER JOIN material m ON p.material_id = m.id"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    get_ledger = "SELECT id, ledger_name FROM ledger"
                    cursor.execute(get_ledger)
                    items_ledger_data = cursor.fetchall()
                    get_materials = "SELECT id, material_name FROM material"
                    cursor.execute(get_materials)
                    items_materials_data = cursor.fetchall()
                    return render_template('delete_purchased.html', items_data=items_data, items_ledger_data=items_ledger_data,items_material_data=items_materials_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


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
                    get_material_qty = "SELECT material_id, quantity_sub_unit, unit, quantity_sub_unit, total_amount,ledger_id FROM purchased WHERE purchased_id=%s"
                    cursor.execute(get_material_qty, p_id)
                    data = cursor.fetchone()
                    qty = data['quantity_sub_unit']
                    mat_id = data['material_id']
                    sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE material_id=%s"
                    cursor.execute(sql_quantity, (qty, mat_id))
                    insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id, amount,comments) VALUES (%s, %s,%s,NULL,%s,'Money Received as Refund')"
                    cursor.execute(insert_sql, (date_time, data['ledger_id'], data['material_id'], data['total_amount']))
                    del_items = "DELETE FROM purchased WHERE purchased_id=%s"
                    cursor.execute(del_items, p_id)
                    connection.commit()
                    del_items_material_movements = "DELETE FROM material_movement WHERE purchase_id=%s"
                    cursor.execute(del_items_material_movements, p_id)
                    connection.commit()
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), 'Deleted Purchase ID-{}'.format(p_id),
                                      str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    connection.close()
                    return redirect(url_for('delete_purchased_db'))
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)

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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
            product_rate = 1 if str(request.form['prate']) == "" else int(request.form['prate'])
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

            if item1 == 0 and item2 == 0 and item3 == 0 and item4 == 0 and item5 == 0 and item6 == 0 and item7 == 0 \
                    and item8 == 0 and item9 == 0 and item10 == 0 and product_rate == 0:
                flag = "Minimum 1 Item's quantity is expected ..."
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('component_master'))
            elif item1 < 0 and item2 < 0 and item3 < 0 and item4 < 0 and item5 < 0 and item6 < 0 and item7 < 0 \
                    and item8 < 0 and item9 < 0 and item10 < 0 and product_rate < 0:
                flag = "Quantity can't be less than 1"
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('component_master'))
            else:
                data = dict()
                list_handler = list()
                if product_name == "":
                    flag = "Product Name is expected."
                    flash(flag)
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
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
                        flag = 'You have provided duplicate item names - %s' % sum_of_dupes
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        connection.close()
                    except Exception as e:
                        flag = 'Exception %s' % str(e)
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
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
                                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag,
                                                  str(session['username']),
                                                  utilities.get_ip(), utilities.get_mac())
                                return redirect(url_for('component_master'))
                            else:
                                sql = "INSERT INTO component_master(product_name,date_time,added_by,comments," \
                                      "product_spec,component_flag, product_rate,ip_address,mac_id) " \
                                      "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                cursor.execute(sql,
                                               (product_name, date_time, str(session['username']), product_comments,
                                                str(data), 'Y', product_rate, ip, mac))

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
                                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag,
                                                  str(session['username']),
                                                  utilities.get_ip(), utilities.get_mac())
                                return redirect(url_for('component_master'))
                        except Exception as e:
                            flag = "Failure with %s" % e
                            flash(flag)
                            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag,
                                              str(session['username']),
                                              utilities.get_ip(), utilities.get_mac())
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
            get_product_data = "SELECT id,date_time, product_name,product_rate,product_spec,added_by FROM component_master WHERE component_flag=%s"
            cursor.execute(get_product_data, 'Y')
            data = cursor.fetchall()
            for items in data:
                items['date_time'] = datetime.strptime(str(items['date_time']), '%Y%m%d%H%M%S').strftime('%d-%m-%Y')
                dict_data = ast.literal_eval(items['product_spec'])
                for material in dict_data:
                    get_item_unit = "SELECT sub_unit FROM material WHERE id=%s"
                    cursor.execute(get_item_unit, material)
                    items_unit_data = cursor.fetchone()
                    value = str(ast.literal_eval(items['product_spec'])[material])+str(items_unit_data['sub_unit'])
                    dict_data[material] = value
                # dict_data = ast.literal_eval(items['product_spec'])
                named_item = convertid2name(str(dict_data))
                named_item = str(json.dumps(named_item).replace('{', '')).replace('}', '').replace('\"', '').replace(
                    ':', ' -')
                items['product_spec'] = named_item
                list_data.append(items)
            return render_template('show_component_master.html', items_data=list_data)
    except Exception as e:
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
        return str(e)


@app.route('/view_manufactured_details')
def view_manufactured_details():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_product_data = "SELECT id, product_name,product_rate,product_spec,added_by FROM product WHERE component_flag=%s"
            cursor.execute(get_product_data, 'N')
            data = cursor.fetchall()
            return render_template('show_manufacture_details.html', items_data=data)
    except Exception as e:
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
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
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
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
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
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
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
        return str(e)


@app.route('/process_alter_billing/<int:p_id>', methods=['GET'])
def process_alter_billing(p_id):
    # p_id = 12
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_unit_comments = "SELECT sell_date,ledger_id,product_id,quantity,rate,amount FROM sell where sell_id=%s"
            cursor.execute(get_unit_comments, p_id)
            dat = cursor.fetchall()
            connection.close()
            return jsonify({'sell_date': dat[0]['sell_date'], 'ledger_id': dat[0]['ledger_id'], 'quantity': dat[0]['quantity'], 'rate': dat[0]['rate'], 'total_amount': dat[0]['amount'], 'product': dat[0]['product_id']})
    except Exception as e:
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
        return str(e)


@app.route('/process_alter_component_master/<int:p_id>', methods=['GET'])
def process_alter_component_master(p_id):
    # p_id = 12
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            get_unit_comments = "SELECT sell_date,ledger_id,product_id,quantity,rate,amount FROM sell where sell_id=%s"
            cursor.execute(get_unit_comments, p_id)
            dat = cursor.fetchall()
            connection.close()
            return jsonify({'sell_date': dat[0]['sell_date'], 'ledger_id': dat[0]['ledger_id'], 'quantity': dat[0]['quantity'], 'rate': dat[0]['rate'], 'total_amount': dat[0]['amount'], 'product': dat[0]['product_id']})
    except Exception as e:
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
        return str(e)


@app.route('/process_alter_purchased/<int:p_id>', methods=['GET'])
def process_alter_purchased(p_id):
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
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
        return str(e)


@app.route('/create_units')
def create_units():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        return render_template('new_units_add.html')


@app.route('/unit_creation', methods=['POST'])
def unit_creation():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        if request.method == 'POST':
            connection = connect_to_db()
            unit = request.form['unitname']
            unit = unit.replace(' ','')
            if len(unit) <= 0:
                flag = 'Invalid Unit'
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('create_units'))
            else:
                if connection.open == 1:
                    # Add Unit to DB
                    try:
                        with connection.cursor() as cursor:
                            get_items = "INSERT INTO units(date_time, unit) VALUES(%s,%s)"
                            cursor.execute(get_items, (date_time,unit))
                            connection.commit()
                            flag = 'Successfully Added the new {} unit'.format(unit)
                            flash(flag)
                            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                              utilities.get_ip(), utilities.get_mac())
                            return redirect(url_for('create_units'))
                    except Exception as e:
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


@app.route('/unit_modification', methods=['POST'])
def unit_modification():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if request.method == 'POST':
            unit_id = request.form['units_list']
            unit_name = str(request.form['new_name']).replace(' ','')
            if unit_id == "0" and len(unit_name) <= 0:
                flag = 'Invalid Data. Please try again.'
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'modify_units', str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('modify_units'))
            else:
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
                            flag = "Successfully Updated - {} to {} at {}".format(item['unit'], unit_name, datetime.now())
                            flash(flag)
                            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                              utilities.get_ip(), utilities.get_mac())
                            return redirect(url_for('modify_units'))
                except Exception as e:
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    return str(e)
                finally:
                    connection.close()


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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'delete_units', str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    return redirect(url_for('delete_units'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                    get_items = "SELECT id, DATE_FORMAT(date_time,'%d-%m-%Y') as date_time, unit FROM units"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    return render_template('view_units.html', items_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


@app.route('/show_finished_products/<int:p_id>', methods=['GET'])
def show_finished_products(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)


@app.route('/show_sell_products/<int:p_id>', methods=['GET'])
def show_sell_products(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
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
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
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
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
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
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)
        finally:
            cursor.close()
            connection.close()


# @app.route('/billing_creation', methods=['POST', 'GET'])
# def billing_creation():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
#         mac = utilities.get_mac()
#         ip = utilities.get_ip()
#         if request.method == 'POST':
#             ledger_id = int(request.form['ledgers_dat'])
#             pdate = request.form['pdate']
#             qty_unit = int(request.form['qtykg']) if request.form['qtykg'] != "" else 0
#             product_id = request.form['products_dat']
#             totamt = int(request.form['totamt']) if request.form['totamt'] != "" else 0
#             rate = int(request.form['recamt']) if request.form['recamt'] != "" else 0
#             if ledger_id == 0:
#                 flag = "Ledger not selected."
#                 flash(flag)
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return redirect(url_for('add_billing'))
#             elif rate <= 0 or totamt <= 0:
#                 flag = "Rate or Amount is either zero or less than zero.."
#                 flash(flag)
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return redirect(url_for('add_billing'))
#             elif qty_unit == 0 or pdate == "" or product_id == "" or totamt == 0:
#                 flag = "Invalid Data"
#                 flash(flag)
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'add_billing', str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return redirect(url_for('add_billing'))
#             else:
#                 connection = connect_to_db()
#                 with connection.cursor() as cursor:
#                     try:
#                         get_product_name = "SELECT product_name FROM product WHERE id=%s"
#                         cursor.execute(get_product_name, product_id)
#                         names = cursor.fetchone()
#                         get_ledger_name = "SELECT ledger_name FROM ledger WHERE id=%s"
#                         cursor.execute(get_ledger_name, ledger_id)
#                         ledger_name = cursor.fetchone()
#                         sql = "INSERT INTO sell(sell_date,ledger_id,product_id,quantity," \
#                               "rate, amount,added_by,ip_address,mac_id) " \
#                               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#                         cursor.execute(sql, (pdate, ledger_id, product_id, qty_unit, rate, totamt, str(session['username']), ip, mac))
#                         connection.commit()
#                         check_products = "SELECT id,quantity FROM product_qty WHERE product_name=%s"
#                         cursor.execute(check_products, names['product_name'])
#                         data = cursor.fetchone()
#                         if int(data['quantity']) < qty_unit:
#                             flag = "Insufficient Quantity. Please manufacture..."
#                             flash(flag)
#                             write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag,
#                                               str(session['username']),
#                                               utilities.get_ip(), utilities.get_mac())
#                             return redirect(url_for('add_billing'))
#                         else:
#                             sql_quantity = "UPDATE product_qty SET quantity = quantity - %s WHERE product_name=%s and id=%s"
#                             cursor.execute(sql_quantity, (qty_unit, names['product_name'], str(data['id'])))
#                             connection.commit()
#                         flag = 'Successfully Sold {} to {} on {}' .format(names['product_name'], ledger_name['ledger_name'], date_time)
#                         flash(flag)
#                         write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
#                                           utilities.get_ip(), utilities.get_mac())
#                         return redirect(url_for('add_billing'))
#                     except Exception as e:
#                         flag = "Failure with %s" % str(e)
#                         flash(flag)
#                         write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
#                                           utilities.get_ip(), utilities.get_mac())
#                         return redirect(url_for('add_billing'))
#                     finally:
#                         connection.close()


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
            new_date = datetime.strptime(pdate,'%d-%m-%Y').strftime('%Y%m%d') + str(datetime.now().strftime('%H%M%S'))
            if ledger_id == 0:
                flag = "Ledger not selected."
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('direct_billing'))
            elif rate <= 0 or totamt <= 0:
                flag = "Rate or Amount is either zero or less than zero.."
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('direct_billing'))
            elif qty_unit == 0 or pdate == "" or product_id == "" or totamt == 0:
                flag = "Invalid Data"
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'direct_billing', str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                        get_sell_id = "SELECT MAX(sell_id) as id FROM sell"
                        cursor.execute(get_sell_id)
                        sell_data_id = cursor.fetchone()
                        for item in product_data:
                            # Get Material Movement
                            # get_material_cdate = "SELECT closing_balance,mat_id FROM material_movement WHERE txn_date = (SELECT MAX(txn_date) FROM material_movement WHERE mat_id=(SELECT id FROM material WHERE material_name=%s));"
                            # cursor.execute(get_material_cdate, item)
                            # cdate = cursor.fetchone()
                            # Add Material Movement
                            # final_closing = int(cdate['closing_balance']) + int(product_data[item])
                            get_mat_id = "SELECT id FROM material WHERE material_name=%s"
                            cursor.execute(get_mat_id, item)
                            mat_id = cursor.fetchone()
                            sql_mat_mov = "INSERT INTO material_movement(mat_id,txn_date,amount,txn_type,purchase_id,sell_id) VALUES(%s,%s,%s,%s,%s,%s)"
                            cursor.execute(sql_mat_mov, (mat_id['id'], new_date, -product_data[item],
                                                         'Sale','0', sell_data_id['id']))
                            sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE " \
                                           "material_id=(SELECT id FROM material WHERE material_name=%s)"
                            cursor.execute(sql_quantity, (product_data[item], item))
                            # cursor.execute(sql_update_flag, item)
                        connection.commit()
                        insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id,amount,comments,sell_id) VALUES (%s, %s,NULL,%s,%s,'Money Received on Sell',%s)"
                        cursor.execute(insert_sql, (date_time, ledger_id, data_id['id'], totamt,sell_data_id['id']))
                        connection.commit()

                        for item in product_data:
                            check_material = "SELECT quantity FROM material_qty WHERE material_id=(SELECT id from material WHERE material_name=%s)"
                            cursor.execute(check_material, (item))
                            data_checked = cursor.fetchone()
                            if int(data_checked['quantity']) < int(product_data[item]):
                                list_of_ofs_items.append(item)
                        flag = 'Successfully Sold {} to {} on {}' .format(names['product_name'], ledger_name['ledger_name'], date_time) if not any(list_of_ofs_items) else 'Sold %s to %s on %s with Insufficient Materials - %s' % (names['product_name'],ledger_name['ledger_name'],date_time,','.join(str(n) for n in list_of_ofs_items))
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('direct_billing'))
                    except Exception as e:
                        flag = "Failure with %s" % str(e)
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('direct_billing'))
                    finally:
                        connection.close()


@app.route('/alter_direct_billing', methods=['POST'])
def alter_direct_billing():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        mac = utilities.get_mac()
        ip = utilities.get_ip()
        list_of_ofs_items = list()
        if request.method == 'POST':
            sell_id = request.form['sellid']
            ledger_id = int(request.form['ledgers_dat'])
            pdate = request.form['pdate']
            product_name = request.form['product_name']
            quantity = request.form['quantity']
            orgquantity = request.form['orgquantity']
            totamt = int(request.form['amount'])
            rate = int(request.form['rate'])
            new_date = datetime.strptime(pdate, '%d-%m-%Y').strftime('%Y%m%d') + str(datetime.now().strftime('%H%M%S'))
            if ledger_id == 0:
                flag = "Ledger not selected."
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('direct_billing'))
            elif int(quantity) <=0 or rate < 0 or totamt < 0:
                flag = "Rate or Amount is either zero or less than zero.."
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('delete_billings'))
            else:
                connection = connect_to_db()
                with connection.cursor() as cursor:
                    try:
                        if rate > 0:
                            sql_update_product_master = "UPDATE product_master SET product_rate=%s WHERE product_name=%s"
                            cursor.execute(sql_update_product_master, (rate, product_name))
                            connection.commit()
                        get_product_id = "SELECT id FROM component_master WHERE product_name=%s"
                        cursor.execute(get_product_id,product_name)
                        product_id = cursor.fetchone()
                        flag = 'y'
                        get_product_name = "SELECT product_spec FROM component_master WHERE id=%s"
                        cursor.execute(get_product_name, (product_id['id']))
                        names = cursor.fetchone()
                        product_data = product_manipulation(convertid2name(names['product_spec']), quantity)
                        product_data_revert = product_manipulation(convertid2name(names['product_spec']), orgquantity)
                        get_ledger_name = "SELECT ledger_name FROM ledger WHERE id=%s"
                        cursor.execute(get_ledger_name, ledger_id)
                        ledger_name = cursor.fetchone()
                        sql = "UPDATE sell SET ledger_id=%s,product_id=%s,quantity=%s,rate=%s, " \
                              "amount=%s WHERE sell_id=%s"
                        cursor.execute(sql, (ledger_id, product_id['id'], quantity, rate, totamt, sell_id))
                        connection.commit()
                        # get_sell_id = "SELECT MAX(sell_id) as id FROM sell"
                        # cursor.execute(get_sell_id)
                        # data_id = cursor.fetchone()
                        for item in product_data_revert:
                            sql_add_quantity = "UPDATE material_qty SET quantity = quantity + %s WHERE " \
                                               "material_id=(SELECT id FROM material WHERE material_name=%s)"
                            cursor.execute(sql_add_quantity, (product_data_revert[item], item))
                            connection.commit()
                        for item in product_data:
                            # Get Material Movement
                            # get_material_cdate = "SELECT closing_balance,mat_id FROM material_movement WHERE txn_date = (SELECT MAX(txn_date) FROM material_movement WHERE mat_id=(SELECT id FROM material WHERE material_name=%s));"
                            # cursor.execute(get_material_cdate, item)
                            # cdate = cursor.fetchone()
                            # Add Material Movement
                            # final_closing = int(cdate['closing_balance']) + int(product_data[item])

                            get_mat_id = "SELECT id FROM material WHERE material_name=%s"
                            cursor.execute(get_mat_id, item)
                            mat_id = cursor.fetchone()
                            sql_mat_mov = "UPDATE material_movement SET txn_date=%s,amount=%s,txn_type=%s," \
                                          "purchase_id=%s WHERE sell_id=%s and mat_id=%s"
                            cursor.execute(sql_mat_mov, (new_date, -product_data[item],
                                                         'Sale','0', sell_id,mat_id['id']))
                            sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE " \
                                           "material_id=(SELECT id FROM material WHERE material_name=%s)"
                            cursor.execute(sql_quantity, (product_data[item], item))
                            # cursor.execute(sql_update_flag, item)
                        connection.commit()
                        update_sql = "UPDATE cash SET date_time=%s,ledger_id=%s, amount=%s WHERE sell_id=%s"
                        cursor.execute(update_sql, (date_time, ledger_id, totamt, sell_id))
                        connection.commit()

                        for item in product_data:
                            check_material = "SELECT quantity FROM material_qty WHERE material_id=(SELECT id from material WHERE material_name=%s)"
                            cursor.execute(check_material, (item))
                            data_checked = cursor.fetchone()
                            if int(data_checked['quantity']) < int(product_data[item]):
                                list_of_ofs_items.append(item)
                        flag = 'Successfully Sold {} to {} on {}' .format(product_name, ledger_name['ledger_name'], date_time) if not any(list_of_ofs_items) else 'Sold %s to %s on %s with Insufficient Materials - %s' % (product_name,ledger_name['ledger_name'],date_time,','.join(str(n) for n in list_of_ofs_items))
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('delete_billings'))
                    except Exception as e:
                        flag = "Failure with %s" % str(e)
                        flash(flag)
                        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                          utilities.get_ip(), utilities.get_mac())
                        return redirect(url_for('delete_billings'))
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
                    # for items in items_data:
                    #     items['sell_date'] = datetime.strptime(str(items['sell_date']), '%d-%m-%yyyy').strftime(
                    #     '%d-%m-%Y')
                    return render_template('view_billings.html', items_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


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
                    get_items = "SELECT sell_id,sell_date,l.ledger_name,p.product_name,quantity,rate,amount, s.added_by,s.ip_address,s.mac_id FROM sell s INNER join ledger l ON s.ledger_id = l.id INNER JOIN product_master p ON s.product_id=p.id"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                with connection.cursor() as cursor:
                    get_ledgers = "SELECT id,ledger_name FROM ledger"
                    cursor.execute(get_ledgers)
                    ledger_data = cursor.fetchall()

                    return render_template('delete_sell_items.html', items_data=items_data, ledger_data=ledger_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


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
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


@app.route('/receive_from_ledger')
def receive_from_ledger():
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
                    return render_template('receive_from_ledger.html', ledger_data=items_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


@app.route('/show_ledger_credit/<int:p_id>')
def show_ledger_credit(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_product_qty = "SELECT SUM(amount) AS Amount FROM cash WHERE ledger_id = %s"
                    cursor.execute(get_product_qty, p_id)
                    data = cursor.fetchone()
                    connection.close()
                    amt = int(data['Amount']) if data['Amount'] is not None else 0
                    return jsonify({'due': amt})
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


@app.route('/paid_to_ledger', methods=['POST'])
def paid_to_ledger():
    date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    ledger_id = int(request.form['ledgers_dat'])
    payamount = int(request.form['payamount'])
    comments = request.form['paycomments']
    if ledger_id == 0 or payamount <= 0 or comments == '':
        flag = "Invalid Data"
        flash(flag)
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'paid_to_ledger', str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
        return redirect(url_for('pay_to_ledger'))
    connection = connect_to_db()
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                insert_sql = "INSERT INTO cash(date_time, ledger_id, material_id, product_id, amount, comments) " \
                             "VALUES (%s,%s,NULL,NULL,%s,%s)"
                cursor.execute(insert_sql, (date_time, ledger_id, payamount, comments))
                connection.commit()
                flag = 'Payment entry was Successfully done at {}'.format(date_time)
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('pay_to_ledger'))
        except Exception as e:
            flag = "Failure with %s" % e
            flash(flag)
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return redirect(url_for('pay_to_ledger'))
        finally:
            connection.close()


@app.route('/received_from_ledger', methods=['POST'])
def received_from_ledger():
    date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    ledger_id = int(request.form['ledgers_dat'])
    payamount = int(request.form['payamount'])
    comments = request.form['paycomments']
    if ledger_id == 0 or payamount <= 0 or comments == '':
        flag = "Invalid Data"
        flash(flag)
        write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'receive_from_ledger', str(session['username']),
                          utilities.get_ip(), utilities.get_mac())
        return redirect(url_for('receive_from_ledger'))
    connection = connect_to_db()
    if connection.open == 1:
        # Populate ledger names from table
        try:
            with connection.cursor() as cursor:
                insert_sql = "INSERT INTO cash(date_time, ledger_id, material_id, product_id, amount, comments) " \
                             "VALUES (%s,%s,NULL,NULL,%s,%s)"
                cursor.execute(insert_sql, (date_time, ledger_id, -payamount, comments))
                connection.commit()
                connection.commit()
                flag = 'Payment entry was Successfully done at {}'.format(date_time)
                flash(flag)
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return redirect(url_for('receive_from_ledger'))
        except Exception as e:
            flag = "Failure with %s" % e
            flash(flag)
            return redirect(url_for('receive_from_ledger'))
        finally:
            connection.close()


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
                    get_items = "select c.id, DATE_FORMAT(c.date_time,'%d-%m-%Y') as date_time, l.ledger_name, m.material_name, pr.product_name, amount from cash c INNER join ledger l ON c.ledger_id = l.id LEFT JOIN material m ON m.id=c.material_id LEFT JOIN product_master pr ON pr.id=c.product_id WHERE c.product_id IS NOT NULL OR c.material_id IS NOT NULL"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('show_cash_report.html', items_data=items_data)

                # with connection.cursor() as cursor:
                #     get_items = "SELECT id,ledger_name FROM ledger"
                #     cursor.execute(get_items)
                #     ledger_data = cursor.fetchall()
                # with connection.cursor() as cursor:
                #     get_materials = "SELECT id,material_name FROM material"
                #     cursor.execute(get_materials)
                #     material_data = cursor.fetchall()
                #     return render_template('show_cash_report.html', ledger_data=ledger_data,
                #                            material_data=material_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


@app.route('/show_ledger_tx_report')
def show_ledger_tx_report():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate material names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "select c.id, DATE_FORMAT(c.date_time,'%d-%m-%Y') as date_time, l.ledger_name, " \
                                "c.amount from cash c INNER join ledger l ON c.ledger_id = l.id WHERE " \
                                "c.material_id IS NULL AND c.product_id IS NULL;"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    get_ledger = "SELECT id, ledger_name FROM ledger"
                    cursor.execute(get_ledger)
                    items_ledger_data = cursor.fetchall()
                    return render_template('show_ledger_transactions.html', items_data=items_data, items_ledger_data=items_ledger_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


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
                    get_items = "select c.id as id, DATE_FORMAT(c.date_time,'%d-%m-%y') as Transaction_Time, l.ledger_name as Ledger_Name, m.material_name as Material_Name, pr.product_name as Product_Name, ABS(c.amount) as Amount, CASE WHEN amount > 0 THEN 'DEBIT' WHEN amount < 0 THEN 'CREDIT' END AS Transaction_Type from cash c INNER join ledger l ON c.ledger_id = l.id LEFT JOIN material m ON m.id=c.material_id LEFT JOIN product_master pr ON pr.id=c.product_id;"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                with open(full_fname, 'w', newline='') as csvFile:
                    fields = ['id', 'Transaction_Time', 'Ledger_Name', 'Material_Name', 'Product_Name','Amount', 'Transaction_Type']
                    writer = csv.DictWriter(csvFile, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(items_data)
                csvFile.close()
                return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


# @app.route('/download_cash_report_by_entity_as_csv', methods=['POST'])
# def download_cash_report_by_entity_as_csv():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#
#         p_id = request.form['param']
#         filename = 'Cash_Report_{}.csv' .format(str(datetime.now().strftime("%Y%m%d%H%M%S")))
#         full_fname = app.config['UPLOAD_FOLDER'] + filename
#         connection = connect_to_db()
#         if connection.open == 1:
#             # Populate material names from table
#             try:
#                 with connection.cursor() as cursor:
#                     get_items = "select c.id as ID, DATE_FORMAT(c.date_time,'%d-%m-%y') as Transaction_Time, l.ledger_name as Ledger_Name, m.material_name AS Material_Name, pr.product_name as Product_Name, amount as Amount, CASE WHEN amount > 0 THEN 'SALE' WHEN amount < 0 THEN 'PURCHASE' END as Transaction_Type from cash c INNER join ledger l ON c.ledger_id = l.id LEFT JOIN material m ON m.id = c.material_id LEFT JOIN product_master pr ON pr.id=c.product_id WHERE (c.product_id IS NOT NULL OR c.material_id IS NOT NULL) AND c.ledger_id={}".format(p_id)
#                     cursor.execute(get_items)
#                     items_data = cursor.fetchall()
#                     connection.close()
#                 with open(full_fname, 'w', newline='') as csvFile:
#                     fields = ['ID', 'Transaction_Time', 'Ledger_Name', 'Material_Name', 'Product_Name','Amount', 'Transaction_Type']
#                     writer = csv.DictWriter(csvFile, fieldnames=fields)
#                     writer.writeheader()
#                     writer.writerows(items_data)
#                 csvFile.close()
#                 return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
#             except Exception as e:
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return str(e)


@app.route('/download_ledger_tx_report_as_csv' , methods=['POST'])
def download_ledger_tx_report_as_csv():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        filename = 'Ledger_Transaction_Report_{}.csv' .format(date_time)
        filename_tot = 'Ledger_Transaction_Report_Total_{}.csv' .format(date_time)
        full_fname = app.config['UPLOAD_FOLDER'] + filename
        full_fname_total = app.config['UPLOAD_FOLDER'] + filename_tot
        if request.method == 'POST':
            ledger_id = int(request.form['ledger_data'])
            txn_date = request.form['ledger_daterange']
            date_from = str(str(txn_date.split("-")[0]).replace(" ","")).split("/")
            date_to = str(str(txn_date.split("-")[1]).replace(" ","")).split("/")
            total_from_date = str(date_from[1]+'-'+date_from[0]+'-'+date_from[2]+' 00:00:00')
            total_to_date = str(date_to[1]+'-'+date_to[0]+'-'+date_to[2]+' 00:00:00')
            connection = connect_to_db()
            if connection.open == 1:
                # Populate material names from table
                try:
                    with connection.cursor() as cursor:
                        get_items = "select c.id, DATE_FORMAT(c.date_time,'%d-%m-%y') as Date_time, l.ledger_name as Ledger_Name,c.amount as Amount, CASE WHEN amount > 0 THEN 'DEBIT' WHEN amount < 0 THEN 'CREDIT' END AS Transaction_Type from cash c INNER join ledger l ON c.ledger_id = l.id WHERE (c.material_id IS NULL AND c.product_id IS NULL) AND c.ledger_id = {} AND DATE_FORMAT(c.date_time,'%d-%m-%Y %k:%i:%s') BETWEEN '{}' AND '{}'".format(ledger_id,total_from_date,total_to_date)
                        cursor.execute(get_items)
                        items_data = cursor.fetchall()
                        connection.close()
                    with open(full_fname, 'w', newline='') as csvFile:
                        fields = ['id', 'Date_time', 'Ledger_Name', 'Amount', 'Transaction_Type']
                        writer = csv.DictWriter(csvFile, fieldnames=fields)
                        writer.writeheader()
                        writer.writerows(items_data)
                        csvFile.close()
                    with open(full_fname, 'r', newline='') as csvFile, open(full_fname_total, "w") as csvFile2:
                        Reader = csv.reader(csvFile, delimiter=',')
                        writer = csv.writer(csvFile2)
                        print(Reader)
                        c = 1
                        Rows = list(Reader)
                        Tot_rows = len(Rows)
                        print(Tot_rows)
                        total=0
                        for row in Rows:
                            if c != 1:
                                r = row[3]
                                total = total + int(r)
                            c += 1
                        print(total)

                        # data = dict()
                        # data[Tot_rows+1][0] = 'Total'
                        # data[Tot_rows+1][1] = total
                        # print(data)
                        row_total = total
                        data = [{'Total'},{row_total}]
                        total_header = 'Total'

                        writer.writerows(data)
                        csvFile.close()
                        csvFile2.close()

                    return send_from_directory(app.config['UPLOAD_FOLDER'], filename_tot, as_attachment=True)
                except Exception as e:
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
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
                    get_product_qty = "SELECT pr.product_spec, s.quantity, s.amount,s.ledger_id FROM sell s INNER JOIN product_master pr ON s.product_id = pr.id WHERE sell_id=%s "
                    cursor.execute(get_product_qty, p_id)
                    data = cursor.fetchone()
                    new_data = product_manipulation(ast.literal_eval(data['product_spec']),1)
                    for item in new_data:
                        qty = new_data[item]
                        get_material_cdate = "SELECT closing_balance,mat_id FROM material_movement WHERE txn_date = (SELECT MAX(txn_date) FROM material_movement WHERE mat_id=(SELECT id FROM material WHERE material_name=%s))  AND mat_id=(SELECT id FROM material WHERE material_name=%s);"
                        cursor.execute(get_material_cdate, (item,item))
                        cdate = cursor.fetchone()
                        final_closing = int(cdate['closing_balance']) - int(qty)
                        sql_mat_mov = "INSERT INTO material_movement(mat_id,txn_date,opening_balance,closing_balance,txn_type) VALUES(%s,%s,%s,%s,%s)"
                        cursor.execute(sql_mat_mov,
                                       (cdate['mat_id'], date_time, cdate['closing_balance'], final_closing, 'Cancelled'))
                        sql_quantity = "UPDATE material_qty SET quantity = quantity + %s WHERE material_id=(SELECT id FROM material WHERE material_name=%s)"
                        cursor.execute(sql_quantity, (new_data[item], item))
                        connection.commit()
                    del_items = "DELETE FROM sell WHERE sell_id=%s"
                    cursor.execute(del_items, p_id)
                    connection.commit()
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), 'Deleted Sell ID-{}'.format(p_id), str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id, amount,comments)" \
                                 " VALUES (%s, %s,NULL,%s,%s,'Reversed')"
                    cursor.execute(insert_sql, (date_time, data['ledger_id'], p_id, -(data['amount'])))
                    connection.commit()
                    connection.close()
                    return redirect(url_for('delete_billings'))
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


# @app.route('/alteration_billings', methods=['POST'])
# def alteration_billings():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
#         mac = utilities.get_mac()
#         ip = utilities.get_ip()
#         if request.method == 'POST':
#             ledger_id = int(request.form['ledgers_dat'])
#             pdate = request.form['sdate']
#             product_id = request.form['products_dat']
#             qty_unit = int(request.form['qtykg']) if request.form['qtykg'] != "" else 0
#             product_id = request.form['sell_ids']
#             totamt = int(request.form['totamt']) if request.form['totamt'] != "" else 0
#             rate = int(request.form['recamt']) if request.form['recamt'] != "" else 0
#             if product_id == 0:
#                 flag = "Sell ID not selected."
#                 flash(flag)
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return redirect(url_for('alter_billing'))
#             elif qty_unit == 0 or pdate == "" or product_id == "" or totamt == 0:
#                 flag = "Invalid Data"
#                 flash(flag)
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag + 'alter_billing',
#                                   str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return redirect(url_for('alter_billing'))
#             else:
#                 connection = connect_to_db()
#                 with connection.cursor() as cursor:
#                     try:
#                         flag = 'y'
#                         get_product_name = "SELECT product_name,product_spec FROM component_master WHERE id=%s and component_flag=%s"
#                         cursor.execute(get_product_name, (product_id, flag))
#                         names = cursor.fetchone()
#                         product_data = product_manipulation(convertid2name(names['product_spec']), qty_unit)
#
#                         for item in product_data:
#                             # Get Material Movement
#                             get_material_cdate = "SELECT closing_balance,mat_id FROM material_movement WHERE txn_date = (SELECT MAX(txn_date) FROM material_movement WHERE mat_id=(SELECT id FROM material WHERE material_name=%s));"
#                             cursor.execute(get_material_cdate, item)
#                             cdate = cursor.fetchone()
#                             # Add Material Movement
#                             final_closing = int(cdate['closing_balance']) + int(product_data[item])
#                             sql_mat_mov = "INSERT INTO material_movement(mat_id,txn_date,opening_balance,closing_balance,txn_type) VALUES(%s,%s,%s,%s,%s)"
#                             cursor.execute(sql_mat_mov, (cdate['mat_id'], date_time, cdate['closing_balance'],
#                                                          final_closing, 'Sale'))
#                             sql_quantity = "UPDATE material_qty SET quantity = quantity - %s WHERE " \
#                                            "material_id=(SELECT id FROM material WHERE material_name=%s)"
#                             cursor.execute(sql_quantity, (product_data[item], item))
#                             # cursor.execute(sql_update_flag, item)
#                         connection.commit()
#                         sql = "INSERT INTO product_master(product_name,date_time,added_by,comments," \
#                               "product_spec,link_component_flag, product_rate,ip_address,mac_id) " \
#                               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#                         cursor.execute(sql,
#                                        (names['product_name'], date_time, str(session['username']), 'Directly Added',
#                                         str(product_data), product_id, rate, ip, mac))
#                         connection.commit()
#                         get_product_name = "SELECT MAX(id) as id FROM product_master"
#                         cursor.execute(get_product_name, )
#                         data_id = cursor.fetchone()
#                         get_ledger_name = "SELECT ledger_name FROM ledger WHERE id=%s"
#                         cursor.execute(get_ledger_name, ledger_id)
#                         ledger_name = cursor.fetchone()
#                         sql = "INSERT INTO sell(sell_date,ledger_id,product_id,quantity," \
#                               "rate, amount,added_by,ip_address,mac_id) " \
#                               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#                         cursor.execute(sql, (
#                         pdate, ledger_id, data_id['id'], qty_unit, rate, totamt, str(session['username']), ip, mac))
#                         connection.commit()
#
#                         insert_sql = "INSERT INTO cash(date_time,ledger_id, material_id, product_id,amount,comments) VALUES (%s, %s,NULL,%s,%s,'Money Received on Sell')"
#                         cursor.execute(insert_sql, (date_time, ledger_id, data_id['id'], totamt))
#                         connection.commit()
#                         for item in product_data:
#                             check_material = "SELECT quantity FROM material_qty WHERE material_id=(SELECT id from material WHERE material_name=%s)"
#                             cursor.execute(check_material, (item))
#                             data_checked = cursor.fetchone()
#                             if int(data_checked['quantity']) < int(product_data[item]):
#                                 list_of_ofs_items.append(item)
#                         flag = 'Successfully Sold {} to {} on {}'.format(names['product_name'],
#                                                                          ledger_name['ledger_name'],
#                                                                          date_time) if not any(
#                             list_of_ofs_items) else 'Sold %s to %s on %s with Insufficient Materials - %s' % (
#                         names['product_name'], ledger_name['ledger_name'], date_time,
#                         ','.join(str(n) for n in list_of_ofs_items))
#                         flash(flag)
#                         write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
#                                           utilities.get_ip(), utilities.get_mac())
#                         return redirect(url_for('direct_billing'))
#                     except Exception as e:
#                         flag = "Failure with %s" % str(e)
#                         flash(flag)
#                         write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), flag, str(session['username']),
#                                           utilities.get_ip(), utilities.get_mac())
#                         return redirect(url_for('direct_billing'))
#                     finally:
#                         connection.close()


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
                    for items in items_data:
                        items['date_time'] = datetime.strptime(str(items['date_time']), '%Y%m%d%H%M%S').strftime(
                            '%d-%m-%Y')
                        dict_data = ast.literal_eval(items['product_spec'])
                        for material in dict_data:
                            get_item_unit = "SELECT sub_unit FROM material WHERE id=%s"
                            cursor.execute(get_item_unit, material)
                            items_unit_data = cursor.fetchone()
                            value = str(ast.literal_eval(items['product_spec'])[material]) + str(items_unit_data['sub_unit'])
                            dict_data[material] = value
                    # dict_data = ast.literal_eval(items['product_spec'])
                        named_item = convertid2name(str(dict_data))
                        named_item = str(json.dumps(named_item).replace('{', '')).replace('}', '').replace('\"',
                                                                                                           '').replace(
                            ':', ' -')
                        items['product_spec'] = named_item
                        list_data.append(items)
                    return render_template('delete_component_master.html', items_data=list_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
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
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), 'Deleted Component ID-{}'.format(p_id),
                                      str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())

                    for key in ast.literal_eval(fetched_data['product_spec']):
                        get_usage_data = "SELECT usage_flag FROM material WHERE id=%s"
                        cursor.execute(get_usage_data, key)
                        fetched_usage_data = cursor.fetchone()
                        usage_add = int(fetched_usage_data['usage_flag']) - 1
                        upd_items = 'UPDATE material SET usage_flag=%s WHERE id=%s' % (usage_add, key)
                        cursor.execute(upd_items)
                    connection.commit()
                    return redirect(url_for('delete_component_details'))
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


# @app.route('/show_mm_report')
# def show_mm_report():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         connection = connect_to_db()
#         if connection.open == 1:
#             # Populate material names from table
#             try:
#                 with connection.cursor() as cursor:
#                     # get_materials = "SELECT id, material_name FROM material"
#                     # cursor.execute(get_materials)
#                     # items_mat_data = cursor.fetchall()
#                     get_items = "select mv.id,m.material_name,mv.opening_balance, mv.closing_balance, mv.txn_type, DATE_FORMAT(mv.txn_date,'%d-%m-%Y') as date_and_time, diff from material_movement mv LEFT JOIN material m ON m.id=mv.mat_id;"
#                     cursor.execute(get_items)
#                     items_data = cursor.fetchall()
#                     connection.close()
#                     return render_template('show_material_movement.html', items_data=items_data,)
#             except Exception as e:
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return str(e)


@app.route('/download_mm_report_as_csv', methods=['POST'])
def download_mm_report_as_csv():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        filename = 'Material_Movement_{}.csv' .format(str(datetime.now().strftime("%Y%m%d%H%M%S")))
        full_fname = app.config['UPLOAD_FOLDER'] + filename
        if request.method == 'POST':
            material_id = int(request.form['items_mat_data'])
            txn_date = request.form['daterange']
            date_from = str(str(txn_date.split("-")[0]).replace(" ","")).split("/")
            date_to = str(str(txn_date.split("-")[1]).replace(" ","")).split("/")
            total_from_date = str(date_from[1]+'-'+date_from[0]+'-'+date_from[2]+' 00:00:00')
            total_to_date = str(date_to[1]+'-'+date_to[0]+'-'+date_to[2]+' 00:00:00')
            connection = connect_to_db()
            if connection.open == 1:
                # Populate material names from table
                try:
                    with connection.cursor() as cursor:
                        get_items = "select mv.id,m.material_name,mv.opening_balance, mv.closing_balance, mv.txn_type, DATE_FORMAT(mv.txn_date,'%d-%m-%y') as date_and_time, (mv.closing_balance-mv.opening_balance) as difference from material_movement mv LEFT JOIN material m ON m.id=mv.mat_id WHERE mv.mat_id={} AND DATE_FORMAT(mv.txn_date,'%d-%m-%Y %k:%i:%s') BETWEEN '{}' AND '{}'" .format(material_id,total_from_date,total_to_date)
                        cursor.execute(get_items)
                        items_data = cursor.fetchall()
                        connection.close()
                    with open(full_fname, 'w', newline='') as csvFile:
                        fields = ['id', 'material_name', 'opening_balance', 'closing_balance', 'difference', 'txn_type',
                                  'date_and_time']
                        writer = csv.DictWriter(csvFile, fieldnames=fields)
                        writer.writeheader()
                        writer.writerows(items_data)
                    csvFile.close()
                    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
                except Exception as e:
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    return str(e)


@app.route('/show_logs')
def show_logs():
    if session.get('username') is None and session.get('username') == 'superadmin':
        return redirect(url_for('login'))
    else:
        try:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                get_product_data = "SELECT id, DATE_FORMAT(txn_date,'%d-%m-%Y %k:%i:%s') as txn_date, txn_msg, added_by FROM log_data"
                cursor.execute(get_product_data)
                data = cursor.fetchall()
                return render_template('super_admin/show_logs.html', items_data=data)
        except Exception as e:
            return str(e)


@app.route('/show_cash_report_by_entity/<int:p_id>')
def show_cash_report_by_entity(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "select c.id, DATE_FORMAT(c.date_time,'%d-%m-%y') as date_time, l.ledger_name, m.material_name, pr.product_name, amount from cash c INNER join ledger l ON c.ledger_id = l.id LEFT JOIN material m ON m.id = c.material_id LEFT JOIN product_master pr ON pr.id=c.product_id WHERE (c.product_id IS NOT NULL OR c.material_id IS NOT NULL) AND c.ledger_id={}".format(p_id)
                    cursor.execute(get_items)
                    data = cursor.fetchall()
                    connection.close()
                    return jsonify({'dat1': data})
                    # return render_template('show_materials.html', items_data=data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


# @app.route('/delete_all_data')
# def delete_all_data():
#     if session.get('username') is None:
#         return redirect(url_for('login'))
#     else:
#         connection = connect_to_db()
#         if connection.open == 1:
#             # Populate billing from table
#             try:
#                 with connection.cursor() as cursor:
#                     get_items = "SELECT "
#                     cursor.execute(get_items)
#                     items_data = cursor.fetchall()
#                     connection.close()
#                     return render_template('delete_all_data.html', items_data=items_data)
#             except Exception as e:
#                 write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
#                                   utilities.get_ip(), utilities.get_mac())
#                 return str(e)


@app.route('/alter_billings')
def alter_billings():
    connection = ''
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        try:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                get_items = "SELECT sell_id from sell"
                cursor.execute(get_items)
                items_pur_data = cursor.fetchall()
            with connection.cursor() as cursor:
                get_items = "SELECT id, ledger_name from ledger"
                cursor.execute(get_items)
                items_ledger_data = cursor.fetchall()
            with connection.cursor() as cursor:
                get_items = "SELECT id,product_name from product_master"
                cursor.execute(get_items)
                items_products_data = cursor.fetchall()
            return render_template('alter_billings.html', sell_data=items_pur_data, ledger_data=items_ledger_data, product_data=items_products_data)
        except Exception as e:
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)
        finally:
            connection.close()


@app.route('/delete_ledger_tx')
def delete_ledger_tx():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate material names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "select c.id, DATE_FORMAT(c.date_time,'%d-%m-%Y') as date_time, l.ledger_name, " \
                                "c.amount from cash c INNER join ledger l ON c.ledger_id = l.id WHERE " \
                                "c.material_id IS NULL AND c.product_id IS NULL;"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    get_ledger = "SELECT id, ledger_name FROM ledger"
                    cursor.execute(get_ledger)
                    items_ledger_data = cursor.fetchall()
                    return render_template('delete_ledger_transactions.html', items_data=items_data, items_ledger_data=items_ledger_data)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)
            finally:
                connection.close()


@app.route('/del_ledger_data/<int:p_id>')
def del_ledger_data(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    del_items = "DELETE FROM cash WHERE id=%s"
                    cursor.execute(del_items, p_id)
                    connection.commit()
                    write_to_log_data(date_time, 'Deleted Cash ID-{}'.format(p_id),
                                      str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                    connection.close()
                    return redirect(url_for('delete_ledger_tx'))
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


@app.route('/process_edit_data/<int:p_id>', methods=['GET'])
def process_edit_data(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = ''
        # p_id = 12
        try:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                get_mat_comments = "select DATE_FORMAT(c.date_time,'%d-%m-%Y') as date_time, c.ledger_id, abs(amount) as amount from cash c LEFT JOIN material m ON m.id=c.material_id LEFT JOIN product_master pr ON pr.id=c.product_id WHERE c.id={}".format(p_id)
                cursor.execute(get_mat_comments)
                dat = cursor.fetchone()
                return jsonify({'date': dat['date_time'], 'ledger_name': dat['ledger_id'],'amount': dat['amount']})
        except Exception as e:
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)
        finally:
            connection.close()


@app.route('/process_edit_purchase_data/<int:p_id>', methods=['GET'])
def process_edit_purchase_data(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = ''
        # p_id = 12
        try:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                get_purchase_data = "SELECT p.purchased_id, p.purchased_date, p.ledger_id, p.quantity_unit, p.total_amount, p.quantity_sub_unit, p.sub_unit,p.unit, p.material_id, p.rate FROM purchased p WHERE purchased_id={}".format(p_id)
                cursor.execute(get_purchase_data)
                dat = cursor.fetchone()
                return jsonify({'id': dat['purchased_id'], 'purchased_date': dat['purchased_date'], 'ledger_id': dat['ledger_id'], 'quantity_unit': dat['quantity_unit'], 'total_amount': dat['total_amount'], 'quantity_sub_unit': dat['quantity_sub_unit'], 'sub_unit': dat['sub_unit'], 'unit': dat['unit'],'material_id': dat['material_id'],'rate': dat['rate']})
        except Exception as e:
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)
        finally:
            connection.close()


@app.route('/process_edit_sell_data/<int:p_id>', methods=['GET'])
def process_edit_sell_data(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = ''
        # p_id = 12
        try:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                get_sell_data = "SELECT sell_id,sell_date,ledger_id,p.product_name,quantity,rate,amount FROM sell s  INNER JOIN product_master p ON s.product_id=p.id WHERE sell_id={}".format(p_id)
                cursor.execute(get_sell_data)
                dat = cursor.fetchone()
                return jsonify({'sell_id': dat['sell_id'], 'sell_date': dat['sell_date'], 'ledger_name': dat['ledger_id'], 'product_name': dat['product_name'], 'quantity': dat['quantity'], 'rate': dat['rate'], 'amount': dat['amount']})
        except Exception as e:
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)
        finally:
            connection.close()


@app.route('/process_edit_ledger_data/<int:p_id>', methods=['GET'])
def process_edit_ledger_data(p_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = ''
        # p_id = 12
        try:
            connection = connect_to_db()
            with connection.cursor() as cursor:
                get_sell_data = "SELECT id, ledger_name, DATE_FORMAT(date_time,'%d-%m-%Y') as date_time, added_by, comments FROM ledger WHERE id={}".format(p_id)
                cursor.execute(get_sell_data)
                dat = cursor.fetchone()
                return jsonify({'ledger_id': dat['id'], 'creation_date': dat['date_time'],
                                'ledger_name': dat['ledger_name']})
        except Exception as e:
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)
        finally:
            connection.close()


@app.route('/ledger_tx_modification', methods=['POST'])
def ledger_tx_modification():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        ledger_data = None
        receiptid = None
        payment = None
        amount = None
        min = None
        try:
            connection = connect_to_db()
            if request.method == 'POST':
                ledger_id = request.form['ledger_data']
                receiptid = request.form['receiptid']
                date = datetime.strptime(str(request.form['min']), '%d-%m-%Y').strftime('%Y%m%d')+'000000'
                amount = int(request.form['amount'])
                payment = request.form['payment']
                if not ledger_id or not receiptid or not date or not amount or not payment:
                    flag = "Invalid Data"
                    write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), '{}- on ledger tx update'.format(flag),
                                      str(session['username']),
                                      utilities.get_ip(), utilities.get_mac())
                else:
                    with connection.cursor() as cursor:
                        upd_items = 'UPDATE cash SET ledger_id=%s, date_time=%s, amount=%s WHERE id=%s' % (ledger_id, date, amount if payment == "1" else -amount, receiptid)
                        cursor.execute(upd_items)
                        connection.commit()
                    return redirect(url_for('delete_ledger_tx'))
        except Exception as e:
            write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                              utilities.get_ip(), utilities.get_mac())
            return str(e)
        finally:
            connection.close()


@app.route('/show_material_movement', methods=['GET'])
def show_material_movement():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        connection = connect_to_db()
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    get_items = "select mv.id,m.material_name,mv.amount, mv.txn_type, mv.txn_date as date_and_time, purchase_id, sell_id from material_movement mv LEFT JOIN material m ON m.id=mv.mat_id ORDER BY date_and_time ASC"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    data = {'dat1': items_data}
                    all_data = arranged_dict_for_material_movement(data)
                    a = frame_material_moment(all_data)
                    return render_template('show_material_movement.html', items_data=a)
            except Exception as e:
                write_to_log_data(str(datetime.now().strftime("%Y%m%d%H%M%S")), str(e), str(session['username']),
                                  utilities.get_ip(), utilities.get_mac())
                return str(e)


def arranged_dict_for_material_movement(data):
    phrase = dict()
    data_level_one = data['dat1']
    leng = len(data_level_one)
    for item in range(0, leng, 1):
        item_name = str(data_level_one[item]['material_name'])
        if item_name not in phrase.keys():
            phrase[item_name] = {data_level_one[item]['date_and_time']: [data_level_one[item]['amount'],
                                                                         data_level_one[item]['id']]}
        else:
            phrase[item_name].update({data_level_one[item]['date_and_time']: [data_level_one[item]['amount'],
                                                                              data_level_one[item]['id']]})
    return phrase


def frame_material_moment(data):
    data_level_one = sorted(list(data))
    record = list()
    open_bal = 0
    for item in data_level_one:
        dates = data[item]
        date_list = list(dates)
        for rec_date in date_list:

            idx = date_list.index(rec_date)
            if idx == 0:
                # record['date'] = rec_date
                # record['material_name'] = item
                # record['opening_balance'] = '0'
                # record['closing_balance'] = dates[rec_date]
                date_only = str(rec_date[:-6])
                rec_date_old = datetime.strptime(date_only, '%Y%m%d').strftime("%d-%m-%Y")
                record.append({'date_and_time': rec_date_old, 'material_name': item, 'opening_balance': 0,
                               'closing_balance': int(dates[rec_date][0]) - 0, 'id': dates[rec_date][1],
                               'diff': int(dates[rec_date][0]) - 0,
                               'txn_type': 'Purchase' if int(dates[rec_date][0]) > 0 else 'Sale'})
            else:
                for i in range(0, len(record)):
                    open_bal = record[i]['closing_balance']
                opening_balance = open_bal
                closing_balance = int(dates[rec_date][0]) + opening_balance
                date_only = str(rec_date[:-6])
                rec_date_old = datetime.strptime(date_only, '%Y%m%d').strftime("%d-%m-%Y")
                record.append({'date_and_time': rec_date_old, 'material_name': item, 'opening_balance': opening_balance,
                               'closing_balance': closing_balance, 'id': dates[rec_date][1],
                               'diff': closing_balance - opening_balance,
                               'txn_type': 'Purchase' if int(dates[rec_date][0]) > 0 else 'Sale'})
    return record


if __name__ == '__main__':
    app.run(debug=True)
