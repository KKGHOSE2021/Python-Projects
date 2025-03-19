""" purpose: basic optimizing of vehicle charge """

import numpy as np
import datetime as dt
#import pytz
import pulp
#from pulp.constants import LpStatusNotSolved, LpStatusOptimal, LpStatusInfeasible, LpStatusUnbounded, LpStatusUndefined
from pulp.constants import LpStatusOptimal
from pulp import LpProblem, LpVariable, LpMinimize, lpSum
import time
import os

#import pywintypes
import win32com.client
from win32com.client import constants
from win32com.server.exception import COMException
import winerror

import win32ui  # for the message boxes
import win32con # for the message boxes

__version__ = '0.1'

#----------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------

class ChargeOptimizer(object):
    """ main optimizer """

    def __init__(self, battery, priceseries, connection_pattern):
        """ assumptions: priceseries.dates include enddate
             consumptions in connection_pattern in soc% (full charge=1.0),
             idem for battery attributes
        """
        self.battery = battery
        self.priceseries = priceseries
        self.connection_pattern = connection_pattern
        self.solver = pulp.solvers.COINMP_DLL() # or None
        self.publisher = None # result publisher, , assumed to have a 'publish_results' method

    def run(self, window = 24):
        """ optimizes charge/discharge with a rolling window over the priceseries, launching a lpsolve on each window
            optimization window is extended when needed for consistent optimization
        """
        runtime_start = time.clock()
        price_dates = self.priceseries.dates
        prices = self.priceseries.prices
        nbperiods = len(price_dates) - 1
        if self.publisher is not None:
            self.publisher.publish_results([('Date', 'Price (EUR/MWh)', 'Soc(kWh)', 'Vol.(kWh)', 'Inj.(kWh)', 'Cost(EUR)',
                                             'Soc w/o optim', 'Vol. w/o optim', 'Cost w/o optim')])
        connections = Connections(self.connection_pattern, price_dates[0], price_dates[-1])
        connection_dates = connections.dates
        consumptions = connections.consumptions
        nbconnections_dates = len(connection_dates)
        shift = connections.shift
        max_charge_speed = self.battery.max_charge_speed
        max_discharge_speed = self.battery.max_discharge_speed
        solve_lp = self.solve_lp
        soc = self.battery.start_soc
        soc_no_optim = self.battery.start_soc
        total_cost = 0.0
        total_cost_no_optim = 0.0
        t = 0  # index in self.dates
        s = connections.startdate_period + 1 # index in connections.dates
        # connection_dates[s] is the smallest connection_date that is >= prices_dates[t]
        while t + window - 1 < nbperiods:
            tend = t + window - 1
            # optimize over [t, tend]  (hour tend included)
            # create variables :
            # list of tuples (start_date, duration(min), consumption(%soc), price, volume_in, volume_out)
            variables = []
            s1 = s
            s01 = s
            t1 = t
            if connection_dates[s1] < price_dates[t1]:
                break
            # again, connection_dates[s1] is the smallest connection_date that is >= prices_dates[t1]
            extend = False
            last_window_variable = -1 # index of last variable that lies within [t, tend+1[
            while t1 <= tend or extend:
                s2 = s1
                while connection_dates[s2] < price_dates[t1 + 1] and s2 < nbconnections_dates - 1:
                    s2 += 1
                # stop when last connection date is reached (happens only on the last week of optimization)
                # (after this s2, we are either not connected up to last price_date and there is nothing to optimize
                #  or we are always connected up to at least last price_date and optimization cannot be consistent)
                if connection_dates[s2] < price_dates[t1 + 1]:
                    s01 = s1 = s2
                    break
                # process each subinterval (when not empty) [t1, s1],[s1,s1+1],[s1+1,s1+2],...[s2-1,t1+1]
                # (when t1 <= s1 < t1+1 <= s2) (or just [t1,t1+1] when t1+1 < s2=s1)
                for k in range(s1, s2 + 1):
                    dstart = connection_dates[k - 1] if k > s1 else price_dates[t1]
                    dend = connection_dates[k] if k < s2 else price_dates[t1 + 1]
                    # isconnected indicates whether we're connected on period [dstart,dend]
                    isconnected = (k % 2) != shift
                    if dend > dstart and isconnected:
                        duration = dend - dstart
                        duration = round(duration.total_seconds() / 60) # resolution for duration : minute
                        #todo exact duration with DST + treat cases of non-existent or ambiguous connection_dates
                        ##assuming hourly granularity for price_dates, exact duration (accouting for DST)
                        ##can be computed the following way:...
                        varindex = len(variables)
                        vin = LpVariable("vin" + str(varindex), lowBound = 0.0, upBound = max_charge_speed * duration)
                        vout = 0.0
                        if max_discharge_speed > 0.0:
                            vout = LpVariable("vout" + str(varindex), lowBound = 0.0,
                                                upBound = max_discharge_speed * duration)
                        variables.append((dstart, duration, consumptions[k] if dend == connection_dates[k] else 0.0,
                                            prices[t1], vin, vout))
                    if extend and not isconnected:
                        break
                s1 = s2
                if t1 <= tend:
                    s01 = s2
                    last_window_variable = len(variables) - 1
                # if a connection crosses default optimization horizon, extend it up to end of the connection
                #  (for constraint consistency)
                if t1 >= tend and t1 < nbperiods - 1 and isconnected and connection_dates[s2] > price_dates[t1 + 1]:
                    extend = True
                else:
                    extend = False
                t1 += 1
            soc, soc_no_optim, cost, cost_no_optim = solve_lp(variables, soc, soc_no_optim, last_window_variable)
            total_cost += cost
            total_cost_no_optim += cost_no_optim
            if soc < 0:
                print 'break on negative soc %f , window: %s-%s' % (soc, str(price_dates[t]), str(price_dates[t+window]))
                break
            s = s01
            #print 'done window: %s-%s' % (str(price_dates[t]),str(price_dates[t+window]))
            t += window
        runtime_end = time.clock()
        runtime = runtime_end-runtime_start
        print "done: window %dh in %.03f sec." % (window, runtime_end-runtime_start)
        return runtime, total_cost, total_cost_no_optim

    def solve_lp(self, variables, start_soc, start_soc_no_optim, last_window_variable):
        """ setup and solve pulp lp problem """
        if len(variables) > 0:
            prob = LpProblem("charge optimization", LpMinimize)
            # a variable is (0:lpvar, 1:start_date, 2:duration, 3:consumption, 4:price)
            # a variable is (0:start_date, 1:duration, 2:consumption, 3:price, 4:vin, 5, vout)
            # set objective (no discount rate for now)
            midbid = self.priceseries.midbid_spread
            askmid = self.priceseries.askmid_spread
            prob += lpSum([ variable[4]*(variable[3]+askmid) - variable[5]*(variable[3]-midbid)
                            for variable in variables]), "charge costs"
            # set constraints
            soc = start_soc # each soc variable i represent soc on first instant of period covered by vin_i
            max_charge_speed = self.battery.max_charge_speed
            min_soc = self.battery.min_soc
            capacity = self.battery.capacity
            for variable in variables:
                start_date, duration, consumption, price, vin, vout = variable
                soc += vin - vout - consumption
                prob += min_soc + 1e-5 <= soc, ""
                prob += soc <= 1.0, ""
            # solve and publish results
            prob.solve(self.solver)
            if prob.status == LpStatusOptimal:
                results = []
                soc = start_soc
                soc_no_optim = start_soc_no_optim
                total_cost = 0.0
                total_cost_no_optim = 0.0
                resappend = results.append
                timedelta = dt.timedelta
                for i in range(last_window_variable+1):
                    start_date, duration, consumption, price, vin, vout = variables[i]
                    vin = pulp.value(vin)
                    vout = pulp.value(vout)
                    # note cap. is in kWh while prices are in EUR/MWh
                    cost = (vin * (price+askmid) - vout * (price-midbid)) * capacity / 1000
                    new_soc_no_optim = min(1.0, soc_no_optim + max_charge_speed * duration)
                    vin_no_optim = new_soc_no_optim - soc_no_optim
                    cost_no_optim = vin_no_optim * capacity * price / 1000
                    vol = vin - vout
                    volplus = vol if vol > 0.0 else 0.0
                    resappend((start_date, price, soc*capacity, vol*capacity, volplus*capacity, cost,
                                soc_no_optim*capacity, vin_no_optim*capacity, cost_no_optim))
                    soc += (vin-vout)
                    soc_no_optim += vin_no_optim
                    if consumption != 0.0:
                        resappend((start_date+timedelta(hours=duration/60), 'NA', soc*capacity, -consumption*capacity, 0.0, 0.0,
                                soc_no_optim*capacity, -consumption*capacity, 0.0))
                        soc -= consumption
                        soc_no_optim -= consumption
                    total_cost += cost
                    total_cost_no_optim += cost_no_optim
            else:
                results = [(pulp.LpStatus[prob.status],)]
                soc = -1
                soc_no_optim = -1
                total_cost = 0.0
                total_cost_no_optim = 0.0
            if self.publisher is not None:
                self.publisher.publish_results(results)
        else:
            soc = start_soc
            soc_no_optim = start_soc_no_optim
            total_cost = 0.0
            total_cost_no_optim = 0.0
        return soc, soc_no_optim, total_cost, total_cost_no_optim

class PriceSeries(object):
    """ dates in local time, assumed to contain end date (ie len(dates) = len(prices) + 1)
        price taker point of view, ie we buy at price+askmid_spread,
        we sell at price-midbid_spread
        all prices and spreads assumed in EUR/Mwh
    """
    def __init__(self, dates = None, prices = None):
        self.dates = dates
        self.prices = prices
        self.midbid_spread = 0.0 # in EUR/MWh
        self.askmid_spread = 0.0 # in EUR/MWh

    def read_com_values(self, dates, prices):
        """ dates and prices arguments are assumed to be tuples of tuples  """
        #TODO process #N/A, #ERROR, #VALUE into nans...
        self.prices = np.array(prices).reshape(-1)

        npdates = np.zeros((len(dates)+1,), dtype=object)
        datetime = dt.datetime
        i = 0
        for date, in dates:
            npdates[i] = datetime(date.year, date.month, date.day, date.hour) # hourly resolution here
            i += 1
        # add last date point
        npdates[-1] = npdates[-2] + dt.timedelta(hours=1) # this "assumes" hourly granularity for dates
        self.dates = npdates


class Battery(object):
    """ capacity in kWh, other energy attributes converted to capacity% aka soc%
        energy speed attributes in soc%/min
        default is a battery that charges in 6 hours
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.max_charge_speed = 1.0 / (6.0*60)   # in soc%/min
        self.max_discharge_speed = 0.0
        self.min_soc = 0.0
        self.start_soc = 1.0

    def set_max_charge_speed(self, max_charge_speed):
        """ set max charge speed with scaling """
        self.max_charge_speed = max_charge_speed / self.capacity # charge speed in soc%/min

    def set_max_discharge_speed(self, max_discharge_speed):
        """ set max discharge speed with scaling """
        self.max_discharge_speed = max_discharge_speed / self.capacity # charge speed in soc%/min

    def set_min_soc(self, min_soc):
        """ set min soc with scaling """
        self.min_soc = min_soc / self.capacity # min_soc in soc%

    def set_start_soc(self, start_soc):
        """ set start soc with scaling """
        self.start_soc = start_soc / self.capacity # start soc in soc%


class ConnectionTemplate(object):
    """ convention for days of week : 0:Mon, 1:Tue, 2:Wed, 3:Thu, 4:Fri, 5:Sat, 6:Sun
        start and end time in decimal hours counted from 00:00 midnight, both are < 24.0
         they represent a local time rather than a time span from 00:00 (eg 8.0 means 8:00am even when this crosses a DST boundary)
        wihtout a nbweeks, a connection cannot last more than 1 week, eg Mon 00:00 to Tue 00:00 is always
         interpreted as a 24h connection, not a 1week + 24h connection
        a list of non-overlapping ConnectionTemplate represents a weekly connection pattern
        a template is allowed to crosses the end of week (Sun 23:59:59), eg representing a connection from Sun 19:00 to Mon 8:00
         if a weekly pattern is sorted by startday+starttime, such a template is necessarily the last item in the list
        consumption is the energy consumption following this connection, expressed in soc%
         0.0 if it is not a trip/drive
    """
    def __init__(self, startday, starttime, endday, endtime, consumption = 0.0):
        if isinstance(startday, basestring):
            startday = self.daysOfWeek.index(startday) # TODO capture exception if not found for clearer user error message
        if isinstance(endday, basestring):
            endday = self.daysOfWeek.index(endday)
        self.startday = startday
        self.starttime = starttime
        self.endday = endday
        self.endtime = endtime
        self.consumption = consumption

    daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    @staticmethod
    def timetostring(atime):
        """ printed with minute resolution """
        return '%02d:%02d' % (int(atime), round((atime - int(atime))*60))

    def __repr__(self):
        return ''.join([self.daysOfWeek[self.startday], ' ', self.timetostring(self.starttime), '-',
                        self.daysOfWeek[self.endday], ' ', self.timetostring(self.endtime)])



class Connections(object):
    """ array of specific connections, localized in time, constructed from an iterable of ConnectionTemplate
        templates assumed sorted by startday+starttime, non-overlapping
    """
    def __init__(self, templates, startdate, enddate):
        startdate0 = startdate
        startdate = dt.datetime(startdate.year, startdate.month, startdate.day) # strip time info from startdate
        enddate = dt.datetime(enddate.year, enddate.month, enddate.day)
        oneday = dt.timedelta(days=1)
        oneweek = dt.timedelta(days=7)
        while startdate.weekday() != 0: # set startdate to begining of week
            startdate = startdate - oneday
        while enddate.weekday() != 0: # set enddate to end of week
            enddate = enddate + oneday
        nbweeks = (enddate - startdate).days / 7
        nbtemplates = len(templates)
        connections = np.zeros((nbweeks * nbtemplates * 2,), dtype=object)
        consumptions = np.zeros((len(connections),))
        timedelta = dt.timedelta
        last_template = templates[-1]
        shift = 0
        if last_template.endday < last_template.startday: # treat case where a template crosses end of week
            shift = 1
        for i, template in enumerate(templates):
            start_index = shift + 2*i
            end_index = shift + 2*i + 1 if (i < nbtemplates - 1) or shift == 0 else 0
            # note the following can produce non-existent or ambiguous connection dates (always local)
            connections[start_index] = startdate + timedelta(days=template.startday, hours=template.starttime)
            connections[end_index] = startdate + timedelta(days=template.endday, hours=template.endtime)
            consumptions[end_index] = template.consumption
        for i in range(2*nbtemplates, len(connections)):
            connections[i] = connections[i-2*nbtemplates] + oneweek
            consumptions[i] = consumptions[i-2*nbtemplates]
        self.dates = connections
        self.consumptions = consumptions
        self.shift = shift
        # when shift = 0 (resp. = 1), 2 consecutives dates in 'connections' represent a connection period
        #  iif index of first date is even (resp. odd)
        startdate_period = -1
        if len(connections) == 0 or startdate0 >= connections[-1]:
            raise COMException("No connection found over the period", winerror.E_INVALIDARG)
        while startdate0 > connections[startdate_period + 1]:
            startdate_period += 1
        self.startdate_period = startdate_period
        #  connections[startdate_period] < startdate0 <= connections[startdate_period + 1]

#----------------------------------------------------------------------------------------
# COM
#----------------------------------------------------------------------------------------
class Optimizer(object):
    """ COM interface callable from VBA """
    _public_methods_ = [ 'SetWorkbook', 'Run', 'LoadMobilityProfile' ]
    _reg_progid_ = 'VehicleChargeOptimizer.Optimizer'
    _reg_clsid_ = '{E4ECC522-84D6-4E84-8B18-9843B9159460}'  # generated via pythoncom.CreateGuid()

    def __init__(self):
        self.workbook = None
        self.shmain = None
        self.shresults = None
        self.xlapp = None

        self.priceseries = None
        self.battery = None
        self.profile = None # connection profile

        self.window = None

        self.current_result_range = None

    def cleanup(self):
        self.current_result_range = None
        self.shmain = None
        self.shresults = None
        self.workbook = None
        self.xlapp = None

    def open_workbook(self, wkpath, wkname):
        """ smart open of a workbook: if already open in self.xlapp, returns this instance """
        workbook = None
        for workbook1 in self.xlapp.Workbooks:
            if workbook1.Name == wkname:
                workbook = workbook1
                break
        else:
            # create workbook
            activeWorkbook = self.xlapp.ActiveWorkbook
            workbook = self.xlapp.Workbooks.Open(os.path.join(wkpath, wkname))
            if activeWorkbook is not None:
                activeWorkbook.Activate()
        return workbook

    def SetWorkbook(self, workbook):
        """ to be used from vba, note in vba you need to declare a local workbook
              Dim book As Workbook
              Set book = ThisWorkbook
              Call optimizer.SetWorkbook(book)
            Call optimizer.SetWorkbook(ThisWorkbook) will have excel crash on close
        """
        self.workbook = win32com.client.Dispatch(workbook)
        self.shmain = self.workbook.Sheets("Main")
        self.shresults = self.workbook.Sheets("Results")
        self.xlapp = self.workbook.Application

    def UseWorkbook(self, wkpath, wkname):
        """ for testing as standalone
            optimizer.UseWorkbook 
        """
        self.xlapp = win32com.client.gencache.EnsureDispatch('Excel.Application', 0)
        self.xlapp.Visible = True
        workbook = self.open_workbook(wkpath, wkname)
        self.workbook = workbook
        self.shmain = workbook.Sheets("Main")
        self.shresults = workbook.Sheets("Results")

    def convert_mobility_profile(self, profile, locations_dict):
        """ convert mobility profile to connection profile """
        t2t_trips = [] # terminal to terminal trips, a trip is (0:startday, 1:starttime, 2:endday, 3:endtime, 4:kwh)
        trip_ongoing = False
        for day in range(7):
            for hour in range(24):
                trip = profile[hour][6*day:6*(day+1)]
                tripname, loc, start, arrival, km, kwh = trip
                if tripname is not None and tripname != "":
                    destination_has_terminal = locations_dict[loc]
                    if destination_has_terminal:
                        # close ongoing trip if any, else create complete one
                        if trip_ongoing == True:
                            ongoing_trip = t2t_trips[-1]
                            t2t_trips[-1] = (ongoing_trip[0], ongoing_trip[1],
                                             ConnectionTemplate.daysOfWeek[day], arrival,
                                             ongoing_trip[4] + kwh)
                            trip_ongoing = False
                        else:
                            complete_trip = (ConnectionTemplate.daysOfWeek[day], start,
                                             ConnectionTemplate.daysOfWeek[day], arrival,
                                             kwh)
                            t2t_trips.append(complete_trip)
                    else:
                        # add to ongoing trip if any, else open an ongoing trip
                        if trip_ongoing == True:
                            ongoing_trip = t2t_trips[-1]
                            t2t_trips[-1] = (ongoing_trip[0], ongoing_trip[1],
                                             None, None,
                                             ongoing_trip[4] + kwh)
                        else:
                            ongoing_trip = (ConnectionTemplate.daysOfWeek[day], start,
                                            None, None,
                                            kwh)
                            t2t_trips.append(ongoing_trip)
                            trip_ongoing = True
        if trip_ongoing:
            # close ongoing trip with first trip
            if len(t2t_trips) < 2:
                Optimizer.messagebox("Neverending trip (no connection)")
                return
            ongoing_trip = t2t_trips.pop()
            first_trip = t2t_trips[0]
            t2t_trips[0] = (ongoing_trip[0], ongoing_trip[1],
                             first_trip[2], first_trip[3],
                             ongoing_trip[4] + first_trip[4])

        connections = []
        # fill connections with (conn_startday, conn_starttime,
        #                        conn_endday, conn_endtime, consumption_following_the_connection)
        for i in range(len(t2t_trips)):
            nti = i+1 if i+1 < len(t2t_trips) else 0 # next trip index
            connection = (t2t_trips[i][2], t2t_trips[i][3], t2t_trips[nti][0], t2t_trips[nti][1], t2t_trips[nti][4])
            connections.append(connection)

        return connections

    def LoadMobilityProfile(self):
        """ COM exposed, called on 'Load Profile' button : loads mobility profile, converts it into a connection profile """
        workbook_fullname = self.shmain.Range("mobilityProfileBook").Value
        worksheet_name = self.shmain.Range("mobilityProfileSheet").Value
        workbook_fullname_split = os.path.split(workbook_fullname)
        workbook = self.open_workbook(workbook_fullname_split[0], workbook_fullname_split[1])
        worksheet = workbook.Sheets(worksheet_name)
        profile = self.read_contiguous_range(worksheet.Range("B34"), 24, 6*7)
        locations = self.read_contiguous_range(worksheet.Range("C17"), -1, 3)

        locations_dict = {}
        for location in locations:
            # location expected to be (charging station yes/no, None, location code)
            has_terminal = location[0] == "Yes"
            locations_dict[location[2]] = has_terminal

        connections = self.convert_mobility_profile(profile, locations_dict)

        # fill excel range
        connection_range = self.shmain.Range("connections")
        connection_range = Optimizer.offset(connection_range, 2, 0) # skip row headers
        connection_range1 = self.get_contiguous_range(connection_range)
        connection_range1.ClearContents()
        nbrows = len(connections)
        nbcols = len(connections[0])
        bottom_right_cell = Optimizer.offset(connection_range, nbrows-1, nbcols-1)
        rang = self.shmain.Range(connection_range, bottom_right_cell)
        rang.Value = connections

    def Run(self):
        """ main method, called on click button 'Run' """
        self.clear_results()
        self.read_battery()
        self.read_settings()
        self.read_prices()
        self.read_profile()
        charge_optimizer = ChargeOptimizer(self.battery, self.priceseries, self.profile)

        self.current_result_range = self.shresults.Range("results")
        charge_optimizer.publisher = self
        runtime, total_cost, total_cost_no_optim = charge_optimizer.run(self.window)

        shmain = self.shmain
        shmain.Range("runtime").Value = self.time2string(runtime)
        shmain.Range("cost").Value = total_cost
        shmain.Range("costNoOptim").Value = total_cost_no_optim

        #self.cleanup()

    @staticmethod
    def time2string(seconds):
        """ converts decimal seconds into a readable string .d .h .m .s .ms """
        strings = []
        days, remaining_seconds = divmod(seconds, 60 * 60 * 24)
        if days >= 1.0:
            strings.append("%dd" % int(days))
        hours, remaining_seconds = divmod(remaining_seconds, 60 * 60)
        if hours >= 1.0:
            strings.append("%dh" % int(hours))
        minutes, remaining_seconds = divmod(remaining_seconds, 60)
        if minutes >= 1.0:
            strings.append("%dm" % int(minutes))
        seconds = int(remaining_seconds)
        if seconds >= 1.0:
            strings.append("%ds" % int(seconds))
        time_string = None
        if len(strings) == 0:
            time_string = "< 1s"
        else:
            time_string = ' '.join(strings)
        return time_string

    def clear_results(self):
        """ clear existing results in excel """
        result_range = self.shresults.Range("results")
        result_range = self.get_contiguous_range(result_range)
        result_range.ClearContents()

        shmain = self.shmain
        shmain.Range("runtime").ClearContents()
        shmain.Range("cost").ClearContents()
        shmain.Range("costNoOptim").ClearContents()

    def publish_results(self, tuplelist):
        """ List (or tuple) of tuples to be copied to xl at self.current_result_range,
             each tuple copied to a row, ALL tuples assumed to have the same length
            Datetime can be copied as such, no need for conversion to PyTime
            self.current_range is then moved below the copied block
        """
        nbrows = len(tuplelist)
        nbcols = len(tuplelist[0])
         # Resize does not work with pywin32 !!
        bottom_right_cell = Optimizer.offset(self.current_result_range, nbrows-1, nbcols-1)
        rang = self.current_result_range.Worksheet.Range(self.current_result_range, bottom_right_cell)
        rang.Value = tuplelist
        self.current_result_range = Optimizer.offset(self.current_result_range, nbrows, 0)

    def read_settings(self):
        """ read optimization settings from excel """
        self.window = int(self.shmain.Range("window").Value)

    def read_battery(self):
        """ read battery info from excel """
        capacity = self.shmain.Range("capacity").Value # in kWh
        max_charge_speed = self.shmain.Range("speed").Value # in kWh/min
        max_discharge_speed = self.shmain.Range("dischargeSpeed").Value # in kWh/min
        min_soc = self.shmain.Range("minCharge").Value # in kWh
        start_soc = self.shmain.Range("startSoc").Value # in kWh

        self.battery = Battery(capacity)
        self.battery.set_max_charge_speed(max_charge_speed)
        self.battery.set_max_discharge_speed(max_discharge_speed)
        self.battery.set_min_soc(min_soc)
        self.battery.set_start_soc(start_soc)

    def read_prices(self):
        """ read price series from excel """
        pricerange = self.shmain.Range("prices")
        pricerange = Optimizer.offset(pricerange, 2, 0) # skip row headers
        dates = self.read_contiguous_range(pricerange, -1, 1)
        prices = self.read_contiguous_range(Optimizer.offset(pricerange, 0, 1), -1, 1)

        self.priceseries = PriceSeries()
        self.priceseries.read_com_values(dates, prices)

        midbid_spread = self.shmain.Range("midbid").Value
        askmid_spread = self.shmain.Range("askmid").Value
        self.priceseries.midbid_spread = midbid_spread
        self.priceseries.askmid_spread = askmid_spread

    def read_profile(self):
        """ read connection profile from excel """
        connection_range = self.shmain.Range("connections")
        connection_range = Optimizer.offset(connection_range, 2, 0) # skip row headers
        values = self.read_contiguous_range(connection_range, -1, 5)
        profile = []
        for row_values in values:
            startday, starttime, endday, endtime, consumption = row_values
            #starttime,endtime received as decimal days (natural marshalling by pywin32 from excel format hh::mm),
            # to be converted in decimal hours
            consumption /= self.battery.capacity # consumption in soc%
            profile.append(ConnectionTemplate(startday, starttime*24, endday, endtime*24, consumption))
        #profile.sort(lambda x,y: x.startday - y.startday if x.startday - y.startday != 0 else x.starttime - y.starttime)
        # TODO: sort profile by startday+starttime
        # TODO: check non-overlapping
        self.profile = profile

    def get_contiguous_range(self, topleftcell, nbrows = -1, nbcols = -1):
        """ topLeftCell should be an excel range
            returns a range
        """
        offset = self.offset
        sheet = topleftcell.Worksheet
        bottomrightcell = None
        if nbrows <= 0:
            if topleftcell.Value is not None and offset(topleftcell, 1, 0).Value is not None:
                bottomrightcell = topleftcell.End(constants.xlDown)
            else:
                bottomrightcell = topleftcell
        else:
            bottomrightcell = offset(topleftcell, nbrows - 1, 0)
        if nbcols <= 0:
            if bottomrightcell.Value is not None and offset(bottomrightcell, 0, 1).Value is not None:
                bottomrightcell = bottomrightcell.End(constants.xlToRight)
        else:
            bottomrightcell = offset(bottomrightcell, 0, nbcols - 1)

        return sheet.Range(topleftcell, bottomrightcell)

    def read_contiguous_range(self, topleftcell, nbrows = -1, nbcols = -1):
        """ topLeftCell should be an excel range
            returns a tuple of tuples
        """
        rang = self.get_contiguous_range(topleftcell, nbrows, nbcols)
        values = rang.Value # values is a tuple of tuples or a single item (when topLeftCell == bottomRightCell)
        if not isinstance(values, tuple):
            values = ((values,))
        return values

    @staticmethod
    def offset(rang, nbrows, nbcols):
        """ Offset method of excel range class does not seem to work properly in pwin32 211 !!"""
        return rang.Worksheet.Cells(rang.Row + nbrows, rang.Column + nbcols)

    @staticmethod
    def messagebox(message):
        """ possible window types:
                MB_OK, MB_OKCANCEL, MB_YESNO, MB_RETRYCANCEL, MB_SYSTEMMODAL,
                MB_ICONERROR, MB_ICONQUESTION, MB_ICONEXCLAMATION
            MB_OKCANCEL returns 1 when OK clicked, 2 when Cancel clicked

            note for exceptions: use eg raise COMException("message", winerror.E_INVALIDARG) to have the message
            be displayed by excel
            raise ValueError(message) or raise COMException("message") or raise COMException("message", winerror.DISP_E_EXCEPTION)
            would be swallowed by excel/vba and the error message not properly shown
        """
        win32ui.MessageBox(message, "Message from Python", win32con.MB_OK)


#----------------------------------------------------------------------------------------
# REGISTRATION AND TESTS
#----------------------------------------------------------------------------------------
def debug_test():
    """ function for debugging """
    optimizer = Optimizer()
    optimizer.UseWorkbook("D:/0.Project_Work/python_works/vehicle_charge/Long Jing/121121", "vehicleChargeOptimizer.xlsm")
    optimizer.Run()
    #optimizer.LoadMobilityProfile()

def unit_tests():
    """ basic unit tests """
    onehour = dt.timedelta(hours=1)
    fisrtday = dt.datetime(2012, 10, 01)
    dates = np.array([ fisrtday + i * onehour for i in range(24*7+1)])
    prices = np.arange(1.0, len(dates))
    priceseries = PriceSeries(dates, prices)
    battery = Battery(100)
    Mon, Tue, Wed, Thu, Fri, Sat, Sun = 0, 1, 2, 3, 4, 5, 6
    connection_pattern = [ConnectionTemplate(Mon, 0.0+1.0/3, Mon, 0.0+2.0/3), ConnectionTemplate(Mon, 1.0+0.0, Mon, 1.0+2.0/3),
                          ConnectionTemplate(Mon, 1.0+3.0/4, Mon, 2.0+1.0/4), ConnectionTemplate(Mon, 2.0+1.0/2, Mon, 3.0+0.0),
                          ConnectionTemplate(Mon, 3.0+1.0/4, Mon, 3.0+1.0/3), ConnectionTemplate(Mon, 3.0+1.0/2, Mon, 3.0+3.0/4),
                          ConnectionTemplate(Mon, 4.0+0.0, Mon, 5.0+0.0), ConnectionTemplate(Mon, 5.0+1.0/4, Mon, 7.0+1.0/3),
                          ConnectionTemplate(Mon, 7.0+2.0/3, Mon, 9.0+0.0), ConnectionTemplate(Mon, 10.0+0.0, Mon, 12.0+1.0/3),
                          ConnectionTemplate(Mon, 13.0+0.0, Mon, 15.0+0.0)
                          ]
    optimizer = ChargeOptimizer(battery, priceseries, connection_pattern)
    for window in range(2, 48):
        optimizer.run(window)

    # pattern with EOW crossing
    connection_pattern.append(ConnectionTemplate(Sun, 7.0+2.0/3, Mon, 0.0+1.0/4))
    for window in range(2, 48):
        optimizer.run(window)


# to debug with PythonWin Trace Collector Debugging tool or "python -m win32traceutil.py " from a console :
#  import win32traceutil
#  or run the script with the --debug option
if __name__ == '__main__':
    win32com.client.gencache.EnsureDispatch('Excel.Application', 0) # ensure makepy is run
    print "Registering COM server..."
    import win32com.server.register
    #win32com.server.register.UseCommandLine(Optimizer)
    unit_tests()
    #debug_test()


