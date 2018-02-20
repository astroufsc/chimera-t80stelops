#!/usr/bin/env python
import copy
import datetime

from chimera.core.callback import callback
from chimera.core.chimeraobject import ChimeraObject
from chimera.core.exceptions import ObjectNotFoundException, ChimeraException
from chimera.core.manager import Manager
from pymodbus.exceptions import ConnectionException


class SchedCallbacks(object):
    def __init__(self, localManager, schedname, data):
        self._data = data
        self.schedname = schedname

        @callback(localManager)
        def SchedActionBeginClbk(action, message):
            self.update_sched_msg(message)

        @callback(localManager)
        def SchedStateChangedClbk(newState, oldState):
            self.update_sched_state(newState)

        self.SchedStateChangedClbk = SchedStateChangedClbk
        self.SchedActionBeginClbk = SchedActionBeginClbk

    def update_sched_state(self, state):
        self._data['scheduler_state_%s' % self.schedname].update(
            {'state': str(state), 'last_update': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')})

    def update_sched_msg(self, message):
        self._data['scheduler_msg_%s' % self.schedname]['message'] = message
        self._data['scheduler_msg_%s' % self.schedname]['last_update'] = datetime.datetime.utcnow().strftime(
            '%Y-%m-%d %H:%M:%S')
        # self.update_schedulers()


class T80STelops(ChimeraObject):
    __config__ = {"query_delay": 300,  # seconds between querying the instruments
                  "dt_max": 20 * 60,  # Max time to data be considered too old. seconds.
                  "telescopes": [],
                  "domes": [],
                  "cameras": [],
                  "weatherstations": [],
                  "fans": [],
                  "seeingmonitors": [],
                  "schedulers": [],
                  "local_manager_ip": "127.0.0.1",
                  "local_manager_port": 9001,
                  }

    def __init__(self):
        ChimeraObject.__init__(self)

    def __start__(self):

        # Reset data
        self._data = dict()
        self.setHz(1. / self["query_delay"])

        self.localManager = Manager(self["local_manager_ip"], self["local_manager_port"])

        # Define callbacks for scheduler actions
        if self["schedulers"] is not None:

            self.CallBacks = []

            for sched in self["schedulers"]:
                self.schedname = sched.split('/')[-1]
                self._data['scheduler_msg_%s' % self.schedname] = dict()
                self._data['scheduler_state_%s' % self.schedname] = dict()

                self.CallBacks.append(SchedCallbacks(self.localManager, self.schedname, self._data))

                self.getManager().getProxy(sched).actionBegin += self.CallBacks[-1].SchedActionBeginClbk
                self.getManager().getProxy(sched).stateChanged += self.CallBacks[-1].SchedStateChangedClbk

            self.update_schedulers()

        self.control()

    def get_instrument(self, location):
        try:
            instrument = copy.copy(self.getManager().getProxy(location))
        except ObjectNotFoundException:
            instrument = None
        return instrument

    def control(self):
        self.log.debug('T80STelops control.')
        self.query_instruments()
        return True

    def query_instruments(self):

        # Seeing monitors
        if self["seeingmonitors"] is not None:
            for sm in self["seeingmonitors"]:
                monitor = self.get_instrument(sm)
                if monitor:
                    smname = sm.split('/')[-1]
                    self._data['seeing_%s' % smname] = dict()
                    for param in ('seeing', 'seeing_at_zenith', 'airmass', 'flux'):
                        try:
                            aux = monitor.__getattr__(param)()
                            # val = 'NaN' if datetime.datetime.utcnow() > aux.time + datetime.timedelta(
                            #     seconds=self['dt_max']) else '%.2f' % aux.value
                            val = '%.2f' % aux.value
                            self._data['seeing_%s' % smname][param] = val + ' ' + str(aux.unit)
                            self._data['seeing_%s' % smname]['last_update'] = aux.time.strftime('%Y-%m-%d %H:%M:%S')
                        except AttributeError:
                            pass
                        except NotImplementedError:
                            pass

        # Weather Stations
        if self["weatherstations"] is not None:
            for ws in self["weatherstations"]:
                weatherstation = self.get_instrument(ws)
                if weatherstation:
                    wsname = ws.split('/')[-1]
                    self._data['weather_%s' % wsname] = dict()
                    for param in ('temperature', 'dew_point', 'humidity', 'wind_speed', 'wind_direction', 'pressure',
                                  'sky_transparency'):
                        try:
                            aux = weatherstation.__getattr__(param)()
                            # val = 'NaN' if datetime.datetime.utcnow() > aux.time + datetime.timedelta(
                            #     seconds=self['dt_max']) else '%.2f' % aux.value
                            val = '%.2f' % aux.value
                            self._data['weather_%s' % wsname][param] = val + ' ' + str(aux.unit)
                            self._data['weather_%s' % wsname]['last_update'] = aux.time.strftime('%Y-%m-%d %H:%M:%S')
                        except KeyError:
                            ### There is a weather station that is having trouble:
                            # KeyError: '#'
                            pass
                        except AttributeError:
                            pass
                        except TypeError:
                            pass
                    try:
                        self._data['weather_%s' % wsname]['ok_to_open'] = str(weatherstation.okToOpen())
                    except AttributeError:
                        pass

        # Telescopes
        if self["telescopes"] is not None:
            for tel in self["telescopes"]:
                telescope = self.get_instrument(tel)
                try:
                    if telescope:
                        try:
                            pos = telescope.getPositionRaDec()
                            telname = tel.split('/')[-1]
                            self._data['telescope_%s' % telname] = {'ra': str(pos.ra),
                                                                    'dec': str(pos.dec),
                                                                    'ra_deg': float(pos.ra.D),
                                                                    'dec_deg': float(pos.dec.D),
                                                                    'state': 'Tracking' if telescope.isTracking() else 'Stopped',
                                                                    'last_update': datetime.datetime.utcnow().strftime(
                                                                        '%Y-%m-%d %H:%M:%S')}
                            try:
                                self._data.update({'cover': 'Open' if telescope.isCoverOpen() else 'Closed'})
                            except AttributeError:
                                pass
                            if telname == "T80S":
                                for sensor in telescope.getSensors():
                                    if sensor[0] in ('TM1', 'TM2', 'FrontRing', 'TubeRod'):
                                        self._data['telescope_%s' % telname][sensor[0]] = '%.2f deg_C' % sensor[1]
                        except ChimeraException:
                            pass
                except TypeError:
                    pass

        if self["domes"] is not None:
            for dom in self["domes"]:
                dome = self.get_instrument(dom)
                if dome:
                    pos = dome.getAz()
                    try:
                        self._data['dome_%s' % dom.split('/')[-1]] = {'azimuth': str(pos),
                                                                      'state': str(dome.getMode()),
                                                                      'last_update': datetime.datetime.utcnow().strftime(
                                                                          '%Y-%m-%d %H:%M:%S')}
                        try:
                            self._data['dome_%s' % dom.split('/')[-1]].update(
                                {'slit': 'OPEN' if dome.isSlitOpen() else 'CLOSED'})
                            self._data['dome_%s' % dom.split('/')[-1]].update(
                                {'flap': 'OPEN' if dome.isFlapOpen() else 'CLOSED'})
                        except NotImplementedError:
                            pass
                    except TypeError:
                        pass
        if self["cameras"] is not None:
            for cam in self["cameras"]:
                camera = self.get_instrument(cam)
                if camera:
                    camname = cam.split('/')[-1]
                    self._data['camera_%s' % camname] = dict()
                    try:
                        # self._data['camera_%s' % camname]['status'] = 'Exposing' if camera.isExposing() else 'Idle'
                        self._data['camera_%s' % camname]['temperature'] = "%.2f" % camera.getTemperature()
                        self._data['camera_%s' % camname]['pressure'] = "%.3f" % camera.getPressure()
                    except AttributeError:
                        pass
                    self._data['camera_%s' % camname]['last_update'] = datetime.datetime.utcnow().strftime(
                        '%Y-%m-%d %H:%M:%S')

        if self["fans"] is not None:
            for fan in self["fans"]:
                fanname = fan.split('/')[-1]
                f = self.get_instrument(fan)
                if f:
                    try:
                        self._data['fan_%s' % fanname] = {'state': 'ON' if f.isSwitchedOn() else 'OFF'}
                    except ConnectionException:
                        continue
                    except AttributeError:
                        continue
                    try:
                        self._data['fan_%s' % fanname]['speed'] = f.getRotation()
                    except AttributeError:
                        pass
                    self._data['fan_%s' % fanname]['last_update'] = datetime.datetime.utcnow().strftime(
                        '%Y-%m-%d %H:%M:%S')

        self.update_schedulers()

    def update_schedulers(self):
        if self["schedulers"] is not None:
            for sched in self["schedulers"]:
                try:
                    self.schedname = sched.split('/')[-1]
                    f = self.get_instrument(sched)
                    self._data['scheduler_state_%s' % self.schedname].update({'state': str(f.state()),
                                                                              'last_update': datetime.datetime.utcnow().strftime(
                                                                                  '%Y-%m-%d %H:%M:%S')})
                except AttributeError:
                    self.log.error("Error updating scheduler %s" % sched)

    def get_data(self):
        return self._data
