from bottle import route, run, debug, template, request, static_file, error
import datetime
import pyGLITCH_backend as pgb

#@route('/hello/<name>')
#def index(name):
#    return template('<b>Hello {{name}}</b>!', name=name)

@route('/')
def index():
    return "Hello world"

@route('/<long_string>')
def printname(long_string):
    """
    Parse incoming string using basic Python string operations
    """
    parsed = long_string.split("&")
    code = parsed[0].lstrip("dbcode=")
    print(code)
    entity = parsed[1].lstrip("entity_num=")
    print(entity)
    pc = parsed[2].lstrip("probe_code=")
    sd = parsed[3].lstrip("start_date=")
    ed = parsed[4].lstrip("end_date=")
    interval = parsed[5].lstrip("interval=")

    start_date = datetime.datetime(int(sd[0:4]), int(sd[4:6]), int(sd[6:8]), int(sd[8:10]), int(sd[10:12]), 0)
    start_date_string = datetime.datetime.strftime(start_date,'%Y-%m-%d %H:%M:%S')
    end_date = datetime.datetime(int(ed[0:4]), int(ed[4:6]), int(ed[6:8]), int(ed[8:10]), int(ed[10:12]), 0)
    end_date_string = datetime.datetime.strftime(end_date,'%Y-%m-%d %H:%M:%S')

    table_name = code + entity

    printable = "starts on: " + datetime.datetime.strftime(start_date,'%Y-%m-%d %H:%M:%S') + " and ends on: " + datetime.datetime.strftime(end_date,'%Y-%m-%d %H:%M:%S')

    returning_string = "You have chosen " + pc + " from table " + table_name + " which " + printable + " and aggregates for " + interval + " minutes!"

    #print(code, entity, pc, start_date_string, end_date_string, interval)

    returning_html = pgb.simple_glitch(code, entity, pc, start_date_string, end_date_string, interval)
    #print returning_html
    
    print returning_html
    return returning_html

run(host='localhost', port=8080)