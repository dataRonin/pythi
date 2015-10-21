#!usr/bin/python
import pymssql
import time
import datetime
import itertools
import sys

""" map_glitch_2.py maps the FSDBDATA database for GLITCH, providing the column names that are likely useful for glitching. To refine this output, use the :mod:`pyGLITCH_backend`. This module is never explicitly called.

Fox Peterson 2015, CCSA3.0 License
"""


def connect():
    """ Connect to the fsdbdata database - read only access

    .. warning :: The connection parameters are nested in this function. It is a read only user of 'ltermeta'.
    """

    conn = pymssql.connect(server = 'stewartia.forestry.oregonstate.edu:1433', user='ltermeta', password='$CFdb4LterWeb!')
    cursor = conn.cursor()

    return conn, cursor


def gather_column_names(cursor, table_name):
    """ get the available column names

    :cursor: the pymssql cursor created by :func:`connect`
    :table_name: an FSBDDATA table, as specified in :mod:`map_glitch_ui`
    """

    cnames = []
    try:
        get_cnames = "select column_name from fsdbdata.information_schema.columns where table_name like \'" + table_name + "\' and column_name not like \'dbcode\' and column_name not like \'stcode\' and column_name not like \'entity\' and column_name not like \'format\' and column_name not like \'%method\' and column_name not like \'event_code\' and column_name not like \'%level\' and column_name not like \'sitecode\' and column_name not like \'height\' and column_name not like \'%depth\' and column_name not like \'max%\' and column_name not like \'min%\' and column_name not like \'%max%\' and column_name not like \'%min%\' and column_name not like \'%stddev\'"

        cursor.execute(get_cnames)

        # will be only one item on each row
        for row in cursor:
            cnames.append(str(row[0]))

        return cnames

    except Exception:

        print("An exception has been thrown getting information on your selected table from information schema. Please check map_glitch_2.py")
        import pdb; pdb.set_trace()

        return False

def system_tables(cursor, table_name, probe_code, cnames, startdate, enddate):
    """ Figures out the names of the columns in your selected table, as well as what the PROBE is called, and orders them in a way that the glitcher can understand.

    .. warning :: if you add new tables or columns, you'll want to obey the conventions taht the word for the PROBE should contain the word "probe" and the word for the "date" should contain the word "date". If this is not the case, you'll need to add an extra sql statement here like this example below, either by using the word "probe_code" as a variable with the new name inserted, or by simply fixing the string

    .. Example ::
    >>> probe_code = 'my_new_name_for_probe_code'
    >>> new_sql_statement = "select " + cnames_to_list + " from fsdbdata.dbo." + table_name + " where date_time >= \'" + startdate + "\' and date_time <= \'" + enddate +"\' and " + probe_code + "like \'" + probe_code +"\' order by date_time asc"
    
    :table_name: an FSDBDATA table, like MS04310
    :probe_code: the name of a probe, like AIRCEN01
    :cnames: the column names, created by :func:`gather_column_names`
    """

    cnames_to_list = ', '.join(cnames)

    ### Try Probe and probe_code as the names for the PROBE

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

            od = dict(zip(cnames, [[str(x)] for x in first_entry]))

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

                od = dict(zip(cnames, [[str(x)] for x in first_entry]))

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

                    od = dict(zip(cnames, [[str(x)] for x in first_entry]))

                    for row in cursor:
                        for index, y in enumerate(cnames):
                            od[y].append(str(row[index]))

                    #import pdb; pdb.set_trace()
                    return od
                except Exception:
                    print("I failed")

if __name__ == "__main__":

    # this is really all there is to it --> 
    # we need to know simply the table, probe, start date, and end date column names which we get
    _, cursor = connect()
    cnames = gather_column_names(cursor, table_name)
    output1 = system_tables(cursor, table_name, probe_code, cnames, startdate, enddate)
