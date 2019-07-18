from flask import Flask, render_template,redirect, url_for, request, flash, session, jsonify
import pymysql.cursors
from datetime import datetime
import utilities
import collections
import ast
app = Flask(__name__)
app.secret_key = 'dot tell me again'


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


@app.route('/material_creation', methods=['POST', 'GET'])
def material_creation():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        date_time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        mac = utilities.get_mac()
        ip = utilities.get_ip()
        if request.method == 'POST':
            material_name = request.form['materialname']
            unit = request.form['units']
            subunit = request.form['sub_units']
            comments = request.form['matcomments']
            if material_name == "":
                flag = "Invalid Data"
                flash(flag)
                return redirect(url_for('create_material'))
            else:
                connection = connect_to_db()
                with connection.cursor() as cursor:
                    try:
                        sql = "INSERT INTO material(material_name,unit,sub_unit,date_time,added_by,comments,ip_address,mac_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, (material_name, unit, subunit, date_time, str(session['username']), comments, ip, mac))
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


@app.route('/material_deletion',  methods=['POST', 'GET'])
def material_deletion():
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
                    del_items = "DELETE FROM material WHERE material_name=%s"
                    cursor.execute(del_items, material_name)
                    connection.commit()
                    connection.close()
                    flag = "Successfully deleted - {} at - {}" .format(material_name, datetime.now())
                    flash(flag)
                    return redirect(url_for('delete_material'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                return 'Exception'


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
        if material_name == "" and mat_comments == "":
            flash('Invalid Data. Please try again.')
            return redirect(url_for('modify_material'))
        if connection.open == 1:
            # Populate ledger names from table
            try:
                with connection.cursor() as cursor:
                    select_item = 'SELECT material_name FROM material WHERE id=%s'
                    cursor.execute(select_item, material_id)
                    item = cursor.fetchone()
                    if mat_comments and material_id and material_name == "":
                        upd_items = 'UPDATE material SET comments="%s" WHERE id=%s' % (mat_comments, material_id)
                    elif material_name and material_id:
                        upd_items = 'UPDATE material SET material_name="%s" WHERE id=%s' % (material_name, material_id)
                    else:
                        upd_items = 'UPDATE material SET material_name="%s", comments="%s" WHERE id=%s' % (material_name, mat_comments, material_id)
                    cursor.execute(upd_items)
                    connection.commit()
                    connection.close()
                    flag = "Successfully Updated - {} to {} at {}".format(item['material_name'], material_name, datetime.now())
                    flash(flag)
                    return redirect(url_for('modify_material'))
                    # return render_template('delete_ledger.html', items_data=items_data)
            except Exception as e:
                return str(e)


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
                    get_items = "SELECT id, material_name, comments FROM material"
                    cursor.execute(get_items)
                    items_data = cursor.fetchall()
                    connection.close()
                    return render_template('alter_material.html', items_data=items_data)
            except Exception as e:
                return 'Exception'


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
            return 'Exception'
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
            totamt = int(request.form['totamt'])
            rate = int(request.form['recamt'])

            if qty_unit == "" or pdate == "" or material == "" or qty_sub_unit == "" or rate == "":
                flag = "Invalid Data"
                flash(flag)
                return redirect(url_for('new_purchased_db'))
            else:
                connection = connect_to_db()
                with connection.cursor() as cursor:
                    try:
                        sql = "INSERT INTO purchased(purchased_date,ledger_id,unit,sub_unit," \
                              "quantity_unit, quantity_sub_unit,rate, total_amount, material_id, added_by,ip_address,mac_id) " \
                              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, (pdate, ledger_id, unit, subunit, qty_unit, qty_sub_unit, rate, totamt, material, str(session['username']), ip, mac))
                        connection.commit()
                        get_material_purchased = "SELECT id FROM material_qty WHERE material_id=%s"
                        cursor.execute(get_material_purchased, material)
                        data = cursor.fetchone()
                        if data is None:
                            sql_quantity = "INSERT INTO material_qty(material_id,quantity) VALUES(%s,%s)"
                            cursor.execute(sql_quantity, (material, qty_sub_unit))
                            connection.commit()
                        else:
                            sql_quantity = "UPDATE material_qty SET quantity = quantity + %s WHERE material_id=%s and id=%s"
                            cursor.execute(sql_quantity, (qty_sub_unit, material, str(data['id'])))
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


@app.route('/check_buildout')
def check_buildout():
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
                    return render_template('check_buildout.html', items_data=items_data)
            except Exception as e:
                return str(e)


@app.route('/buildout')
def buildout():
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
                    return render_template('buildout.html', items_data=items_data)
            except Exception as e:
                return str(e)


@app.route('/new_buildout_creation', methods=['POST', 'GET'])
def new_buildout_creation():
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
                return redirect(url_for('buildout'))
            else:
                data = dict()
                list_handler = list()
                if product_name == "" or product_color == "" or product_qty == "" or product_rate == "" or product_comments == "" or product_date == "":
                    flag = "Invalid Data"
                    flash(flag)
                    return redirect(url_for('buildout'))
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
                        redirect(url_for('buildout'))
                    return redirect(url_for('buildout'))
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
                                    return redirect(url_for('buildout'))
                        except Exception as e:
                            flag = "Failure with %s" % e
                            flash(flag)
                            return redirect(url_for('buildout'))
                        finally:
                            connection.close()
                        if any(list_of_ofs_items):
                            flag = "Insufficient Materials - %s " % str(list_of_ofs_items)
                            flash(flag)
                            return redirect(url_for('buildout'))


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
                # print(tempo)
                c = {tempo[key]: value for key, value in a.items()}
                # print(c)
                temp[i]['product_spec'] = c
            # print(temp)
            return render_template('show_product_details.html', items_data=temp)
    except Exception as e:
        return 'Exception'


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
            get_mat_comments = "SELECT comments FROM material where id=%s"
            cursor.execute(get_mat_comments, p_id)
            dat = cursor.fetchall()
            connection.close()
            return jsonify({'data': dat[0]['comments']})
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


if __name__ == '__main__':
    app.run(debug=True)