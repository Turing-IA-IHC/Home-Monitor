"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Template to analyze classes of recognizers.
"""

import sys
import numpy as np
from numba import guvectorize, boolean, int64
from datetime import datetime, timedelta
from time import time, sleep
from pickle import dump, load
from os.path import dirname
import shutil

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from FactAnalyzer import FactAnalyzer
from DataPool import LogTypes, SourceTypes, Messages, Data

class Event:
    """ Class to represent an event """
    Moment:float
    Name:str
    def __init__(self, m:float, n:str):
        self.Moment = m
        self.Name = n.lower()

class AbnormalEventAnalyzer(FactAnalyzer):
    """ Class to analyze classes of recognizers. """
    EventsDatabase = []
    SimulationStep = 0
    Simulated_current_time = datetime(2020, 9, 9, 8, 7, 20)
    TimeWindow = 7
    Keeping_Weeks = 16
    Threshold = 0.5
    Backward_events = []
    Expected_events = []
    Last_Cleaning_Day = datetime(1970, 1, 1)

    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start processing
        pass
    
    def loadModel(self):
        """ Loads model """
        self.load_knowledge()

    def loaded(self):
        """ Implement me! :: Just after load the model and channels """
        self.ME_CONFIG['ALWAYS_ABNORMAL'] = [x.lower() for x in self.ME_CONFIG['ALWAYS_ABNORMAL']]
        self.ME_CONFIG['ALWAYS_NORMAL'] = [x.lower() for x in self.ME_CONFIG['ALWAYS_NORMAL']]

    def analyze(self, data):
        """ Exec analysis of activity """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())
        
        if self.Last_Cleaning_Day < d_current:
            self.remove_old_data()
            self.Last_Cleaning_Day = d_current + timedelta(days=1)

        dataReturn = []
        event_name = Misc.hasKey(data.data, 'class', '')
        event_name = '' if event_name.lower() == 'none' else event_name.lower()
        if self.analyze_event(event_name) < self.Threshold or event_name in self.ME_CONFIG['ALWAYS_ABNORMAL']:
            if not event_name in self.ME_CONFIG['ALWAYS_NORMAL']:
                dataInf = self.data_from_event(Event(d_current, event_name))
                dataReturn.append(dataInf)

        backward_event_list = self.backward_events_detect()
        for be in backward_event_list:
            dataInf = self.data_from_event(be, occurred=False)
            dataReturn.append(dataInf)

        expected_event_list = self.expected_events_predict()
        for ee in expected_event_list:
            dataInf = self.data_from_event(ee, occurred=False)
            dataReturn.append(dataInf)
        
        self.save_knowledge()

        return dataReturn

    def showData(self, dataanalyzeed:Data, dataSource:Data):
        """ To show data if this module start standalone """
        self.log('An event to notify:' + dataanalyzeed.data, LogTypes.INFO)
    
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Allows to simulate data if this module start standalone """

        if self.SimulationStep == 0:
            self.file = open(self.SimulatingPath, 'r').readlines()
            self.file_length = len(self.file)

        dataReturn = []

        if dataFilter.package != '':
            for target_list in self.file:
                if len(target_list) < 10:
                    continue
                dataSimulated = Data()
                dataSimulated = dataSimulated.parse(target_list, False, True)
                if dataSimulated.package == dataFilter.package and dataSimulated.source_name == dataFilter.source_name:
                    dataReturn.append(dataSimulated)
                    dataReturn.insert(0, {'queryTime':time()})
                    return dataReturn

        if self.SimulationStep < self.file_length:
            if len(self.file[self.SimulationStep]) < 10:
                dataReturn.insert(0, {'queryTime':time()})
                self.SimulationStep += 1
                return dataReturn

            dataSimulated = Data()
            dataSimulated = dataSimulated.parse(self.file[self.SimulationStep], False, True)

            self.SimulationStep += 1
            dataReturn.append(dataSimulated)
            dataReturn.insert(0, {'queryTime':time()})
        else:
            self.SimulationStep = 0
            dataReturn = self.simulateData(dataFilter)

        return dataReturn

    # =========== Auxiliar methods =========== #

    @guvectorize([(int64[:], int64, int64, int64, boolean[:])], '(n),(),(),()->(n)', target='parallel')
    def filter_moment_speedup(moment_list, searched_moment, t0, t1, res):
        secFloat = searched_moment / 86400 # Seconds per day
        secOfDay = (float(secFloat) - int(secFloat)) * 86400
        t0 = secOfDay - (t0 * 60) # change to seconds
        t1 = secOfDay + (t1 * 60) # change to seconds
        for i in range(moment_list.shape[0]):
            srchFloat = moment_list[i] / 86400 # Seconds per day
            srch = (srchFloat - int(srchFloat)) * 86400
            res[i] = srch >= t0 and srch <= t1

    moments = []
    def filter_moment(self, moment, t0:int=None, t1:int=None):
        """ Allows to filter events in same moment of day """
        if len(self.moments) != len(self.EventsDatabase):
            self.moments = np.zeros(len(self.EventsDatabase), dtype=np.int64)
            for i, e in enumerate(self.EventsDatabase):
                self.moments[i] = e.Moment.timestamp()
        searched_moment = int64(moment.timestamp())
        t0 = int64(self.TimeWindow) if t0 == None else int64(t0)
        t1 = int64(self.TimeWindow) if t1 == None else int64(t1)
        out = np.zeros(len(self.moments), dtype=np.bool)
        AbnormalEventAnalyzer.filter_moment_speedup(self.moments, searched_moment, t0, t1, out)
        results = []
        for i, m in enumerate(out):
            if m:
                results.append(self.EventsDatabase[i])
        return results

    def at_same_time(self, d_search:datetime):
        """ Define if an hour and now are near or similar moment in day (omits date) """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())
        t1 = (d_current - timedelta(minutes=self.TimeWindow)).time()
        t2 = (d_current + timedelta(minutes=self.TimeWindow)).time()
        t_search = d_search.time()
        result = t1 <= t_search and t_search <= t2
        return result

    def at_same_week_day(self, d_search:datetime):
        """ Define if a date and today is the same week day """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())
        result = d_current.weekday() == d_search.weekday()
        return result

    def at_last_7_days(self, d_search:datetime):
        """ Define if a date is in seven days before today """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())
        result = ((d_current - timedelta(days=7, minutes=self.TimeWindow)) <= d_search)
        return result

    def at_same_month_moment(self, d_search:datetime):
        """ Define if a date and todey are in same month moment, for example, monthend """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())
        m_current = d_current.day / ((d_current + timedelta(days=31)).replace(day=1) - timedelta(days=1)).day
        m_search = d_search.day / ((d_search + timedelta(days=31)).replace(day=1) - timedelta(days=1)).day
        result = abs(m_current - m_search) <= 0.1 # 3 días de márgen
        return result

    def distinct(self, event_list):
        """ Retrive an list of events and return distinct name list """
        new_list = []
        for ev in event_list:
            if not ev.Name in new_list:
                new_list.append(ev.Name)
        return new_list

    def count(self, event_list):
        """ Counts how many times appears and each event in the list """
        new_list = self.distinct(event_list)
        count_list = []
        for nl in new_list:
            count_list.append([nl, len(list(filter(lambda x: x.Name == nl, event_list)))])
        return count_list

    def analyze_event(self, event_name='', record=True):
        """ Principal method to identify if an event is normal or abnormal """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())
        event_name = event_name.lower()

        Events_moment = self.filter_moment(d_current)
        Events_none  = list(filter(lambda x: x.Name == '', Events_moment))
        Events_event = list(filter(lambda x: x.Name == event_name, Events_moment))

        if len(Events_event) > 0:
            same_day_none  = list(filter(lambda x: self.at_same_week_day(x.Moment), Events_none))
            same_day_event = list(filter(lambda x: self.at_same_week_day(x.Moment), Events_event))
            same_day_total = len(same_day_event) + len(same_day_none)
            same_day_value = 0 if same_day_total == 0 else len(same_day_event) / same_day_total
            #print('Tasa:', same_day_value, 'Eventos:', len(same_day_event), 'Total:', same_day_total, 'en el mismo día de la semana')
            
            last_week_none  = list(filter(lambda x: self.at_last_7_days(x.Moment), Events_none))
            last_week_event = list(filter(lambda x: self.at_last_7_days(x.Moment), Events_event))
            last_week_total = len(last_week_event) + len(last_week_none)
            last_week_value = 0 if last_week_total == 0 else len(last_week_event) / last_week_total
            #print('Tasa:', last_week_value, 'Eventos:', len(last_week_event), 'Total:', last_week_total, 'en los últimos 7 días')
            
            same_month_moment_none  = list(filter(lambda x: self.at_same_month_moment(x.Moment), Events_none))
            same_month_moment_event = list(filter(lambda x: self.at_same_month_moment(x.Moment), Events_event))
            same_month_moment_total = len(same_month_moment_event) + len(same_month_moment_none)
            same_month_moment_value = 0 if same_month_moment_total == 0 else len(same_month_moment_event) / same_month_moment_total
            #print('Tasa:', same_month_moment_value, 'Eventos:', len(same_month_moment_event), 'Total:', same_month_moment_total, 'en el mismo mometo del mes')
            
            acumulated = same_day_value + last_week_value + same_month_moment_value
            #print('With',min(1, acumulated), 'is', 'Normal' if acumulated >= 0.5 else 'Abnormal')
        else:
            acumulated = 0

        # Avoid same event many times in time window
        if record:
            Events_moment = self.filter_moment(d_current, self.TimeWindow, 0)
            exists = list(filter(lambda x: x.Name == event_name, Events_moment))
            if len(exists) == 0:
                evnt = Event(d_current, event_name)
                self.EventsDatabase.append(evnt)
        
        # Remove backward events
        self.Backward_events = list(filter(lambda x: x.Name != event_name, self.Backward_events))
        # Remove expected events
        self.Expected_events = list(filter(lambda x: x.Name != event_name, self.Expected_events))
        
        return round(min(1, acumulated), 2)

    def backward_events_detect(self):
        """ Detect events wich must to happened but don't do it """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())
        
        Events_moment = self.filter_moment(d_current)
        Events_no_none  = list(filter(lambda x: x.Name != '', Events_moment))
        expected = list(filter(lambda x: (self.at_same_week_day(x.Moment) or \
                self.at_last_7_days(x.Moment) or \
                self.at_same_month_moment(x.Moment))
            , Events_no_none))

        expected = self.distinct(expected)
        Events_moment = self.filter_moment(d_current, self.TimeWindow, 60)
        for event_name in expected:
            if self.analyze_event(event_name, record=False) >= self.Threshold:
                exists = list(filter(lambda x: x.Name == event_name, Events_moment))
                if len(exists) == 0:
                    evnt = Event(d_current + timedelta(minutes=self.TimeWindow), event_name)
                    self.Backward_events.append(evnt) # Put in backward events
        
        to_alert = list(filter(lambda x: x.Moment < d_current, self.Backward_events))
        self.Backward_events = list(filter(lambda x: x.Moment >= d_current, self.Backward_events))
        return to_alert

    def expected_events_predict(self, event_name=''):
        """ Detect events wich will happend raised by other event """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())

        if event_name != '':
            occurrences = list(filter(lambda x: x.Name == event_name, self.EventsDatabase))
            events = []
            for evnt in occurrences:
                Events_moment = self.filter_moment(evnt.Moment, 0, self.TimeWindow)
                events += list(filter(lambda x: x.Name != '' and x.Name != event_name, Events_moment))
            events = self.count(events)
            for e in events:
                e_name = e[0]
                e_count = e[1]
                if e_count / len(occurrences) >= self.Threshold:                
                    evnt = Event(d_current + timedelta(minutes=self.TimeWindow), e_name)
                    self.Expected_events.append(evnt) # Put in backward events

        to_alert = list(filter(lambda x: x.Moment < d_current, self.Expected_events))
        self.Expected_events = list(filter(lambda x: x.Moment >= d_current, self.Expected_events))
        return to_alert

    def reset_knowledge(self):
        """ Regenerate model or knowledge forgetting all events """
        d = datetime.fromtimestamp(time()) - timedelta(weeks=self.Keeping_Weeks)
        while d <= datetime.fromtimestamp(time()):
            evnt = Event(d, '')
            self.EventsDatabase.append(evnt)
            d = d + timedelta(minutes=15)
        self.save_knowledge()

    def load_knowledge(self):
        """ Loads database of events or knowledge """
        try:
            file_name = dirname(__file__) + "/model/data.ab"
            self.EventsDatabase = load(open(file_name, 'rb'))
        except:
            try:
                file_name = dirname(__file__) + "/model/data.ab.bck"
                self.EventsDatabase = load(open(file_name, 'rb'))
            except:
                self.reset_knowledge()

    def save_knowledge(self):
        """ Save database of events or knowledge """
        file_name = dirname(__file__) + "/model/data.ab"
        shutil.copy(file_name, file_name + ".bck")
        dump(self.EventsDatabase, open(file_name, 'wb'))
    
    @guvectorize([(int64[:], int64, boolean[:])], '(n),()->(n)', target='parallel')
    def remove_old_data_speedup(moment_list, minimus_moment, res):
        for i in range(moment_list.shape[0]):
            res[i] = moment_list[i] >= minimus_moment

    def remove_old_data(self):        
        """ Remove old data """ 
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())
        
        moments = np.zeros(len(self.EventsDatabase), dtype=np.int64)
        for i, e in enumerate(self.EventsDatabase):
            moments[i] = e.Moment.timestamp()
        
        min_moment = int64((d_current - timedelta(weeks=self.Keeping_Weeks)).timestamp())
        out = np.zeros(len(moments), dtype=np.bool)
        AbnormalEventAnalyzer.remove_old_data_speedup(moments, min_moment, out)
        res = []
        for i, evnt in enumerate(self.EventsDatabase):
            if out[i]:
                res.append(evnt)
        self.EventsDatabase = res
    
    def data_from_event(self, evnt:Event, occurred:bool=True):
        """ Build a Data object from an Event object        
            occurred: indicate if event occurred or is backwarded
        """
        dataInf = Data()
        dataInf.source_type = self.ME_TYPE
        dataInf.source_name = self.ME_NAME
        dataInf.source_item = '' if occurred else 'backwarded'
        dataInf.data = evnt.Name
        return dataInf

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = AbnormalEventAnalyzer()
    #comp.reset_knowledge()
    comp.setLoggingSettings(LogTypes.DEBUG)
    comp.init_standalone(path=dirname(__file__))
    sleep(600)
