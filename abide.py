import numpy as np
import heapq

LAT = 0.01

class Kernel:
    def __init__(self): self.q, self.n = [], 0
    def send(self, time, agent, msg):
        heapq.heappush(self.q, (time, self.n, agent, msg)); self.n += 1
    def run(self, end):
        while self.q:
            time, _, agent, msg = heapq.heappop(self.q)
            if time > end: break
            agent.receive(self, time, msg)

class Exchange:
    def __init__(self): self.price = 100.0
    def receive(self, k, t, msg):
        kind, sender, qty = msg
        self.price += 0.001 * qty * (1 if kind == "MKT_BUY" else -1)
        k.send(t + LAT, sender, ("FILL", self.price, qty))

class Noise:
    def __init__(self, ex, rng): self.ex, self.rng = ex, rng
    def receive(self, k, t, msg):
        if msg == "WAKE":
            kind = self.rng.choice(["MKT_BUY", "MKT_SELL"])
            k.send(t + LAT, self.ex, (kind, self, 1))
            k.send(t + self.rng.exponential(1.0), self, "WAKE")

class TWAP:
    def __init__(self, ex, qty, n, dt):
        self.ex, self.q, self.n, self.dt = ex, qty, n, dt
        self.sent, self.fills, self.arrival = 0, [], None
    def receive(self, k, t, msg):
        if msg == "WAKE":
            if self.arrival is None: self.arrival = self.ex.price
            k.send(t + LAT, self.ex, ("MKT_BUY", self, self.q)); self.sent += 1
            if self.sent < self.n: k.send(t + self.dt, self, "WAKE")
        else:
            self.fills.append((msg[1], msg[2]))

k, ex = Kernel(), Exchange()
for i in range(20):
    k.send(0, Noise(ex, np.random.default_rng(i)), "WAKE")
me = TWAP(ex, qty=10, n=10, dt=5.0)
k.send(100, me, "WAKE")
k.run(300)

avg = sum(p * q for p, q in me.fills) / sum(q for _, q in me.fills)
print("slippage (bps):", (avg - me.arrival) / me.arrival * 1e4)