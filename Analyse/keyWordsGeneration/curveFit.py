"""
曲线拟合的例程
"""


import numpy as np
import pylab as plt
# import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

x = range(0, 10, 1)
y = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1]

# 拟合高斯分布
def gaussian(x, *param):
    return param[0] * np.exp(-np.power(x - param[2], 2.) / (2 * np.power(param[4], 2.))) + \
           param[1] * np.exp(-np.power(x - param[3], 2.) / (2 * np.power(param[5], 2.)))
# 拟合了两次可还行


popt, pcov = curve_fit(gaussian, x, y, p0=[3, 4, 3, 6, 1, 1])
print('popt')
print(popt)
print('pcov')
print(pcov)

plt.plot(x, y, 'b+:', label='data')
plt.plot(x, gaussian(x, *popt), 'ro:', label='fit')
plt.legend()
plt.show()