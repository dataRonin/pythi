from bottle import route, run, debug, template, request, static_file, error, static_file, get, post
import datetime
import pyGLITCH_backend as pgb
import requests
import datetime
import map_glitch_ui as ui

@route('/')
def index():
    return "<h1>Choose you a Probe for Great Good!</h1>"

@error(404)
def error404(error):
    return "404 : This isn\'t the data you were looking for"

@error(403)
def error403(error):
    return "403 : Abandon all hope of getting this data."

@error(500)
def error500(error):
    return "500 : Oh look, you\'ve gone and broken our webpage. Gee, thanks. You should probably check to be sure we measured that thing during the time you selected."

@route('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js/')

@route('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css/')

@get('/<filename:re:.*\.(jpg|png|gif|ico|svg)>')
def images(filename):
    return static_file(filename, root='img/')

# accordion routes to the big accordion table containing all the entities
@route('/accordion')
def generate_accordion():
    giant_string = ui.accordion_table()
    return giant_string

# probes picks up the probes from the form in /accordion and generates a probe lookup based on them
@route('/probes', method='POST')
def links_to_probes():
    """ creates links to generate urls with probe names from selection"""
    startdate = request.forms.get('startdate')
    print startdate
    enddate = request.forms.get('enddate')
    print enddate
    bigname = request.forms.get('menu-selection')
    pp = ui.all_the_probes(bigname)
    return_string = ui.accordion_probes(bigname, startdate, enddate)
    return return_string

# dbcode grabs the probe specifics based on the seven digit db code and gets the right data from the back end
@route('/<dbcode>', method='POST')
def links_to_datas(dbcode):
    """ takes the input from the probes menu and sends it to the back end"""
    startdate = request.forms.get('startdate')
    enddate = request.forms.get('enddate')
    pc = request.forms.get('menu-selection')
    
    # the 7-digit code, like MS04312 etc.
    dbcode = dbcode

    # in minutes
    interval = request.forms.get('interval')

    date_error = "you must enter the date time as YYYY-MM-DD HH:MM:SS"

    try:
        start_date_string = startdate
    except Exception:
        return date_error
    try:
        end_date_string = enddate
    except Exception:
        return date_error

    # in most cases we shouldn't mess this up, it should always be 7, probably change this.
    if len(dbcode) > 5:
        code = str(dbcode[0:5])
        entity = str(dbcode[5:7])

    returning_html = pgb.simple_glitch(code, entity, pc, start_date_string, end_date_string, interval)
    return returning_html

@route('/data/<long_string>')
def printname(long_string):
    """
    Parse incoming string using basic Python string operations
    This method is for hans to use when he incorporates it into the Cold Fusion
    It is not part of PYTHI. If you deleted it, PYTHI would not care.
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


    returning_html = pgb.simple_glitch(code, entity, pc, start_date_string, end_date_string, interval)

    return returning_html

run(host='localhost', port=8080)