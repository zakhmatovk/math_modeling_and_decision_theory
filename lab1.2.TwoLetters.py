import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math

def exp_random(l, coef=1):
    return -math.log(1 - np.random.random()) * 50
    return coef * np.exp(-1 * l * np.random.random())

def create_letters():
    one_sum = exp_random(5, 1000)
    your, other = [one_sum, one_sum * 2][::(-1) ** np.random.randint(2)]
    return your, other

def process(total_count, segment_total):
    yours = []
    others = []
    for _ in range(total_count):
        your, other = create_letters()
        yours.append(int(your))
        others.append(int(other))
    max_value = max(yours + others)
    step = (max_value // segment_total) or 1
    your_totals = {}
    other_totals = {}
    for idx in range(len(yours)):
        your_totals.setdefault((yours[idx] // step) * step, []).append(yours[idx])
        other_totals.setdefault((yours[idx] // step) * step, []).append(others[idx])
    yours = [sum(v) // len(v) for k, v in sorted(your_totals.items(), key=lambda x: x[0])]
    others = [sum(v) // len(v) for k, v in sorted(other_totals.items(), key=lambda x: x[0])]
    return sorted(your_totals.keys()), yours, others

sums, yours_values, others_values = process(1000000, 100)

plt.plot(sums, yours_values, 'r-')
plt.plot(sums, others_values, 'g-')
plt.show()