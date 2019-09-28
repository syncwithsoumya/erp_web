create table log_data(
id int NOT NULL AUTO_INCREMENT,
txn_date VARCHAR(20) NOT NULL,
txn_msg VARCHAR(1000) NOT NULL,
added_by varchar(50) NOT NULL,
ip_address varchar(20) NOT NULL,
mac_id varchar(20),
PRIMARY KEY (id)
);
create table units(
id int NOT NULL AUTO_INCREMENT,
date_time VARCHAR(15),
unit VARCHAR(20) NOT NULL,
PRIMARY KEY (id),
UNIQUE KEY(unit)
);
create table user_table(
id int NOT NULL AUTO_INCREMENT,
    user_name varchar(50) NOT NULL,
    Pass varchar(50) NOT NULL,
    device_id varchar(50) NOT NULL,
    ip varchar(50) NOT NULL,
    last_login varchar(50),
    ac_creation_date varchar(20),
    ac_created_by varchar(50),
    secret_key varchar(10),
    user_type varchar(10) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY(user_name)
    );
    
create table ledger(
id int NOT NULL AUTO_INCREMENT,
    ledger_name varchar(50) NOT NULL,
    date_time varchar(50) NOT NULL,
    added_by varchar(50) NOT NULL,
    comments varchar(50),
    ip_address varchar(20),
    mac_id varchar(20),
    PRIMARY KEY (id),
    UNIQUE KEY(ledger_name)
    );
create table material(
id int NOT NULL AUTO_INCREMENT,
    material_name varchar(50) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    sub_unit VARCHAR(20) NOT NULL,
    usage_flag VARCHAR(20) NOT NULL,
    date_time varchar(50) NOT NULL,
    added_by varchar(50) NOT NULL,
    comments varchar(50),
    ip_address varchar(20),
    mac_id varchar(20),
    PRIMARY KEY (id),
    UNIQUE KEY(material_name)
    );

    
create table component_master(
id int NOT NULL AUTO_INCREMENT,
    product_name varchar(50) NOT NULL,
    date_time varchar(50) NOT NULL,
    added_by varchar(50) NOT NULL,
    comments varchar(50),
    product_spec varchar(5000) NOT NULL,
    component_flag VARCHAR(2) NOT NULL,
    product_rate INTEGER(10) NOT NULL,
    ip_address varchar(20),
    mac_id varchar(20),
    PRIMARY KEY (id)
    );

create table product_master(
id int NOT NULL AUTO_INCREMENT,
    product_name varchar(50) NOT NULL,
    date_time varchar(50) NOT NULL,
    added_by varchar(50) NOT NULL,
    comments varchar(50),
    product_spec varchar(5000) NOT NULL,
    link_component_flag INT NOT NULL,
    product_rate INTEGER(10) NOT NULL,
    ip_address varchar(20),
    mac_id varchar(20),
    PRIMARY KEY (id)
    );
    
create table material_qty
(
ID int NOT NULL AUTO_INCREMENT,
material_id INTEGER(50) NOT NULL,
quantity INTEGER(50) NOT NULL,
PRIMARY KEY (id)
);

create table product_qty
(
ID int NOT NULL AUTO_INCREMENT,
product_name VARCHAR(50) NOT NULL,
quantity INTEGER(50) NOT NULL,
PRIMARY KEY (id),
UNIQUE KEY(product_name)
);

create table purchased
(
purchased_id int NOT NULL AUTO_INCREMENT,
    purchased_date varchar(50) NOT NULL,
    ledger_id INTEGER(50) NOT NULL,
    unit varchar(50) NOT NULL,
    sub_unit varchar(50) NOT NULL,
    quantity_unit INTEGER(50) NOT NULL,
	quantity_sub_unit INTEGER(50) NOT NULL,
    rate INTEGER(50) NOT NULL,
    total_amount INTEGER(50) NOT NULL,
    material_id INTEGER(50) NOT NULL,
    added_by varchar(50) NOT NULL,
    ip_address varchar(20),
    mac_id varchar(20),
    PRIMARY KEY (purchased_id)
    );

create table cash
(
id int NOT NULL AUTO_INCREMENT,
date_time VARCHAR(15),
ledger_id INTEGER(100) NOT NULL,
material_id INTEGER(100),
product_id INTEGER(100),
amount INTEGER(100) NOT NULL,
comments VARCHAR(1000),
purchased_id INTEGER(100),
sell_id INTEGER(100),
PRIMARY KEY (id)
);

create table sell
(
sell_id int NOT NULL AUTO_INCREMENT,
sell_date varchar(50) NOT NULL,
product_id INTEGER(100) NOT NULL,
quantity INTEGER(100) NOT NULL,
rate INTEGER(100) NOT NULL,
amount INTEGER(100) NOT NULL,
ledger_id INTEGER(50) NOT NULL,
added_by varchar(50) NOT NULL,
ip_address varchar(20),
mac_id varchar(20),
PRIMARY KEY (sell_id)
);

create table material_movement(
id int NOT NULL AUTO_INCREMENT,
mat_id int NOT NULL,
txn_date VARCHAR(20) NOT NULL,
amount INTEGER(200) NOT NULL,
txn_type VARCHAR(20) NOT NULL,
purchase_id int,
sell_id int,
PRIMARY KEY (id)
);