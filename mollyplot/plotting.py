import matplotlib.pyplot as plt
from astropy import units as u
from astropy.coordinates import SpectralCoord
from ancillary import short_header
import numpy as np


def main_plot(selected_slots, x_units, doppler_rest, offset, vline, hline, limits):
    """
    Main plot routine

    Parameters
    ----------
    selected_slots : dict
        Dictionary with the selected slots
    x_units : str
        Units of the X-axis
    doppler_rest :
    offset :
    vline :
    hline :

    Returns
    -------

    """
    # Default matplotlib color list for plotting in loop
    colors = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]

    # Clear previous plot
    plt.clf()

    for index, slot in enumerate(selected_slots):
        try:
            offset = index * float(offset)
            color = colors[slot % 10]
            slot_plot(selected_slots[slot],slot, offset, x_units, color, doppler_rest)
            short_header(selected_slots[slot], slot)
        except:
            print("Spectrum           " + str(slot) + "  skipped. Invalid format")

    # Plot vline
    if vline != "off":
        plt.axvline(float(vline), color="k", ls="dashed")
    # Plot hline
    if hline != "off":
        plt.axhline(float(hline), color="k", ls="dashed")

    # Limits
    l = limits[0]
    r = limits[1]
    b = limits[2]
    t = limits[3]

    # x-limits
    if not (l == 0 and r == 0):
        plt.xlim(l, r)

    if not (b == 0 and t == 0):
        plt.ylim(b, t)

    # Labels
    x_label = {"a": "Wavelenght ($\AA$)", "km/s": "km/s", "p": "Pixel"}

    plt.xlabel(x_label[x_units], size=15)
    plt.ylabel("Counts", size=15)

    # Legends
    ncol = int(np.ceil(len(selected_slots) / 25))  # 25 leyendas por culumna
    plt.legend(bbox_to_anchor=(1.05, 1),
                loc="upper left",
                fontsize="small",
                ncol=ncol,
                title="Slots",
                handlelength=0.5,
                markerscale=4,
                )
    plt.tight_layout()
    plt.draw()


def slot_plot(slot,number,offset,x_units, color, doppler_rest):
    """
    This function plot a single slot spectra.

    Parameters
    ----------
    slot : trm.molly.molly.Molly
        Molly object containing the spectrum

    offset : float
        Offset introduced in the Y-axis

    x_units : str
        Units of the X-asis

    color : str
        Color of the spectrun to plot.

    doppler_rest : float
        Central wavelength in the km/s representation.

    Returns
    -------
        Step plot of the spectrum and its corresponding error.
    """
    # X-axis units (default in Angstrom)
    x_angs = SpectralCoord(slot.wave * u.angstrom)

    units_dict = { "a": x_angs.value,
                   "km/s": x_angs.to(u.km / u.s,doppler_convention="optical",doppler_rest=doppler_rest * u.angstrom).value,
                   "p": np.arange(len(x_angs.value)) + 1,
                  }

    # Read spectrum from slot
    x = units_dict[x_units]
    y = slot.f + offset
    error = slot.fe

    # Plot spectrum and error
    plt.fill_between(x, y - error, y + error, color=color, step="mid", alpha=0.3, lw=0)
    plt.step(x, y, where="mid", lw=0.8, color=color, label=number)



















