import sys

import idlsave
from datetime import date, timedelta

file_path = 'gev_nar.sav'
sav_file = idlsave.read(file_path)

gv = sav_file.gv     # Flares
nar = sav_file.nar   # ARs

times = [int(entry[0]) for entry in gv]
print('Maximum time since beginning of day (in hundredths):', max(times))

print('Last GEV record:')
print(gv[-1])

print('Last NAR record:')
print(nar[-1])

day_val = -1    # Number of days of particular gev entry since December 31, 1978

print('C2.2 class flare with AR #2672:')
for entry in gv:
    # Two digit numbers are ASCII values of chars (that's just the way they are stored in the sav file)
    if int(entry[4][0]) == 67 and int(entry[4][1]) == 50 and int(entry[4][3]) == 50 and int(entry[7]) == 2672:
        print(entry)
        day_val = int(entry[1])
        break

if day_val == -1:
    print('No entry found for the desired query...')
    sys.exit()

start_date = date(1978, 12, 31)
day_delta = timedelta(day_val)
offset = start_date + day_delta
print('Time of found gev record:', offset)