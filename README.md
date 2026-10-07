# TWAP Execution Simulator

A minimal discrete-event market simulator for measuring the slippage of a TWAP (time-weighted average price) execution strategy against a background of noise traders.

~60 lines of Python, no dependencies beyond NumPy. Built to understand how agent-based market simulation works (the kernel / agent / message-passing pattern used in frameworks like ABIDES) before moving to a real framework.

## How it works

- **Kernel**: a priority queue of `(time, seq, agent, msg)` events. Pops the earliest event and delivers it to the target agent. The sequence number breaks ties deterministically.
- **Exchange**: a toy price-impact model. Every market order moves the price linearly: `price += 0.001 * qty * side`. The fill is returned to the sender after a fixed latency (`LAT`) at the post-impact price.
- **Noise traders** (x20): wake at exponentially distributed intervals and send 1-lot market buys or sells with equal probability. They make the price a random walk.
- **TWAP agent**: at t=100, starts buying 10 lots every 5 seconds, 10 slices total (100 lots). It records the price at its first wake-up as the arrival price.

## Metric

Implementation shortfall vs. arrival price, in basis points:

```
slippage_bps = (avg_fill_price - arrival_price) / arrival_price * 1e4
```

## Run

```bash
pip install numpy
python sim.py
```

Example output:

```
slippage (bps): 5.18
```

## Sanity check

Each 10-lot slice moves the price by 0.01 (about 1 bp at a price of 100). Slice `i` fills about `i` bps above arrival, so the mean over 10 slices is roughly 5.5 bps from self-impact alone. The noise traders add random variation around that. Results of about 5 bps are therefore expected.

## Limitations

This is a toy, not a realistic market model:

- No order book. Only market orders, filled instantly against a single price.
- Linear, permanent price impact with no decay or resilience.
- Fills happen at the post-impact price, which overstates slippage compared to filling at the pre-impact price.
- Noise traders are symmetric and uninformed. No momentum, no informed flow, no spread.
- Fixed latency, no queueing.
- One seeded run is a single sample. Loop over seeds to get a slippage distribution.

## Possible extensions

- Limit order book with price-time priority
- Impact decay (transient + permanent components)
- Compare TWAP vs. VWAP vs. front-loaded schedules
- Slippage distribution across many seeds
- Informed traders / momentum agents

## Design notes

Agents never touch each other directly; everything goes through `Kernel.send`. That keeps the simulation deterministic and makes it easy to add latency or new agent types without changing existing ones.
