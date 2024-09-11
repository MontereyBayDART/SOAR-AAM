Weather data was taken from the NOAA Integrated Surface Dataset for each of the airports in the initial
study with an ASOS/AWOS station:
https://www.ncei.noaa.gov/data/global-hourly/

For ISD documentation, refer to
https://www.itl.nist.gov/div898/winds/NIST_TN/doc/ish-format-document.pdf.

Data used:
Station Name
Time
Report Type
WND points 4 (wind speed, m/s, scaling factor 10), 5 (quality code,1 and 5 acceptable);
CIG points 1 (cloud ceiling height, m), 2 (quality code);
VIS points 1 (horizontal visibility, m), 2 (quality code)

Test conditions:
3 statute mile visibility horizontally, 1,000 foot cloud height.
3kn cross wind for hover testing, 10kn cross wind for flight testing

Civil twilight times were determined from https://aa.usno.navy.mil/data/RS_OneYear and manually
imported into Excel, from which a .csv was exported. Civil twilight was used as is standard in
aviation for determining daytime flight rules. Daylight savings time was not accounted for in the
civil twilight dataset used. This inaccuracy was not deemed significant enough to greatly affect
the analysis. However, for a more detailed analysis, this should be accounted for.
