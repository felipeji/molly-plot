#!/usr/bin/env python3
from cmd2 import Cmd
import os
from ancillary import *
from plotting import main_plot


# Las siguiente dos lineas son para que no pete el MATPLOTLIB fuera de ANACONDA
import matplotlib
matplotlib.use("Qt5Agg")
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

        # ===================
        # Default values
        # =================

        # load
        self.fname = "spectrum"
        self.start_l = 1
        self.first_l = 1
        self.last_l = 1

        # offset
        self.offset = 0

        # vline
        self.vline = "off"

        # hline
        self.hline = "off"

        # axes
        self.x_units = "a"
        self.y_ax = "counts"
        self.doppler_rest = 6562.760  # Default Halpha

        # Hide command unused
        self.hidden_commands += ['alias', 'edit', 'history', 'macro', 'py',
                                 'run_pyscript', 'run_script', 'set', 'shell',
                                 'shortcuts']

    # ==============================================================================
    #  Load the spectra
    # ==============================================================================
    def do_load(self, inp):
        "Load .mol spectra into slots"

        # Set default values
        fname = self.fname
        start = self.start_l
        first = self.first_l
        last = self.last_l

        # Catching variables from terminal
        inps = inp.split()

        variables = {
            "fname": {"message": "File name [" + str(fname) + "]: ", "default": fname},
            "first": {
                "message": "First slot to read into [" + str(start) + "]: ",
                "default": first,
            },
            "last": {
                "message": "Last slot to read into [" + str(last) + "]: ",
                "default": last,
            },
            "start": {
                "message": "Start spectrum in file [" + str(start) + "]: ",
                "default": start,
            },
        }

        inputs = catch_inpunt(variables, inps)

        # Read imputs setting expected type (default are str)
        fname = inputs["fname"]
        # Check and fix extension
        if not (fname.endswith(".mol")):
            fname = fname + ".mol"

        first = int(inputs["first"])
        last = int(inputs["last"])
        start = int(inputs["start"])

        # Set global values
        self.fname = fname
        self.start_l = start
        self.first_l = first
        self.last_l = last

        # Load, read, and storage selected spectra into slots dictionary
        loader(fname, self.slots, first, last, start)

    # ==============================================================================
    # offset
    # ==============================================================================
    def do_offset(self, inp):

        # Set default values
        offset = self.offset

        inps = inp.split()
        variables = {
            "off": {
                "message": "Offset between spectra [" + str(offset) + "]: ",
                "default": offset,
            },
        }
        inputs = catch_inpunt(variables, inps)

        # Set global value
        self.offset = inputs["off"]

    # ==============================================================================
    # axes
    # ==============================================================================
    def do_axes(self, inp):
        inps = inp.split()
        variables = {
            "x_units": {"message": "X axis type [a]: ", "default": "a"},
            "y_ax": {"message": "Y axis type [counts]: ", "default": "counts"},
                    }
        inputs = catch_inpunt(variables, inps)
        self.x_units = inputs["x_units"]
        self.y_ax = inputs["y_ax"]

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
        # Set fancy name in the figure frame
        plt.figure("MOLLY-plot")

        # Slots selection

        inps = inp.split()
        plot_variables = {
            "first": {"message": "First slot to plot [1]: ", "default": 1},
            "last": {"message": "Last slot to plot [1]: ", "default": 1},
            "limits": {"message": "Enter plot limits (Left,Right, Bottom,Top): ","default": "0,0,0,0"},
                        }

        inputs = catch_inpunt(plot_variables, inps)

        # Asignamos los imputs a las variables y le damos el tipo esperado

        first = int(inputs["first"])
        last = int(inputs["last"])

        if first == 0 and last == 0:
            selection = pick()
        else:
            selection = np.arange(first, last + 1)  # range of selected slots

        limits = eval(inputs["limits"])

        # For km/s axes
        if self.x_units == "km/s":
            try:
                self.doppler_rest = float(input("Central wavelength [6562.760]: "))
            except:
                self.doppler_rest = 6562.760

        # Actual plot
        plt.figure("MOLLY-plot")

        # Dictionary with the selected slots to plot
        selected_slots = dict_slicer(self.slots, selection)
        main_plot(selected_slots, self.x_units, self.doppler_rest, self.offset, self.vline, self.hline,limits)

    def do_vline(self, inp):

        inps = inp.split()
        vline_variables = {
            "vline": {
                "message": "Plot a vertical line at [" + str(self.vline) + "]: ",
                "default": self.vline,
            },
        }
        self.vline = catch_inpunt(vline_variables, inps)["vline"]

    # ==============================================================================
    # hline
    # ==============================================================================
    def do_hline(self, inp):

        inps = inp.split()
        hline_variables = {
            "hline": {
                "message": "Plot a vertical line at [" + str(self.hline) + "]: ",
                "default": self.hline,
            },
        }
        self.hline = catch_inpunt(hline_variables, inps)["hline"]

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
