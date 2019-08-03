create database erp_web;
use erp_web;
create table erp_web.ledger(
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
create table erp_web.material(
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
create table erp_web.user_table(
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
    
create table erp_web.component_master(
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

create table erp_web.product_master(
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
    
create table erp_web.material_qty
(
ID int NOT NULL AUTO_INCREMENT,
material_id INTEGER(50) NOT NULL,
quantity INTEGER(50) NOT NULL,
PRIMARY KEY (id)
);

create table erp_web.product_qty
(
ID int NOT NULL AUTO_INCREMENT,
product_name VARCHAR(50) NOT NULL,
quantity INTEGER(50) NOT NULL,
PRIMARY KEY (id),
UNIQUE KEY(product_name)
);

create table erp_web.purchased
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

create table erp_web.cash
(
id int NOT NULL AUTO_INCREMENT,
date_time VARCHAR(15),
ledger_id INTEGER(100) NOT NULL,
material_id INTEGER(100),
product_id INTEGER(100),
amount INTEGER(100) NOT NULL,
comments VARCHAR(1000),
PRIMARY KEY (id)
);



create table erp_web.units(
id int NOT NULL AUTO_INCREMENT,
unit VARCHAR(20) NOT NULL,
PRIMARY KEY (id),
UNIQUE KEY(unit)
);

create table erp_web.sell
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
select * from erp_web.ledger;
select * from erp_web.material;
select * from erp_web.component_master;
select * from erp_web.product;
UPDATE erp_web.material SET usage_flag=0 WHERE id in (1,2,3);
select * from  erp_web.purchased;
select * from erp_web.material_qty;
select * from erp_web.product_qty;
select * from erp_web.units;
delete from erp_web.purchased where purchased_id in (1,2,3,4,5,6);
delete from erp_web.material_qty where id in (5);
delete from erp_web.purchased where purchased_id in (7,8);
SELECT purchased_id, purchased_date, s.ledger_name, quantity_KG, total_amount, receive_amount, no_of_piece, m.material_name, added_by FROM erp_web.purchased p, (select ledger_name from erp_web.ledger where id IN (SELECT ledger_id from erp_web.purchased)) s,(select material_name from erp_web.material where id IN (SELECT material_id from erp_web.purchased)) m;
SELECT s.* FROM (select ledger_name from weledger where id = 7 ) s;
rollback;
SELECT purchased_id, purchased_date, l.ledger_name, quantity_KG, total_amount, receive_amount, no_of_piece, m.material_name, p.added_by  FROM erp_web.purchased p INNER JOIN erp_web.ledger l ON p.ledger_id = l.id INNER JOIN erp_web.material m ON p.material_id = m.id;
select m.material_name, q.quantity from erp_web.material_qty q INNER JOIN erp_web.material m ON q.material_id = m.id;

delete from erp_web.ledger where id in (12,13,14,15);
delete from erp_web.material where id in (9,10,11,12);
delete from erp_web.product where id in (1,2,3,4,5,6);
drop table erp_web.material;
drop table erp_web.ledger;
drop table erp_web.product_master;
drop table erp_web.component_master;
drop table erp_web.product_qty;
drop table erp_web.cash;
drop table erp_web.purchased;
drop table erp_web.sell;
drop table erp_web.material_qty;
SELECT purchased_id, purchased_date, l.ledger_name, p.quantity_unit, total_amount, rate, quantity_sub_unit, m.material_name, p.added_by  FROM erp_web.purchased p INNER JOIN erp_web.ledger l ON p.ledger_id = l.id INNER JOIN erp_web.material m ON p.material_id = m.id;
drop table erp_web.material_qty;
alter table erp_web.product_qty CHANGE product_id product_name varchar(1000);
alter table erp_web.product ADD COLUMN component_flag VARCHAR(2) AFTER product_rate;
select * from erp_web.sell;
select * from erp_web.cash;

delete from erp_web.sell where sell_id in (1,2,3,4,5,6,7);
SELECT sell_id,sell_date,l.ledger_name,p.product_name,quantity,rate,amount, s.added_by,s.ip_address,s.mac_id FROM erp_web.sell s INNER join erp_web.ledger l ON s.ledger_id = l.id INNER JOIN erp_web.product p ON s.product_id=p.id;
SELECT id, product_name,product_rate,product_spec,added_by FROM erp_web.product WHERE component_flag='y';
DELETE FROM erp_web.material WHERE material_name='dfhd' AND usage_flag != 'N';
select * from erp_web.cash;
select c.date_time, l.ledger_name, amount from erp_web.cash c INNER join erp_web.ledger l ON c.ledger_id = l.id;
select c.id as id, c.date_time as Entry_Time, l.ledger_name as Ledger_Name, c.amount as Amount, CASE WHEN amount > 0 THEN 'DEBIT' WHEN amount < 0 THEN 'CREDIT' END AS Transaction_Type from erp_web.cash c INNER join erp_web.ledger l ON c.ledger_id = l.id;
SELECT pr.product_spec,s.quantity,s.amount FROM erp_web.sell s INNER JOIN erp_web.product pr ON s.product_id = pr.id WHERE sell_id=4;

select c.id, c.date_time, l.ledger_name, material_id, product_id, amount from erp_web.cash c INNER join erp_web.ledger l ON c.ledger_id = l.id RIGHT JOIN material m ON m.id=c.material_id;