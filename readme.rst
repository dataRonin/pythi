****************************************
PYTHI : PYthon-based Time Harmonizer and Integrator
****************************************

PYTHI (pronounced *pith-thee*) is a **bottle-backed time aggregator**.  Its
goal is to make possible all the functionality of **GLITCH** without relying on reference tables or CGI scripts. Operating under the wonderful WSGI protocols, PYTHI is **faster** and **more flexible** than **GLITCH** (rip: 2014). It provides a simple ``http`` based API that can be nested into the **GLITCH** ``[GET]`` syntax, or it can be called independently to respond to arbitrary HTTP requests by displaying html output. PYTHI can be used for **MS001, MS043 and testing is being conducted on MS005 and HT004**.


.. image:: http://i.imgur.com/1mBoSxy.jpg
    :alt: Mr.T shuns bad science
    :width: 500
    :height: 500
    :align: center


PYTHI is written in Python, (v. 2.7.10) and under the hood it needs the
`Bottle`_ and `Pymssql`_ libraries.


.. contents::
    :local:
    :depth: 1
    :backlinks: none


=============
Main Features
=============

* Supports ``[GET]`` request syntax used by Perl CGI scripts and "Cold Fusion" 
* Formatted, simple output can be easily copied into a .csv
* Does not need reference tables
* Authorization to the SQL-server using read-only authentication
* Open-Source and easy to read and work with
* Fails by throwing boolean falses to prevent bad data escaping
* Supports Python 2.7, which is commonly used by scientists
* Linux, Mac OS X ... and Windows?
* Documentation
* Octocat is the best.


=====
Usage
=====


Start the application from the command line


.. code-block:: bash

    $ python glitch_bottle.py


Point your web browser to your desired endpoint

.. code-block:: curl http://localhost:8080/dbcode=[5-character-code]&entity_num=[2-digit-entity]&probe_code=[8-character-probe-code]&start_date=[14-digit-date-integer]&end_date=[14-digit-date-integer]&interval=[integer-minutes-less-than-1440]



--------

*What follows is a detailed documentation. It covers the command syntax,
advanced usage, and also features additional examples.*


===========
map_glitch_2.py
===========

Using god's gift to SQL, the information_schema structure, we execute this:

.. code-block:: python

    get_cnames = "select column_name from fsdbdata.information_schema.columns where table_name like \'" + table_name + "\' and column_name not like \'dbcode\' and column_name not like \'stcode\' and column_name not like \'entity\' and column_name not like \'format\' and column_name not like \'%method\' and column_name not like \'event_code\' and column_name not like \'%level\' and column_name not like \'sitecode\' and column_name not like \'height\' and column_name not like \'%depth\' and column_name not like \'max%\' and column_name not like \'min%\' and column_name not like \'%max%\' and column_name not like \'%min%\' and column_name not like \'%stddev\'"

that's right, it's all the column names you'll ever need to do all the harmonization and aggregation. Subsequently, we "try" all of the four methods of combining Probe, Probe_code, Date, and Date_Time to get the appropriate information, like this:

.. code-block:: python

        sql = "select " + cnames_to_list + " from fsdbdata.dbo." + table_name + " where date >= \'" + startdate + "\' and date <= \'" + enddate +"\' and probe like \'" + probe_code +"\' order by date asc"

This information is returned so that Glitching may occur.

===========
pyGLITCH_backend.py
===========

Discussion of the back-end integration here

=============
glitch_bottle.py
=============


Discussion of the web interface here


=======
License
=======

Please see `LICENSE <http://creativecommons.org/licenses/by-sa/3.0/>`_.

