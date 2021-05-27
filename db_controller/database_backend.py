# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later

PostgreSQL DB backend.

Each one of the CRUD operations should be able to open a database connection if
there isn't already one available (check if there are any issues with this).

Documentation:
    About the Basic Product Store data on the database to generate CRUD operations from endpoint of the API:
    - Insert Store data
    - Update Store data
    - Delete Store data
    - Search Store data by ID
    - Search Store data by Status

    About the User to authenticate request endpoints on the API adding security to the operations:
    - Validate user data
    - Insert user data
    - Update user password hashed
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A19.1 ($Rev: 1 $)"

import json
import logging
from datetime import datetime

import psycopg2
from sqlalchemy import Column, String, Numeric, Boolean
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

from db_controller import mvc_exceptions as mvc_exc
from logger_controller.logger_control import *
from model.StoreModel import StoreModel
from model.ProductModel import ProductModel
from utilities.Utility import Utility as Util

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

Base = declarative_base()
logger = configure_db_logger()


# Datos de conecxion a base de datos
def init_connect_db():
    r"""
    Contiene la inicializacion de datos para conectar a base de datos.
    :return: list_data_cnx
    """
    init_cnx_db_data = []

    cfg = Util.get_config_constant_file()

    # TEST:
    db_host = cfg['DB_RDS']['HOST_DB']
    db_username = cfg['DB_RDS']['USER_DB']
    db_password = cfg['DB_RDS']['PASSWORD_DB']
    db_port = cfg['DB_RDS']['PORT_DB']
    db_driver = cfg['DB_RDS']['SQL_DRIVER']
    db_name = cfg['DB_RDS']['DATABASE_NAME']

    data_connection = [db_host, db_username, db_password, db_port, db_name]

    init_cnx_db_data.append(data_connection)

    return data_connection


def session_to_db():
    r"""
    Get and manage the session connect to the database engine.

    :return connection: Object to connect to the database and transact on it.
    """

    data_bd_connection = init_connect_db()

    connection = None

    try:

        if data_bd_connection:

            connection = psycopg2.connect(user=data_bd_connection[1],
                                          password=data_bd_connection[2],
                                          host=data_bd_connection[0],
                                          port=data_bd_connection[3],
                                          database=data_bd_connection[4])

        else:
            logger.error('Some data is not established to connect PostgreSQL DB. Please verify it!')

    except (Exception, psycopg2.Error) as error:
        logger.exception('Can not connect to database, verify data connection to %s', data_bd_connection[4],
                         error, exc_info=True)
        raise mvc_exc.ConnectionError(
            '"{}" Can not connect to database, verify data connection to "{}".\nOriginal Exception raised: {}'.format(
                data_bd_connection[0], data_bd_connection[4], error
            )
        )

    return connection


def scrub(input_string):
    """Clean an input string (to prevent SQL injection).

    Parameters
    ----------
    input_string : str

    Returns
    -------
    str
    """
    return "".join(k for k in input_string if k.isalnum())


def create_cursor(conn):
    r"""
    Create an object statement to transact to the database and manage his data.

    :param conn: Object to connect to the database.
    :return cursor: Object statement to transact to the database with the connection.

    """
    try:
        cursor = conn.cursor()

    except (Exception, psycopg2.Error) as error:
        logger.exception('Can not create the cursor object, verify database connection', error, exc_info=True)
        raise mvc_exc.ConnectionError(
            'Can not connect to database, verify data connection.\nOriginal Exception raised: {}'.format(
                error
            )
        )

    return cursor


def disconnect_from_db(conn):
    r"""
    Generate close session to the database through the disconnection of the conn object.

    :param conn: Object connector to close session.
    """

    if conn is not None:
        conn.close()


def close_cursor(cursor):
    r"""
    Generate close statement to the database through the disconnection of the cursor object.

    :param cursor: Object cursor to close statement.
    """

    if cursor is not None:
        cursor.close()


def get_datenow_from_db():
    r"""
    Get the current date and hour from the database server to set to the row registered or updated.

    :return last_updated_date: The current day with hour to set the date value.
    """

    conn = None
    cursor = None
    last_updated_date = None
    sql_nowdate = ''

    try:

        sql_nowdate = 'SELECT now()'

        conn = session_to_db()
        cursor = create_cursor(conn)

        cursor.execute(sql_nowdate)

        result = cursor.fetchall()

        if result is not None:
            last_updated_date = result

        cursor.close()

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database.".format(error)
        )
    finally:
        disconnect_from_db(conn)

    return last_updated_date


def exists_row_registered(table_name, column_name, data_find):
    r"""
    Looking for a user by name on the database to valid authentication.

    :param table_name:
    :param column_name: The column name to valid existence on the db.
    :param data_find: The data to filter and looking for if a row exists registered.
    :return result: Boolean to valid if the data exists on the table.
    """

    conn = session_to_db()

    cursor = create_cursor(conn)

    sql_check = "SELECT EXISTS(SELECT 1 FROM {} WHERE {} = {} LIMIT 1)".format(table_name, column_name, data_find)

    cursor.execute(sql_check)

    result = cursor.fetchone()[0]

    close_cursor(cursor)
    disconnect_from_db(conn)

    return result


def exists_data_row(table_name, column_name, column_filter1, value1, column_filter2, value2):
    r"""
    Transaction that validates the existence and searches for a certain record in the database.

    :param table_name: The table name to looking for data.
    :param column_name: The name of the column to find existence.
    :param column_filter1: The name of the first column filter to looking for data.
    :param value1: The value of the first filter to looking for data.
    :param column_filter2: The name of the next column filter to looking for data.
    :param value2: The value of the next filter to looking for data.
    :return row_data: The data if row exists.
    """

    conn = None
    cursor = None
    row_data = None

    try:
        conn = session_to_db()
        cursor = create_cursor(conn)

        sql_exists = f"SELECT {column_name} FROM {table_name} " \
                     f"WHERE {column_filter1} = {value1} AND {column_filter2} = '{value2}'"

        cursor.execute(sql_exists)

        row_exists = cursor.fetchall()

        for r_e in row_exists:

            logger.info('Row Info in Query: %s', str(r_e))

            if r_e is None:
                r_e = None
            else:
                row_data = r_e[column_name]

            # row_exists.close()

            close_cursor(cursor)

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, table_name)
        )
    finally:
        disconnect_from_db(conn)

    return row_data


def validate_transaction(table_name,
                         column_name,
                         column_filter1, value1,
                         column_filter2, value2,
                         column_filter3, value3):
    r"""
    Transaction that validates the existence and searches for a certain record in the database.

    :param table_name: The table name to looking for data.
    :param column_name: The name of the column to find existence.
    :param column_filter1: The name of the first column filter to looking for data.
    :param value1: The value of the first filter to looking for data.
    :param column_filter2: The name of the next column filter to looking for data.
    :param value2: The value of the next filter to looking for data.
    :param column_filter3: The name of the next column filter to looking for data.
    :param value3: The value of the next filter to looking for data.
    :return row_data: The data if row exists.
    """

    conn = None
    cursor = None
    row_data = None

    try:
        conn = session_to_db()
        cursor = create_cursor(conn)

        sql_exists = 'SELECT {} FROM {} WHERE {} = {} AND {} = {} AND {} = {}'.format(column_name, table_name,
                                                                                      column_filter1, value1,
                                                                                      column_filter2,
                                                                                      "'" + value2 + "'",
                                                                                      column_filter3,
                                                                                      "'" + value3 + "'")

        cursor.execute(sql_exists)

        row_exists = cursor.fetchall()

        for r_e in row_exists:

            logger.info('Row Info in Query: %s', str(r_e))

            if r_e is None:
                r_e = None
            else:
                row_data = r_e[column_name]

            close_cursor(cursor)

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, table_name)
        )
    finally:
        disconnect_from_db(conn)

    return row_data


class StoreModelDb(Base):
    r"""
    Class to instance the data of a Store on the database.
    Transactions:
     - Insert: Add Van data to the database if not exists.
     - Update: Update Van data on the database if exists.
    """

    cfg = Util.get_config_constant_file()

    __tablename__ = cfg['DB_OBJECTS']['STORE_TABLE']

    id_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['ID_STORE'], Numeric, primary_key=True)
    name_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_NAME'], String)
    code_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_CODE'], String)
    street_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_STREET_ADDRESS'], String)
    external_number_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_NUMBER_EXT_ADDRESS'], String)
    suburb_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_SUBURB_ADDRESS'], String)
    city_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_CITY_ADDRESS'], String)
    country_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_COUNTRY_ADDRESS'], String)
    postal_code_store = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_POSTAL_CODE'], String)
    minimum_stock = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['STORE_MIN_STOCK'], Numeric)
    creation_date = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['CREATION_DATE'], String)
    last_update_date = Column(cfg['DB_COLUMNS_DATA']['STORE_API']['LAST_UPDATE_DATE'], String)

    def manage_store_data(self, store_obj):

        store_data = {}

        store_dict = Util.set_data_input_store_dict(store_obj)

        if exists_data_row(self.__tablename__,
                           self.id_store,
                           self.id_store,
                           store_dict.get("store_id"),
                           self.code_store,
                           store_dict.get("store_code")):

            store_data = update_store_data(store_dict)
        else:
            store_data = insert_new_store(store_dict)

        return store_data


# Add Store data to insert the row on the database
def insert_new_store(data_store):
    r"""
    Transaction to add data of a store and inserted on database.
    The data that you can insert are:

    :param data_store: Store object model to add new store data.
    :return store_data_inserted: Dictionary that contains Store data inserted on db.
    """

    conn = None
    cursor = None
    store_data_inserted = dict()

    cfg = Util.get_config_constant_file()

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        table_name = cfg['DB_OBJECTS']['STORE_TABLE']

        created_at = get_datenow_from_db()
        last_update_date = get_datenow_from_db()

        store_id = data_store.get("store_id")
        store_code = data_store.get("store_code")
        store_name = data_store.get("store_name")
        store_street_address = data_store("street_address")
        store_external_number = data_store("external_number_address")
        store_suburb_address = data_store.get("suburb_address")
        store_city_address = data_store.get("city_address")
        store_country_address = data_store.get("country_address")
        store_zippostal_code = data_store.get("zip_postal_code_address")
        store_min_inventory = data_store.get("minimum_inventory")

        if not Util.validate_store_code_syntax(store_code):
            logger.error('Can not read the recordset: {}, because the store code is not valid: {}'.format(store_code,
                                                                                                          table_name))
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    store_id, table_name
                )
            )

        data_insert = (store_id, store_code, store_name, store_external_number, store_street_address,
                       store_suburb_address, store_city_address, store_country_address, store_zippostal_code,
                       store_min_inventory,)

        sql_store_insert = 'INSERT INTO {} ' \
                           '(id_store, ' \
                           'store_name, ' \
                           'store_code, ' \
                           'store_street_address, ' \
                           'store_external_number, ' \
                           'store_suburb_address, ' \
                           'store_city_address, ' \
                           'store_country_address, ' \
                           'store_zippostal_code, ' \
                           'store_min_inventory, ' \
                           'creation_date, ' \
                           'last_update_date) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(table_name)

        cursor.execute(sql_store_insert, data_insert)

        conn.commit()

        logger.info('Store inserted %s', "{0}, Code: {1}, Name: {2}".format(store_id, store_code, store_name))

        close_cursor(cursor)

        row_exists = validate_transaction(table_name,
                                          'id_store',
                                          'id_store', store_id,
                                          'store_code', store_code,
                                          'store_name', store_name)

        address_store = Util.format_store_address(store_street_address,
                                                  store_external_number,
                                                  store_suburb_address,
                                                  store_zippostal_code,
                                                  store_city_address,
                                                  store_country_address)

        store_data_inserted = {
            "IdStore": store_id,
            "CodeStore": store_code,
            "NameStore": store_name,
            "AddressStore": address_store,
            "MinimumStock": store_min_inventory,
            "CreationDate": created_at,
            "Message": "Store Inserted Successful",
        }

        if not str(store_id) not in str(row_exists):
            store_data_inserted = {
                "IdStore": store_id,
                "CodeStore": store_code,
                "NameStore": store_name,
                "AddressStore": address_store,
                "MinimumStock": store_min_inventory,
                "CreationDate": created_at,
                "Message": "Store already Inserted",
            }

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception was occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, table_name)
        )
    finally:
        disconnect_from_db(conn)

    return json.dumps(store_data_inserted)


# Update Store data registered
def update_store_data(data_store):
    r"""
    Transaction to update data of a store registered on database.
    The data that you can update are:

    :param data_store: Dictionary of all data store to update.
    :return store_data_updated: Dictionary that contains Store data updated on db.
    """

    conn = None
    cursor = None
    store_data_updated = dict()

    cfg = Util.get_config_constant_file()

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        last_update_date = get_datenow_from_db()

        table_name = cfg['DB_OBJECTS']['STORE_TABLE']

        # store_id = data_store.get("store_id")
        store_code = data_store.get("store_code")
        store_name = data_store.get("store_name")
        street_address = data_store("street_address")
        external_number_address = data_store("external_number_address")
        suburb_address = data_store.get("suburb_address")
        city_address = data_store.get("city_address")
        country_address = data_store.get("country_address")
        zip_postal_code_address = data_store.get("zip_postal_code_address")
        minimum_stock = data_store.get("minimum_inventory")

        store_id = select_store_id(store_code)

        # update row to database
        sql_update_store = 'UPDATE {} ' \
                           'SET store_name=%s, ' \
                           'store_street_address=%s, ' \
                           'store_external_number=%s, ' \
                           'store_suburb_address=%s, ' \
                           'store_city_address=%s, ' \
                           'store_country_address=%s, ' \
                           'store_zippostal_code=%s, ' \
                           'store_min_inventory=%s, ' \
                           'last_update_date=%s ' \
                           'WHERE id_store=%s AND store_code=%s'.format(table_name)

        cursor.execute(sql_update_store, (store_name,
                                          street_address,
                                          external_number_address,
                                          suburb_address,
                                          city_address,
                                          country_address,
                                          zip_postal_code_address,
                                          minimum_stock,))

        address_store = Util.format_store_address(street_address,
                                                  external_number_address,
                                                  suburb_address,
                                                  zip_postal_code_address,
                                                  city_address,
                                                  country_address)

        conn.commit()

        close_cursor(cursor)

        row_exists = validate_transaction(table_name,
                                          'id_store',
                                          'id_store', store_id,
                                          'store_code', store_code,
                                          'store_name', store_name)

        store_data_updated = {
            "IdStore": store_id,
            "CodeStore": store_code,
            "NameStore": store_name,
            "AddressStore": address_store,
            "MinimumStock": minimum_stock,
            "LastUpdateDate": last_update_date,
            "Message": "Store Updated Successful",
        }

        if not str(store_id) in str(row_exists):
            store_data_updated = {
                "IdStore": store_id,
                "CodeStore": store_code,
                "NameStore": store_name,
                "AddressStore": address_store,
                "MinimumStock": minimum_stock,
                "LastUpdateDate": last_update_date,
                "Message": "Store not updated",
            }

            logger.error('Can not read the recordset: {}, because is not stored on table: {}'.format(store_id,
                                                                                                      table_name))
            raise SQLAlchemyError(
                "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(table_name)
            )

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, table_name)
        )
    finally:
        disconnect_from_db(conn)

    return json.dumps(store_data_updated)


# Delete store registered by id
def delete_store_data(store_code):
    r"""
    Transaction to delete a Store data registered on database from his code.

    :param store_code: Code to looking for a Store data to delete.
    :return store_data_delete: Dictionary contains Van data deleted.
    """

    conn = None
    cursor = None
    store_data_deleted = dict()

    cfg = Util.get_config_constant_file()

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        table_name = cfg['DB_OBJECTS']['STORE_TABLE']

        store_id = select_store_id(store_code)

        # delete row to database
        sql_delete_van = "DELETE FROM {} WHERE id_store=%s AND store_code=%s".format(table_name)

        cursor.execute(sql_delete_van, (store_id, store_code,))

        conn.commit()

        close_cursor(cursor)

        store_data_deleted = {
            "IdStore": store_id,
            "CodeStore": store_code,
            "Message": "Store Deleted Successful",
        }

        row_exists = exists_data_row(table_name,
                                     'id_store',
                                     'id_store', store_id,
                                     'store_code', store_code)

        if str(store_id) in str(row_exists):
            store_data_deleted = {
                "IdStore": store_id,
                "CodeStore": store_code,
                "Message": "Store not deleted",
            }

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, table_name)
        )
    finally:
        disconnect_from_db(conn)

    return json.dumps(store_data_deleted)


# Select all data store by store code from db
def select_by_store_code(store_code):
    r"""
    Get all the Store's data looking for specific store code on database.

    :param store_code: The code of the store to looking for his data.
    :return data_store_by_code: Dictionary that contains all the Store's data by specific code.
    """

    conn = None
    cursor = None

    store_data_by_code = []
    data_store_all = dict()

    cfg = Util.get_config_constant_file()

    try:

        conn = session_to_db()

        cursor = create_cursor(conn)

        table_name = cfg['DB_OBJECTS']['STORE_TABLE']

        if not Util.validate_store_code_syntax(store_code):
            logger.error('Can not read the recordset: {}, because the store code is not valid: {}'.format(store_code,
                                                                                                          table_name))
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    store_code, table_name
                )
            )

        sql_store_by_code = " SELECT id_store, " \
                            "        store_name, " \
                            "        store_code, " \
                            "        store_street_address, " \
                            "        store_external_number, " \
                            "        store_suburb_address, " \
                            "        store_city_address, " \
                            "        store_country_address, " \
                            "        store_zippostal_code, " \
                            "        store_min_inventory, " \
                            "        creation_date, " \
                            "        last_update_date" \
                            " FROM {}" \
                            " WHERE store_code = %s".format(table_name)

        cursor.execute(sql_store_by_code, (store_code,))

        result = cursor.fetchall()

        if result is None:
            logger.error('Can not read the recordset, because is not stored: %s', store_code)
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    store_code, table_name
                )
            )

        for store_data in result:
            if store_data is None:
                logger.error('Can not read the recordset: {}, '
                             'because is not stored on table: {}'.format(store_code, table_name))
                raise SQLAlchemyError(
                    "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(table_name)
                )

            id_store = store_data['id_store']
            name_store = store_data['store_name']
            code_store = store_data['store_code']
            street_address = store_data['store_street_address']
            external_number_address = store_data['store_external_number']
            suburb_address = store_data['store_suburb_address']
            city_address = store_data['store_city_address']
            country_address = store_data['store_country_address']
            zip_postal_code_address = store_data['store_zippostal_code']
            minimum_stock = store_data['store_min_inventory']
            fecha_creacion = datetime.strptime(str(store_data['creation_date']), "%Y-%m-%d %H:%M:%S")
            fecha_actualizacion = datetime.strptime(str(store_data['last_update_date']), "%Y-%m-%d %H:%M:%S")

            address_store = Util.format_store_address(street_address,
                                                      external_number_address,
                                                      suburb_address,
                                                      zip_postal_code_address,
                                                      city_address,
                                                      country_address)

            logger.info('Store Registered: %s', 'IdStore: {}, '
                                                'CodeStore: {}, '
                                                'NameStore: {}, '
                                                'AddressStore: {}, '
                                                'MinimumStock: {}, '
                                                'CreationDate: {} '.format(id_store,
                                                                           code_store,
                                                                           name_store,
                                                                           address_store,
                                                                           minimum_stock,
                                                                           fecha_creacion))

            store_data_by_code += [{
                "Store": {
                    "IdStore": id_store,
                    "CodeStore": code_store,
                    "NameStore": name_store,
                    "AddressStore": address_store,
                    "MinimumStock": minimum_stock,
                    "CreationDate": fecha_creacion,
                    "LastUpdateDate": fecha_actualizacion,
                }
            }]

        close_cursor(cursor)

        data_store_all = json.dumps(store_data_by_code)

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, table_name)
        )
    finally:
        disconnect_from_db(conn)

    return data_store_all


# Select stock in specific product by store code
def select_stock_in_product(store_code, product_sku):
    r"""
    Get the store stock in a single product looking for by product sku.

    :param product_sku: SKU of product to find stock in a store.
    :param store_code: The store code to looking for stock by product sku
    :return data_van_by_status: Dictionary that contains all the Van's data by specific status.
    """

    cfg = Util.get_config_constant_file()

    conn = None
    cursor = None

    stock_data_by_sku = []
    data_stock_all = dict()

    store_table = cfg['DB_OBJECTS']['STORE_TABLE']
    product_table = cfg['DB_OBJECTS']['PRODUCT_TABLE']

    try:

        conn = session_to_db()

        cursor = create_cursor(conn)

        sql_stock_by_sku = " SELECT " \
                           "   store.store_code, " \
                           "   store.store_name, " \
                           "   prod.product_sku, " \
                           "   prod.product_stock " \
                           " FROM {} store, {} prod " \
                           " WHERE store.id_store = prod.product_store_id " \
                           " AND store.store_code = %s " \
                           " AND prod.product_sku = %s".format(store_table, product_table)

        cursor.execute(sql_stock_by_sku, (store_code, product_sku,))

        result = cursor.fetchall()

        if not Util.validate_store_code_syntax(store_code):
            logger.error('Can not read the recordset: {}, because the store code is not valid'.format(store_code))

        if result is None:
            logger.error('Can not read the recordset: {}, '
                         'because is not stored on table: {}'.format(store_code, store_table))
            raise SQLAlchemyError(
                "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(store_table)
            )

        for stock_data in result:
            code_store = stock_data['store_code']
            name_store = stock_data['store_name']
            sku_product = stock_data['product_sku']
            stock_product = stock_data['product_stock']

            logger.info('Product Stock: %s', 'CodeStore: {}, '
                                             'NameStore: {}, '
                                             'SKU: {}, '
                                             'Stock: {} '.format(code_store,
                                                                 name_store,
                                                                 sku_product,
                                                                 stock_product))

            stock_data_by_sku += [{
                "ProductStock": {
                    "CodeStore": code_store,
                    "NameStore": name_store,
                    "SKU": sku_product,
                    "Stock": stock_product,
                }
            }]

        close_cursor(cursor)

        data_stock_all = json.dumps(stock_data_by_sku)

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {} - {}.".format(error,
                                                                                                       store_table,
                                                                                                       product_table)
        )
    finally:
        disconnect_from_db(conn)

    return data_stock_all


# Select all stock in specific product code
def select_all_stock_in_product(product_sku):
    r"""
    Get the store stock in a single product looking for by product sku.

    :param product_sku: SKU of product to find stock in a store.
    :return data_van_by_status: Dictionary that contains all the Van's data by specific status.
    """

    cfg = Util.get_config_constant_file()

    conn = None
    cursor = None

    stock_data_by_sku = []
    data_stock_all = dict()

    store_table = cfg['DB_OBJECTS']['STORE_TABLE']
    product_table = cfg['DB_OBJECTS']['PRODUCT_TABLE']

    try:

        conn = session_to_db()

        cursor = create_cursor(conn)

        sql_stock_by_sku = " SELECT " \
                           "   store.store_code, " \
                           "   store.store_name, " \
                           "   prod.product_sku, " \
                           "   prod.product_stock " \
                           " FROM {} store, {} prod " \
                           " WHERE store.id_store = prod.product_store_id " \
                           " AND prod.product_sku = %s".format(store_table, product_table)

        cursor.execute(sql_stock_by_sku, (product_sku,))

        result = cursor.fetchall()

        if result is None:
            logger.error('Can not read the recordset: {}, '
                         'because is not stored on table: {}'.format(product_sku, product_table))
            raise SQLAlchemyError(
                "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(product_table)
            )

        for stock_data in result:
            code_store = stock_data['store_code']
            name_store = stock_data['store_name']
            sku_product = stock_data['product_sku']
            stock_product = stock_data['product_stock']

            logger.info('Product Stock: %s', 'CodeStore: {}, '
                                             'NameStore: {}, '
                                             'SKU: {}, '
                                             'Stock: {} '.format(code_store,
                                                                 name_store,
                                                                 sku_product,
                                                                 stock_product))

            stock_data_by_sku += [{
                "SKU": sku_product,
                "ProductStock": {
                    "CodeStore": code_store,
                    "NameStore": name_store,
                    "Stock": stock_product,
                }
            }]

        close_cursor(cursor)

        data_stock_all = json.dumps(stock_data_by_sku)

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {} - {}.".format(error,
                                                                                                       store_table,
                                                                                                       product_table)
        )
    finally:
        disconnect_from_db(conn)

    return data_stock_all


class ProductModelDb(Base):
    r"""
    Class to instance the data of a Van on the database.
    Transactions:
     - Insert: Add Product data to the database if not exists.
     - Update: Update Product data on the database if exists.
    """

    cfg = Util.get_config_constant_file()

    __tablename__ = cfg['DB_OBJECTS']['PRODUCT_TABLE']

    id_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['ID'], Numeric, primary_key=True)
    sku_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['SKU'], String)
    unspc_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['UNSPC'], String)
    brand_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['BRAND'], String)
    category_id = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['CATEGORY_ID'], Numeric)
    parent_category_id = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['PARENT_CAT_ID'], Numeric)
    uom_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['UOM'], String)
    stock_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['STOCK'], Numeric)
    store_id_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['STORE_ID'], Numeric)
    name_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['NAME'], String)
    title_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['TITLE'], String)
    long_description_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['LONG_DESCRIPTION'], String)
    photo_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['PHOTO'], String)
    price_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['PRICE'], Numeric)
    tax_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['TAX_PRICE'], Numeric)
    currency_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['CURRENCY'], String)
    status_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['STATUS'], String)
    published_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['PUBLISHED'], Boolean)
    manage_stock_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['MANAGE_STOCK'], Boolean)
    length_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['LENGTH'], Numeric)
    width_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['WIDTH'], Numeric)
    height_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['HEIGHT'], Numeric)
    weight_product = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['WEIGHT'], Numeric)
    creation_date = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['CREATION_DATE'], String)
    last_update_date = Column(cfg['DB_COLUMNS_DATA']['PRODUCT_API']['LAST_UPDATE_DATE'], String)

    def manage_product_data(self, product_obj):

        product_data = {}
        product_input_dic = {}

        product_input_dic = Util.set_data_input_product_dict(product_obj)

        product_sku = product_input_dic.get("product_sku")
        product_store_code = product_input_dic.get("product_store_code")

        product_store_id = select_store_id(product_store_code)
        product_id = select_product_id(product_sku, product_store_code)

        if exists_data_row(self.__tablename__,
                           self.id_product,
                           self.id_product,
                           product_id,
                           self.store_id_product,
                           product_store_id):

            product_data = update_product_data(product_input_dic)
        else:
            product_data = insert_new_product(product_input_dic)

        return product_data


# Add Product data to insert the row on the database
def insert_new_product(data_product):
    r"""
    Transaction to add data of a product and inserted on database.
    The data that you can insert are:

    :param data_product: Dictionary of all data product to insert.
    :return product_data_inserted: Dictionary that contains product data inserted on db.
    """

    conn = None
    cursor = None
    product_data_inserted = dict()

    cfg = Util.get_config_constant_file()

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        table_name = cfg['DB_OBJECTS']['PRODUCT_TABLE']

        creation_date = get_datenow_from_db()
        last_update_date = get_datenow_from_db()

        product_sku = data_product.get('product_sku')
        product_unspc = data_product.get('product_unspc')
        product_brand = data_product.get('product_brand')
        product_category_id = data_product.get('category_id')
        product_parent_category_id = data_product.get('parent_category_id')
        product_uom = data_product.get('unit_of_measure')
        product_stock = data_product.get('product_stock')
        product_store_code = data_product.get('product_store_code')
        product_name = data_product.get('product_name')
        product_title = data_product.get('product_title')
        product_long_description = data_product.get('product_long_description')
        product_photo = data_product.get('product_photo')
        product_price = data_product.get('product_price')
        product_tax = data_product.get('product_tax')
        product_currency = data_product.get('product_currency')
        product_status = data_product.get('product_status')
        product_published = data_product.get('product_published')
        product_manage_stock = data_product.get('product_manage_stock')
        product_length = data_product.get('product_length')
        product_width = data_product.get('product_width')
        product_height = data_product.get('product_height')
        product_weight = data_product.get('product_weight')

        product_store_id = select_store_id(product_store_code)
        product_id = select_product_id(product_sku, product_store_id)

        sql_product_insert = 'INSERT INTO {} ' \
                             '    (product_id, ' \
                             '     product_sku, ' \
                             '     product_unspc, ' \
                             '     product_brand, ' \
                             '     category_id, ' \
                             '     parent_category_id, ' \
                             '     unit_of_measure, ' \
                             '     product_stock, ' \
                             '     product_store_id, ' \
                             '     product_name, ' \
                             '     product_title, ' \
                             '     product_long_description, ' \
                             '     product_photo, ' \
                             '     product_price, ' \
                             '     product_tax, ' \
                             '     product_currency, ' \
                             '     product_status, ' \
                             '     product_published, ' \
                             '     product_manage_stock, ' \
                             '     product_length, ' \
                             '     product_width, ' \
                             '     product_height, ' \
                             '     product_weight, ' \
                             '     creation_date, ' \
                             '     last_update_date) ' \
                             'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
                             '%s, %s, %s, %s, %d)'.format(table_name)

        data_add_product = (product_id,
                            product_sku,
                            product_unspc,
                            product_brand,
                            product_category_id,
                            product_parent_category_id,
                            product_uom,
                            product_stock,
                            product_store_id,
                            product_name,
                            product_title,
                            product_long_description,
                            product_photo,
                            product_price,
                            product_tax,
                            product_currency,
                            product_status,
                            product_published,
                            product_manage_stock,
                            product_length,
                            product_width,
                            product_height,
                            product_weight,
                            creation_date,
                            last_update_date)

        cursor.execute(sql_product_insert, data_add_product)

        conn.commit()

        logger.info('Product inserted %s', "{0}, Code: {1}, Name: {2}".format(table_name, product_sku, product_name))

        close_cursor(cursor)

        row_exists = exists_data_row(table_name, 'product_id',
                                     'product_id', product_id,
                                     'product_store_id', product_store_id)

        product_data_inserted += [{
            "Product": {
                "IdProduct": product_id,
                "SKUProduct": product_sku,
                "UNSPC": product_unspc,
                "NameProduct": product_name,
                "TitleProduct": product_title,
                "BrandProduct": product_brand,
                "UOMProduct": product_uom,
                "CategoryIdProduct": product_category_id,
                "ParentCategoryIdProduct": product_parent_category_id,
                "StockProduct": product_stock,
                "CodeStore": product_store_code,
                "LongDescriptionProduct": product_long_description,
                "PhotoProduct": product_photo,
                "Prices": {
                    "PriceProduct": product_price,
                    "TaxPriceProduct": product_tax,
                    "CurrencyPriceProduct": product_currency,
                },
                "StatusProduct": product_status,
                "PublishedProduct": product_published,
                "ManageStockProduct": product_manage_stock,
                "Volumetry": {
                    "LengthProduct": product_length,
                    "WidthProduct": product_width,
                    "HeightProduct": product_height,
                    "WeightProduct": product_weight,
                },
                "CreationDate": creation_date,
                "LastUpdateDate": last_update_date,
            }
        }]

        if not str(product_id) not in str(row_exists):
            product_data_inserted += [{
                "Product": {
                    "IdProduct": product_id,
                    "SKUProduct": product_sku,
                    "UNSPC": product_unspc,
                    "NameProduct": product_name,
                    "TitleProduct": product_title,
                    "BrandProduct": product_brand,
                    "UOMProduct": product_uom,
                    "CategoryIdProduct": product_category_id,
                    "ParentCategoryIdProduct": product_parent_category_id,
                    "StockProduct": product_stock,
                    "CodeStore": product_store_code,
                    "LongDescriptionProduct": product_long_description,
                    "PhotoProduct": product_photo,
                    "Prices": {
                        "PriceProduct": product_price,
                        "TaxPriceProduct": product_tax,
                        "CurrencyPriceProduct": product_currency,
                    },
                    "StatusProduct": product_status,
                    "PublishedProduct": product_published,
                    "ManageStockProduct": product_manage_stock,
                    "Volumetry": {
                        "LengthProduct": product_length,
                        "WidthProduct": product_width,
                        "HeightProduct": product_height,
                        "WeightProduct": product_weight,
                    },
                    "CreationDate": creation_date,
                    "LastUpdateDate": last_update_date,
                }
            }]

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception was occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, table_name)
        )
    finally:
        disconnect_from_db(conn)

    return json.dumps(product_data_inserted)


# Update Product data registered
def update_product_data(data_product):
    r"""
    Transaction to update data of a Van registered on database.
    The data that you can update are:

    :param data_product: Dictionary of all data product to update.
    :return product_data_updated: Dictionary that contains Product data updated on db.
    """

    conn = None
    cursor = None
    product_data_updated = dict()

    cfg = Util.get_config_constant_file()

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        last_update_date = get_datenow_from_db()

        product_table = cfg['DB_OBJECTS']['PRODUCT_TABLE']

        product_sku = data_product.get('product_sku')
        category_id = data_product.get('category_id')
        parent_category_id = data_product.get('parent_category_id')
        product_stock = data_product.get('product_stock')
        product_store_code = data_product.get('product_store_code')
        product_name = data_product.get('product_name')
        product_title = data_product.get('product_title')
        product_long_description = data_product.get('product_long_description')
        product_photo = data_product.get('product_photo')
        product_price = data_product.get('product_price')
        product_tax = data_product.get('product_tax')
        product_currency = data_product.get('product_currency')
        product_status = data_product.get('product_status')
        product_published = data_product.get('product_published')
        manage_stock = data_product.get('product_manage_stock')

        product_store_id = select_store_id(product_store_code)
        product_id = select_product_id(product_sku, product_store_id)

        # update row to database
        sql_update_product = ' UPDATE {} ' \
                             ' SET product_sku=%s, ' \
                             '     category_id=%s, ' \
                             '     parent_category_id=%s, ' \
                             '     product_stock=%s, ' \
                             '     product_name=%s, ' \
                             '     product_title=%s, ' \
                             '     product_long_description=%s, ' \
                             '     product_photo=%s, ' \
                             '     product_price=%s, ' \
                             '     product_tax=%s, ' \
                             '     product_currency=%s, ' \
                             '     product_status=%s, ' \
                             '     product_published=%s, ' \
                             '     product_manage_stock=%s ' \
                             '     last_update_date=%s' \
                             ' WHERE product_id={} AND product_store_id={}'.format(product_table,
                                                                                   product_id,
                                                                                   product_store_id)

        cursor.execute(sql_update_product, (product_sku,
                                            category_id,
                                            parent_category_id,
                                            product_stock,
                                            product_name,
                                            product_title,
                                            product_long_description,
                                            product_photo,
                                            product_price,
                                            product_tax,
                                            product_currency,
                                            product_status,
                                            product_published,
                                            manage_stock,
                                            last_update_date,))

        conn.commit()

        close_cursor(cursor)

        row_exists = validate_transaction(product_table,
                                          'product_id',
                                          'product_id', product_id,
                                          'product_store_id', product_store_id,
                                          'product_sku', product_sku)

        product_data_updated = {
            "Product": {
                "IdProduct": product_id,
                "SKUProduct": product_sku,
                "NameProduct": product_name,
                "TitleProduct": product_title,
                "CategoryIdProduct": category_id,
                "ParentCategoryIdProduct": parent_category_id,
                "StockProduct": product_stock,
                "CodeStore": product_store_code,
                "LongDescriptionProduct": product_long_description,
                "PhotoProduct": product_photo,
                "Prices": {
                    "PriceProduct": product_price,
                    "TaxPriceProduct": product_tax,
                    "CurrencyPriceProduct": product_currency,
                },
                "StatusProduct": product_status,
                "PublishedProduct": product_published,
                "ManageStockProduct": manage_stock,
                "LastUpdateDate": last_update_date,
                "Message": "Product data Updated Successful"
            }
        }

        if str(product_id) not in str(row_exists):
            product_data_updated = {
                "Product": {
                    "IdProduct": product_id,
                    "SKUProduct": product_sku,
                    "NameProduct": product_name,
                    "TitleProduct": product_title,
                    "CategoryIdProduct": category_id,
                    "ParentCategoryIdProduct": parent_category_id,
                    "StockProduct": product_stock,
                    "CodeStore": product_store_code,
                    "LongDescriptionProduct": product_long_description,
                    "PhotoProduct": product_photo,
                    "Prices": {
                        "PriceProduct": product_price,
                        "TaxPriceProduct": product_tax,
                        "CurrencyPriceProduct": product_currency,
                    },
                    "StatusProduct": product_status,
                    "PublishedProduct": product_published,
                    "ManageStockProduct": manage_stock,
                    "LastUpdateDate": last_update_date,
                    "Message": "Product not Updated"
                }
            }

            logger.error('Can not read the recordset: {}, beacause is not stored on table: {}'.format(product_id,
                                                                                                      product_table))
            raise SQLAlchemyError(
                "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(product_table)
            )

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, product_table)
        )
    finally:
        disconnect_from_db(conn)

    return json.dumps(product_data_updated)


# Delete Product registered by id and code
def delete_product_data(product_sku, product_store_code):
    r"""
    Transaction to delete a Product data registered on database.

    :param product_sku: Id to looking for a Store data to delete.
    :param product_store_code: Code to looking for a Store data to delete.
    :return product_data_delete: Dictionary contains product data deleted.
    """

    conn = None
    cursor = None
    product_data_deleted = dict()

    cfg = Util.get_config_constant_file()

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        product_table = cfg['DB_OBJECTS']['PRODUCT_TABLE']

        product_store_id = select_store_id(product_store_code)
        product_id = select_product_id(product_sku, product_store_id)

        # delete row to database
        sql_delete_van = "DELETE FROM {} WHERE product_id=%s AND product_store_id=%s".format(product_table)

        cursor.execute(sql_delete_van, (product_id, product_store_id,))

        conn.commit()

        close_cursor(cursor)

        product_data_deleted = {
            "IdProduct": product_id,
            "SKUProduct": product_sku,
            "StoreCode": product_store_code,
            "Message": "Product Deleted Successful",
        }

        row_exists = exists_data_row(product_table,
                                     'product_id',
                                     'product_id', product_id,
                                     'product_store_id', product_store_id)

        if str(product_id) in str(row_exists):
            product_data_deleted = {
                "IdProduct": product_id,
                "SKUProduct": product_sku,
                "StoreCode": product_store_code,
                "Message": "Product not Deleted",
            }

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, product_table)
        )
    finally:
        disconnect_from_db(conn)

    return json.dumps(product_data_deleted)


# Select all products by sku from db
def select_by_product_sku(product_sku):
    r"""
    Get all the product data looking for specific sku on database.

    :param product_sku:
    :return data_product_by_sku: Dictionary that contains all the Product's data by specific SKU.
    """

    conn = None
    cursor = None

    product_data_by_sku = []
    data_product_all = dict()

    cfg = Util.get_config_constant_file()

    try:

        conn = session_to_db()

        cursor = create_cursor(conn)

        product_table = cfg['DB_OBJECTS']['PRODUCT_TABLE']
        store_table = cfg['DB_OBJECTS']['STORE_TABLE']

        sql_product_by_sku = " SELECT " \
                             "   prod.product_id, " \
                             "   prod.product_sku," \
                             "   prod.product_unspc," \
                             "   prod.product_brand," \
                             "   prod.category_id," \
                             "   prod.parent_category_id," \
                             "   prod.unit_of_measure," \
                             "   prod.product_stock," \
                             "   store.store_code," \
                             "   store.store_name" \
                             "   prod.product_name," \
                             "   prod.product_title," \
                             "   prod.product_long_description," \
                             "   prod.product_photo," \
                             "   prod.product_price," \
                             "   prod.product_tax," \
                             "   prod.product_currency," \
                             "   prod.product_status," \
                             "   prod.product_published," \
                             "   prod.product_manage_stock," \
                             "   prod.product_length," \
                             "   prod.product_width," \
                             "   prod.product_height," \
                             "   prod.product_weight," \
                             "   prod.creation_date," \
                             "   prod.last_update_date" \
                             " FROM {} prod, {} store " \
                             " WHERE store.id_store = prod.product_store_id " \
                             " AND prod.product_sku = %s;".format(product_table, store_table)

        cursor.execute(sql_product_by_sku, (product_sku,))

        result = cursor.fetchall()

        if result is None:
            logger.error('Can not read the recordset, because is not stored: %s', product_sku)
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    product_sku, product_table
                )
            )

        for product_data in result:
            if product_data is None:
                logger.error('Can not read the recordset: {}, '
                             'because is not stored on table: {}'.format(product_sku, product_table))
                raise SQLAlchemyError(
                    "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(product_sku)
                )

            product_id = product_data['product_id']
            sku_product = product_data['product_sku']
            product_unspc = product_data['product_unspc']
            product_brand = product_data['product_brand']
            category_id = product_data['category_id']
            parent_category_id = product_data['parent_category_id']
            unit_of_measure = product_data['unit_of_measure']
            product_stock = product_data['product_stock']
            product_store_code = product_data['store_code']
            product_store_name = product_data['store_name']
            product_name = product_data['product_name']
            product_title = product_data['product_title']
            product_long_description = product_data['product_long_description']
            product_photo = product_data['product_photo']
            product_price = product_data['product_price']
            product_tax = product_data['product_tax']
            product_currency = product_data['product_currency']
            product_status = product_data['product_status']
            product_published = product_data['product_published']
            product_manage_stock = product_data['product_manage_stock']
            product_length = product_data['product_length']
            product_width = product_data['product_width']
            product_height = product_data['product_height']
            product_weight = product_data['product_weight']
            fecha_creacion = datetime.strptime(str(product_data['creation_date']), "%Y-%m-%d %H:%M:%S")
            fecha_actualizacion = datetime.strptime(str(product_data['last_update_date']), "%Y-%m-%d %H:%M:%S")

            logger.info('Van Registered: %s', 'IdProduct: {}, '
                                              'SKUProduct: {}, '
                                              'UNSPC: {}, '
                                              'NameProduct: {}, '
                                              'TitleProduct: {}, '
                                              'BrandProduct: {} '.format(product_id,
                                                                         product_sku,
                                                                         product_unspc,
                                                                         product_name,
                                                                         product_title,
                                                                         product_brand))

            product_data_by_sku += [{
                "Product": {
                    "IdProduct": product_id,
                    "SKUProduct": sku_product,
                    "UNSPC": product_unspc,
                    "NameProduct": product_name,
                    "TitleProduct": product_title,
                    "BrandProduct": product_brand,
                    "UOMProduct": unit_of_measure,
                    "CategoryIdProduct": category_id,
                    "ParentCategoryIdProduct": parent_category_id,
                    "StockProduct": product_stock,
                    "CodeStore": product_store_code,
                    "NameStore": product_store_name,
                    "LongDescriptionProduct": product_long_description,
                    "PhotoProduct": product_photo,
                    "Prices": {
                        "PriceProduct": product_price,
                        "TaxPriceProduct": product_tax,
                        "CurrencyPriceProduct": product_currency,
                    },
                    "StatusProduct": product_status,
                    "PublishedProduct": product_published,
                    "ManageStockProduct": product_manage_stock,
                    "Volumetry": {
                        "LengthProduct": product_length,
                        "WidthProduct": product_width,
                        "HeightProduct": product_height,
                        "WeightProduct": product_weight,
                    },
                    "CreationDate": fecha_creacion,
                    "LastUpdateDate": fecha_actualizacion,
                }
            }]

        close_cursor(cursor)

        data_product_all = json.dumps(product_data_by_sku)

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, product_table)
        )
    finally:
        disconnect_from_db(conn)

    return data_product_all


# Update stock by product sku and store_code
def update_product_store_stock(stock, product_sku, store_code):
    r"""
    Transaction to update the stock/inventory of a product registered on database.

    :param stock: The number of stock or inventory to assign to the product.
    :param product_sku: The SKU identifier to setup the stock updated.
    :param store_code: The store code to looking for the store to update the inventory product.

    :return product_stock_updated: The dictionary to view on the front of a product stock updated.
    """

    cfg = Util.get_config_constant_file()

    conn = None
    cursor = None
    product_stock_updated = dict()

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        last_update_date = get_datenow_from_db()

        store_table = cfg['DB_OBJECTS']['STORE_TABLE']
        product_table = cfg['DB_OBJECTS']['PRODUCT_TABLE']

        if not Util.validate_store_code_syntax(store_code):
            logger.error('Can not read the recordset: {}, because the store code is not valid: {}'.format(store_code,
                                                                                                          store_table))
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    store_code, store_table
                )
            )

        sql_update_stock = " UPDATE {}" \
                           " SET	product_stock = %s, " \
                           "        last_update_date = %s " \
                           " WHERE product_store_id = (" \
                           "        SELECT store.id_store " \
                           "        FROM {} store" \
                           "        WHERE store.store_code = %s)" \
                           " AND product_sku = %s".format(product_table, store_table)

        cursor.execute(sql_update_stock, (stock, last_update_date, "'" + store_code + "'", "'" + product_sku + "'",))

        conn.commit()

        close_cursor(cursor)

        row_exists = exists_row_registered(store_table, 'store_code', "'" + store_code + "'")

        product_stock_updated = {
            "StoreCode": store_code,
            "ProductSku": product_sku,
            "ProductStock": str(stock),
            "LastUpdateDate": last_update_date,
            "Message": "Product Stock Updated Successful",
        }

        if not row_exists:
            product_stock_updated = {
                "StoreCode": store_code,
                "ProductSku": product_sku,
                "ProductStock": str(stock),
                "LastUpdateDate": last_update_date,
                "Message": "Store not exists",
            }

            logger.error('Can not read the recordset: {}, because is not stored on table: {}'.format(store_code,
                                                                                                     store_table))
            raise SQLAlchemyError(
                "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(store_table)
            )

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error, product_table)
        )
    finally:
        disconnect_from_db(conn)

    return json.dumps(product_stock_updated)


def select_store_id(store_code):
    r"""
    Get the store identifier of a Store registered.

    :param store_code: Code store to find the Id.
    :return store_id_by_code: Id of the store by his code.
    """

    cfg = Util.get_config_constant_file()

    conn = None
    cursor = None

    store_id_by_code = int()

    store_table = cfg['DB_OBJECTS']['STORE_TABLE']

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        if not Util.validate_store_code_syntax(store_code):
            logger.error('Can not read the recordset: {}, because the store code is not valid: {}'.format(store_code,
                                                                                                          store_table))
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    store_code, store_table
                )
            )

        sql_store_id = "SELECT id_store FROM {} WHERE store_code  = %s".format(store_table)

        cursor.execute(sql_store_id, (store_code,))

        store_id_by_code = cursor.fetchone()[0]

        if store_id_by_code is None:
            logger.error('Can not read the recordset: {}, '
                         'because is not stored on table: {}'.format(store_code, store_table))
            raise SQLAlchemyError(
                "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(store_table)
            )

        close_cursor(cursor)

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error,
                                                                                                  store_table)
        )
    finally:
        disconnect_from_db(conn)

    return store_id_by_code


def select_product_id(product_sku, product_store_id):
    r"""
    Get the product identifier of a Product registered.

    :param product_sku: Code SKU of product to find the Id.
    :param product_store_id: Id of the store assign to the product.
    :return data_van_by_status: Dictionary that contains all the Van's data by specific status.
    """

    cfg = Util.get_config_constant_file()

    conn = None
    cursor = None

    product_id_by_code = int()

    product_table = cfg['DB_OBJECTS']['PRODUCT_TABLE']

    try:
        conn = session_to_db()

        cursor = create_cursor(conn)

        sql_product_id = "SELECT product_id FROM {} WHERE product_sku=%s AND product_store_id=%s".format(product_table)

        cursor.execute(sql_product_id, (product_sku, product_store_id,))

        product_id_by_code = cursor.fetchone()[0]

        if product_id_by_code is None:
            logger.error('Can not read the recordset: {}, '
                         'because is not stored on table: {}'.format(product_sku, product_table))
            raise SQLAlchemyError(
                "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(product_table)
            )

        close_cursor(cursor)

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database on table {}.".format(error,
                                                                                                  product_table)
        )
    finally:
        disconnect_from_db(conn)

    return product_id_by_code


class UsersAuth(Base):
    r"""
    Class to instance User data to authenticate the API.
    Transactions:
     - Insert: Add user data to the database if not exists.
     - Update: Update user data on the database if exists.
    """

    cfg = Util.get_config_constant_file()

    __tablename__ = cfg['DB_AUTH_OBJECT']['USERS_AUTH']

    user_id = Column(cfg['DB_AUTH_COLUMNS_DATA']['USER_AUTH']['USER_ID'], Numeric, primary_key=True)
    user_name = Column(cfg['DB_AUTH_COLUMNS_DATA']['USER_AUTH']['USER_NAME'], String, primary_key=True)
    user_password = Column(cfg['DB_AUTH_COLUMNS_DATA']['USER_AUTH']['USER_PASSWORD'], String)
    password_hash = Column(cfg['DB_AUTH_COLUMNS_DATA']['USER_AUTH']['PASSWORD_HASH'], String)
    last_update_date = Column(cfg['DB_AUTH_COLUMNS_DATA']['USER_AUTH']['LAST_UPDATE_DATE'], String)

    @staticmethod
    def manage_user_authentication(user_id, user_name, user_password, password_hash):

        try:

            user_verification = validate_user_exists(user_name)

            # insert validation
            if user_verification[0]:

                # update method
                update_user_password_hashed(user_name, password_hash)

            else:
                # insert

                insert_user_authenticated(user_id, user_name, user_password, password_hash)

        except SQLAlchemyError as e:
            logger.exception('An exception was occurred while execute transactions: %s', e)
            raise mvc_exc.ItemNotStored(
                'Can\'t insert user_id: "{}" with user_name: {} because it\'s not stored in "{}"'.format(
                    user_id, user_name, UsersAuth.__tablename__
                )
            )


# Transaction to looking for a user on db to authenticate
def validate_user_exists(user_name):
    r"""
    Looking for a user by name on the database to valid authentication.

    :param user_name: The user name to valid authentication on the API.
    :return result: Boolean to valid if the user name exists to authenticate the API.
    """

    cfg = Util.get_config_constant_file()

    conn = session_to_db()

    cursor = create_cursor(conn)

    table_name = cfg['DB_AUTH_OBJECT']['USERS_AUTH']

    sql_check = "SELECT EXISTS(SELECT 1 FROM {} WHERE username = {} LIMIT 1)".format(table_name, "'" + user_name + "'")

    cursor.execute(sql_check)

    result = cursor.fetchone()

    close_cursor(cursor)
    disconnect_from_db(conn)

    return result


# Transaction to update user' password  hashed on db to authenticate
def update_user_password_hashed(user_name, password_hash):
    r"""
    Transaction to update password hashed of a user to authenticate on the API correctly.

    :param user_name: The user name to update password hashed.
    :param password_hash: The password hashed to authenticate on the API.
    """

    cfg = Util.get_config_constant_file()

    conn = session_to_db()

    cursor = create_cursor(conn)

    last_update_date = get_datenow_from_db()

    table_name = cfg['DB_AUTH_OBJECT']['USERS_AUTH']

    # update row to database
    sql_update_user = "UPDATE {} SET password_hash = %s, last_update_date = %s WHERE username = %s".format(
        table_name
    )

    cursor.execute(sql_update_user, (password_hash, last_update_date, user_name,))

    conn.commit()

    close_cursor(cursor)
    disconnect_from_db(conn)


def insert_user_authenticated(user_id, user_name, user_password, password_hash):
    r"""
    Transaction to add a user data to authenticate to API, inserted on the db.

    :param user_id: The Id of the user to add on the db.
    :param user_name: The user name of the user to add on the db.
    :param user_password:  The password od the user to add on the db.
    :param password_hash: The password hashed to authenticate on the API.
    """

    cfg = get_config_constant_file()

    conn = session_to_db()

    cursor = create_cursor(conn)

    last_update_date = get_datenow_from_db()

    table_name = cfg['DB_AUTH_OBJECT']['USERS_AUTH']

    data = (user_id, user_name, user_password, password_hash,)

    sql_user_insert = 'INSERT INTO {} (user_id, username, password, password_hash) ' \
                      'VALUES (%s, %s, %s, %s)'.format(table_name)

    cursor.execute(sql_user_insert, data)

    conn.commit()

    logger.info('Usuario insertado %s', "{0}, User_Name: {1}".format(user_id, user_name))

    close_cursor(cursor)
    disconnect_from_db(conn)


# Function not used.
# Deprecated
def get_data_user_authentication(session, table_name, user_name):
    user_auth = []

    user_auth_data = {}

    try:
        sql_user_data = " SELECT user_name, user_password, password_hash, last_update_date " \
                        " FROM {} " \
                        " WHERE user_name = {} ".format(table_name, "'" + user_name + "'")

        user_auth_db = session.execute(sql_user_data)

        for user in user_auth_db:
            if user is not None:

                user_name_db = user['username']
                user_password_db = user['password']
                password_hash = user['password_hash']
                last_update_date = datetime.strptime(str(user['last_update_date']), "%Y-%m-%d")

                user_auth += [{
                    "username": user_name_db,
                    "password": user_password_db,
                    "password_hash": password_hash,
                    "date_updated": last_update_date
                }]

            else:
                logger.error('Can not read the recordset, beacause is not stored')
                raise SQLAlchemyError(
                    "Can\'t read data because it\'s not stored in table {}. SQL Exception".format(table_name)
                )

        user_auth_data = json.dumps(user_auth)

        user_auth_db.close()

    except SQLAlchemyError as sql_exec:
        logger.exception(sql_exec)
    finally:
        session.close()

    return user_auth_data
