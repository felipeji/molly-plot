#!/usr/bin/env python3
from astropy import units as u
from astropy.coordinates import SpectralCoord
import numpy as np
from trm.molly import rmolly 
import cmd2

import os

# Default matplotlib color list for ploting in loop
import matplotlib.pyplot as plt
# Fuente tipo latex
# plt.rc('text', usetex=True)
plt.rc("font", family="serif")
plt.ion()

color = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]



# Las siguiente dos lineas son para que no pete el MATPLOTLIB fuera de ANACONDA
import matplotlib
matplotlib.use("Qt5Agg")
# ['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo', 'Qt5Agg',
# 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg',
#'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']




"""
# =============================================================================
# Installation neededs
# =============================================================================

conda create --name molly-plot python=3.8
conda install astropy=5
conda install -c conda-forge cmd2

# Install trm

pip install git+https://github.com/WarwickAstro/trm-molly.git#egg=trm-molly


"""







print("# ==================================================================")
print("")
print(" #     #                                 ######            ")
print(" ##   ##  ####  #      #      #   #      #     # #       ####  #####")
print(" # # # # #    # #      #       # #       #     # #      #    #   #  ")
print(" #  #  # #    # #      #        #   ###  ######  #      #    #   #  ")
print(" #     # #    # #      #        #        #       #      #    #   #  ")
print(" #     # #    # #      #        #        #       #      #    #   #  ")
print(" #     #  ####  ###### ######   #        #       ######  ####    #  ")
print("")
print("# ==================================================================")

# alias mplot /Users/felipe/MollyPlot/molly-plot.py


# ==============================================================================
# Ancillary functions
# ==============================================================================


def catch_inpunt(v_dict, inps):
    """
    Dada una lista de diccionario de variables y una lista de imputs
    
    list = ["variable_name": {message: 'message to be printed', default: 1},
            "variable_name": {message: 'message to be printed', default: 1},
           ]
    The order in the list is important. Elements are readed in the list order
    """
    inputs = {}
    for index, v_name in enumerate(v_dict):
        message = v_dict[v_name]["message"]
        default = v_dict[v_name]["default"]
        try:
            inputs[v_name] = inps[index]
        except:
            inputs[v_name] = input(message) or default

    return inputs


def loader(fname, slots, first, last, start):
    # Try reading the file
    try:
        readed = rmolly(fname)[start - 1 :]
    except:
        print("Could not open " + fname)

    # Loading spec in the dictionary container
    readed_spectra = 0
    for index in range(last - first + 1):
        # try for prevent an error when reading empty slots
        try:
            slot_n = first + index
            slots[slot_n] = readed[index]
            # Print short header info
            readed_spectra += 1
            short_header(slots[slot_n], slot_n)
        except:
            pass
    if readed_spectra != 0:
        print(" Read           " + str(readed_spectra) + "  spectra from " + fname)


def short_header(spect, slot):
    "Print shor header in the MOLLY style "
    obj = spect.head["Object"]
    run = spect.head["Run"]
    exp = spect.head["Dwell"]
    # date
    d = "{:02d}".format(spect.head["Day"])
    m = "{:02d}".format(spect.head["Month"])
    y = str(spect.head["Year"])
    date = d + "/" + m + "/" + y
    # Time
    t = spect.head["UTC"]
    h = int(t)
    m = (t * 60) % 60
    s = (t * 3600) % 60
    time = "%02d:%02d:%02d" % (h, m, s)
    print(
        "   ", slot, ", obj: ", obj, ", run ", run, " exp: ", exp, " time: ", date, time
    )


# xa


def main_plot(spect, color, slot_n, x_ax, doppler_rest, offset, vline, hline):
    "Main Plot routine"
    x_u = SpectralCoord(spect.wave * u.angstrom)  # X-axis with units

    ax = {
        "a": x_u.value,
        "km/s": x_u.to(
            u.km / u.s,
            doppler_convention="optical",
            doppler_rest=doppler_rest * u.angstrom,
        ).value,
        "p": np.arange(len(x_u.value)) + 1,
    }

    x = ax[x_ax]
    y = spect.f + offset
    error = spect.fe

    plt.fill_between(x, y - error, y + error, color=color, step="mid", alpha=0.3, lw=0)
    plt.step(x, y, where="mid", lw=0.8, color=color, label=str(slot_n))

    # Plot vline
    if vline != "off":
        plt.axvline(float(vline), color="k", ls="dashed")
    # Plot hline
    if hline != "off":
        plt.axhline(float(hline), color="k", ls="dashed")


def merge(ranges):
    slots = []
    for r in ranges:
        for slot in range(r[0], r[1] + 1):
            slots.append(slot)
    slots = np.unique(slots)

    return slots


def pick():
    "Roting for picking spectra"
    print("# ==========================")
    print(" Picking spectra to plot")
    print("# ==========================")
    list_inputs = []
    inp = None
    while inp != "q" and inp != "0,0":
        inp = input("Enter series of slot ranges (0,0, for ending the selection): ")
        try:
            tpl = eval(inp)
            list_inputs.append(tpl)

        except:
            pass
    print("  ***  Entry finished  ***\n")
    selected = merge(list_inputs)
    return selected


# =============================================================================
# Class for using abbreviations. We should NOT used it in the future
# =============================================================================
class AbbrevMixin:
    """A cmd2 plugin (mixin class) which adds support for abbreviated commands."""

    def __init__(self, *args, **kwargs):
        "Initialize this plugin."
        # code placed here runs before cmd2 initializes
        super().__init__(*args, **kwargs)
        # code placed here runs after cmd2 initializes
        # this is where you register any hook functions
        self.add_settable(
            cmd2.Settable("abbrev", bool, "Accept command abbreviations", self)
        )
        self.register_postparsing_hook(self.cmd2_abbrev_hook)

    def cmd2_abbrev_hook(
        self, data: cmd2.plugin.PostparsingData
    ) -> cmd2.plugin.PostparsingData:
        """Postparsing hook which interprets abbreviated command names."""
        target = "do_" + data.statement.command
        if target not in dir(self):
            # check if the entered command might be an abbreviation
            cmds = self.get_all_commands()
            funcs = [func for func in cmds if func.startswith(data.statement.command)]
            if len(funcs) == 1:
                raw = data.statement.raw.replace(data.statement.command, funcs[0], 1)
                data.statement = self.statement_parser.parse(raw)
        return data


# ==============================================================================


class CLI(AbbrevMixin, cmd2.Cmd):
    # Path autocomplete
    complete_load = cmd2.Cmd.path_complete

    # Intro
    prompt = "molly-plot> "
    intro = "Welcome! Type ? to list commands"

    def __init__(self):
        super().__init__()

        # This is the container dictionary for the espectra. Spectra are indexes
        # with key following natural notation i.e. starting with 1
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
        self.x_ax = "a"
        self.y_ax = "counts"
        self.doppler_rest = 6562.760  # Halpha
        
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
            "x_ax": {"message": "X axis type [a]: ", "default": "a"},
            "y_ax": {"message": "Y axis type [counts]: ", "default": "counts"},
        }
        inputs = catch_inpunt(variables, inps)
        self.x_ax = inputs["x_ax"]
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

        inps = inp.split()
        plot_variables = {
            "first": {"message": "First slot to plot [1]: ", "default": 1},
            "last": {"message": "Last slot to plot [1]: ", "default": 1},
            "limits": {
                "message": "Enter plot limits (Left,Right, Bottom,Top): ",
                "default": "0,0,0,0",
            },
        }

        inputs = catch_inpunt(plot_variables, inps)

        # Selection of the spectra
        # Asignamos los imputs a las variables y le damos el tipo esperado

        first = int(inputs["first"])
        last = int(inputs["last"])

        if first == 0 and last == 0:
            selected_slots = pick()
        else:
            selected_slots = np.arange(first, last + 1)  # range of selected slots

        limits = eval(inputs["limits"])

        # For km/s axes
        if self.x_ax == "km/s":
            try:
                self.doppler_rest = float(input("Central wavelength [6562.760]: "))
            except:
                self.doppler_rest = 6562.760

        # =====================================================================
        # Figure
        # =====================================================================
        plt.figure("MOLLY-plot")

        plt.clf()

        for index, slot in enumerate(selected_slots):
            try:
                main_plot(
                    self.slots[slot],
                    color[slot % 10],
                    slot,
                    self.x_ax,
                    self.doppler_rest,
                    offset=index * float(self.offset),
                    vline=self.vline,
                    hline=self.hline,
                )

                short_header(self.slots[slot], slot)
            except:
                print("Spectrum           " + str(slot) + "  skipped. Invalid format")

        # Limits
        l = limits[0]
        r = limits[1]
        b = limits[2]
        t = limits[3]

        # x limits
        if not (l == 0 and r == 0):
            plt.xlim(l, r)

        if not (b == 0 and t == 0):
            plt.ylim(b, t)

        # Labels
        x_label = {"a": "Wavelenght ($\AA$)", "km/s": "km/s", "p": "Pixel"}

        plt.xlabel(x_label[self.x_ax], size=15)
        plt.ylabel("Counts", size=15)

        # Legends
        ncol = int(np.ceil(len(selected_slots) / 25))  # 25 leyendas por culumna
        plt.legend(
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
            fontsize="small",
            ncol=ncol,
            title="Slots",
            handlelength=0.5,
            markerscale=4,
        )

        plt.tight_layout()
        plt.draw()

    # ==============================================================================
    # vline
    # ==============================================================================
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
            chunk = f.readlines()[25 * index : (25 * index) + 25]
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
