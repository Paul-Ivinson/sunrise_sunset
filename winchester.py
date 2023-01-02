#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  winchester.py
#
#  Copyright 2022 Paul Ivinson <paivinson@gmail.com>
#
# V1 initial writing                                20Dec2022   
#
#
"""winchester Version 1.0.0
"""
""" 
Calculate the sun rise annd sun set times for Winchester, Hants, UK

optional arguments:
  -h, --help            show this help message and exit
  -q                    Quiet - absolutely no messages. Useful from the
                        command line. Make this the first option or you will
                        get messages as the other options are processed.
  -v, --verbose         Verbose - extra messages. Don't use -v and -q together
                        because the behaviour isn't defined.
  --date Date           Date of sunrise & sunset in the format YYYYMMDD.
                        Defaults to today.
  --zenith Zenith       The zenith of the sun at sunrise and sunset.

  zenith should be one of the following
      official:     90 degrees 50 minutes
      civil:        96 degrees 
      nautical:     102 degrees 
      astronomical: 108 degrees

"""

# Built-in Python modules
import os
import sys
import argparse
import datetime
import time
import re
import unittest

# Additional modules
# we could do the following 
# import dateutil.tz
# but it makes usage rather messy i.e.
# dateutil.tz.tz.tzutc()
from dateutil import tz

#---- our own modules ---------------------------------#
import sunrise_sunset

# Note the start time. Do this as soon as possible, even before the
# various class and function definitions have been read.
start_time = time.time()

#===============================================================#
# Default values are here to allow this module to be imported.  #
#===============================================================#
verbose          = 1  # verbose = 1 gets you basic messages.
debug            = False
total_time       = 0.0
    
#===============================================================#
# define Exceptions                                             #
#===============================================================#

# None so far

#===============================================================#
# define classes                                                #
#===============================================================#

# None so far
        
#===============================================================#
# define functions                                              #
#===============================================================#
# Utility functions ============================================#
def message(verbosity, msg, module=__name__):
    global verbose, start_time
    if verbosity == 0 and verbose == 0:
        # Cleaner messages when in quiet mode
        print(msg)
    elif verbosity <= verbose:
        print("---- %4.4f %s - %s" % ((time.time()-start_time), module, msg))
    return

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

#==== Used by the argument parsing =====================================
def valid_date(date_str):
    "Validates a date in the format YYYYMMDD, Returns a datetime.date object"

    # is the supplied date the correct length?
    if not len(date_str) == 8:
        msg = 'valid_date - Error validating date. Wrong number of characters. Date="%s"' % date_str
        raise argparse.ArgumentTypeError(msg)

    # is the supplied date all digits?
    if not is_integer(date_str):
        msg = 'valid_date - Error validating date. Format not YYYYMMDD Date="%s"' % date_str
        raise argparse.ArgumentTypeError(msg)

    year  = int(date_str[:4])
    month = int(date_str[4:6])
    day   = int(date_str[6:8])
    #print('year = ', year, 'month = ', month, 'day = ', day)

    try:
        date_obj = datetime.date(year, month, day)
    except ValueError:
        msg = "valid_date - Error validating date. Value error. Year = '%s', Month = '%s', Day = '%s'" % (year, month, day)
        raise argparse.ArgumentTypeError(msg)

    return(date_obj)

#====================================================================#
# Setup functions (return True or False)                             #
#====================================================================#

# None so far

#====================================================================#
# Checking functions (return True or False)                          #
#====================================================================#

# None so far

#===============================================================#
# processing finctions                                          #
#===============================================================#

# None so far

#===============================================================#
# define main()                                                 #
#===============================================================#
def main():
    global verbose

    #==================================================================#
    # Parse arguments                                                  #
    #==================================================================#
    parser = argparse.ArgumentParser(
        description=__doc__,
        # Take control of the formatting of the epilog
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        
        zenith should be one of the following
            official:     90 degrees 50 minutes
            civil:        96 degrees 
            nautical:     102 degrees 
            astronomical: 108 degrees
        """,
        add_help=True)

    # First argument to be processed is ..
    parser.add_argument('-q',              dest='verbose',  action='store_const', const=0, default=1, help="Quiet - absolutely no messages. Useful from the command line. Make this the first option or you will get messages as the other options are processed.")
    
    # Positional args come next
    #     None

    # Optional args
    parser.add_argument('-v', '--verbose', dest='verbose',  action='count',                default=1, help="Verbose - extra messages. Don't use -v and -q together because the behaviour isn't defined.")
    parser.add_argument('--date',          dest='Date',     metavar='Date', type=valid_date, help='Date of sunrise & sunset in the format YYYYMMDD.')
    parser.add_argument('--zenith',        dest='Zenith',   metavar='Zenith', choices=['official', 'civil', 'nautical', 'astronomical'], default='official', help='The zenith of the sun at sunrise and sunset.')

    this_script = os.path.basename(sys.argv[0])

    args = vars(parser.parse_args())

    for key in args.keys():
        o = key
        a = args[key]
        # Standard options
        if o == 'v': verbose = a
        if o == 'q': verbose = 0
        #if o == 'h': usage()
        #if o == 'help': usage()
        if o == 'verbose': verbose = a
        # Now print the option - if -q then message will be suppressed
        message (1, 'Option %s = %s' %(o,a))
        # Options specific to this script
        if o == 'Date': date_given = a
        if o == 'Zenith': zenith = a
        
    message(1, "%s" % re.sub(r'\n', '', __doc__))
    message(1, "Started %s" % time.strftime("%a, %d %b %Y %H:%M:%S"))
    message(1, "Python interpreter running on %s" % re.sub(r'\n', '', sys.platform))
    message(1, "Interpreter version = %s" % re.sub(r'\n', '', sys.version))
    message(1, "Invoked via %s" % sys.argv[0])        
        
    if sys.platform.lower()[0:5] == 'linux':
        message(1, '%s - Running on Linux.' % this_script)

    if sys.platform.lower()[0:6] == 'cygwin':
        message(1, '%s - Running on Cygwin.' % this_script)

    message(1,'%s - Verbose level = %s' % (this_script, verbose))
    message(1,'%s - Initialisation complete.' % this_script)

    #===============================================================#
    # Start work                                                    #
    #===============================================================#
    # Preserve the incoming argv set
    master_argv = sys.argv

    winchester_latitude  = 51.0632
    winchester_longitude = -1.308
    
    today = False
    if not date_given:
        date_given = datetime.date.today()
        today = True
        
    ss_verbose = verbose - 1
    if ss_verbose < 0: 
        ss_verbose = 0

    winchester_location = sunrise_sunset.location(winchester_latitude, winchester_longitude, ss_verbose)
    sunrise = winchester_location.sunrise(date_given, zenith)
    sunset = winchester_location.sunset(date_given, zenith)
    day_length = sunset - sunrise 
    
    if today:
        message(0, "Sunrise in Winchester (UK) today is %i:%02i:%02i" % (sunrise.hour, sunrise.minute, sunrise.second))
        message(0, "Sunset in Winchester (UK) today is %i:%02i:%02i" % (sunset.hour, sunset.minute, sunset.second))
        message(0, "Day length in Winchester (UK) today is %s" % day_length)
    else:
        message(0, "Sunrise in Winchester (UK) on %i-%02i-%02i is %i:%02i:%02i" % (sunrise.year, sunrise.month, sunrise.day, sunrise.hour, sunrise.minute, sunrise.second))
        message(0, "Sunset in Winchester (UK) on %i-%02i-%02i is %i:%02i:%02i" % (sunset.year, sunset.month, sunset.day, sunset.hour, sunset.minute, sunset.second))
        message(0, "Day length in Winchester (UK) on %i-%02i-%02i is %s" % (sunset.year, sunset.month, sunset.day, day_length))
                
    message(1, "Finished!")
    return(errors)

#=====================================================================#
# Help text and utilities                                             #
#=====================================================================#

def usage(*args):
    sys.stdout = sys.stderr
    for msg in args: print(msg)
    print(__doc__)
    sys.exit(2)

#=====================================================================#
#                      Main program                                   #
#=====================================================================#
errors = 0
if __name__=="__main__":          # If this script is run as a program
    #=================================================================#
    # Call main()                                                     #
    #=================================================================#
    errors = main()

    sys.exit(errors)
