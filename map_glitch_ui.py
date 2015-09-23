#!usr/bin/python
import pymssql
import time
import datetime
import itertools
import sys
from map_glitch_2 import connect

def all_the_tables(cur, dbcode):
    """ gets all the possible tables for any given probe code"""
    sql = "select table_name from fsdbdata.information_schema.tables where table_name like \'" + dbcode + "%\' order by table_name asc"

    names_of_tables = []
    cur.execute(sql)

    # in this loop, specify which "tables" you don't want to use - can be from any db.
    for row in cur:
        tn = str(row[0])
        if tn[-2:-1] =='0':
            continue
        elif "_" in tn:
            continue
        elif tn == 'MS04310' or tn == "MS00110":
            continue
        else:
            stringify = '<li id=\"' + tn + '\"><a href=\"#\">' + tn + '</a></li>'
            names_of_tables.append(stringify)

    new_names = "".join(names_of_tables)

    return new_names

def all_the_probes(seven_digit_db_code):
    """ Gets all the probes for a given tablename 

    :seven_digit_db_code: The long dbcode + entity (MS04314), sometimes also called table_name
    """
    
    _, cur = connect()

    tablename = str(seven_digit_db_code)

    possible_probes = []

    sql = "select distinct(probe) from fsdbdata.dbo." + tablename + " order by probe asc"

    try:
        cur.execute(sql)
    
    except Exception:
        try:
            sql = "select distinct(probe_code) from fsdbdata.dbo." + tablename + " order by probe_code asc"
            cur.execute(sql)
        except Exception:
            return possible_probes


    for row in cur:
        possible_probes.append(str(row[0]))

    return possible_probes

def html_probes_list(possible_probes):
    """ Make the html probes into a list of probes - old method"""

    starting_string = "<ul>"
    ending_string = "</ul>"


    inner_list = []
    for each_probe in possible_probes:

        item = "<li id=\'" + each_probe + "\'>" + each_probe + "</li>"

        inner_list.append(item)
    inner_list_as_string = "".join(inner_list)

    final_list_as_string = starting_string + inner_list_as_string + ending_string

    return final_list_as_string

def accordion_probes(seven_digit_db_code, startdate, enddate):
    """ Generate nice interface for probes - one big table that can be clicked on for each probe"""

    _,cur = connect()

    pp = all_the_probes(seven_digit_db_code)

    pp_list = []

    for each_probe in pp:

        stringify = '<li id=\"' + each_probe + '\"><a href=\"#\">' + each_probe + '</a></li>'

        pp_list.append(stringify)

    new_names = "".join(pp_list)

    # this giant string is the HTML which is generated
    huge_string = """
    <!doctype html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="I pity the foo who doesn't use PYTHI">
    <meta name="author" content="Fox Peterson">
    <title> PYTHI | PYthon-based Time-Series Harmonization and Interpolation </title>
    <link href='//fonts.googleapis.com/css?family=Open+Sans:400,700' rel='stylesheet' type='text/css'>
    <link href="http://maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css" rel="stylesheet">
    <script src = "//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    </head>
    <style>
        * {
        margin: 0;
        padding: 0;
        -webkit-box-sizing: border-box;
        -moz-box-sizing: border-box;
        box-sizing: border-box;
    }

    body {
        background: #2d2c41;
        font-family: 'Open Sans', Helvetica neue,   Sans-serif;
    }

    ul {
        list-style-type: none;
    }

    a {
        color: #b63b4d;
        text-decoration: none;
    }

    form {
        background: #2d2c41;
        font-family: 'Open Sans', Helvetica neue;
        text-decoration: none;
        text-align: center;
        color: white;
        padding: 40px 0px 40px 0px;
    }

    #myform {
        width: 100%;
        max-width: 360px;
        margin: 30px auto 30px;
        padding: 10px 10px 10px 10px;
        background: #FFF;
        -webkit-border-radius: 4px;
        -moz-border-radius: 4px;
        border-radius: 4px;
        color : gray;
    }

    #menu-selection {
      background-color: #2d2c41;
      color : white;
      padding : 10px 10px 10px 10px;
      margin: 10px;
    }

    #start_date {
      background-color:  #2d2c41;
      color : white;
      padding : 10px 10px 10px 10px;
      margin: 10px;
    }

    #end_date {
      background-color: #2d2c41;
      color : white;
      padding : 10px 10px 10px 10px;
      margin: 10px;
    }

    #interval {
      background-color: #2d2c41;
      color : white;
      padding : 10px 10px 10px 10px;
      margin: 10px;
    }

    /** =======================
     * Main Container
     ===========================*/
    h1 {
        color: #FFF;
        font-size: 24px;
        font-weight: 400;
        text-align: center;
        margin-top: 80px;
     }

    h1 a {
        color: #c12c42;
        font-size: 16px;
     }

     .accordion {
        width: 100%;
        max-width: 360px;
        margin: 30px auto 20px;
        background: #FFF;
        -webkit-border-radius: 4px;
        -moz-border-radius: 4px;
        border-radius: 4px;
     }

    .accordion .link {
        cursor: pointer;
        display: block;
        padding: 15px 15px 15px 42px;
        color: #4D4D4D;
        font-size: 14px;
        font-weight: 700;
        border-bottom: 1px solid #CCC;
        position: relative;
        -webkit-transition: all 0.4s ease;
        -o-transition: all 0.4s ease;
        transition: all 0.4s ease;
    }

    .accordion li:last-child .link {
        border-bottom: 0;
    }

    .accordion li i {
        position: absolute;
        top: 16px;
        left: 12px;
        font-size: 18px;
        color: #595959;
        -webkit-transition: all 0.4s ease;
        -o-transition: all 0.4s ease;
        transition: all 0.4s ease;
    }

    .accordion li i.fa-chevron-down {
        right: 12px;
        left: auto;
        font-size: 16px;
    }

    .accordion li.open .link {
        color: #b63b4d;
    }

    .accordion li.open i {
        color: #b63b4d;
    }

    .accordion li.open i.fa-chevron-down {
        -webkit-transform: rotate(180deg);
        -ms-transform: rotate(180deg);
        -o-transform: rotate(180deg);
        transform: rotate(180deg);
    }

    .accordion li.default .submenu {display: block;}

    button {
        cursor: pointer;
        background-color: #2d2c41;
        color : white;
        padding : 10px 10px 10px 10px;
        margin: 10px;
        border-box : 3px;
        border-color: white;
        width: 50%;
        max-width: 300px;
        margin: 30px auto 20px;
        -webkit-border-radius: 4px;
        -moz-border-radius: 4px;
        border-radius: 4px;
    }

    button:hover{
        background-color: red;
    }
    /**-----------------------
     * Submenu - within the drop down
     -----------------------------*/
    .submenu {
       display: none;
       background: #444359;
       font-size: 14px;
    }

    .submenu li {
       border-bottom: 1px solid #4b4a5e;
    }

    .submenu a {
       display: block;
       text-decoration: none;
       color: #d9d9d9;
       padding: 12px;
       padding-left: 42px;
       -webkit-transition: all 0.25s ease;
       -o-transition: all 0.25s ease;
       transition: all 0.25s ease;
    }

    .submenu a:hover {
       background: #b63b4d;
       color: #FFF;
    }

    </style>
    <body>
    <h1>Choose a Probe</h1>
    <ul id="accordion" class="accordion">
        <li>
            <div class="link"><i class="fa fa-line-chart"></i>Choose Probe<i class="fa fa-chevron-down"></i>
            </div>
            <ul class="submenu"> """ + new_names + """

            </ul>
        </li>
    </ul>
    <p hidden id="not_here"></p>
    <div id = "myform">
        <form action=\"/""" + seven_digit_db_code + """\" method="POST">
        <label>Selected Probe:</label>
        <p><input name="menu-selection" type="text" id = "menu-selection" a href="#" readonly></p>
        <label> Start Date Time</label>
        <p><input name = "startdate" type="text" id="start_date" a href= "#" value=\"""" +startdate + """\" readonly></p>
        <label> End Date Time </label>
        <p><input name = "enddate" type="text" id="end_date" a href = "#" value=\"""" + enddate + """\" readonly></p>
        <label> Minutes </label>
        <p><input name = "interval" type="text" id="interval" a href = "#"></p>
        <button type="submit">Submit Me</button>
        </form>
    </div>
    </body>
    <script>
    $(function() {
    var Accordion = function(el, multiple) {
        this.el = el || {};
        this.multiple = multiple || false;

        // Private Variables
        var links = this.el.find('.link');
        // Event
        links.on('click', {el: this.el, multiple: this.multiple}, this.dropdown)
    }

    Accordion.prototype.dropdown = function(e) {
        var $el = e.data.el;
            $this = $(this),
            $next = $this.next();

        $next.slideToggle();
        $this.parent().toggleClass('open');

        if (!e.data.multiple) {
            $el.find('.submenu').not($next).slideUp().parent().removeClass('open');
        };
    }   

    var accordion = new Accordion($('#accordion'), false);
    });
    </script>
    <script>
    $(document).ready(function() {

        $("ul.submenu li").click(function() {
            console.log($(this).text());
            $("#menu-selection").val($(this).text()); 
        });             
    });
    </script>
    """

    return huge_string

def accordion_table():
    """ Makes another lovely table for the possible entities in one of these databases

    .. note :: This is where you can add in new databases!
    """
    _,cur = connect()

    list_of_new_names = []

    # this is where you could add a new table, like CF012
    for each_table in ['MS001','MS043','MS005','HT004']:

        nn = all_the_tables(cur, each_table)

        list_of_new_names.append(nn)

    huge_string = """
    <!doctype html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="I pity the foo who doesn't use PYTHI">
    <meta name="author" content="Fox">
    <title> PYTHI | PYthon-based Time-Series Harmonization and Interpolation </title>
    <link href='//fonts.googleapis.com/css?family=Open+Sans:400,700' rel='stylesheet' type='text/css'>
    <link href="http://maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css" rel="stylesheet">
    <script src = "//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    </head>
    <style>
        * {
        margin: 0;
        padding: 0;
        -webkit-box-sizing: border-box;
        -moz-box-sizing: border-box;
        box-sizing: border-box;
    }

    body {
        background: #2d2c41;
        font-family: 'Open Sans', Helvetica neue,   Sans-serif;
    }

    ul {
        list-style-type: none;
    }

    a {
        color: #b63b4d;
        text-decoration: none;
    }

    form{
        background: #2d2c41;
        font-family: 'Open Sans', Helvetica neue;
        text-decoration: none;
        text-align: center;
        color: white;
        padding: 40px 0px 40px 0px;
    }

    #myform{
        width: 100%;
        max-width: 360px;
        margin: 30px auto 30px;
        padding: 10px 10px 10px 10px;
        background: #FFF;
        -webkit-border-radius: 4px;
        -moz-border-radius: 4px;
        border-radius: 4px;
        color : gray;
    }

    #menu-selection{
      background-color: #2d2c41;
      color : white;
      padding : 10px 10px 10px 10px;
      margin: 10px;
    }

    #start_date{
      background-color:  #2d2c41;
      color : white;
      padding : 10px 10px 10px 10px;
      margin: 10px;
    }

    #end_date{
      background-color: #2d2c41;
      color : white;
      padding : 10px 10px 10px 10px;
      margin: 10px;
    }

    /** =======================
     * Main Container
     ===========================*/
    h1 {
        color: #FFF;
        font-size: 24px;
        font-weight: 400;
        text-align: center;
        margin-top: 80px;
     }

    h1 a {
        color: #c12c42;
        font-size: 16px;
     }

     .accordion {
        width: 100%;
        max-width: 360px;
        margin: 30px auto 20px;
        background: #FFF;
        -webkit-border-radius: 4px;
        -moz-border-radius: 4px;
        border-radius: 4px;
     }

    .accordion .link {
        cursor: pointer;
        display: block;
        padding: 15px 15px 15px 42px;
        color: #4D4D4D;
        font-size: 14px;
        font-weight: 700;
        border-bottom: 1px solid #CCC;
        position: relative;
        -webkit-transition: all 0.4s ease;
        -o-transition: all 0.4s ease;
        transition: all 0.4s ease;
    }

    .accordion li:last-child .link {
        border-bottom: 0;
    }

    .accordion li i {
        position: absolute;
        top: 16px;
        left: 12px;
        font-size: 18px;
        color: #595959;
        -webkit-transition: all 0.4s ease;
        -o-transition: all 0.4s ease;
        transition: all 0.4s ease;
    }

    .accordion li i.fa-chevron-down {
        right: 12px;
        left: auto;
        font-size: 16px;
    }

    .accordion li.open .link {
        color: #b63b4d;
    }

    .accordion li.open i {
        color: #b63b4d;
    }
    .accordion li.open i.fa-chevron-down {
        -webkit-transform: rotate(180deg);
        -ms-transform: rotate(180deg);
        -o-transform: rotate(180deg);
        transform: rotate(180deg);
    }

    .accordion li.default .submenu {display: block;}

    button {
        cursor: pointer;
        background-color: #2d2c41;
        color : white;
        padding : 10px 10px 10px 10px;
        margin: 10px;
        border-box : 3px;
        border-color: white;
        width: 50%;
        max-width: 300px;
        margin: 30px auto 20px;
        -webkit-border-radius: 4px;
        -moz-border-radius: 4px;
        border-radius: 4px;
        }

    button:hover{
        background-color: red;
    }
    /**---------------------------
     * Submenu
     -----------------------------*/
     .submenu {
        display: none;
        background: #444359;
        font-size: 14px;
     }

     .submenu li {
        border-bottom: 1px solid #4b4a5e;
     }

     .submenu a {
        display: block;
        text-decoration: none;
        color: #d9d9d9;
        padding: 12px;
        padding-left: 42px;
        -webkit-transition: all 0.25s ease;
        -o-transition: all 0.25s ease;
        transition: all 0.25s ease;
     }

     .submenu a:hover {
        background: #b63b4d;
        color: #FFF;
     }

    button {
        cursor: pointer;
        background-color: #2d2c41;
        color : white;
        padding : 10px 10px 10px 10px;
        margin: 10px;
        border-box : 3px;
        border-color: white;
        width: 50%;
        max-width: 300px;
        margin: 30px auto 20px;
        -webkit-border-radius: 4px;
        -moz-border-radius: 4px;
        border-radius: 4px;
     }
    </style>
    <body>
    <h1>Choose a Database </h1>
    <ul id="accordion" class="accordion">
        <li>
            <div class="link"><i class="fa fa-desktop"></i>MS001<i class="fa fa-chevron-down"></i></div>
            <ul class="submenu"> """ + list_of_new_names[0] + """

            </ul>
        </li>
        <li>
            <div class="link"><i class="fa fa-cogs"></i>MS043<i class="fa fa-chevron-down"></i></div>
            <ul class="submenu"> """ + list_of_new_names[1] + """
            </ul>
        </li>
        <li>
            <div class="link"><i class="fa fa-wrench"></i>MS005<i class="fa fa-chevron-down"></i></div>
            <ul class="submenu"> """ + list_of_new_names[2] + """
            </ul>
        </li>
        <li>
            <div class="link"><i class="fa fa-tint"></i>HT004<i class="fa fa-chevron-down"></i></div>
            <ul class="submenu">""" + list_of_new_names[3] + """
            </ul>
        </li>
    </ul>
    <p hidden id="not_here"></p>
    <div id = "myform">
        <form action = "/probes" method="POST">
        <label>Selected Database:</label>
        <p><input name="menu-selection" type="text" id = "menu-selection" a href="#" readonly></p>
        <label> Start Date Time</label>
        <p><input name = "startdate" type="text" id="start_date" a href = "#"></p>
        <label> End Date Time </label>
        <p><input name = "enddate" type="text" id="end_date" a href = "#"></p>
        <button type="submit" id="button"> Submit Me </button>
        </form>
    </div>
    </body>
    <script>
    $(function() {
    var Accordion = function(el, multiple) {
        this.el = el || {};
        this.multiple = multiple || false;

        // Private variables
        var links = this.el.find('.link');
        // Evento
        links.on('click', {el: this.el, multiple: this.multiple}, this.dropdown)
    }

    Accordion.prototype.dropdown = function(e) {
        var $el = e.data.el;
            $this = $(this),
            $next = $this.next();

        $next.slideToggle();
        $this.parent().toggleClass('open');

        if (!e.data.multiple) {
            $el.find('.submenu').not($next).slideUp().parent().removeClass('open');
        };
    }   

    var accordion = new Accordion($('#accordion'), false);
    });
    </script>
    <script>
    $(document).ready(function() {

        $("ul.submenu li").click(function() {
            console.log($(this).text());
            $("#menu-selection").val($(this).text()); 
        });             
    });
    </script>
    """

    return huge_string