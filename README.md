sunrise_sunset
===============

Calculate sun rise and sun set times.

Sunrise/Sunset Algorithm

There are many implementations of this algorithm but most can be
traced back to the Almanac for Computers, 1990 published by 
Nautical Almanac Office, United States Naval Observatory, Washington, DC 20392
    
See also https://en.m.wikipedia.org/wiki/Sunrise_equation     

Inputs:
    day, month, year:      date of sunrise/sunset
    latitude, longitude:   location for sunrise/sunset
    zenith:                Sun's zenith for sunrise/sunset
        official     = 90 degrees 50 minutes
        civil        = 96 degrees
        nautical     = 102 degrees
        astronomical = 108 degrees

    NOTE: longitude is positive for East and negative for West
    
    The algorithm assumes the use of trig functions in "degree" mode, 
    rather than "radian" mode. 

1. First calculate the day of the year

    N1 = floor(275 * month / 9)
    N2 = floor((month + 9) / 12)
    N3 = (1 + floor((year - 4 * floor(year / 4) + 2) / 3))
    N = N1 - (N2 * N3) + day - 30

2. Convert the longitude to hour value and calculate an approximate time

    lngHour = longitude / 15

    if rising time is desired:
      t = N + ((6 - lngHour) / 24)
    if setting time is desired:
      t = N + ((18 - lngHour) / 24)

3. Calculate the Sun's mean anomaly

    M = (0.9856 * t) - 3.289

4. Calculate the Sun's true longitude

    L = M + (1.916 * sin(M)) + (0.020 * sin(2 * M)) + 282.634
    NOTE: L potentially needs to be adjusted into the range [0,360) by adding/subtracting 360

5. Right ascension

    1. Calculate the Sun's right ascension

        RA = atan(0.91764 * tan(L))
        NOTE: RA potentially needs to be adjusted into the range [0,360) by adding/subtracting 360

    2. Right ascension value needs to be in the same quadrant as L

        Lquadrant  = (floor( L/90)) * 90
        RAquadrant = (floor(RA/90)) * 90
        RA = RA + (Lquadrant - RAquadrant)

    3. Right ascension value needs to be converted into hours

        RA = RA / 15

6. Calculate the Sun's declination

    sinDec = 0.39782 * sin(L)
    cosDec = cos(asin(sinDec))

7. Local hour angle

    1. Calculate the Sun's local hour angle

	    cosH = (cos(zenith) - (sinDec * sin(latitude))) / (cosDec * cos(latitude))
	
	    if (cosH >  1) 
	      the sun never rises on this location (on the specified date)
	    if (cosH < -1)
	      the sun never sets on this location (on the specified date)

    2. Finish calculating H and convert into hours

	    if if rising time is desired:
	      H = 360 - acos(cosH)
	    if setting time is desired:
	      H = acos(cosH)
	
	    H = H / 15

8. Calculate local mean time of rising/setting

    T = H + RA - (0.06571 * t) - 6.622

9. Adjust back to UTC

    UT = T - lngHour
    NOTE: UT potentially needs to be adjusted into the range [0,24) by adding/subtracting 24

10. Convert UT value to local time zone of latitude/longitude

    localT = UT + localOffset
