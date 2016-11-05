import MySQLdb
import parsers.parser_new_data as parser

MYSQL_HOST = "cal-patent-lab.chhaitskv8dz.us-west-2.rds.amazonaws.com"
MYSQL_USERNAME = "***REMOVED***"
MYSQL_PASSWORD = "***REMOVED***"
MYSQL_DB = "***REMOVED***"

def db(host, username, psswd, db):
    db = MySQLdb.connect(host, username, psswd, db)
    return db

def insert_decision(cursor, table_name, patent_id, decision):
    # SQL query to add a new row containing patent id and deciscion
    # the invalidated field of the table takes an int as an input
    if decision == "invalidated":
        dec = 1
    else:
        dec = 0
    sql_query = "INSERT INTO {} (patent_id, invalidated) VALUES ({}, {})".format(
        table_name, str(patent_id), dec)

    cursor.execute(sql_query)
    return


def update_table(db):
    # statu contains false if the db was not updated
    status = False
    try:
        db.commit()
        status = True
    except:
        db.rollback()

    # Closing the connection
    db.close()
    return status


def populate_table_decision(db, table_name, patent_id, decision):
    cursor = db.cursor()
    status = update_table(db)
    return status


if __name__ == "__main__":
    print('Example')
    # Example of file being parsed and the data stored in the db
    # Please change the path adequatly for the ptab text file
    patent_id=parser.parsePatentId("RetrievePdf_008.txt")
    decision = parser.parseDecision("RetrievePdf_008.txt")
    db = db(MYSQL_HOST, MYSQL_USERNAME, MYSQL_USERNAME, MYSQL_DB)
    status = populate_table_decision(db, 'patents', patent_id, decision)
    print(status)
