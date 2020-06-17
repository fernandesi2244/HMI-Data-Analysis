from sunpy.net import jsoc, Fido, attrs as a
from sunpy.net.jsoc import *
import astropy.units as u
import time
import os

class DownloadStager(object):
    """
    Represents a month of a specific year that you want to stage download requests for.
    Scroll all the way to the bottom for usage.

    """

    MAX_ATTEMPTS = 10   # Max attempts of program before quitting and logging time range. If your requests typically fail while using the terminal, you may want to increase this value.
    MAX_FILES_FOR_HALVING = 2500    # Max number of files to have in a download request. If your computer consistently throws HTTP Errors while using the terminal, you may want to decrease this value.

    def __init__(self, year, month, days_in_month):
        """
        Initialize data for a specific month's download request.

        year: year of month you want data for
        month: numerical value of month; ordinal-based, not zero-based (DO NOT FILL IN 0s FOR SINGLE-DIGIT MONTHS)
        days_in_month: the number of days in the month for that that specific year

        """

        self.year = year
        self.month = month
        self.days_in_month = days_in_month

        self.client = jsoc.JSOCClient()
        self.series_name = 'hmi.sharp_cea_720s'
        self.notify_address = 'fernandesi2244@gmail.com'

        self.no_tries = 0
    
    def log_problem(self, start, end):
        """
        Logs any problematic time ranges to 'DownloadRequestData/problem_requests.txt'

        start: the start day
        end: the end day

        """

        time.sleep(5)
        with open(os.path.join('DownloadRequestData', 'problem_requests.txt'), "a") as problems_file:
            message = f"FAIL! Timespan: {self.month:02d}/{start:02d}/{self.year} to {self.month:02d}/{end:02d}/{self.year}\n"
            problems_file.write(message)
            print(message)
    
    def log_success(self, start, end, id):
        """
        Logs successful staging requests (with their IDs) to 'DownloadRequestData/request_numbers.txt'

        start: the start day
        end: the end day
        id: the id of the request

        """

        time.sleep(5)
        with open(os.path.join('DownloadRequestData', 'request_numbers.txt'), "a") as successes_file:
            message = f"SUCCESS! Timespan: {self.month:02d}/{start:02d}/{self.year} to {self.month:02d}/{end:02d}/{self.year}; ID: {id}\n"
            successes_file.write(message)
            print(message)

    def run(self):
        """
        Calls function to stage request.

        """

        self.no_tries = 0
        self.get_files(1, self.days_in_month)
    
    def get_files(self, start, end):
        """
        Recursively makes stage requests (on shorter timespans, as necessary) to the JSOCClient and attempts
        to address any server errors that may occur during program execution.

        start: the day to start from
        end: the day to end on

        """

        start_time = f"{self.year}-{self.month:02d}-{start:02d}T00:00:00"
        end_time   = f"{self.year}-{self.month:02d}-{end:02d}T23:00:00"

        print("Attempting to get request for:")
        print("\tStart Time:", start_time)
        print("\tEnd Time:  ", end_time)

        try:
            res = self.client.search(
                a.Time(start_time, end_time), 
                a.jsoc.Series(self.series_name),
                a.jsoc.Notify(self.notify_address),
                a.vso.Sample(3600*u.second),
                a.jsoc.Segment('bitmap'))
            
            file_num = len(res)
            if file_num > DownloadStager.MAX_FILES_FOR_HALVING:
                print(f'Halving (Number of files = {file_num})...')
                first_upper_bound = (start+end)//2
                self.no_tries = 0
                self.get_files(start, first_upper_bound)
                self.no_tries = 0
                self.get_files(first_upper_bound+1, end)
                return

            self.no_tries += 1
            print("search() function successful; attempting to request data...")

            time.sleep(5)

            requests = self.client.request_data(res)
            print("request_data() function successful")
        except Exception as e:
            print('Caught Exception:')
            print('\t'+repr(e))
            if self.no_tries > DownloadStager.MAX_ATTEMPTS:
                print('Max tries reached in try-except')
                self.log_problem(start, end)
                return
            print('Waiting 60 seconds to try again...')
            time.sleep(60)
            self.get_files(start, end)
            return
        
        print('Request ID:', requests.id)
        print('Request Status:', requests.status)

        if requests.status == 2:
            try:
                print('Running get_request()...')
                res = self.client.get_request(requests, path = 'HMI Downloaded Files')
            except Exception:
                pass
            if requests.status == 1:
                print('Status = 1; good to go!')
                time.sleep(1)
                self.log_success(start, end, requests.id)
            elif requests.status == 6:
                # Double-tapping method simply re-runs the get_request() command after a short period of time; this usually works
                print('Status = 6; trying double-tapping method')
                code6Max = 5
                currentTries = 0
                while(currentTries < code6Max):
                    currentTries +=1
                    time.sleep(10)
                    try:
                        print('Running get_request()...')
                        res = self.client.get_request(requests, path = 'HMI Downloaded Files')
                    except Exception:
                        pass
                    if requests.status == 1:
                        break
                if requests.status == 1:
                    print('Double-tapping method worked!')
                    time.sleep(1)
                    self.log_success(start, end, requests.id)
                else:
                    print("Double-tapping method didn't work!")
                    if self.no_tries > DownloadStager.MAX_ATTEMPTS:
                        self.log_problem(start, end)
                        return
                    print('Waiting 15 seconds to try again...')
                    time.sleep(15)
                    self.get_files(start, end)
            else:
                print('Request Status:', requests.status)
                print("Let's try again...")
                if self.no_tries > DownloadStager.MAX_ATTEMPTS:
                    self.log_problem(start, end)
                    return
                print('Waiting 20 seconds to try again...')
                time.sleep(20)
                self.get_files(start, end)
        elif requests.status == 4:
            print("Let's try again...")
            if self.no_tries > DownloadStager.MAX_ATTEMPTS:
                self.log_problem(start, end)
                return
            print('Waiting 30 seconds to try again...')
            time.sleep(30)
            self.get_files(start, end)
        elif requests.status == 6:
            # Double-tapping method simply re-runs the get_request() command after a short period of time; this usually works
            print('Status = 6; trying double-tapping method')
            code6Max = 5
            currentTries = 0
            while(currentTries < code6Max):
                currentTries +=1
                time.sleep(10)
                try:
                    print('Running get_request()...')
                    res = self.client.get_request(requests, path = 'HMI Downloaded Files')
                except Exception:
                    pass
                if requests.status == 1:
                    break
            if requests.status == 1:
                print('Double-tapping method worked!')
                time.sleep(1)
                self.log_success(start, end, requests.id)
            else:
                print("Double-tapping method didn't work!")
                if self.no_tries > DownloadStager.MAX_ATTEMPTS:
                    self.log_problem(start, end)
                    return
                print('Waiting 15 seconds to try again...')
                time.sleep(15)
                self.get_files(start, end)
        elif requests.status == 1:
            print('Status = 1; good to go!')
            time.sleep(1)
            self.log_success(start, end, requests.id)
        else:
            print("Let's try again...")
            if self.no_tries > DownloadStager.MAX_ATTEMPTS:
                self.log_problem(start, end)
                return
            print('Waiting 60 seconds to try again...')
            time.sleep(60)
            self.get_files(start, end)
    
    def run_range(self, start, end):
        """
        Stages download request for a specific range of dates.
        This function is commonly used when the program stalls on a particular month so that you can easily
        request the data yourself without visiting the terminal. See bottom of script for usage.

        start: the start day
        end: the end day

        """

        self.no_tries = 0
        print(f'Running with custom timeframe: {self.month:02d}/{start:02d}/{self.year} to {self.month:02d}/{end:02d}/{self.year}')
        self.get_files(start, end)
        self.no_tries = 0


'''
EXAMPLE USAGE:

Recall that you call the constructor with (year, month, days in month)

august_2013 = DownloadStager(2013, 8, 31)
august_2013.run()

september_2013 = DownloadStager(2013, 9, 30)
september_2013.run()

october_2013 = DownloadStager(2013, 10, 31)
october_2013.run()

november_2013 = DownloadStager(2013, 11, 30)
november_2013.run()

december_2013 = DownloadStager(2013, 12, 31)
december_2013.run()


IF THE PROGRAM GETS STUCK ON A MONTH AND YOU NEED TO MANUALLY RUN ON SPECIFIC RANGES AFTER STOPPING THE PROGRAM:

january_2015 = DownloadStager(2015, 1, 31)
january_2015.run_range(16, 23)
'''

# START ENTERING YOUR COMMANDS HERE: