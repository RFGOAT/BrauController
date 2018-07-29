#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:44:11 2018

@author: achim
"""

#######	Example	#########
import PID as PID_class

import control.matlab as ctrl


Kessel = ctrl.tf([1],[540,1])

#Regler=PID_class.PID(3.0,3,0)
#Regler.setPoint(5.0)
#while True:
#     pid = Regler.update(measurement_value)


