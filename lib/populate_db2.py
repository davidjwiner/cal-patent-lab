#!/usr/bin/env python
import sys
import MySQLdb
import parsers.parser_new_data as parser
from os import listdir
from os.path import isfile, join
import html

MYSQL_HOST = "cal-patent-lab.chhaitskv8dz.us-west-2.rds.amazonaws.com"
MYSQL_USERNAME = "teamrocket"
MYSQL_PASSWORD = "teamrocket"
MYSQL_DB = "teamrocket"


def db(host, username, psswd, db):
    db = MySQLdb.connect(host, username, psswd, db)
    return db


def insert_decision(cursor, table_name, patent_id, decision, claim_text):
    # SQL query to add a new row containing patent id and deciscion
    # the invalidated field of the table takes an int as an input
    sql_query = ('INSERT INTO {} (patent_id, invalidated, claims_text) VALUES '
       '(%s, %s, %s)'.format(table_name))
    cursor.execute(sql_query, (patent_id, dec, claim_text))
    return


def update_table(db):
    # statu contains false if the db was not updated
    status = False
    try:
        db.commit()
        status = True
    except:
        db.rollback()
    return status


#def populate_table_decision(db, table_name, patent_id, decision, claim_text):
    #cursor = db.cursor()
    #insert_decision(cursor, table_name, patent_id, decision,claim_text)
    #return status


if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) != 2:
        print("Usage: populate_db2.py path_to_parsed_files path_to_patent_tsv_files")
        sys.exit(1)
    
    srcdir, tsvdir = argv
    ptabfiles = [join(srcdir, f) for f in listdir(srcdir) if isfile(join(srcdir, f))]
    tsvfiles = [join(tsvdir, f) for f in listdir(tsvdir) if isfile(join(tsvdir, f))]
    
    decision_table = dict()
    for file_name in ptabfiles:
        patent_id=parser.parsePatentId(file_name)
        if patent_id:
            decision = parser.parseDecision(file_name)
            decision_table[patent_id] = [decision, False]  # False = has not been written to DB
    
    db = db(MYSQL_HOST, MYSQL_USERNAME, MYSQL_USERNAME, MYSQL_DB)
    cursor = db.cursor()
    for file_name in tsvfiles:
        claims = open(file_name, 'r')
        for line in claims:
            # isolate patent #, claims text
            patent_id, patent_body = line.split('\t')
            patent_id = patent_id.strip()
            # Some entries in the TSV files are published applications, e.g. 2004/0204653
            # Skip these, since we only want granted patents
            if "/" in patent_id:
                continue
            _, claim_text = patent_body.split('CLAIMS. ')
            claim_text = html.unescape(claim_text.strip())
            dec = None
            if patent_id in decision_table:
                if decision_table[patent_id] == "not invalidated":
                    dec = 0
                elif decision_table[patent_id] == "invalidated":
                    dec = 1
            status = insert_decision(cursor, 'patents_decision', patent_id, dec, claim_text)
    
    for patent_id in decision_table:
        decision, is_written = decision_table[patent_id]
        if not is_written:
            dec = None
            if decision == "not invalidated":
                dec = 0
            elif decision == "invalidated":
                dec = 1
            claim_text = None
            status = insert_decision(cursor, 'patents_decision', patent_id, dec, claim_text)
    status = update_table(db)
    db.close()


