import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

from numbergame.bots import BinarySearchBot
from numbergame.statistics import performance_scaling



sizes = np.array([10, 50, 100, 500, 1_000, 5_000, 10_000])
results = performance_scaling(BinarySearchBot, 
                              [10, 50, 100, 500, 1_000, 5_000, 10_000],
                              10_000,
                              )
means = np.array([result.mean for result in results])
stds = np.array([result.std for result in results])


# Fit to logarithmic model
x = np.linspace(sizes.min(), sizes.max())


def fitfunc(log2x, a: float, b: float):
    return a*log2x + b


(a, b), pcov, *_ = curve_fit(fitfunc, np.log2(sizes), means, sigma=stds)


fig, ax = plt.subplots()
ax.plot(x, a*np.log2(x) + b, label=f'f(x) = {a:0.2f} $\\log_2(x)$ + {b:0.2f}')
ax.errorbar(sizes, means, stds, label='Data', linestyle='', marker='o')
ax.set_xscale('log')
ax.set_xlabel('Size of guess interval')
ax.set_ylabel('Average number of guesses')
ax.set_title('Performance of the binary search strategy')
ax.legend()
ax.grid(True)
plt.show()
