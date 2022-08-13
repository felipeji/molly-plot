#!/usr/bin/env python3
from astropy import units as u 
from astropy.coordinates import SpectralCoord 
import numpy as np
from trm import molly
from cmd import Cmd
import os
import matplotlib.pyplot as plt
# Default matplotlib color list for ploting in loop
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
        
    
    
    
def short_header(spect,slot):
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

    
def main_plot(spect,color,slot_n,x_ax,doppler_rest,offset):
    "Plot routine"
    x_u = SpectralCoord(spect.wave * u.angstrom ) # X-axis with units

    ax = {'a':x_u.value,
          'km/s': x_u.to(u.km / u.s, doppler_convention='optical',doppler_rest=doppler_rest * u.angstrom).value,
          'p':  np.arange(len(x_u.value))+1}

    x = ax[x_ax]
    y = spect.f + offset
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
    print("  ***  Entry finished  ***\n")  
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
        print(output.strip('\n'))
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
                # Print short header info
                readed_spectra += 1
                short_header(self.spects[slot_n],slot_n)
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
                main_plot(self.spects[slot],color[slot%10],slot,self.x_ax,self.doppler_rest,offset=index*self.offset)
                short_header(self.spects[slot],slot)
            except:
                print( "Spectrum           "+str(slot)+"  skipped. Invalid format")
  
        # Limits     
        l = limits[0]    
        r = limits[1]
        b = limits[2]
        t = limits[3]
        
        # x limits
        if not(l == 0 and r == 0):
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
    



    # #==============================================================================
    # # vlines         
    # #==============================================================================
    # def do_vlines(self,inp):
    #     inps = inp.split()
    #     vlines_variables = {"vlines": {'message': 'Plot a vertical line at [0.0]: ', 'default': 0},
    #                       }    
    #     pos = catch_inpunt(vlines_variables,inps)['vlines']                
    #     plt.axvline(pos,color='k',ls='dashed')


    # #==============================================================================
    # # hlines      
    # #==============================================================================
    # def do_hlines(self,inp):
    #     inps = inp.split()
    #     hline_variables = {"hline": {'message': 'Plot an horizontal line at [0.0]: ', 'default': 0},
    #                       }    
    #     pos = catch_inpunt(hline_variables,inps)['hline']                
    #     plt.axhline(pos,color='k',ls='dashed')


        
    
    # =============================================================================
    # INFO         
    # =============================================================================

    def do_info(self, inp):
        info_file_path = os.path.dirname(__file__) + "/info.txt"
        inp = ''
        index = 0
        line = 0
        
        while inp != 'q' and line != '' :
            f = open(info_file_path, "r")
            chunk = f.readlines()[25*index:(25*index)+25]
            for line in chunk:
                line = line.strip('\n')
                print(line)
            f.close()
            
            inp =  input("Enter for more, q for quit:")
            index += 1 

        


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














