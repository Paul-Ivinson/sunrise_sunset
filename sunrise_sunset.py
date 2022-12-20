#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  sunrise_sunset
#
#  Copyright 2022 Paul Ivinson <paivinson@gmail.com>
#
# V1 initial writing                                27Oct2022
# V1.1 Added tests                                  22Nov2022
# V1.2 Tidy up for sdist packaging                  07Dec2022   
# V1.2.1 Improve formating of minutes & seconds     20Dec2022 
#
#
"""sunrise_sunset Version 1.2.1
"""
"""
required arguments (unless --test):
  --latitude Latitude   Latitude of the location for sunrise and sunset.
                        Required unless --test     
  --longitude Longitude Longitude of the location for sunrise and sunset.
                        Required unless --test
  
optional arguments:
  -h, --help            show this help message and exit
  -q                    Quiet - absolutely no messages. Useful from the
                        command line. Make this the first option or you will
                        get messages as the other options are processed.
  -v, --verbose         Verbose - extra messages. Don't use -v and -q together
                        because the behaviour isn't defined.
  --test                Run a basic test and exit.
  --date Date           Date of sunrise & sunset in the format YYYYMMDD.
  --zenith Zenith       The zenith of the sun at sunrise and sunset.

  Latitude is a given as an angle that ranges from -90deg at the south pole to 90deg at the north pole, with 0deg at the Equator.
        
  Longitude is a given as an angle which is positive for East and negative for West.
  0deg longitude by convention is the International Reference Meridian for the Earth passing near the Royal Observatory in Greenwich, England

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
import math
import unittest

# Additional modules
# we could do the following 
# import dateutil.tz
# but it makes usage rather messy i.e.
# dateutil.tz.tz.tzutc()
from dateutil import tz

#---- our own modules ---------------------------------#
#- None at this time

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
# define unit tests                                             #
#===============================================================#

class testcases(unittest.TestCase):
    
    def setup(self):
        self.test_location = location(51.41416666, -1.515)

    def test_valid_date(self):
        self.date_given = valid_date("20221120")
        self.assertIsInstance(self.date_given, datetime.date)
            
    def test_bad_date(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            date_given = valid_date("2022-11-20")

    def test_good_latitude(self):
        good_latitude = valid_latitude("51.41416666")
        self.assertIsInstance(good_latitude, float)
        
    def test_bad_latitude(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            bad_latitude = valid_latitude("95.00")
            
    def test_latitude_equator(self):
        equator_latitude = valid_latitude("0.00")
        self.assertIsInstance(equator_latitude, float)
        self.assertEqual(equator_latitude, 0.00)
            
    def test_good_longitude(self):
        good_longitude = valid_longitude("-1.515")
        self.assertIsInstance(good_longitude, float)
        
    def test_bad_longitude(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            bad_longitude = valid_longitude("189.00")            
            
    def test_sunrise_today(self):
        "Test sunrise calcualtion for today"
        
        test_location = location(51.41416666, -1.515)
        #date_given = valid_date("20221122")
        date_today = datetime.date.today()
        sun_rise = test_location.sunrise(date_today, "official")
        self.assertIsInstance(sun_rise, datetime.date)
        
    def test_sunrise_22Nov2022(self):
        "Test sunrise calculation for 22 Nov 2022"
        test_location = location(51.41416666, -1.515)
        date_given = valid_date("20221122")
        sun_rise = test_location.sunrise(date_given, "official")        
        self.assertIsInstance(sun_rise, datetime.date)
        
        # print(sun_rise)
        
        # local_hour = 7, local_minute = 34, local_second = 44
        self.assertEqual(sun_rise.hour, 7)
        self.assertEqual(sun_rise.minute, 34)
        self.assertEqual(sun_rise.second, 44)
        
    def test_sunset_today(self):
        "Test sunset calcualtion for today"
        
        test_location = location(51.41416666, -1.515)
        #date_given = valid_date("20221122")
        date_today = datetime.date.today()
        sun_set = test_location.sunset(date_today, "official")
        self.assertIsInstance(sun_set, datetime.date)
        
    def test_sunset_22Nov2022(self):
        "Test sunset calculation for 22 Nov 2022"
        test_location = location(51.41416666, -1.515)
        date_given = valid_date("20221122")
        sun_set = test_location.sunset(date_given, "official")        
        self.assertIsInstance(sun_set, datetime.date)
        
        #print(sun_set)
        
        # local_hour = 16, local_minute = 8, local_second = 55
        self.assertEqual(sun_set.hour, 16)
        self.assertEqual(sun_set.minute, 8)
        self.assertEqual(sun_set.second, 55)        

def suite():

    # Add tests manually  
    #suite = unittest.TestSuite()
    #suite.addTest(testcases('test_valid_latitude'))
    
    # or use test discovery 
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testcases)
    return suite
    
#===============================================================#
# define Exceptions                                             #
#===============================================================#

# None so far

#===============================================================#
# define classes                                                #
#===============================================================#

class local_template:

    def __init__(self) -> None:
        self.verbose = 1
        self.start_time = time.time()
        self.typename  = type(self).__name__
        self.classname = str(__class__).split()[1].strip("'>")

    def message(self, verbosity, msg, classname = '',  method = ''):
        """ Local message handling method. """
        # Next line commented out for performance - reinstate if needed
        # this_function_name = sys._getframe(  ).f_code.co_name
        if classname == '':
            classname = self.classname
        #print "Verbosity = %s. self.verbose = %s" % (verbosity, self.verbose)
        if verbosity <= self.verbose:
            print("---- %4.4f %s.%s - %s" % ((time.time()-self.start_time), classname, method, msg))
        return

    def set_verbose(self, verbosity):
        "Set the amount of messages produced. Returns the setting in force at the time of the call."
        this_function_name = sys._getframe(  ).f_code.co_name
        old_verbosity = self.verbose
        self.verbose = verbosity
        classname = self.classname
        
        if old_verbosity != self.verbose:
          if verbosity > 0:
              # If we are being asked to be anything but quiet then print a message.
              own_msg = "set_verbose - Altering verbose from %s to %s" % (old_verbosity, self.verbose)
              print("---- %4.4f %s.%s - %s" % ((time.time()-self.start_time), classname, this_function_name, own_msg))
              
        return(old_verbosity)

    def push_verbose(self, verbosity):
        """Set verbose level but save the preceeding state to be re-instated later. Returns the setting in force at the time of the call."""
        this_function_name = sys._getframe(  ).f_code.co_name
        self.verbose_stack.append(self.verbose)
        return(self.set_verbose(verbosity))

    def pop_verbose(self):
        """Returns the verbose level to the preceeding state. Returns the setting in force at the time of the call."""
        this_function_name = sys._getframe(  ).f_code.co_name
        if len(self.verbose_stack) > 0: verbosity = self.verbose_stack.pop()
        else: verbosity = 0
        return(self.set_verbose(verbosity))

class location(local_template):
    "The location for which you wish to calculate the sunrise and sunset times."

    def __init__(self, latitude, longitude, verbose=1) -> None:
        super().__init__()
        # Got to be a better way to do this but I haven't found it yet.
        this_function_name = sys._getframe(  ).f_code.co_name
        # Override super().__init__ variables
        self.typename  = type(self).__name__
        self.classname = str(__class__).split()[1].strip("'>")
        self.set_verbose(verbose)
        
        self.message(1, "location class constructor", method = this_function_name)
        self.latitude = latitude
        self.longitude = longitude
        self.zenith = 'official',
        
        assert type(self.latitude) == float
        assert type(self.longitude) == float
        
        return  
        
    def ss_sin(self, angle_360):
        "Returns the sine of an angle. Angle given in degrees."
        
        ss_sine = math.sin((math.radians(angle_360)))
        
        return(ss_sine)
        
    def ss_cos(self, angle_360):
        "Returns the cosine of an angle. Angle given in degrees."
        
        # ss_cosine = math.cos((pi/180)*angle_360))
        ss_cosine = math.cos((math.radians(angle_360)))
        
        return(ss_cosine)
        
    def ss_tan(self, angle_360):
        "Returns the tangent of an angle. Angle given in degrees."
        
        # ss_tangent = math.tan((pi/180)*angle_360))
        ss_tangent = math.tan((math.radians(angle_360)))
        
        return(ss_tangent)
            
    def ss_asin(self, ss_sine):
        "Returns the angle represented by a sine. Return value in degrees."
        
        angle_360 = math.degrees(math.asin(ss_sine))
        
        return(angle_360)
        
    def ss_acos(self, ss_cosine):
        "Returns the angle represented by a cosine. Return value in degrees."
        
        angle_360 = math.degrees(math.acos(ss_cosine))
        
        return(angle_360)
        
    def ss_atan(self, ss_tangent):
        "Returns the angle represented by a tangent. Return value in degrees."
        
        angle_360 = math.degrees(math.atan(ss_tangent))
        
        return(angle_360)
        
    def ss_calc(self, date, zenith, rising):
        """ Calculate sunrise or sunset time for a given date.
            date: an instance of datetime.date
            zenith: string - see help for values
            rising: boolean - true for rising time, false for setting time
        """
        
        #==== Convert zenith ============================================#
        if zenith == "official":
            zenith_deg = 90.0 + (50.0/60.0)
        elif zenith == "civil":
            zenith_deg = 96.0
        elif zenith == "nautical":
            zenith_deg = 102.0
        elif zenith == "astronomical":    
            zenith_deg = 108.0
        else:
            zenith = "default (official)"
            zenith_deg = 90.00 + (50.0/60.0)    
            
        self.message(2, "Using zenith - %s = %.3f deg" % (zenith, zenith_deg), method='ss_calc')        
        
        # Set up a string for messages
        if rising:
            rising_setting = 'rising'
        else:
            rising_setting = 'setting'
            
        #================================================================#
        # 1. first calculate the day of the year
        # N1 = floor(275 * month / 9)
        # N2 = floor((month + 9) / 12)
        # N3 = (1 + floor((year - 4 * floor(year / 4) + 2) / 3))
        # N = N1 - (N2 * N3) + day - 30
        
        # The range of N is 1 to 365
        
        N1 = math.floor((275 * date.month) / 9)
        N2 = math.floor((date.month + 9) / 12)
        N3 = (1 + math.floor((date.year - 4 * math.floor(date.year / 4) + 2) / 3))
        N = N1 - (N2 * N3) + date.day - 30
        
        self.message(2, "Day of the year is %s" % N, method='ss_calc')
        
        # Alternative python way of calculating day of the year
        # print("Day of the year = %s" % date.timetuple().tm_yday)
        # N = date.timetuple().tm_yday
        
        #===============================================================#
        # 2. convert the longitude to hour value and calculate an approximate time
        # lngHour = longitude / 15
        #
        # if rising time is desired:
        #     t = N + ((6 - lngHour) / 24)
        # if setting time is desired:
        #     t = N + ((18 - lngHour) / 24)
        
        lngHour = self.longitude / 15
        
        # By definition the sun is overhead the Greenwich meridian at 12:00
        # So if we start a clock 12 hours earlier then, when viewed from the
        # point where the Greenwich meridian crosses the equator, you could
        # expect the sun to rise at 06:00 and set at 18:00 on the equinox.
        # If we were to measure days by using a star then each following day
        # the sunrise would get later by 1/365 of a day.
        
        # So t is expressed in fractions of days not a time in hours, mins. 
        # If we express the parameters as (N, longitude) then 
        # for (0,90) t = 0.75 and for (365, -180) t = 366.25 for sunset
        # Because -180 < longitude < 180 then t cannot go negative.
        
        if rising:
            t  = N + ((6 - lngHour) / 24)
        else:
            t = N + ((18 - lngHour) / 24)
        
        self.message(3, "Longitude expressed in hours = %s" % lngHour, method='ss_calc')
        self.message(3, "Approximate time (%s) = %s" % (rising_setting, t), method='ss_calc')
        
        #===============================================================#
        # 3. calculate the Sun's mean anomaly
        # M = (0.9856 * t) - 3.289
        # See https://en.m.wikipedia.org/wiki/Mean_anomaly
        # Mean anomaly does not measure an angle between any physical 
        # objects (except at pericenter or apocenter, or for a circular orbit). 
        # It is simply a convenient uniform measure of how far around its 
        # orbit a body has progressed since pericenter. 
        
        # For the Gregorian calendar, the average length of the calendar 
        # year (the mean year) across the complete leap cycle of 400 years
        # is 365.2425 days (97 out of 400 years are leap years). 
        # 365.2596358 days is the length of time in an anomalistic year: the time interval between two successive passages of the periapsis
        
        # Convert the time of the orbit to degrees
        # Don't know where the -3.289 comes from or for what in adjusts
        # It may be to compensate for the 9 days between the winter solstice
        # and the start of the year. 
        
        mean_anomaly  = ((360 / 365.2596358) * t) - 3.289
        
        self.message(3, "Sun's mean anomaly = %s" % (mean_anomaly), method='ss_calc')

        #===============================================================#    
        # 4. calculate the Sun's true longitude
        # L = M + (1.916 * sin(M)) + (0.020 * sin(2 * M)) + 282.634
        # NOTE: L potentially needs to be adjusted into the range 0-360 by adding/subtracting 360
        
        # This is how far round the earth is in its orbit.
        # This is where we compensate for the Equation of Time
        # See https://en.m.wikipedia.org/wiki/Equation_of_time
        
        # The equation of time is two sine waves superimposed. 
        # The first is caused by the eccentricity of the earths orbit. It's 
        # a sine wave with a one year period and an amplitude of 7.66 minutes
        # The second is caused by the Obliquity of the ecliptic, a name for
        # tilt of the earth's rotation axis relative to the plane of its 
        # orbit. This is a sine wave with a period of 1/2 a year and an
        # amplitude of 9.87 minutes
        # Both these waves start thier period at the Spring Equinox which 
        # corresponds to the sun's longitude of 282.634 deg
        
        # In one minute the sun moves through 360 deg / (24 hrs * 60 mins) = 0.25 deg
        # eccentricity_amplitude = 7.66 * 360.0  / (24.0 * 60.0 ) = 1.915
        # obliquity_amplitude = 9.87 * 360.0  / (24.0 * 60.0 ) = 2.4675
        
        eccentricity_amplitude = 1.916 # Rounding up
        obliquity_amplitude = 0.020   # Don't know why this is so small
        
        #print("eccentricity_amplitude = %s" % eccentricity_amplitude)
        #print("obliquity_amplitude = %s" % obliquity_amplitude)
        
        sun_true_longitude =  mean_anomaly + (eccentricity_amplitude * self.ss_sin(mean_anomaly)) + (obliquity_amplitude * self.ss_sin(2 * mean_anomaly)) + 282.634
        
        if sun_true_longitude > 360.0:
            sun_true_longitude = sun_true_longitude - 360.0
        elif sun_true_longitude < 0.0:
            sun_true_longitude = sun_true_longitude + 360.0
            
        self.message(3, "Sun's true longitude (%s) = %s" % (rising_setting, sun_true_longitude), method='ss_calc')
        
        #===============================================================#
        # 5a. calculate the Sun's right ascension
        # RA = atan(0.91764 * tan(L))
        # NOTE: RA potentially needs to be adjusted into the range [0,360) by adding/subtracting 360
        
        right_ascension = self.ss_atan(0.91764 * self.ss_tan(sun_true_longitude))
            
        if right_ascension > 360.0:
            right_ascension = right_ascension - 360.0
        elif right_ascension < 0.0:
            right_ascension = right_ascension + 360.0
            
        self.message(3, "Sun's right ascension before quadrant calculation (%s) = %s" % (rising_setting, right_ascension), method='ss_calc')
        
        #===============================================================#
        # 5b. right ascension value needs to be in the same quadrant as L
        # Lquadrant  = (floor( L/90)) * 90   # Value in [0, 90, 180, 270]
        # RAquadrant = (floor(RA/90)) * 90
        # RA = RA + (Lquadrant - RAquadrant)
        
        Lquadrant  = (math.floor( sun_true_longitude / 90.0)) * 90.0
        RAquadrant = (math.floor(right_ascension / 90.0)) * 90.0
        right_ascension = right_ascension + (Lquadrant - RAquadrant)
        
        self.message(3, "Sun's right ascension (%s) = %s" % (rising_setting, right_ascension), method='ss_calc')
        
        #===============================================================#
        # 5c. right ascension value needs to be converted into hours
        # RA = RA / 15
        
        right_ascension_hours = right_ascension / 15.0
        
        self.message(3, "Sun's right ascension in hours (%s) = %s" % (rising_setting, right_ascension_hours), method='ss_calc')
        
        #===============================================================#
        # 6. calculate the Sun's declination
        # sinDec = 0.39782 * sin(L)
        # cosDec = cos(asin(sinDec))

        sinDec = 0.39782 * self.ss_sin(sun_true_longitude)   
        cosDec = self.ss_cos(self.ss_asin(sinDec))
        
        self.message(3, "Sun's declination (%s) = %s, %s" % (rising_setting, sinDec, cosDec), method='ss_calc')
        
        #===============================================================#
        # 7a. calculate the Sun's local hour angle
        # cosH = (cos(zenith) - (sinDec * sin(latitude))) / (cosDec * cos(latitude))
        # if (cosH >  1) 
        #  the sun never rises on this location (on the specified date)
        # if (cosH < -1)
        #  the sun never sets on this location (on the specified date)
        
        # See https://en.m.wikipedia.org/wiki/Solar_zenith_angle
        # cos(solar_zenith_angle) = (sin(local_latitude) * sin(solar_declination)) + (cos(local_latitude) * cos(solar_declination) * cos(hour_angle))
        # Solve for hour_angle
        # Sunset and sunrise occur (approximately) when the zenith angle is 90°
        # and that is when cos(hour_angle) = -tan(local_latitude)*tan(solar_declination)
        
        cosH = (self.ss_cos(zenith_deg) - (sinDec * self.ss_sin(self.latitude))) / (cosDec * self.ss_cos(self.latitude))
        
        self.message(3, "Sun's local hour angle (%s) = %s" % (rising_setting, cosH), method='ss_calc')
        
        if cosH >  1.0:
            self.message(1, "The sun never rises on this location (on the specified date).", method='ss_calc')
        if cosH < -1.0:
            self.message(1, "The sun never sets on this location (on the specified date).", method='ss_calc')
            
        #===============================================================#
        # 7b. finish calculating H and convert into hours
        # if if rising time is desired:
        #     H = 360 - acos(cosH)
        # if setting time is desired:
        #     H = acos(cosH)
        #
        # H = H / 15
        
        if rising:
            hour_angle = 360 - self.ss_acos(cosH)
        else:
            hour_angle = self.ss_acos(cosH)
        
        #print(cosH)
        
        hour = hour_angle / 15.0
        
        self.message(3, "Sun %s time (hours) = %s" % (rising_setting, hour), method='ss_calc')
        
        #===============================================================#
        #8. calculate local mean time of rising/setting
        # T = H + RA - (0.06571 * t) - 6.622
        
        local_mean_time = hour + right_ascension_hours - (0.06571 * t) - 6.622
        
        self.message(3, "Local mean time (%s) = %s" % (rising_setting, local_mean_time), method='ss_calc')
        
        #===============================================================#
        #9. adjust back to UTC
        # UT = T - lngHour
        # NOTE: UT potentially needs to be adjusted into the range [0,24) by adding/subtracting 24
        
        UTC = local_mean_time - lngHour
        
        if UTC > 24.0:
            UTC = UTC - 24.0
        elif UTC < 0.0:
            UTC = UTC + 24.0
        
        if rising:
            self.message(3, "Rising time (UTC) = %s" % UTC, method='ss_calc')
        else:
            self.message(3, "Setting time (UTC) = %s" % UTC, method='ss_calc')

        #10. convert UT value to local time zone of latitude/longitude
        # localT = UT + localOffset
        
        local_hour = int(UTC) 
        local_minute_dec = UTC - local_hour
        local_minute = int(local_minute_dec * 60.0)
        local_second_dec = UTC - local_hour - (local_minute / 60.0)
        local_second = int(local_second_dec * 3600.0)
        
        self.message(2, "local_hour = %s, local_minute = %s, local_second = %s" % (local_hour, local_minute, local_second), method='ss_calc')
        
        year = date.year 
        month = date.month
        day = date.day
        
        return datetime.datetime(year, month, day, hour=local_hour, minute=local_minute, second=local_second, tzinfo=tz.tzutc())

    def sunrise(self, date, zenith):
        """ Calculate sunrise for a given date.
            date: an instance of datetime.date
            zenith: string - see help for values
        """
        
        this_function_name = sys._getframe(  ).f_code.co_name
        self.message(1, "sunrise method called", method = this_function_name)
        
        sunrise_time = self.ss_calc(date, zenith, True)
        
        self.message(1, "Sunrise is %i:%02i:%02i" % (sunrise_time.hour, sunrise_time.minute, sunrise_time.second), method = this_function_name)
        
        return sunrise_time
        
    def sunset(self, date, zenith):
        """ Calculate sunset time for a given date.
            date: an instance of datetime.date
            zenith: string - see help for values
        """
                
        this_function_name = sys._getframe(  ).f_code.co_name
        self.message(1, "sunset method called", method = this_function_name)                
        
        sunset_time = self.ss_calc(date, zenith, False)
        
        self.message(1, "Sunset is %i:%02i:%02i" % (sunset_time.hour, sunset_time.minute, sunset_time.second), method = this_function_name)
        
        return sunset_time
        
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
    
def valid_latitude(latitude):
    "Latitude is given as an angle that ranges from -90° at the south pole to 90deg at the north pole, with 0° at the Equator. Note: returns a float."
    
    if not is_number(latitude):
        msg = 'valid_latitude - Error validating latitude. Latitude must be a number.'
        raise argparse.ArgumentTypeError(msg)
        
    latitude_float = float(latitude)
    
    if not (latitude_float <= 90.0 and latitude_float >=-90.0) :
        msg = 'valid_latitude - Error validating latitude. Latitude is a given as an angle that ranges from -90deg at the south pole to 90deg at the north pole, with 0deg at the Equator.'
        raise argparse.ArgumentTypeError(msg)
        
    return(latitude_float)    
    
def valid_longitude(longitude):
    "Longitude is given as an angle which is positive for East and negative for West. Note: returns a float."
    
    if not is_number(longitude):
        msg = 'valid_longitude - Error validating longitude. longitude must be a number.'
        raise argparse.ArgumentTypeError(msg)
    
    longitude_float = float(longitude)
    
    if not (longitude_float <= 180.0 and longitude_float >= -180.0):
        msg = 'valid_longitude - Error validating longitude. longitude is a given as an angle which is positive for East and negative for West.'
        raise argparse.ArgumentTypeError(msg)
        
    return(longitude_float)        

def print_there(x, y, text):
    "function to overprint previous output on terminal device"
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()

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

    opt_test = False

    #==================================================================#
    # Parse arguments                                                  #
    #==================================================================#
    parser = argparse.ArgumentParser(
        description=__doc__,
        # Take control of the formatting of the epilog
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Latitude is a given as an angle that ranges from -90deg at the south pole to 90deg at the north pole, with 0deg at the Equator.
        
        Longitude is a given as an angle which is positive for East and negative for West.
        0deg longitude by convention is the International Reference Meridian for the Earth passing near the Royal Observatory in Greenwich, England

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
    
    # Required args - unless --test 
    parser.add_argument('--latitude',  dest='Latitude',  metavar='Latitude',  type=valid_latitude,  help='Latitude of the location for sunrise and sunset. Required unless --test')
    parser.add_argument('--longitude', dest='Longitude', metavar='Longitude', type=valid_longitude, help='Longitude of the location for sunrise and sunset. Required unless --test')

    # Optional args
    parser.add_argument('-v', '--verbose', dest='verbose',  action='count',                default=1, help="Verbose - extra messages. Don't use -v and -q together because the behaviour isn't defined.")
    parser.add_argument('--test',          dest='opt_test', action='store_true',                      help="Run a basic test and exit.")
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
        if o == 'opt_test': opt_test = a
        # Options specific to this script
        if o == 'Date': date_given = a
        if o == 'Latitude': latitude = a
        if o == 'Longitude': longitude = a
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

    #=== TEST ======================================================#
    if opt_test:
        if verbose == 0:
          verbose = 1
        message(1, "running tests")
        runner = unittest.TextTestRunner()
        runner.run(suite())

    else:
        if not date_given:
            # message(0, "Date is required")
            # return(4)
            date_given = datetime.date.today()
        elif not latitude: 
            message(0, "Latitude is required")
            return(4)
        elif not longitude:
            message(0, "Longitude is required")
            return(4)
        
        new_place = location(latitude, longitude, verbose)
        sun_rise = new_place.sunrise(date_given, zenith)
        sun_set = new_place.sunset(date_given, zenith)
        
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
