import numpy as np
import cmd2
from trm.molly import rmolly



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
    """
    Load .mol file into slots dictionary following natural notation (i.e. starting with 1)

    Parameters
    ----------
    fname : str
        .mol file name

    slots : dict
        Container dictionary

    first : int
        First slot to read into

    last : int
        Last slot to read into

    start : int
        Start spectrum in file.

    Returns
    -------
    slots dictionary with the readed spectrum.

    """
    try:
        readed = rmolly(fname)[start - 1:]
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
    print("   ", slot, ", obj: ", obj, ", run ", run, " exp: ", exp, " time: ", date, time)


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
# Class for using abbreviations. We should NOT use it in the future
# =============================================================================
class AbbrevMixin:
    """A cmd2 plugin (mixin class) which adds support for abbreviated commands."""

    def __init__(self, *args, **kwargs):
        """Initialize this plugin."""
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



def dict_slicer(dictionary,key_list):
    sliced_dict = {}
    for key in key_list:
        sliced_dict[key] = dictionary[key]
    return sliced_dict