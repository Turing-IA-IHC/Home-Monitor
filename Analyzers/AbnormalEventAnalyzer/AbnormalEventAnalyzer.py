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
from datetime import datetime, timedelta
from time import time, sleep
from pickle import dump, load
from os.path import dirname

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from FactAnalyzer import FactAnalyzer
from DataPool import LogTypes, SourceTypes, Messages, Data

class Event(object):
    """ Class to represent an event """
    Moment:float
    Name:str
    def __init__(self, m:float, n:str):
        self.Moment = m
        self.Name = n.lower()

class AbnormalEventAnalyzer(FactAnalyzer):
    """ Class to analyze classes of recognizers. """
    EventsDatabase = []
    TimeWindow = 7
    Keeping_Weeks = 16
    Threshold = 0.5
    Backward_events = []
    Expected_events = []
    simulationStep = 0
    Simulated_current_time = datetime(2020, 9, 9, 8, 7, 20)

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
        """ Implement me! :: Exec analysis of activity """
        d_current = self.Simulated_current_time if self.Simulating else datetime.fromtimestamp(time())

        dataReturn = []
        event_name = Misc.hasKey(data.data, 'class', '')
        event_name = '' if event_name.lower() == 'none' else event_name.lower()
        auxData = '"t":"json", "idSource":"{}"'
        if self.analyze_event(event_name) < self.Threshold or event_name in self.ME_CONFIG['ALWAYS_ABNORMAL']:
            if not event_name in self.ME_CONFIG['ALWAYS_NORMAL']:
                dataInf = self.data_from_event(Event(d_current, event_name))
                dataInf.aux = '{' + auxData.format(data.id) + '}'
                dataReturn.append(dataInf)

        backward_event_list = self.backward_events_detect()
        for be in backward_event_list:
            dataInf = self.data_from_event(be, occurred=False)
            dataInf.aux = '{' + auxData.format(data.id) + '}'
            dataReturn.append(dataInf)

        expected_event_list = self.expected_events_predict()
        for ee in expected_event_list:
            dataInf = self.data_from_event(ee, occurred=False)
            dataInf.aux = '{' + auxData.format(data.id) + '}'
            dataReturn.append(dataInf)
        
        self.save_knowledge()

        return dataReturn

    def showData(self, dataanalyzeed:Data, dataSource:Data):
        """ To show data if this module start standalone """
        self.log('An event to notify:' + dataanalyzeed.data, LogTypes.INFO)
    
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Allows to simulate data if this module start standalone """

        if self.simulationStep == 0:
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

        if self.simulationStep < self.file_length:
            if len(self.file[self.simulationStep]) < 10:
                dataReturn.insert(0, {'queryTime':time()})
                self.simulationStep += 1
                return dataReturn

            dataSimulated = Data()
            dataSimulated = dataSimulated.parse(self.file[self.simulationStep], False, True)

            self.simulationStep += 1
            dataReturn.append(dataSimulated)
            dataReturn.insert(0, {'queryTime':time()})
        else:
            self.simulationStep = 0
            dataReturn = self.simulateData(dataFilter)

        return dataReturn

    # =========== Auxiliar methods =========== #

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
        """ Retrive an list of events an return distinct name list """
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
        #print('Detected a', event_name, 'at', d)

        Events_none  = list(filter(lambda x: x.Name == '', self.EventsDatabase))
        Events_event = list(filter(lambda x: x.Name == event_name, self.EventsDatabase))

        same_day_none  = list(filter(lambda x: self.at_same_time(x.Moment) and self.at_same_week_day(x.Moment), Events_none))
        same_day_event = list(filter(lambda x: self.at_same_time(x.Moment) and self.at_same_week_day(x.Moment), Events_event))
        same_day_total = len(same_day_event) + len(same_day_none)
        same_day_value = 0 if same_day_total == 0 else len(same_day_event) / same_day_total
        #print('Tasa:', same_day_value, 'Eventos:', len(same_day_event), 'Total:', same_day_total, 'en el mismo día de la semana')
        
        last_week_none  = list(filter(lambda x: self.at_same_time(x.Moment) and self.at_last_7_days(x.Moment), Events_none))
        last_week_event = list(filter(lambda x: self.at_same_time(x.Moment) and self.at_last_7_days(x.Moment), Events_event))
        last_week_total = len(last_week_event) + len(last_week_none)
        last_week_value = 0 if last_week_total == 0 else len(last_week_event) / last_week_total
        #print('Tasa:', last_week_value, 'Eventos:', len(last_week_event), 'Total:', last_week_total, 'en los últimos 7 días')
        
        same_month_moment_none  = list(filter(lambda x: self.at_same_time(x.Moment) and self.at_same_month_moment(x.Moment), Events_none))
        same_month_moment_event = list(filter(lambda x: self.at_same_time(x.Moment) and self.at_same_month_moment(x.Moment), Events_event))
        same_month_moment_total = len(same_month_moment_event) + len(same_month_moment_none)
        same_month_moment_value = 0 if same_month_moment_total == 0 else len(same_month_moment_event) / same_month_moment_total
        #print('Tasa:', same_month_moment_value, 'Eventos:', len(same_month_moment_event), 'Total:', same_month_moment_total, 'en el mismo mometo del mes')
        
        acumulated = same_day_value + last_week_value + same_month_moment_value
        #print('With',min(1, acumulated), 'is', 'Normal' if acumulated >= 0.5 else 'Abnormal')

        # Remove old data
        self.EventsDatabase = list(filter(lambda x: x.Moment > (d_current - timedelta(weeks=self.Keeping_Weeks)), self.EventsDatabase))

        # Avoid same event many times in time window
        if record:
            exists = list(filter(lambda x: x.Moment >= (d_current - timedelta(minutes=((self.TimeWindow * 2) + 1))) and x.Name == event_name , self.EventsDatabase))
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
        expected = list(filter(lambda x: self.at_same_time(x.Moment) and x.Name != '' and \
            (self.at_same_week_day(x.Moment) or self.at_last_7_days(x.Moment) or self.at_same_month_moment(x.Moment))
            , self.EventsDatabase))
        expected = self.distinct(expected)
        for event_name in expected:
            if self.analyze_event(event_name, record=False) >= self.Threshold:
                exists = list(filter(lambda x: x.Moment >= (d_current - timedelta(minutes=self.TimeWindow)) and x.Name == event_name, self.EventsDatabase))
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
                events += list(filter(lambda x: evnt.Moment <= x.Moment and x.Moment <= (evnt.Moment + timedelta(minutes=self.TimeWindow)) and x.Name != '' and x.Name != event_name, self.EventsDatabase))
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
        self.EventsDatabase = load(open(dirname(__file__) + '/model/data.ab', 'rb'))

    def save_knowledge(self):
        """ Save database of events or knowledge """
        dump(self.EventsDatabase, open(dirname(__file__) + '/model/data.ab', 'wb'))
   
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
    comp.reset_knowledge()
    comp.setLoggingSettings(LogTypes.INFO)
    comp.init_standalone(path=dirname(__file__))
    sleep(600)
