from bsread import Generator,Source
import numpy as np
from functools import partial


def relnoise(x,fac = 1000):
    return 1/np.sqrt(fac)/np.sqrt(x)


class TestData:
    def __init__(self,tstart=-1,tend=10):
        self.tstart = tstart
        self.tend = tend
        self.pump_drops = 5
        self.pump_frac = .05
        self.pump_noise = .1
        self.sig_noise = .02
        self.pulseId = -1


    def generateData(self,pulse_id):

        t = -(self.tstart - self.tend)*np.random.random_sample() + self.tstart
        tr = pulse_id*.01

        i0 = np.random.gamma(2.3,1)
        sig = (1-np.cos(2*np.pi/.7*t)*np.exp(-t/2))
        pump_on = not np.random.poisson(1./self.pump_drops)
        i_pump = self.pump_frac*(float(pump_on) + self.pump_noise*np.random.randn())
        if t<0:
            i_pump = 0.
        i = (i0 * (1+i_pump*sig))
        i += relnoise(i)*np.random.randn()
        if np.isnan(i):
            i = 0.
        self.i0 = i0
        self.i = i
        self.pump_on = float(pump_on)
        self.t = t
        self.i_pump = i_pump
        self.pulseId = float(pulse_id)

    def getPar(self,pulseId,parameter=None):
        if not pulseId==self.pulseId:
            self.generateData(pulseId)
        return self.__dict__[parameter]







pars =  ['i0','i','t','i_pump','pump_on','pulseId']



def createStream():
    s = TestData()
    generator = Generator()
    for par in pars:
        generator.add_channel(par, partial(s.getPar,parameter=par))
    generator.generate_stream()



class StreamReader:
    def __init__(self,host='localhost', port=9999):
        self.source = Source('localhost', 9999)
        self.s = self.source.connect()


    def readStream(self,Nevents):
        data = []
        for n in range(Nevents):
            m = self.s.receive()
            data.append([m.data.data[par].value for par in pars])

        return np.asarray(data)


