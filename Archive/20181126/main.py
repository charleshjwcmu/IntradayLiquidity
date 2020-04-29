# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:07:09 2018

@author: e620927
"""

PRODUCTION_ENVRIONMENT = True
import os
import gc

if PRODUCTION_ENVRIONMENT:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes-Production"
else:    
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes"
os.chdir(code_dir)

import main_IntradayLiquidity
gc.collect()

import main_IntradayLiquidity_IL
gc.collect()
