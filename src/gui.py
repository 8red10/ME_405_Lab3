'''!
@file gui.py
    This file contains code to run the GUI for the step response of the proportional
    controller with the motor as actuator and encoder as sensor. GUI also includes 
    the feature to input the desired control gain used for the proportional controller.
    If no value is input, the default value of 0.01 is used. The GUI is intended to 
    communicate with the STM32 Nucleo L476RG board over serial port 
    /dev/tty.usbmodem2055377C39472 at a baud rate of 115200. These values are included
    in as global variables at the top of this file for ease of use with varying 
    configurations. Data from the motor is expected to be sent to this file by printing 
    data in CSV format as time,position. Other information read over serial is 
    discarded. Some debugging information is kept to better inform the user. 

@author Jack Krammer and Jason Chang
@date   20-Feb-2024
@copyright (c) 2024 by mecha04 and released under MIT License
'''

import math
import time
import tkinter
from random import random
from serial import Serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

PORT_NAME = '/dev/tty.usbmodem2055377C39472'
BAUD_RATE = 115200
DEFAULT_KP = 0.01

# TODO:
#
#   make it so that the plot can get the kp value and it can be an input to the get_data() function ---- DONE
#
#   check that the bytearray object will have the number be correctly sent (check with numbers that require more than one byte) --- DONE
#
#   check that the kp value goes through correctly --- DONE
# 
#   check the lab 3 requirements
#
#   update / commit all git repositories
#
#   put motor and encoder files into lab3/src

def get_data(kp):
    '''!
    Opens the serial port to read data from the connected Nucleo's main file. First, ends the current 
    main function and reboots the Nucleo. From here, reads the xdata,ydata pairs until the terminating 
    string is read. Lines of information that is not in the proper format, or isn't data is discarded.
    Lastly, this function returns the x and y data as a tuple (x_data_array, y_data_array). 
    @param      kp -> A positive nonzero number (integer or float) to use as the kp value for the 
                step response. 
    @returns    A tuple of the x data array and y data array in the format (x_data_array, y_data_array).
    '''
    print(f'starting to get data')
    # initialize the x and y data arrays
    xdata = []
    ydata = []

    # open the serial port
    with Serial(PORT_NAME, BAUD_RATE) as ser:
        # flush all serial output on this port
        ser.reset_output_buffer()
        # stop the current running program
        ser.write(b'\x03')
        # flush all serial input on this port
        ser.reset_input_buffer()
        # put microcontroller in regular REPL mode and reboot microcontroller
        ser.write(b'\x02\x04')
        
        # initialize the terminating string
        term_str = 'End'
        # waiting for input string
        input_str = 'Input the desired float type Kp value (control gain value) for the next sample:'
        # initialize the line read from serial
        data_str = ''
        # initialize the input kp value as bytes to send over serial
        kp_str = (str(kp))
        kp_bytes = bytearray()
        kp_bytes.extend(kp_str.encode('ascii'))

        # read lines from port until 'End'
        while term_str != data_str:
            # read a line from serial
            line = ser.readline()
            # print(f'line read from serial: {line}') # for debugging
            # get the data from this line
            data_str = (line[:-2]).decode('ascii')

            # check if the line read is asking for the input Kp value
            if data_str.strip() == input_str:
                # ser.write(b'\x02') # put microcontroller in regular REPL mode
                ser.write(kp_bytes)
                ser.write(b'\r\n')
            
            # otherwise, parse the input like normal
            else:
                data = data_str.split(',')
                # check that there is at least two columns 
                if len(data) >= 2:
                    # try to convert data to a float, if error then ignore that line
                    try:
                        x = float((data[0]).strip())
                        y = float((data[1]).strip())
                        xdata.append(x)
                        ydata.append(y)
                    except:
                        print(f'was not able to convert col 0 = "{(data[0]).strip()}" or col 1 = "{(data[1]).strip()}" to float')
                else:
                    print(f'not enough columns of data from line = "{data_str.strip()}"')
        # end while 
        # stop the current running program
        ser.write(b'\x03')
    # end serial
    
    # indicate done reading data
    print(f'reached the terminating string "{term_str}", done reading data.')
    # print the data read
    print(f'data read from controller:')
    for i in range(len(xdata)):
        print(f'{xdata[i]},{ydata[i]}')
    print(f'done printing data read from serial port "{PORT_NAME}" at baud rate "{BAUD_RATE}"\n')
    
    # return the tuple of xdata and ydata arrays
    return (xdata,ydata)


def plot_example(plot_axes, plot_canvas, xlabel, ylabel, get_data_input=DEFAULT_KP):
    '''!
    Gets data from the connected Nucleo over serial. The main function in the 
    connected Nucleo should print the data in the format xdata,ydata. All other
    information printed in different formats will be discarded. Then plots the 
    data into a GUI. The data should be the step response of a a proportional
    controller loop when a motor is set to a certain position and the position
    is read from the encoder reader.
    @param      plot_axes -> The plot axes supplied by Matplotlib.
    @param      plot_canvas -> The plot canvas, also supplied by Matplotlib.
    @param      xlabel -> The label for the plot's horizontal axis.
    @param      ylabel -> The label for the plot's vertical axis.
    @param      get_data_input -> A parameter to pass to the get_data() function 
                that gets the data over serial from the connected Nucleo.
    @returns    None.
    '''
    # get the data printed as a result of the main function
    xdata, ydata = get_data(get_data_input)

    # Draw the plot. Of course, the axes must be labeled. A grid is optional
    plot_axes.plot(xdata, ydata)
    plot_axes.set_xlabel(xlabel)
    plot_axes.set_ylabel(ylabel)
    plot_axes.grid(True)
    plot_canvas.draw()

def get_kp_value_input(tk_entry):
    '''!
    Gets the Kp value from the field in the GUI. Returns the value if it is a positive 
    nonzero number. Otherwise, returns the default Kp value.
    @param      tk_entry -> A Tkinter Entry object that the .get() function is applied to
                to get the value in the field.
    @returns    The input value if the input was a positive nonzero number. Otherwise, 
                returns the default Kp value.
    '''
    # get the value in the entry box
    val = tk_entry.get() # the entry will initially be a string

    # try to convert the value to a float
    try:
        # convert string entered into a float
        num_val = float(val)
        # check if the value is greater than zero
        if num_val > 0:
            # return the positive nonzero number entered
            return num_val
        # otherwise, have zero or a negative number
        else:
            # return the default kp value
            return DEFAULT_KP
    # some error happened
    except:
        # return the default kp value
        return DEFAULT_KP
    

def tk_matplot(plot_function, xlabel, ylabel, title):
    '''!
    Create a TK window with one embedded Matplotlib plot.
    This function makes the window, displays it, and runs the user interface
    until the user closes the window. The plot function, which must have been
    supplied by the user, should draw the plot on the supplied plot axes and
    call the draw() function belonging to the plot canvas to show the plot. 
    @param      plot_function -> The function which, when run, creates a plot.
    @param      xlabel -> The label for the plot's horizontal axis.
    @param      ylabel -> The label for the plot's vertical axis.
    @param      title -> A title for the plot; it shows up in window title bar.
    @returns    None.
    '''
    # Create the main program window and give it a title
    tk_root = tkinter.Tk()
    tk_root.wm_title(title)

    # Create a Matplotlib 
    fig = Figure()
    axes = fig.add_subplot()

    # Create the drawing canvas and a handy plot navigation toolbar
    canvas = FigureCanvasTkAgg(fig, master=tk_root)
    toolbar = NavigationToolbar2Tk(canvas, tk_root, pack_toolbar=False)
    toolbar.update()

    # create the label, entry, and button to get the Kp value
    label_kp_help   = tkinter.Label(master=tk_root,
                                    text="recommended Kp = 0.06 (no load) OR 0.05 (flywheel)")
    label_kp        = tkinter.Label(master=tk_root,
                                    text="^input kp value above")
    entry_kp        = tkinter.Entry(master=tk_root)
    button_kp       = tkinter.Button(master=tk_root,
                                     text="<-- Submit Kp Value and Run Test",
                                     command=lambda: plot_function(axes, canvas,
                                                             xlabel, ylabel,
                                                             get_kp_value_input(entry_kp)))

    # Create the buttons that run tests, clear the screen, and exit the program
    button_quit = tkinter.Button(master=tk_root,
                                 text="Quit",
                                 command=tk_root.destroy)
    button_clear = tkinter.Button(master=tk_root,
                                  text="Clear",
                                  command=lambda: axes.clear() or canvas.draw())
    button_run = tkinter.Button(master=tk_root,
                                text="Run Test",
                                command=lambda: plot_function(axes, canvas,
                                                              xlabel, ylabel))

    # Arrange things in a grid because "pack" is weird
    canvas.get_tk_widget().grid(row=0, column=0, columnspan=3)
    toolbar.grid(row=1, column=0, columnspan=3)
    button_run.grid(row=2, column=0)
    button_clear.grid(row=2, column=1)
    button_quit.grid(row=2, column=2)
    # arrange kp entry, button, and label
    entry_kp.grid(row=3, column=0)
    button_kp.grid(row=3, column=1)
    label_kp.grid(row=4, column=0)
    label_kp_help.grid(row=4, column=1)

    # This function runs the program until the user decides to quit
    tkinter.mainloop()


def main():
    '''!
    This function runs when this python file is ran as a main file. 
    @param      None.
    @returns    None.
    '''
    tk_matplot(plot_example,
               xlabel="Time (ms)",
               ylabel="Position (encoder ticks)",
               title="ME 405 Lab 3 Step Response Plots")


# This main code is run if this file is the main program but won't run if this
# file is imported as a module by some other main program
if __name__ == "__main__":
    main()

