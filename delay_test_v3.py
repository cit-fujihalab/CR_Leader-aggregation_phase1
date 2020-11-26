
from time import sleep
from time import perf_counter
import numpy as np

def time_R():
    port = [50080, 50075, 50090, 50085, 50070]
    np.random.choice(port)
    x = np.random.choice( port, size=3, replace=False )
    print(x)

    delay = {
        50070 : 0.026,
        50075 : 0.240,
        50080 : 0.040,
        50085 : 0.047,
        50090 : 0.075
    }
    r = []
    for y in x :
        z = delay.get(y)
        r.append(z)
    r.sort()
    print("今回の遅延時間list", r)
    p_wait_sec = 0
    for sec in r[:]:
        sec = r[0]
        r.remove(sec)
        wait_sec = sec - p_wait_sec
        print(r)
        print("%4f ping-delay" % wait_sec)
        t = perf_counter()
        until = perf_counter() + wait_sec
        while perf_counter() < until:
            pass
        keys = [k for k, v in delay.items() if v == sec]
        print(keys)
        end_time = perf_counter() - t
        print(end_time)
        p_wait_sec = sec

"""
def transfer_port(self, sec):
    people_dict.keys()[people_dict.values().index(search_age)]
    self.delay.keys()[self.delay.valus().index(sec)]
"""

time_R()