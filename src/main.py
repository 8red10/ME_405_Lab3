'''!
@file main.py
This file contains code to test the ProportionalController class. This implements a 
MotorDriver instance as well as an Encoder instance as the actuator and sensor for the
ProportionalController instance, respectively.

Expected pin setup:
    Motor
        PC1 = enable pin (internal with the L6206)
        PA0 = motor input 1 (internal with the L6206)
        PA1 = motor input 2 (internal with the L6206)
    Encoder
        PC6 = encoder input A
        PC7 = encoder input B

Motor wire connections:
    Blue	    Encoder channel B
    Yellow	    Encoder channel A
    Red	        Encoder 5V supply (should be connected to the 3.3V output)
    Black	    Encoder ground
    Orange	    Motor power (for the motor B + connection on the L6206)
    Green	    Motor power (for the motor B - connection on the L6206)
    (None)	    No connection

@author Jack Krammer and Jason Chang
@date   20-Feb-2024
@copyright (c) 2024 by mecha04 and released under MIT License
'''

import pyb
import utime
import motor_driver
import encoder_reader
import proportional_controller as prop_control

PAUSE_MS = 10 # time in milliseconds to wait between proportional controller runs
SAMPLE_PERIOD_MS = 1000 # approximation of the time in milliseconds of the total sample time 
DATA_POINTS = SAMPLE_PERIOD_MS // PAUSE_MS # number of data points in the sample period

def main():
    '''!
    Runs the proportional controller, running closed-loop step-response tests in which the 
    setpoint is changed so as to rotate the motor by about one revolution and stop at its
    final position. The controller is run roughly every 10 milliseconds. The porportional
    controller is used to control a motor as the actuator and uses the motor encoder as the 
    sensor to detect motor position. The motor uses pins PC1 (enable pin), PA0 (motor input 
    1), and PA1 (motor input 2) with Timer 5 to control the PWM. The encoder uses PC6 and
    PC7 with Timer 8 to read position. 
    @param      None.
    @returns    None.
    '''
    # handle keyboard interrupts
    try:
        # indicate initializations
        print('Initializing motor driver, encoder reader, and proportional controller.')
        # create a motor driver object
        motor = motor_driver.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, timer=5)
        # create an encoder reader object
        encoder = encoder_reader.Encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, timer_num=8)
        # create a proportional controller object
        control = prop_control.ProportionalController(Kp=2,
                                                      setpoint=0,
                                                      actuate=motor.set_duty_cycle,
                                                      sense=encoder.read,
                                                      data_points=DATA_POINTS
                                                      )
        # initialize the destination setpoint for the proportional controller
        setpoint = 8150#10000
        # indicate done with initializations
        print('Done initializing.')

        # # initialize the actuation values 
        # vals = [] # for debugging

        # every 10 milliseconds run the proportional controller
        while True:
            # # reset the actuation values
            # vals = [] # for debugging 
            # stop actuating the motor
            motor.set_duty_cycle(0)
            # wait for user input for the Kp control gain value
            Kp_input = input('Input the desired float type Kp value (control gain value) for the next sample: \r\n') # need to include the \r\n so the ser.readline() will not be blocking
            # format the Kp value
            Kp_val = float(Kp_input)
            print(f'Running test using kp = {Kp_val}')
            # reset the encoder value so that the next sample period will run the same as the previous
            encoder.zero()
            # set the Kp value of the proportional controller
            control.set_Kp(Kp_val)
            # initialize a ticks_ms() time object for the start time of this run
            start_time = utime.ticks_ms()
            # run the proportional controller for the desired sample period
            for i in range(DATA_POINTS):
                # run the proportional controller
                # vals.append(control.run(setpoint, start_time)) # for debugging
                control.run(setpoint, start_time)
                # sleep for 10 milliseconds
                utime.sleep_ms(PAUSE_MS)
            # print the result of the sample period run
            control.print_data()
            # # print the actuation values
            # print(f'actuation values:\n{vals}\n') # for debugging 

    except ValueError:
        print(f'\nValueError: Incorrect input for Kp value. Input was "{Kp_input}". Should be a positive nonzero number. Exiting main.\n\n')
    except KeyboardInterrupt:
        print('\nExiting main due to a KeyboardInterrupt.\n\n')


# This main code is run if this file is the main program but won't run if this
# file is imported as a module by some other main program
if __name__ == '__main__':
    main()
