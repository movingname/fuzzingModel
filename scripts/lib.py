# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 17:15:12 2015

@author: rvlfl_000
"""

import math

def fit_powerlaw(data):
    count = 1
    ln_sum = 0
    x_min = 1
    for x in data:
        if x < x_min:
            continue
        count += 1
        
        ln_sum += math.log(x / x_min)

    n = count - 1

    alpha = 1 + n * (1 / ln_sum)
    sigma = (alpha - 1) / math.sqrt(n)
    
    print("alpha = " + str(alpha))
    print("sigma = " + str(sigma))
    
    return (alpha, sigma)
