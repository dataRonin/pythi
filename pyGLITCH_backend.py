#!usr/bin/python
import csv
import pymssql
import time
import datetime
import itertools
import sys
import math
import map_glitch_2 as mg
from collections import defaultdict

def connect():
    ''' connect to the fsdbdata database'''

    conn = pymssql.connect(server = 'stewartia.forestry.oregonstate.edu:1433', user='ltermeta', password='$CFdb4LterWeb!')
    cursor = conn.cursor()

    return conn, cursor

def flag_count(flag_list):
    """ Quickly count flags in a list, outputing a dictionary and an integer of the count.

    The output is like: (<int>, {'x': count(x), 'y': count(y)})
    """
    flag_counter = defaultdict(int)
    for flag in flag_list:
        flag_counter[flag] +=1

    return flag_counter

def daily_flag(flag_counter, critical_value, critical_flag):
    """ Figure out what the daily flag is based on the outputs of the flag counter.
    """
    if flag_counter[critical_flag] >= critical_value:
        return critical_flag

    elif flag_counter['E']/critical_value > 0.05:
        return 'E'
    elif flag_counter['Q']/critical_value > 0.05:
        return 'Q'
    elif flag_counter['M']/critical_value > 0.2:
        return 'M'
    elif (flag_counter['E'] + flag_counter['Q'] + flag_counter['M'])/critical_value > 0.05:
        return 'Q'
    else:
        return critical_flag

def drange(start, stop, step):
  ''' returns a date range generator '''
  r = start
  while r < stop:
      yield r
      r += step

def create_date_list_from_mapg(output_from_mapg):
    """Get all dates where we have valid data to key from"""

    try:
        word = 'DATE_TIME'
        dr_1 = output_from_mapg[word]
        dr = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dr_1]
        return dr

    except Exception:
        try:
            word = 'DATE'
            dr_1 = output_from_mapg[word]
            dr = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dr_1]
            return dr
        except Exception:
            try:
                word = 'DATETIME'
                dr_1 = output_from_mapg[word]
                dr = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dr_1]
                return dr
            except Exception:
                try:
                    word = 'DT'
                    dr_1 = output_from_mapg[word]
                    dr = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dr_1]
                except Exception:
                    print("please specify the date time columns name")
                    return False

def create_date_bounds_from_date_list(dr,interval):
    """ creates date bounds from date list"""

    if dr == False:
        return False

    try:
        first_date = dr[0]
    except Exception:
        first_date = datetime.datetime.strptime(dr[0], '%Y-%m-%d %H:%M:%S')

    try:
        last_date = dr[-1] + datetime.timedelta(minutes=interval)
    except Exception:
        last_date = datetime.datetime.strptime(dr[-1], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=interval)

    return first_date, last_date

def to_dated_dictionary(output_from_mapg, *dr):
    """create a data dictionary containing the data columns which are needed to make the outputs from glitch"""

    try:
        dr
    except NameError:
        dr = create_date_list_from_mapg(output_from_mapg)

    valid_data = {}

    for each_key in output_from_mapg.keys():
        # check each column in the data and if its not the date column or the probe column then we will import it into the data we want to work with
        if 'DATE' in each_key:
            continue
        elif 'PROBE' in each_key:
            continue
        else:
            temp_d = zip(dr,output_from_mapg[each_key])

            # only add it to the valid data if indeed it is actually a valid key
            if each_key not in valid_data:
                valid_data[each_key] = dict(temp_d)
            else:
                print("key is already in valid_data")

    return valid_data

def numeric_or_flag(valid_data):
    """ determine if the data in the valid data is numeric or flag """
    numeric_cols = []
    flag_cols = []

    for each_key in valid_data.keys():
        try:
            is_number = float(list(valid_data[each_key].values())[0])
            numeric_cols.append(each_key)
        except (TypeError, ValueError):
            try:
                is_string = (list(valid_data[each_key].values())[0]).upper()
                flag_cols.append(each_key)
            except AttributeError:
                continue

    return numeric_cols, flag_cols

def is_tot(numeric_cols):
    """ if the column is a total return false """

    istot = [x for x in numeric_cols if 'TOT' in x and 'MEAN' not in x]

    if istot != []:
        return istot
    else:
        return False


def glitch_setup(valid_data, interval, output_from_mapg, dbcode, entity, probe_code):
    """ Set up and ultimately run the GLITCH. Three ranges are passed over: dr, which is the actual dates measurements were taken; super_iterator, which is the ideal range we want to map into, and one_minute_iterator, which is 1 minute copies of the mean that subdivide each actually measured interval. """


    # create a list of dates from output of the map - not an iterator!
    dr = create_date_list_from_mapg(output_from_mapg)

    # create the date bounds from the date list
    first_date, last_date = create_date_bounds_from_date_list(dr, interval)

    # super_iterator is an ideal range from each interval to the next one (i.e. 15 minute intervals, 35 minute intervals, etc.)
    super_iterator = drange(first_date, last_date + datetime.timedelta(minutes=interval), datetime.timedelta(minutes=interval))

    # min range is an ideal range for one minute intervals to aggregate
    temp_one_minute_iterator = drange(first_date, last_date, datetime.timedelta(minutes=1))
    one_minute_iterator = [x for x in temp_one_minute_iterator]

    #import pdb; pdb.set_trace()
    # get the numeric or flag columns
    nc, fc = numeric_or_flag(valid_data)

    # if the numeric data is one column and it is a total, our duration is the number of minutes in that total
    if len(nc) == 1 and is_tot(nc) != False:
        print("use total glitch")

        # identify the data and flags within the valid data
        data = valid_data[nc[0]]
        flags = valid_data[fc[0]]
        name_list = [x for x in nc]

        if len(name_list) > 1:
            print("the name list should not be larger than 1 for this method!")

        flag_list = [x+"_FLAG" for x in name_list]

        # results are from the function `glitch`
        res = glitch(dr, super_iterator, one_minute_iterator, data, flags,"TOTAL")
        res2 = create_glitch(res, "TOTAL")
        returnable = bottle_one(res2, dbcode, entity, probe_code, name_list, flag_list)
        return returnable

    # if the numeric data is one column and it's not total, then we use the normal glitch
    elif len(nc) == 1 and is_tot(nc) == False:

        print("use glitch")
        data = valid_data[nc[0]]
        flags = valid_data[fc[0]]

        name_list = [x for x in nc]

        if len(name_list) > 1:
            print("the name list should not be larger than 1 for this method!")

        flag_list = [x+"_FLAG" for x in name_list]

        res = glitch(dr, super_iterator, one_minute_iterator, data, flags,"NORMAL")
        res2 = create_glitch(res,"NORMAL")
        returnable = bottle_one(res2, dbcode, entity, probe_code, name_list, flag_list)
        return returnable

    # if the numeric data is more than one column and it's all not total, we will use one of the windy methods
    elif len(nc) >= 1 and is_tot(nc)== False:

        print("use windy glitch- either prop or sonic tbd.")
        res_multi = {}
        name_list = []

        # prop
        if len(nc) <= 4:


            try:
                dirname = [x for x in nc if 'DIR' in x][0]
                name_list.append(dirname)
            except Exception:
                pass

            try:
                spdname = [x for x in nc if 'SPD' in x][0]
                name_list.append(spdname)
            except Exception:
                pass

            try:
                magname = [x for x in nc if 'MAG' in x][0]
                name_list.append(magname)
            except Exception:
                pass

        # sonic
        elif len(nc) >=4:


            try:
                dirname = [x for x in nc if 'DIR' in x][0]
                name_list.append(dirname)
            except Exception:
                pass

            try:
                spdname = [x for x in nc if 'SPD' in x][0]
                name_list.append(spdname)
            except Exception:
                pass

            try:
                airname = [x for x in nc if 'AIR' in x][0]
                name_list.append(airname)
            except Exception:
                pass

            try:
                uxname = [x for x in nc if 'WUX' in x][0]
                name_list.append(uxname)
            except Exception:
                pass

            try:
                uyname = [x for x in nc if 'WUY' in x][0]
                name_list.append(uyname)
            except Exception:
                pass

        for each_item in name_list:

            flag_name = each_item + "_FLAG"

            try:
                flags = valid_data[flag_name]

            except Exception:
                # if flags from other attributes fail, result back to the flag from speed for these attributes
                flags = valid_data[fc[0]]

            data = valid_data[each_item]

            res = glitch(dr, super_iterator, one_minute_iterator, data, flags,"NORMAL")

            if each_item not in res_multi:
                res_multi[each_item] = res
            else:
                print("item already accounted for")

            # repopulate the super-iterator
            super_iterator = drange(first_date, last_date + datetime.timedelta(minutes=interval), datetime.timedelta(minutes=interval))

            # repopulate the min-range
            one_minute_iterator = [x for x in drange(first_date, last_date, datetime.timedelta(minutes=1))]

        windmag, winddir = create_glitch_windpro(res_multi[spdname], res_multi[dirname])

        # we only get "mag" from prop
        try:
            res_multi.update({magname : windmag})
        except Exception:
            pass

        res_multi.update({dirname : winddir})

        possible_glitches = res_multi.keys()

        try:
            can_glitch = [x for x in res_multi.keys() if x not in [dirname, magname]]
        except Exception:
            can_glitch = [x for x in res_multi.keys() if x != dirname]

        for each_glitch in can_glitch:
            res2 = create_glitch(res, "NORMAL")
            res_multi.update({each_glitch: res2})

        returnable = bottle_many(res_multi, dbcode, entity, probe_code)
        #print res_multi
        #import pdb; pdb.set_trace()
        return returnable

    # when the numerical columns are more than 1 and the TOTAL needs to be computed
    elif len(nc) >= 1 and is_tot(nc) != False:

        print("Solar...")

        res_multi = {}

        for each_column in nc:
            data = valid_data[each_column]
            flag_name = each_column + "_FLAG"

            try:
                flags = valid_data[flag_name]
            except Exception:
                flags = valid_data[fc[0]]

            if each_column == is_tot(nc):
                res = glitch(dr, super_iterator, one_minute_iterator, data, flags,"TOTAL")
                res2 = create_glitch(res, "TOTAL")
            else:
                res = glitch(dr, super_iterator, one_minute_iterator, data, flags,"NORMAL")
                res2 = create_glitch(res, "NORMAL")

            if each_column not in res_multi:
                res_multi[each_column]=res2
            elif each_column in res_multi:
                print("column already added")

            # repopulate the super-iterator
            super_iterator = drange(first_date, last_date + datetime.timedelta(minutes=interval), datetime.timedelta(minutes=interval))

            # repopulate the min-range
            one_minute_iterator = [x for x in drange(first_date, last_date, datetime.timedelta(minutes=1))]

        #print res_multi
        #import pdb; pdb.set_trace()
        returnable = bottle_many(res_multi, dbcode, entity, probe_code)
        return returnable

def glitch(dr, super_iterator, one_minute_iterator, data, flags, method):
    """ iterating over one data and its flags.
    super_iterator is the ideal interval,
    one_minute_iterator is the one minute interval
    """

    # store the values for the current range and their flags
    t_mean = []
    f_mean = []

    # define some results
    results = {}

    # make an iterator to walk the known date range (i.e. 10:00, 10:05, 10:10 etc.)
    date_range_iterator = iter(dr)

    # the outer try is to wrap the stop iteration
    try:

        # ex. 2010-10-01 00:00:00 - the first date time of the real date range
        try:
            # for python 3
            this_date = next(date_range_iterator)
        except Exception:
            # for python 2
            this_date = date_range_iterator.next()

        # ex. 2010-10-01 00:05:00 - the subsequent date time in the real date range
        try:
            # for python 3
            subsequent = next(date_range_iterator)
        except Exception:
            # for python 2
            subsequent = date_range_iterator.next()

        if method == "TOTAL":
            # calculates the duration between the start date and the next measurement taken. For example, with five minute data going from 2014-11-01 00:00:00 to 2014-11-01 00:00:05, this would give back datetime.timedelta(0,300) --> always it is in (days, seconds)
            duration_1= (subsequent-this_date)
            # convert duration_1 to minutes
            duration = duration_1.seconds/60 + duration_1.days*(86400/60)
        else:
            pass

    except StopIteration:
        print("""You have selected an ending date which occurs prior to the next measurement. Try adding a small amount of time to the input ending date.
        For example, if you gave 2002-10-02 00:00:00 and 2002-10-03 00:00:00 for PPTCEN01, this daily measurement would only include that first midnight point. You could change the end date to 2002-10-03 00:05:00, which would then make sure that the total found at 2002-10-03 was distributed back over the previous interval if needed.
        """)


    # The first point in the super_iterator is the first input for the GLITCH. The first checkpoint is actually the 0th value, but we haven't accumulated data to this point
    try:
        checkpoint = next(super_iterator)
    except Exception:
        checkpoint = super_iterator.next()

    for each_minute in one_minute_iterator:

        # if the minute is the checkpoint, update the dictionary to the accumulated values
        # for example if it is 10-01-01 13:00:00 and that's a 13 min checkpoint, we get the values from 1-13 minutes in the dictionary for that checkpoint(so it is the previous minutes to that one)

        if each_minute == checkpoint and checkpoint not in results:

            # put the checkpoint in the results
            results[checkpoint] = {'val': t_mean, 'fval': f_mean}

            # set the storage to empty
            t_mean = []
            f_mean = []

            # update the checkpoint by 1:
            try:
                checkpoint = next(super_iterator)
            except Exception:
                checkpoint = super_iterator.next()

        elif each_minute == checkpoint and checkpoint in results:
            print("Check point at " + datetime.datetime.strftime(each_minute, '%Y-%m-%d %H:%M:%S') + "is in the results already!")

        elif each_minute != checkpoint:
            pass


        # we check if the value changes and start accumulating to the next date...
        # this would get say between 10-01-01 00:01:00 and 10-01-01 00:05:00 if `this_date` were at 0 and subsequent at 5.
        # for each of these minutes we would give one of the mean values and flags
        if each_minute > this_date and each_minute <= subsequent and method == "TOTAL":

            try:
                # append to the data the total from the subsequent divided by the duration of the interval
                t_mean.append(str(round(float(data[subsequent])/duration,3)))
                f_mean.append(flags[subsequent])
                # if that fails, add the interval
            except Exception:
                t_mean.append(data[subsequent])
                f_mean.append(flags[subsequent])

        # we check if the value changes and start accumulating to the next date...
        # this would get say between 10-01-01 00:01:00 and 10-01-01 00:05:00
        # for each of these minutes we would give one of the mean values and flags
        if each_minute > this_date and each_minute <= subsequent and method =="NORMAL":

            t_mean.append(data[subsequent])
            f_mean.append(flags[subsequent])

        # move up by one the output interval if the current minute is the subsequent. Remove the first entry from the data which represents the former interval and add in the entry for this minute, which represents now.
        if each_minute == subsequent:

            #print("changing minute start from :" + datetime.datetime.strftime(this_date,'%Y-%m-%d %H:%M:%S'))
            this_date = subsequent
            #print("to:" + datetime.datetime.strftime(this_date,'%Y-%m-%d %H:%M:%S'))
            try:
                subsequent = next(date_range_iterator)
            except Exception:
                try:
                    subsequent = date_range_iterator.next()
                except Exception:
                    return results

        elif each_minute > subsequent:
            print("the minute should not exceed the subsequent")

    return results

def create_glitch(results, method):
    """
    Time to make the right glitches
    """
    # output structure
    final_glitch = {}

    for each_glitch in sorted(results.keys()):

        # if it's not the first measurement, we want to make sure that we go from minute 1 to minute end so do this.
        if len(results[each_glitch]['val']) > 1:
            results[each_glitch]['val'].pop(0)
            results[each_glitch]['val'].append(results[each_glitch]['val'][-1])
            results[each_glitch]['fval'].pop(0)
            results[each_glitch]['fval'].append(results[each_glitch]['val'][-1])

        if results[each_glitch] != [] and method == "TOTAL":

            # if the data is precip (or solar total), the results are a sum of the intermediate values, after you have divided by the duration of the interval. If Nones exist it won't add so you will need to instead do the sum of the intermediate values which are not None
            try:
               # now that the duration is being calculated we can sum again
                mean_val = round(sum([float(x) for x in results[each_glitch]['val']]),2)

            except Exception:
                values = [float(results[each_glitch]['val'][index]) for index,x in enumerate(results[each_glitch]['val']) if x != None and x != "None"]

                if values == []:
                    mean_val = "None"

                else:
                    mean_val = round(sum(values),2)

        elif results[each_glitch] != [] and method == "NORMAL":
            try:
                mean_val = round(sum([float(x) for x in results[each_glitch]['val']])/len(results[each_glitch]['val']),2)

            except Exception:
                values = [float(results[each_glitch]['val'][index]) for index,x in enumerate(results[each_glitch]['val']) if x != None and x != "None"]

                if values == []:
                    mean_val = "None"

                else:
                    mean_val = round(sum(values)/len(values),2)

        else:
            print("some other method?")

        # for flagging
        try:
            num_flags = len(results[each_glitch]['fval'])

            if 'E' not in results[each_glitch]['fval'] and 'M' not in results[each_glitch]['fval'] and 'Q' not in results[each_glitch]['fval']:
                flagged_val = 'A'

            else:
                numM = len([x for x in results[each_glitch]['fval'] if x == 'M'])
                numE = len([x for x in results[each_glitch]['fval'] if x == 'E'])
                numQ = len([x for x in results[each_glitch]['fval'] if x == 'Q'])


                if numE/num_flags > 0.05:
                    flagged_val = 'E'
                elif numQ/num_flags > 0.05:
                    flagged_val = 'Q'
                elif (numE + numM + numQ)/num_flags > 0.05:
                    flagged_val = 'Q'
                elif numM/num_flags > 0.2:
                    flagged_val = 'M'
                    mean_val = None
                else:
                    flagged_val = 'A'

        except Exception:
            print("An exception was thrown in flag handling.")
            flagged_val = 'M'
            mean_val = None

        if each_glitch not in final_glitch:
            final_glitch[each_glitch] = {'mean': mean_val, 'flags': flagged_val}
        elif each_glitch in final_glitch:
            print("already have this glitch")

    print(final_glitch)
    return final_glitch

def create_glitch_windpro(results1, results2):
    """
    from the speed we get the x and y components for each direction for the magnitude
    then we add these up over the course of the glitch and take the sqrt
    we also do the wind direction here
    """
    final_glitch_mag= {}
    final_glitch_dir ={}

    for each_glitch in sorted(results1.keys()):

        if results1[each_glitch]['val'] != [] and results2[each_glitch]['val'] != []:

            num_valid_obs = len([x for x in results1[each_glitch]['val'] if x != None and x != 'None'])
            num_valid_obs2 = len([x for x in results2[each_glitch]['val'] if x != None and x != 'None'])

            # the shorter of the two is the length of observations which are valid
            if num_valid_obs > num_valid_obs2:
                num_valid_obs = num_valid_obs2
            else:
                pass

            try:
                ypart = (sum([float(speed) * math.sin(math.radians(float(x))) for (speed, x) in itertools.izip(results1[each_glitch]['val'], results2[each_glitch]['val']) if speed != 'None' and x != 'None'])/num_valid_obs)**2
            except Exception:
                ypart = None

            try:
                xpart = (sum([float(speed) * math.cos(math.radians(float(x))) for (speed, x) in itertools.izip(results1[each_glitch]['val'],results2[each_glitch]['val']) if speed != 'None' and x != 'None'])/num_valid_obs)**2
            except Exception:
                xpart = None

            try:
                glitched_mag = math.sqrt(ypart + xpart)
            except Exception:
                glitched_mag = None

            try:
                theta_u = math.atan2(sum([float(speed) * math.sin(math.radians(float(x))) for (speed, x) in itertools.izip(results1[each_glitch]['val'], results2[each_glitch]['val']) if speed != 'None' and x != 'None'])/num_valid_obs, sum([float(speed) * math.cos(math.radians(float(x))) for (speed, x) in itertools.izip(results1[each_glitch]['val'],results2[each_glitch]['val']) if speed != 'None' and x != 'None'])/num_valid_obs)
            except Exception:
                theta_u = None

            try:
                glitched_dir = round(math.degrees(theta_u),3)
            except Exception:
                glitched_dir = None

            try:
                if glitched_dir < 0.:
                    glitched_dir = 360+glitched_dir
            except Exception:
                glitched_dir = None

            try:
                num_flags = len(results1[each_glitch]['fval'])
                num_flags2 = len(results2[each_glitch]['fval'])

                # if all the flags are okay then the values are ok
                if 'E' not in results1[each_glitch]['fval'] and 'M' not in results1[each_glitch]['fval'] and 'Q' not in results1[each_glitch]['fval'] and 'E' not in results2[each_glitch]['fval'] and 'M' not in results2[each_glitch]['fval'] and 'Q' not in results2[each_glitch]['fval']:

                    glitched_mag_flag = 'A'
                    glitched_dir_flag = 'A'

                else:
                    numM = len([x for x in results1[each_glitch]['fval'] if x == 'M'])
                    numM2 = len([x for x in results2[each_glitch]['fval'] if x == 'M'])
                    numE = len([x for x in results1[each_glitch]['fval'] if x == 'E'])
                    numE2 = len([x for x in results2[each_glitch]['fval'] if x == 'E'])
                    numQ = len([x for x in results1[each_glitch]['fval'] if x == 'Q'])
                    numQ2 = len([x for x in results2[each_glitch]['fval'] if x == 'Q'])

                    # test that the wind is not missing separately
                    if numM2/num_flags2 > 0.2:
                        glitched_dir_flag = 'M'
                        glitched_dir = None
                        glitched_mag_flag = 'M'
                        glitched_mag = None

                    elif numM/num_flags > 0.2:
                        glitched_mag_flag = 'M'
                        glitched_mag = None

                    elif numE/num_flags > 0.05 or numE2/num_flags2 > 0.05:
                        glitched_mag_flag = 'E'
                        glitched_dir_flag = 'E'

                    elif numM/num_flags <= 0.2 and (numE + numM + numQ)/num_flags > 0.05 or numM2/num_flags2 > 0.2 and (numE2 + numM2 + numQ2)/num_flags2 > 0.05:
                        glitched_mag_flag = 'Q'
                        glitched_dir_flag = 'Q'

                    else:
                        glitched_mag_flag = 'A'
                        glitched_dir_flag = 'A'


            except Exception:
                print("an exception was thrown for wind")
                #import pdb; pdb.set_trace()
                glitched_mag_flag = 'M'
                glitched_mag = None
                glitched_dir_flag = 'M'
                glitched_dir = None

        elif results1[each_glitch]['val'] == [] or results2[each_glitch]['val'] == []:
            glitched_mag = None
            glitched_mag_flag = 'M'

        # direction can be missing if there is speed, so separate here.
        if results2[each_glitch]['val'] ==[]:
            glitched_dir = None
            glitched_dir_flag = 'M'

        # throw b or n flag if speed or mag is less than detection limits
        if glitched_mag < 1.0 and glitched_mag > 0.3:
            glitched_mag_flag = "B"
        elif glitched_mag <= 0.3:
            glitched_mag_flag = "N"
        else:
            pass

        try:
            final_glitch_mag[each_glitch] = {'mean': round(glitched_mag,2), 'flags': glitched_mag_flag}
        except Exception:
            final_glitch_mag[each_glitch] = {'mean': None, 'flags': 'M'}

        try:
            final_glitch_dir[each_glitch] = {'mean': round(glitched_dir,2), 'flags': glitched_dir_flag}
        except Exception:
            final_glitch_dir[each_glitch] ={'mean': None, 'flags': 'M'}

    return final_glitch_mag, final_glitch_dir

def bottle_one(results, dbcode, entity, probe_code, name_list, flag_list):
    """ Creates a bottle-served output for a one-mean attribute like airtemp or relhum. Also works for totals. `name_list` and `flag_list` are created when `glitch_setup` is run.
    """


    # cat together the names and flags in the single glitch scenario
    title_string_1 = name_list + flag_list
    title_string = ", ".join(title_string_1)

    # set to a list by force in Python 3
    dates = sorted(list(results.keys()))

    values = [str(results[x]['mean']) for x in dates]
    flags = [str(results[x]['flags']) for x in dates]

    datestrings = [datetime.datetime.strftime(x,'%Y-%m-%d %H:%M:%S') for x in dates]

    all_row = []

    for index, item in enumerate(datestrings):
      new_row = [str(dbcode), str(entity), probe_code, item, values[index], flags[index]]
      nr = ", ".join(new_row)
      nr_1 = nr[0:] +"</br>"
      all_row.append(nr_1)

    my_data = "".join(all_row)

    returnable = "DBCODE, ENTITY, PROBE_CODE, DATE_TIME," + title_string + "</br>" + my_data + "</body></html>"

    return returnable

def bottle_many(results, dbcode, entity, probe_code):
    """ Creates a bottle-served output for a multi-mean attribute like windpro, etc.
    """

    # set to a list by force for python 3
    names = list(results.keys())

    title_string_1 = [names[x] + ", " + names[x] + "_FLAG" for x, value in enumerate(names)]
    title_string = ", ".join(title_string_1)

    dates = sorted(results[names[0]].keys())

    all_row = {}

    all_row_2 = []
    #datestrings = [datetime.datetime.strftime(x,'%Y-%m-%d %H:%M:%S') for x in dates]

    for index, each_key in enumerate(names):
        num_indices = len(names)

        for each_date in dates:

            if each_date not in all_row:
                all_row[each_date]=[datetime.datetime.strftime(each_date,'%Y-%m-%d %H:%M:%S'), dbcode, entity, probe_code , str(results[each_key][each_date]['mean']),str(results[each_key][each_date]['flags'])]

            elif each_date in all_row:
                all_row[each_date].append(str(results[each_key][each_date]['mean']))
                all_row[each_date].append(str(results[each_key][each_date]['flags']))

                if index == num_indices - 1:
                    all_row[each_date].append("</br>")
                else:
                    pass


    for each_item in sorted(all_row.keys()):

        nr = ", ".join(all_row[each_item])
        all_row_2.append(nr)

        my_data = "".join(all_row_2)

    returnable = "DBCODE, ENTITY, PROBE_CODE, DATE_TIME," + title_string + "</br>" + my_data + "</body></html>"

    return returnable


def simple_glitch(dbcode, entity, probe_code, start_date, end_date, interval):
    """ Does a very simple GLITCH, for testing purposes.
    """

    _, cursor = mg.connect()
    dbname = str(dbcode) + str(entity)
    cnames = mg.gather_column_names(cursor, dbname)

    o1 = mg.system_tables(cursor, dbname, probe_code, cnames, start_date, end_date)

    dr = create_date_list_from_mapg(o1)

    fd, ld = create_date_bounds_from_date_list(dr, int(interval))

    vd = to_dated_dictionary(o1, *dr)

    nc, fc = numeric_or_flag(vd)

    returned_html = glitch_setup(vd, int(interval), o1, dbcode, entity, probe_code)

    return returned_html

if __name__ == "__main__":

    _, cursor = mg.connect()

    cnames = mg.gather_column_names(cursor,'MS04313')

    o1 = mg.system_tables(cursor, 'MS04313', 'PPTCEN01', cnames,'2014-11-01 00:00:00','2015-01-20 00:00:00')

    dr = create_date_list_from_mapg(o1)

    fd, ld = create_date_bounds_from_date_list(dr, 90)

    vd = to_dated_dictionary(o1, *dr)

    nc, fc = numeric_or_flag(vd)

    returned_value = glitch_setup(vd, 90, o1, 'MS043','13','PPTCEN01')

    print(returned_value)
