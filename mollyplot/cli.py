#!/usr/bin/env python3
from cmd2 import Cmd
import os
from .ancillary import *
from .plotting import main_plot


# Las siguiente dos lineas son para que no pete el MATPLOTLIB fuera de ANACONDA
import matplotlib
matplotlib.use("TkAgg")
# ['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo', 'Qt5Agg',
# 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg',
# 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']

import matplotlib.pyplot as plt
plt.rc("font", family="serif")
plt.ion()


print("# ==================================================================")
print(" #     #                                 ######            ")
print(" ##   ##  ####  #      #      #   #      #     # #       ####  #####")
print(" # # # # #    # #      #       # #       #     # #      #    #   #  ")
print(" #  #  # #    # #      #        #   ###  ######  #      #    #   #  ")
print(" #     # #    # #      #        #        #       #      #    #   #  ")
print(" #     #  ####  ###### ######   #        #       ######  ####    #  ")
print("# ==================================================================")


# ==============================================================================

class CLI(AbbrevMixin, Cmd):
    # Path autocomplete
    complete_load = Cmd.path_complete

    # Intro
    prompt = "molly-plot> "
    intro = "Welcome! Type ? to list commands"

    def __init__(self):
        super().__init__()

        # This is the container dictionary for the espectra. Spectra are indexes
        # with key following natural notation (i.e. starting with 1).
        self.slots = {}

        # Diccionario con los mesages a mostrar por cada variable

        self.messages = {}

        # ===================
        # Default values
        # =================

        # load
        self.fname = "spectrum"
        self.first_l = 1
        self.last_l = 1
        self.start_l = 1
        # messages
        self.messages['load'] = [
            "File name",
            "First slot to read into",
            "Last slot to read into",
            "Start spectrum in file",
            ]

        # offset
        self.offset = 0
        # messages
        self.messages['offset'] = ["Offset between spectra"]

        # plot
        self.first = 1
        self.last = 1
        self.limits = "0,0,0,0"
        # messages
        self.messages['plot'] = [
            "First slot to plot",
            "Last slot to plot",
            "Enter plot limits (Left,Right, Bottom,Top)"
            ]


        # vline
        self.vline = "off"
        # messages
        self.messages['vline'] = ["Plot a vertical line at"]

        # hline
        self.hline = "off"
        # messages
        self.messages['hline'] = ["Plot a vertical line at"]


        # axes
        self.x_units = "a"
        self.y_ax = "counts"
        self.doppler_rest = 6562.760  # Default Halpha
        # messages
        self.messages['axes'] = [
            "X axis type",
            "Y axis type"
            ]


        # Hide command unused
        self.hidden_commands += ['alias', 'edit', 'history', 'macro', 'py',
                                 'run_pyscript', 'run_script', 'set', 'shell',
                                 'shortcuts']

    # ==============================================================================
    #  Load the spectra
    # ==============================================================================
    def do_load(self,inp):
        inps = inp.split()

        self.fname, self.first_l, self.last_l, start_l = catch_input([self.fname, self.first_l, self.last_l, self.start_l],
                                                                     self.messages['load'],
                                                                     inps)

        # Load, read, and storage selected spectra into slots dictionary
        loader(self.fname, self.slots, self.first_l, self.last_l, self.start_l)

    # ==============================================================================
    # offset
    # ==============================================================================
    def do_offset(self, inp):
        inps = inp.split()
        self.offset = catch_input([self.offset], self.messages['offset'], inps)[0]

    # ==============================================================================
    # axes
    # ==============================================================================
    def do_axes(self, inp):
        inps = inp.split()
        self.x_units, self.y_ax =  catch_input([self.x_units, self.y_ax], self.messages['axes'], inps)

        """
        molly> axes 9
        Invalid type = 9               
        Possible types are:

            PIXELS                                                          
            ANGSTROMS                                                       
            MICRONS                                                         
            NANNOMETRES                                                     
            KM/S                                                            

        Error translating command
        molly> axes
        X axis type [a]: 
            Y axis type [milli]: 8
                Invalid type = 8               
                Possible types are:
                    
                    COUNTS                                                          
                    MILLIJANSKYS                                                    
                    FLAMBDA                                                         
                    AB                                                              
                    RESPONSE                                                        
                    EFFICIENCY                                                      
                    Error translating command
        """

    # ==============================================================================
    # Plot
    # ==============================================================================
    def do_plot(self, inp):
        inps = inp.split()

        self.first, self.last, self.limits = catch_input([self.first, self.last, self.limits],
                                                         self.messages['plot'],
                                                         inps)
        # Enter picking mode
        if self.first == 0 and self.last == 0:
            selection = pick()
        else:
            selection = np.arange(self.first, self.last + 1)  # range of selected slots



        # For km/s axes
        if self.x_units == "km/s":
            try:
                self.doppler_rest = float(input("Central wavelength [6562.760]: "))
            except:
                self.doppler_rest = 6562.760

        # Dictionary with the selected slots to plot
        selected_slots = dict_slicer(self.slots, selection)
        # mMin plot
        limits = eval(self.limits)
        main_plot(selected_slots, self.x_units, self.doppler_rest, self.offset, self.vline, self.hline,limits)

    # ==============================================================================
    # vline
    # ==============================================================================
    def do_vline(self, inp):
        inps = inp.split()
        self.vline = catch_input([self.vline], self.messages['vline'], inps)[0]

    # ==============================================================================
    # hline
    # ==============================================================================
    def do_hline(self, inp):
        inps = inp.split()
        self.hline = catch_input([self.hline], self.messages['hline'], inps)[0]

    # =============================================================================
    # INFO
    # =============================================================================

    def do_info(self, inp):
        info_file_path = os.path.dirname(__file__) + "/data/info.txt"
        inp = ""
        index = 0
        line = 0

        while inp != "q" and line != "":
            f = open(info_file_path, "r")
            chunk = f.readlines()[25 * index: (25 * index) + 25]
            for line in chunk:
                line = line.strip("\n")
                print(line)
            f.close()

            inp = input("Enter for more, q for quit:")
            index += 1

    # ==============================================================================
    # empty line method
    # ==============================================================================
    def emptyline(self):
        pass


"""
 AXES Xaxis Yaxis -- Sets axes for spectrum plots.

 Parameters:
            
     XAXIS -- Xaxis type. Choices are:

         pixels       -- pixel scale (always possible)
         angstroms    -- angstrom wavelength scale (needs wavelength cal)
         microns      -- micron wavelength scale (needs wavelength cal)
         nannometres  -- nannometre wavelength scale (needs wavelength cal)
         km/s         -- Velocity scale in km/s. Will be prompted for a
                         central wavelength when plotting. Needs
                         wavelength cal

     YAXIS -- Yaxis type. Choices are:

         counts       -- raw counts
         millijanskys -- flux density in millijanskys 
                         1 mJy = 10**-26 W/m**2/Hz = 10**-26 ergs/s/cm**2/Hz
                         1 mJy = 16.4 on AB mag scale of Oke, roughly
                                 matches V mag.
         flambda      -- flux in ergs/s/cm**2/A
         AB           -- AB mags = 16.4 - 2.5 LOG10(f/1mJy)
         response     -- Measures reponse of detector etc as AB mag needed
                         to get 1 count/sec/A. Plot allows you to correct
                         this to zero airmass if need be.
         efficiency   -- linearised version of rsponse which allows you
                         to include telescope aperture to get fraction of
                         photons detected. Again can be corrected for

"""
