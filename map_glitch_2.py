#!usr/bin/python
import pymssql
import time
import datetime
import itertools
import sys

def connect():
    ''' connect to the fsdbdata database'''

    conn = pymssql.connect(server = 'stewartia.forestry.oregonstate.edu:1433', user='ltermeta', password='$CFdb4LterWeb!')
    cursor = conn.cursor()

    return conn, cursor


def gather_column_names(cursor, table_name):
    """ get the available column names"""

    cnames = []
    try:
        get_cnames = "select column_name from fsdbdata.information_schema.columns where table_name like \'" + table_name + "\' and column_name not like \'dbcode\' and column_name not like \'stcode\' and column_name not like \'entity\' and column_name not like \'format\' and column_name not like \'%method\' and column_name not like \'event_code\' and column_name not like \'%level\' and column_name not like \'sitecode\' and column_name not like \'height\' and column_name not like \'%depth\' and column_name not like \'max%\' and column_name not like \'min%\' and column_name not like \'%max%\' and column_name not like \'%min%\' and column_name not like \'%stddev\'"

        cursor.execute(get_cnames)

        # will be only one item on each row
        for row in cursor:
            cnames.append(str(row[0]))

        return cnames

    except Exception:

        print("an exception has been thrown getting information from information schema")
        import pdb; pdb.set_trace

        return False

def system_tables(cursor, table_name, probe_code, cnames, startdate, enddate):

    cnames_to_list = ', '.join(cnames)

    """ Try Probe and probe_code """

    try:
        sql = "select " + cnames_to_list + " from fsdbdata.dbo." + table_name + " where date_time >= \'" + startdate + "\' and date_time <= \'" + enddate +"\' and probe_code like \'" + probe_code +"\' order by date_time asc"

        cursor.execute(sql)

        first_entry = cursor.fetchone()

        od = dict(zip(cnames, [[str(x)] for x in first_entry]))

        for row in cursor:
            for index, y in enumerate(cnames):
                od[y].append(str(row[index]))

        #import pdb; pdb.set_trace()
        return od

    except Exception:
        try:
            sql = "select " + cnames_to_list + " from fsdbdata.dbo." + table_name + " where date_time >= \'" + startdate + "\' and date_time <= \'" + enddate +"\' and probe like \'" + probe_code +"\' order by date_time asc"
            cursor.execute(sql)
            first_entry = cursor.fetchone()

            od = dict(zip(cnames_to_list, [[str(x)] for x in first_entry]))

            for row in cursor:
                for index, y in enumerate(cnames):
                    od[y].append(str(row[index]))

            #import pdb; pdb.set_trace()
            return od

        except Exception:
            try:
                sql = "select " + cnames_to_list + " from fsdbdata.dbo." + table_name + " where date >= \'" + startdate + "\' and date <= \'" + enddate +"\' and probe like \'" + probe_code +"\' order by date asc"
                cursor.execute(sql)
                first_entry = cursor.fetchone()

                od = dict(zip(cnames_to_list, [[str(x)] for x in first_entry]))

                for row in cursor:
                    for index, y in enumerate(cnames):
                        od[y].append(str(row[index]))

                #import pdb; pdb.set_trace()
                return od

            except Exception:
                try:
                    sql = "select " + cnames_to_list + " from fsdbdata.dbo." + table_name + " where date >= \'" + startdate + "\' and date <= \'" + enddate +"\' and probe_code like \'" + probe_code +"\' order by date asc"
                    cursor.execute(sql)
                    first_entry = cursor.fetchone()

                    od = dict(zip(cnames_to_list, [[str(x)] for x in first_entry]))

                    for row in cursor:
                        for index, y in enumerate(cnames):
                            od[y].append(str(row[index]))

                    #import pdb; pdb.set_trace()
                    return od
                except Exception:
                    print("I failed")

if __name__ == "__main__":

    # this is really all there is to it
    # we need to know simply the table, probe, sd, and ed column names which we get
    _, cursor = connect()
    cnames = gather_column_names(cursor, table_name)
    output1 = system_tables(cursor, table_name, probe_code, cnames, startdate, enddate)
