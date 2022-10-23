# -*- coding: utf-8 -*-
"""!
@package    Gears
@file       spur_gears.py
@author     Wyatt Conner
@date       10/22/2022
@brief      Library of functions relevant to calculations for Spur Gears.
@details    This contains multiple functions that can calculate the speed, torque, power and stress a spur gear would experience.
            it assumes that you have kno
"""

import math
import numpy
from pint import UnitRegistry

class SpurGears:
    """!
    @brief   This is the class to call for functions relevant to Spur Gears
    @details This contains multiple functions that can calculate the speed, torque, power and stress a spur gear would experience.
    """
    
    def __init__(self):
        print('Spur Gear object Created')
        self.ureg = UnitRegistry()
        
    def transmitted_load(self, power= 0 , pitchline= 0, unit_type = None):
        """!
        @brief      To calucate the transmitted load of a spur gear between a gear and pinon
        @details    This function represents equation 13-35 on page 699 of the 10th
                    edition of Shingley's Mechanical Design Textbook. This represents
                    the load transmitted from gear to the other. It is based upon
                    the power provided to the gear and ptichline of the gear.
                    pitchline is the velocity of the gear in feet/min. This
                    functions primary function is to be called by other functions
                    to use this equation when needed. 
        @param     [power]  This is the power at which is gear is being driven. Units
                            of N-m/s in SI units.
                   [pitch_line]     This is the speed of the gear at which it is
                   rotating, it is expected that you would have already done
                   this calcuation refer to eq 13-34 on pg 699 10th edition. 
                   [unit_type] This can either be 'SI' or 'ENG' to specify what
                   type of units you want the ouput to be. By default it will output
                   SI units.
        """
        # Try to Define our inputs into our desired units
        try:
            self.power = power.to(self.ureg.horsepower)
            self.pitchline = pitchline.to(self.ureg.feet/self.ureg.minute)
            self.unit_type = unit_type
            if self.unit_type == None:
                self.unit_type = self.ureg.newton
        except:
            print('TRANSMITTED_LOAD: Unit Conversion Failed Please Define the correct unit inputs using a unit directory!')
            return(None)
        
        # Calculate the transmitted load EQ 13-35 pg. 699
        self.load = 33_000*self.power.magnitude/self.pitchline.magnitude
        self.output_load_lbf = self.load*self.ureg.lbf
        
        # Ouput desired units based user inputs
        try:
            self.output_load = self.output_load_lbf.to(self.unit_type)
            return(self.output_load)
        except:
            print('TRANSMITTED_LOAD: User defined output units are not a force unit type.')
            return(None)
         
    def load_components (self, W_t = None, pressure_angle = None, unit_type = None):
        """!
        @breif This calculates the components of the transmitted load on the particular gear stage
        @details This uses trignometery to determine all the components of the forces acting on each gear 
                 in a single gear stage. The W_t provided is force tangential to the pitch diameter and with
                 the pressure angle defined the other two components of the radial and magnitude are calculated.
                 The pressure angle is assumed to be 20 degrees unless specified otherwise.
        @param  [W_t] This is the tangential load that transmitted onto both gears and translates across the gear ratio 
                [pressure_angle] This the pressure angle of the gear stage. units degrees or radians
                [unit_type] This is the specified units of the desired outputs.
                 
        """
        self.pressure_angle = pressure_angle
        self.W_t = W_t
        self.unit_type = unit_type
        
        if self.pressure_angle == None:
            self.pressure_angle = 20*self.ureg.degree
                
        if self.W_t == None:
            print('LOAD_COMPONENTS: Provide a transmitted load in in force units')
            return(None)
        
        try:
            self.pressure_angle.ito(self.ureg.radian)
        except:
            print('LOAD_COMPONENTS: Provide the angle unit!')
            self.pressure_angle = None
            
        self.F_radial = self.W_t*math.tan(self.pressure_angle)
        self.F_magnitude = self.W_t/math.cos(self.pressure_angle)
        
        if self.unit_type != None:
            self.F_radial.ito(self.unit_type)
            self.F_magnitude.ito(self.unit_type)
            
        return(self.F_magnitude, self.F_radial)
        
        
        
        
    def pitch_line(self, diameter = 0, gear_speed = 0, unit_type = None):
        """!
        @breif  This is a function that calculates the pitchline with the given diameter and angular speed
        @details This function calculates the pitchline velocity of a gear with the given
                 gear diameter and rotational speed. It uses the equation 13-34 on
                 page 699 of the 10th edition of Shingley's Mechanical Design Textbook.
        @param  [diameter] The pitch diameter of the gear - refer to pg 668
                [gear_speed] The rotational speed of the gear, units such as RPM
                [uit_type] The desired unit of the output of this function, by default its meter/second
        """
        # Try to Define our inputs into our desired units
        try:
            self.diameter = diameter.to(self.ureg.inch)
            self.gear_speed = gear_speed.to(self.ureg.rpm)
            self.unit_type = unit_type
            if self.unit_type == None:
                self.unit_type = self.ureg.meter/self.ureg.second
        except:
            print('PITCH_LINE: Unit Conversion Failed Please Define the correct unit inputs using a directory!')
            return(None)
        # Cacluate the Pitch Line velocity using eq 13-34 from pg 699
        self.V = math.pi*self.diameter.magnitude*self.gear_speed.magnitude/12
        self.pitchline = self.V*self.ureg.feet/self.ureg.minute
        
        try:
            self.output_pitchline = self.pitchline.to(self.unit_type)
            return(self.output_pitchline)
        except:
            print('PITCH_LINE: User defined output units are not a velocity unit type.')
            return(self.pitchline)
        
    def gear_char(self, pitch = None, teeth_num = None, mod = None, circular_pitch = None, diameter = None):
        """!
        @breif This function will solve for the characteristics of a gear with a 2 given parameters of the gear
        @details This function solves for the gears characteristics by iteritavly solving for each value with a few
                 given parameters, this is nice as it allows us to get the specific values we need for our other equations
                 for spur gears, so it streamlines the process. Please make sure your units are consistent otherwise it will
                 have issues. Refer to equations on pg 668 for these calculations.This function doesn't convert units so all
                 inputs must have the same length unit for this function to operate correctly. 
        @param  [pitch] Diametrial pitch of the gear and should have the units of 1/[Length] and reprents the number of teeth per inch of the
                        diameter of the gear.
                [teeth_num] This is the number of teeth on the gear and it is unitless.
                [mod]       This is the module of the gear provide in units[Length]. The module represents the ratio of pitch diameter
                            to the number of teeth.
                [cicular_pitch] This distance between each tooth and should be given in units [Length].
                [diameter]  This the pitch diameter given in units [Length] it is the diameter that represents the average diameter of the inner
                            outer diameter of the teeth of the gear.*
        """
        self.pitch = pitch
        self.teeth_num = teeth_num
        self.mod = mod
        self.circular_pitch = circular_pitch
        self.diameter = diameter
        self.index = 0
        
        while self.index != 6:
            if self.pitch == None:
                try:
                    self.pitch = self.teeth_num/self.diameter
                except:
                    try:
                        self.pitch = math.pi/self.cicular_pitch
                    except:
                        self.pitch = None
                        if self.index == 5:
                            print('GEAR_CHAR: To many unkonws to calculate Pitch or incorrect units.')
                        
                
            if self.teeth_num == None:
                try:
                    self.teeth_num = self.pitch*self.diameter
                except:
                    try:
                        self.teeth_num = self.diameter/self.mod 
                    except:
                        self.teeth_num = None
                        if self.index == 5:
                            print('GEAR_CHAR: To many unknowns to calculate the Number of Teeth or incorrect units.')
                        
            if self.mod == None:
                try:
                    self.mod = self.diameter/self.teeth_num
                except:
                    try:
                        self.mod = self.circular_pitch/math.pi
                    except:
                        self.mod = None
                        if self.index == 5:
                            print('GEAR_CHAR: To many unkowns to calculate the Modeule or incorrect units.')
            
            if self.circular_pitch == None:
                try:
                    self.circular_pitch = math.pi/self.pitch
                except:
                    try:
                        self.circular_pitch = math.pi*self.mod
                    except:
                        self.circular_pitch = None
                        if self.index == 5:
                            print('GEAR_CHAR: To many unkowns to calculate the Cicular Pitch or incorrect units.')
        
            
            if self.diameter == None:
                try:
                    self.diameter = self.teeth_num/self.pitch
                except:
                    try:
                        self.diameter = self.mod*self.teeth_num
                    except:
                        self.diameter = None
                        if self.index == 5:
                            print('GEAR_CHAR: To many unkonws to calculate the Diameter or incorrect units.')
    
            if self.diameter == None or self.circular_pitch == None or self.mod == None or self.teeth_num == None or self.pitch == None:
                self.index += 1
                #print(self.index)
            else:
                #print(self.index)
                return(self.pitch, self.teeth_num, self.mod, self.circular_pitch, self.diameter)
                    
        
                
          
if __name__ == "__main__":
    
    ureg = UnitRegistry()
    Spur = SpurGears()
    power = 35*ureg.horsepower
    input_speed = 1200*ureg.rpm
    
    pinon = Spur.gear_char(pitch = 10/ureg.inch, teeth_num = 16)
    gear  = Spur.gear_char(pitch = 10/ureg.inch, teeth_num = 48)
    ratio = gear[4]/pinon[4]
    speed_2 = input_speed/ratio
    speed_3 = speed_2/ratio
    
    p_1_pitchline = Spur.pitch_line(pinon[4],input_speed,ureg.feet/ureg.minute)
    g_1_pitchline = Spur.pitch_line(gear[4],speed_2,ureg.feet/ureg.minute)
    p_2_pitchline = Spur.pitch_line(pinon[4],speed_2,ureg.feet/ureg.minute)
    g_2_pitchline = Spur.pitch_line(gear[4],speed_3,ureg.feet/ureg.minute)

    p_1_load = Spur.transmitted_load(power, p_1_pitchline, ureg.lbf)
    p_2_load = Spur.transmitted_load(power, p_2_pitchline, ureg.lbf)
    print("Pinon 1 W_t", p_1_load)
    print("Pinon 2 W_t", p_2_load)
    
    g_1_load = Spur.transmitted_load(power, g_1_pitchline, ureg.lbf)
    g_2_load = Spur.transmitted_load(power, g_2_pitchline, ureg.lbf)
    print("Gear 1 W_t", g_1_load)
    print("Gear 2 W_t", g_2_load)
    
    p_1_load_comp = Spur.load_components( p_1_load)
    print("Magnitude force of Pinon 1:", p_1_load_comp[0])
    print("Radial force of Pinon 1:", p_1_load_comp[1])
    
    p_2_load_comp = Spur.load_components( p_2_load)
    print("Magnitude force of Pinon 2:", p_2_load_comp[0])
    print("Radial force of Pinon 2:", p_2_load_comp[1])
    
    
   
    
    
    
    
    
            
        
                