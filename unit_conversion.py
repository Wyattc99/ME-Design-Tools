# -*- coding: utf-8 -*-
"""!
@package    Gears
@file       unit_conversion.py
@author     Wyatt Conner
@date       10/22/2022
@brief      Library of functions to convert units.
@details    This will convert units based on given units and desired units.
"""

class UnitConvert():
    
    def __init__ (self):
        return(None)
    def convert(self, Numerical = 0, unit_in = None, unit_out = None):
        """!
        """
        self.Numerical = Numerical
        self.unit_in = unit_in
        self.unit_out = unit_out
        
        if self.unit_out == None or self.unit_in == None:
            print('Please input units for this arguement')
            return()
        elif self.unit_out == self.unit_in:
            self.ratio = 1
            
        if self.Numerical == 0:
            print(' Enter a non-zero interger to convert units for')
            return()
        
        self.convert_ID = self.unit_in + self.unit_out
        
        return(self.convert_ID)        
        