#!/usr/bin/env python3
from astropy import units as u 
from astropy.coordinates import SpectralCoord 
import numpy as np
from trm import molly
from cmd import Cmd
import os
import matplotlib.pyplot as plt
# Default matplotlib color list for iterating for ploting in loop
color = ['C0','C1','C2','C3','C4','C5','C6','C7','C8','C9'] 

from matplotlib import pylab
# Las siguiente dos lineas son para que no pete el MATPLOTLIB fuera de ANACONDA
import matplotlib
matplotlib.use('Qt4Agg')
#['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']

# Fuente tipo latex
#plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.ion()


print("# ==============================================================")
print("")
print(" #     #                            ######            ")          
print(" ##   ##  ####  #      #      #   # #     # #       ####  #####") 
print(" # # # # #    # #      #       # #  #     # #      #    #   #  ") 
print(" #  #  # #    # #      #        #   ######  #      #    #   #  ") 
print(" #     # #    # #      #        #   #       #      #    #   #  ") 
print(" #     # #    # #      #        #   #       #      #    #   #  ") 
print(" #     #  ####  ###### ######   #   #       ######  ####    #  ") 
print("")
print("# ==============================================================")

# alias mollyplot /Users/felipe/MollyPlot/molly-plot.py



#==============================================================================
# Ancillary functions                                                                 
#==============================================================================


def catch_inpunt(v_dict,inps):
    """
    Dada una lista de diccionario de varianles y una lista de imputs
    
    list = ["variable_name": {message: 'message to be printed', default: 1},
            "variable_name": {message: 'message to be printed', default: 1},
           ]
    The order in the list is important. Elements are readed in the list order
    """
    inputs = {}
    for index, v_name in enumerate(v_dict):
        message = v_dict[v_name]['message']
        default = v_dict[v_name]['default']
        try:
            inputs[v_name] = inps[index]
        except:
            inputs[v_name] = input(message) or default
    
    return inputs
        
    
    
    
def print_info(spect,slot):
    "Given a molly spec print the info in the way that molly does "
    obj = spect.head['Object']
    run = spect.head['Run']
    exp = spect.head['Dwell']
    # date
    d = "{:02d}".format(spect.head['Day'])
    m = "{:02d}".format(spect.head['Month'])
    y = str(spect.head['Year'])
    date = d+'/'+m+'/'+y
    # Time
    t = spect.head['UTC']
    h = int(t)
    m = (t*60) % 60
    s = (t*3600) % 60
    time = "%02d:%02d:%02d" % (h, m, s)
    print("   ",slot, ', obj: ',obj, ', run ',run , ' exp: ',exp , ' time: ',date, time)

      

# xa

    
def step_plot(spect,color,slot_n,x_ax,doppler_rest,off):
    "Plot routine"
    x_u = SpectralCoord(spect.wave * u.angstrom ) # X-axis with units

    ax = {'a':x_u.value,
          'km/s': x_u.to(u.km / u.s, doppler_convention='optical',doppler_rest=doppler_rest * u.angstrom).value,
          'p':  np.arange(len(x_u.value))+1}

    x = ax[x_ax]
    y = spect.f + off
    error = spect.fe

    
    plt.fill_between(x, y-error, y+error,color=color,step='mid',alpha=0.3,lw=0)
    plt.step(x,y, where='mid',lw = 0.8,color=color,label=str(slot_n))    

# Spectrum           90  skipped. Invalid format
# Entry finished
    
def merge(ranges):
    slots = []
    for r in ranges:
        for slot in range(r[0],r[1]+1):
            slots.append(slot)
    slots = np.unique(slots)
     
    return slots 


def pick():
    print("# ==========================")
    print(" Picking spectra to plot")
    print("# ==========================")
    list_inputs = []
    inp = None
    while inp != 'q' and inp != '0,0':
        inp = input('Enter series of slot ranges (0,0, for ending the selection): ')
        try:
           tpl = eval(inp)
           list_inputs.append(tpl)
                  
        except:
            pass
    print("  ***  Entry finished  ***")  
    selected = merge(list_inputs)
    return selected


    

        
    
    

   
#==============================================================================

 
class Plot(Cmd):
    prompt = 'molly-plot> '
    intro = "Welcome! Type ? to list commands"
    
    # This is the container dictionary for the espectra. Spectra are indexes 
    # with key following natural notation i.e. starting with 1
    spects = {}
    x_ax = 'a'
    y_ax = 'counts'
    doppler_rest = 6562.760
    offset = 0
#==============================================================================
# Comandos de  la terminal     
#==============================================================================
    def do_shell(self, line):
        "Run a shell command"
        output = os.popen(line).read()
        print(output)
        self.last_output = output

    #==============================================================================
    #  Load the spectra
    #==============================================================================
    def do_load(self, inp):
        "Load .mol spectra into slots"
        
        # Default values
        fname = ""
        start = 1
        first = 1
        last = 1 

        
        # Catching variables from terminal 
        inps = inp.split()
       
        load_variables = {"fname": {'message': 'File name [spectrum]: ', 'default': fname},
                          "first": {'message': 'First slot to read into [1]: ', 'default': first},
                          "last":  {'message': 'Last slot to read into [1]: ', 'default': last},
                          "start": {'message': 'Start spectrum in file [1]: ', 'default': start},
                          }    
                          
        inputs = catch_inpunt(load_variables,inps)                
                
        # Asignamos los imputs a las variables y le damos el tipo esperado    
        fname = inputs['fname']
        # Check and fix extension
        if not(fname.endswith('.mol')):
            fname = fname + '.mol'
        
        
        start = int(inputs['start'])
        first = int(inputs['first'])
        last = int(inputs['last']) 
        
        # Try reading the file
        try:
            spec = molly.rmolly(fname)[start-1:]
        except:
            print("Could not open "+fname)
            
        # Loading spec in the dictionary container 
        readed_spectra = 0           
        for index in range(last - first+1):
            try:
                slot_n = first + index
                self.spects[slot_n] = spec[index]
                # Print info in the molly way
                readed_spectra += 1
                print_info(self.spects[slot_n],slot_n)
            except:
                pass
        if readed_spectra != 0:
            print(" Read           "+str(readed_spectra)+"  spectra from "+fname)            
            
            
    #==============================================================================
    # Plot         
    #==============================================================================
    def do_plot(self, inp):

        inps = inp.split()
        plot_variables = {"first": {'message': 'First slot to plot [1]: ', 'default': 1},
                          "last": {'message': 'Last slot to plot [1]: ', 'default': 1},
                          "limits": {'message': 'Enter plot limits (Left,Right, Bottom,Top): ', 'default': '0,0,0,0'},
                          }    

        inputs = catch_inpunt(plot_variables,inps)                
        
        # Selection of the spectra        
        # Asignamos los imputs a las variables y le damos el tipo esperado    
        
        first = int(inputs['first'])
        last = int(inputs['last']) 
        
        if first == 0 and last == 0:
            selected_slots = pick()
        else:
            selected_slots = np.arange(first,last+1) # range of selected slots  
        
        
        limits = eval(inputs['limits']) 
        
        
        # For km/s axes
        if self.x_ax == 'km/s':
            try: 
               self.doppler_rest = float(input("Central wavelength [6562.760]: ")) 
            except:
                self.doppler_rest = 6562.760
        

        
        
        # =====================
        # Figure
        # =====================
        # Esta sera la figura donde se pinten los espectros        
        fig = pylab.gcf()                 
        fig.canvas.set_window_title('MOLLY-plot')

        plt.clf()

        for index, slot in enumerate(selected_slots):
            try:
                step_plot(self.spects[slot],color[slot%10],slot,self.x_ax,self.doppler_rest,off=index*self.offset)
                print_info(self.spects[slot],slot)
            except:
                print( "Spectrum           "+str(slot)+"  skipped. Invalid format")
  
        # Limits     
        l = limits[0]    
        r = limits[1]
        b = limits[2]
        t = limits[3]
        # x limitsx
        #section = (x >= l) & (x <= r)   
        if not(l == 0 and r == 0):
            #section[:]=True

            plt.xlim(l,r)
    
        if not(b == 0 and t == 0):
            plt.ylim(b,t)
    
        # Labels and legends
        x_label = {'a':'Wavelenght ($\AA$)',
                   'km/s': 'km/s',
                   'p':  'Pixel'}

        
        plt.xlabel(x_label[self.x_ax],size=15)   
        plt.ylabel('Counts',size=15)
        
        ncol = int(np.ceil(len(selected_slots)/25)) # 25 leyendas por culumna 
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small',ncol=ncol, title='Slots',handlelength=0.5,markerscale=4)


        plt.tight_layout()
        plt.draw()

    #==============================================================================
    # axes
    #==============================================================================
    #X axis type [a]: 
    #Y axis type [milli]: 
    def do_axes(self,inp):
        inps = inp.split()
        axes_variables = {"x_ax": {'message': 'X axis type [a]: ', 'default': 'a'},
                          "y_ax": {'message': 'Y axis type [counts]: ', 'default': 'counts'},
                          }    
        inputs = catch_inpunt(axes_variables,inps)                
        self.x_ax = inputs['x_ax']
        self.y_ax = inputs['y_ax']

    #==============================================================================
    # offset         
    #==============================================================================
    # Offset between spectra [ 0.000000    ]: 
    def do_offset(self,inp):
        inps = inp.split()
        off_variables = {"off": {'message': 'Offset between spectra [0.0]: ', 'default': 0},
                          }    
        inputs = catch_inpunt(off_variables,inps)                
        self.offset = float(inputs['off'])
    
        
        
    #==============================================================================
    # empty line method        
    #==============================================================================
    def emptyline(self):
         pass

    #==============================================================================
    # Exit routine         
    #==============================================================================
    def do_exit(first, inp):
        "Exit the application."
        print('Exiting application. Thanks for using MOLLY-plot')
        return True


Plot().cmdloop()














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


"""
  This program does nothing beyond access this help file which contains                             
  information such as wavelength of lines of various species and values                             
  of physical constants etc.                                                                        
                                                                                                    
  Wavelengths:                                                                                      
                                                                                                    
  HI                                                                                                
                                                                                                    
  Balmer series                                                                                     
                                                                                                    
  Halpha     6562.760       H11 3770.634                                                            
  Hbeta      4861.327       H12 3750.152                                                            
  Hgamma     4340.465       H13 3734.372                                                            
  Hdelta     4101.735       H14 3721.948                                                            
  Hepsilon   3970.074       H15 3711.971                                                            
  Hzeta (H8) 3889.055       H16 3703.853                                                            
  Heta  (H9) 3835.397       H17 3697.152                                                            
  H10        3797.910       H18 3691.555                                                            
                                                                                                    
  Paschen series                                                                                    
                                                                                                      
  Pbeta      12818.082       P13 8665.019                                                           
  Pgamma     10938.095       P14 8598.392                                                           
  Pdelta     10049.374       P15 8545.383                                                           
  Pepsilon    9545.972       P16 8502.483                                                           
  Pzeta (P9)  9229.015       P17 8467.254                                                           
  Peta  (P10  9014.911       P18 8437.995                                                           
  P11         8862.784       P19 8413.318                                                           
  P12         8750.473       P20 8392.397                                                           
                                                                                                    
  HeI                                                                                               
                                                                                                    
  3p-2s    5015.675     3d-2p    5875.618                                                           
  4p-2s    3964.727     4d-2p    4471.681                                                           
  5p-2s    3613.641     5d-2p    4026.189                                                           
  6p-2s    3447.590     6d-2p    3819.761                                                           
  7p-2s    3354.550     7d-2p    3705.003                                                           
  3d-2p    6678.149     3s-2p    7065.188                                                           
  4d-2p    4921.929     4s-2p    4713.20                                                            
  5d-2p    4387.928     5s-2p    4120.86                                                            
  6d-2p    4143.759     6s-2p    3867.53                                                            
  7d-2p    4009.270     7s-2p    3732.94                                                            
  3s-2p    7281.349              7816.16                                                            
  4s-2p    5047.736              9463.66                                                            
  5s-2p    4437.549              9516.70                                                            
  6s-2p    4168.967              9526.17                                                            
  2p-2s   10830.171              9702.66                                                            
  3p-2s    3888.646                                                                                 
                                                                                                    
                                                                                                    
  HeII                                                                                              
                                                                                                    
  3-2      1640.474      9-4     4541.7                                                             
  4-2      1215.171     10-4     4338.8                                                             
  4-3      4685.750     11-4     4199.9                                                             
  5-3      3203.14      12-4     4100.1                                                             
  6-3      2733.4       13-4     4025.7                                                             
  5-4     10123.77      14-4     3968.5                                                             
  6-4      6559.71      15-4     3923.6                                                             
  7-4      5411.551     16-4     3887.5                                                               
  8-4      4859.3                                                                                   
                                                                                                    
                                                                                                    
  NaI                                                                                               
                                                                                                    
  5889.95        6160.76                                                                            
  5895.92        8183.27                                                                            
  6154.23        8194.81                                                                            
                                                                                                    
                                                                                                    
  CaII                                                                                              
                                                                                                    
  3933.67  8498.02                                                                                  
  3968.47  8542.09                                                                                  
           8662.14                                                                                  
                                                                                                    
  FeII                                                                                              
                                                                                                    
     4923.92           5284.09           7222.39                                                    
     5018.44           5303.42           7224.51                                                    
     5030.78           5316.61           7307.97                                                    
     5136.79           5362.86           7320.70                                                    
     5169.03           5534.86           7462.38                                                    
     5197.59           6446.43           7711.73                                                    
     5275.99           6516.05                                                                      
                                                                                                    
                                                                                                    
  KI   -- 7664.91  7698.98                                                                          
  OIII -- 5006.9   4958.9   4363.2                                                                  
  NII  -- 6583.4   6548.1   5754.6                                                                  
  NI   -- 1199.551, 1200.226, 1200.708                                                              
          1492.624, 1492.824, 1494.673                                                              
  NV   -- 1238.800 1242.778                                                                         
  SiIV -- 1393.765 1402.764                                                                         
  CIV  -- 1548.195 1550.768                                                                         
                                                                                                    
  Astronomical quantities                                                                           
                                                                                                    
  1pc    = 3.085678E16 m                                                                            
  M(sun) = 1.989E30 kg                                                                                
  R(sun) = 6.9599E8 m                                                                               
  L(sun) = 3.826E26 W                                                                               
                                                                                                    
  Physical constants (SI units)                                                                     
                                                                                                    
  Speed of ligaht         c   = 2.997925E+8 m/s                                                     
  Gravitational constant  G   = 6.670E-11 N m**2 /kg**2                                             
  Planck's constant       h   = 6.626E-34 J s                                                       
  Charge on the electron  e   = 1.60219E-19 C                                                       
  Boltzmann's constant    k   = 1.38062E-23 J/K                                                     
  Avogadro's number       Na  = 6.02217E23                                                          
  Stefan's constant       Sig = 5.67E-8 J/m**2/K**4  

"""













