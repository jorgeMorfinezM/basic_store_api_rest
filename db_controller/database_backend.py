# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later

PostgreSQL DB backend.

Each one of the CRUD operations should be able to open a database connection if
there isn't already one available (check if there are any issues with this).

Documentation:
    About the Van data on the database to generate CRUD operations from endpoint of the API:
    - Insert Van data
    - Update Van data
    - Delete Van data
    - Search Van data by UUID
    - Search Van data by Status

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


import re
import json
import logging
from datetime import datetime

import psycopg2
from sqlalchemy import Column, String, Numeric
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

    cfg = get_config_constant_file()

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


def get_nextval_economic_number_van(conn):
    r"""
    Get the next value number to set as part of Economic Number in a Van attribute.
    Use it to create a new Van register on the database.

    :param conn: Object to create a session to connect to the database.
    :return economic_number_nextval: The next value data to set to the Van Economic Number.
    """

    cursor = None
    economic_number_nextval = int()
    sql_nextval_seq = ""

    try:
        sql_nextval_seq = "SELECT nextval('urbvan.eco_num_van')"

        cursor = create_cursor(conn)

        cursor.execute(sql_nextval_seq)

        economic_number_nextval = cursor.fetchone()

        close_cursor(cursor)

        if economic_number_nextval:
            return economic_number_nextval

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database.".format(error)
        )


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
        cursor = conn.cursor()

        sql_exists = f"SELECT {column_name} FROM {table_name} " \
                     f"WHERE {column_filter1} = {value1} AND {column_filter2} = '{value2}'"

        cursor.execute(sql_exists)

        row_exists = cursor.fetchall()

        # row_exists = session.execute(sql_exists)

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
        cursor = conn.cursor()

        sql_exists = 'SELECT {} FROM {} WHERE {} = {} AND {} = {} AND {} = {}'.format(column_name, table_name,
                                                                                      column_filter1, value1,
                                                                                      column_filter2, "'" + value2 + "'",
                                                                                      column_filter3, "'" + value3 + "'")

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
    Class to instance the data of a Van on the database.
    Transactions:
     - Insert: Add Van data to the database if not exists.
     - Update: Update Van data on the database if exists.
    """

    cfg = get_config_constant_file()

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

    def manage_van_vehicle_data(self, id_store, name_store, code_store, street_store, ext_num_store, suburb_store,
                                city_store, country_store, postal_code_store, minimum_stock, store_obj):

        store_data = {}

        store_dict = Util.set_data_input_store_dict(id_store, code_store, name_store, street_store, ext_num_store,
                                                    suburb_store, city_store, country_store, postal_code_store,
                                                    minimum_stock)

        if exists_data_row(self.__tablename__,
                           self.id_store,
                           self.id_store,
                           id_store,
                           self.code_store,
                           code_store):

            store_data = update_store_data(self.__tablename__, store_dict)
        else:
            store_data = insert_new_store(self.__tablename__, store_obj)

        return store_data


# Add Store data to insert the row on the database
def insert_new_store(table_name, store_obj: StoreModel):
    r"""
    Transaction to add data of a Van and inserted on database.
    The data that you can insert are:

    :param table_name: The table name to looking for data van.
    :param store_obj: Store object model to add new store data.
    :return store_data_inserted: Dictionary that contains Store data inserted on db.
    """

    conn = None
    cursor = None
    store_data_inserted = dict()

    try:
        conn = session_to_db()

        cursor = conn.cursor()

        created_at = get_datenow_from_db()
        last_update_date = get_datenow_from_db()

        store_id = store_obj.get_id_store()
        store_code = store_obj.get_store_code()
        store_name = store_obj.get_store_name()
        store_external_number = store_obj.get_external_number()
        store_street_address = store_obj.get_street_address()
        store_suburb_address = store_obj.get_suburb_address()
        store_city_address = store_obj.get_city_address()
        store_country_address = store_obj.get_country_address()
        store_zippostal_code = store_obj.get_zip_postal_address()
        store_min_inventory = store_obj.get_minimum_stock()

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
def update_store_data(table_name, data_store):
    r"""
    Transaction to update data of a Van registered on database.
    The data that you can update are:

    :param table_name: The table name to looking for data.
    :param data_store: Dictionary of all data store to update.
    :return store_data_updated: Dictionary that contains Store data updated on db.
    """

    conn = None
    cursor = None
    store_data_updated = dict()

    try:
        conn = session_to_db()

        cursor = conn.cursor()

        last_update_date = get_datenow_from_db()

        store_id = data_store.get("store_id")
        store_code = data_store.get("store_code")
        store_name = data_store.get("store_name")
        street_address = data_store("street_address")
        external_number_address = data_store("external_number_address")
        suburb_address = data_store.get("suburb_address")
        city_address = data_store.get("city_address")
        country_address = data_store.get("country_address")
        zip_postal_code_address = data_store.get("zip_postal_code_address")
        minimum_stock = data_store.get("minimum_inventory")

        if not Util.validate_store_code_syntax(store_code):

            logger.error('Can not read the recordset: {}, because the store code is not valid: {}'.format(store_code,
                                                                                                          table_name))
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    store_id, table_name
                )
            )

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

            logger.error('Can not read the recordset: {}, beacause is not stored on table: {}'.format(store_id,
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


# Delete store registered by id and code
def delete_store_data(table_name, store_id, store_code):
    r"""
    Transaction to delete a Van data registered on database from his uuid and plates.

    :param table_name: The table name to looking for data van.
    :param store_id: Id to looking for a Store data to delete.
    :param store_code: Code to looking for a Store data to delete.
    :return van_data_delete: Dictionary contains Van data deleted.
    """

    conn = None
    cursor = None
    store_data_deleted = dict()

    try:
        conn = session_to_db()

        cursor = conn.cursor()

        if not Util.validate_store_code_syntax(store_code):

            logger.error('Can not read the recordset: {}, because the store code is not valid: {}'.format(store_code,
                                                                                                          table_name))
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    store_id, table_name
                )
            )

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

        if not str(store_id) in str(row_exists):

            store_data_deleted = {
                "IdStore": store_id,
                "CodeStore": store_code,
                "Message": "Store not deleted",
            }

            logger.error('Can not read the recordset: {}, because is not stored on table: {}'.format(store_id,
                                                                                                     table_name))
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}. SQL Exception"'.format(
                    store_id, table_name
                )
            )

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
def select_by_store_code(table_name, store_code):
    r"""
    Get all the Van's data looking for specific status on database.

    :param store_code:
    :param table_name: The table name to looking for data van.
    :return data_store_by_code: Dictionary that contains all the Store's data by specific code.
    """

    conn = None
    cursor = None

    store_data_by_code = []
    data_store_all = dict()

    try:

        conn = session_to_db()

        cursor = conn.cursor()

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

            logger.info('Van Registered: %s', 'IdStore: {}, '
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

        cursor = conn.cursor()

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


# Select stock in specific product by store code
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

        cursor = conn.cursor()

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


class UsersAuth(Base):
    r"""
    Class to instance User data to authenticate the API.
    Transactions:
     - Insert: Add user data to the database if not exists.
     - Update: Update user data on the database if exists.
    """

    cfg = get_config_constant_file()

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

    cfg = get_config_constant_file()

    conn = session_to_db()

    cursor = conn.cursor()

    table_name = cfg['DB_AUTH_OBJECT']['USERS_AUTH']

    sql_check = "SELECT EXISTS(SELECT 1 FROM {} WHERE username = {} LIMIT 1)".format(table_name, "'" + user_name + "'")

    cursor.execute(sql_check)

    result = cursor.fetchone()

    return result


# Transaction to update user' password  hashed on db to authenticate
def update_user_password_hashed(user_name, password_hash):
    r"""
    Transaction to update password hashed of a user to authenticate on the API correctly.

    :param user_name: The user name to update password hashed.
    :param password_hash: The password hashed to authenticate on the API.
    """

    cfg = get_config_constant_file()

    conn = session_to_db()

    cursor = create_cursor(conn)

    last_update_date = get_datenow_from_db()

    table_name = cfg['DB_AUTH_OBJECT']['USERS_AUTH']

    # update row to database
    sql_update_user = "UPDATE {} SET password_hash = %s, last_update_date = NOW() WHERE username = %s".format(
        table_name
    )

    cursor.execute(sql_update_user, (password_hash, user_name,))

    conn.commit()

    close_cursor(cursor)


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


# Function not used.
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

