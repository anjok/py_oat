import sys
import os

from pysiril.siril   import *
from pysiril.wrapper import *

#What should happen, given:
# Light/ISO_Xsec
# Dark/ISO_Xsec
# Flat/ISO_Xsec
# Bias/
# 1) sort Light/Dark/Flat into folders by secs
# 2) process each folder according to type

# ==============================================================================
# EXAMPLE OSC_Processing with functions wrapper
# ==============================================================================

#1. defining command blocks for creating masters and processing lights
def master_bias(bias_dir, name, process_dir):
    cmd.cd(bias_dir )
    cmd.convert( 'bias', out=process_dir, fitseq=True )
    cmd.cd( process_dir )
    cmd.stack( 'bias', type='rej', sigma_low=3, sigma_high=3, norm='no')
    
def master_flat(flat_dir, name, process_dir):
    cmd.cd(flat_dir )
    cmd.convert( f"flat{name}", out=process_dir, fitseq=True )
    cmd.cd( process_dir )
    cmd.preprocess( f"flat{name}", bias='bias_stacked' )
    cmd.stack( f"pp_flat{name}" type='rej', sigma_low=3, sigma_high=3, norm='mul')
    
def master_dark(dark_dir, name, process_dir):
    cmd.cd(dark_dir )
    cmd.convert( f"dark{name}", out=process_dir, fitseq=True )
    cmd.cd( process_dir )
    cmd.stack( f"dark{name}", type='rej', sigma_low=3, sigma_high=3, norm='no')
    
def light(light_dir, name, process_dir, hasflats=True):
    cmd.cd(light_dir)
    cmd.convert(f"light{name}", out=process_dir, fitseq=True )
    cmd.cd( process_dir )
    if hasflats:
        cmd.preprocess(f"light{name}", dark=f'dark{name}_stacked', flat=f'pp_flat{name}_stacked', cfa=True, equalize_cfa=True, debayer=True )
    else:
        cmd.preprocess(name, dark=f'dark{name}_stacked', cfa=True, debayer=True )
    cmd.register(f"pp_light{name}")
    cmd.stack(f"r_pp_light{name}", type='rej', sigma_low=3, sigma_high=3, norm='addscale', output_norm=True, out='../result')
    cmd.close() 
   
# ============================================================================== 
# 2. Starting pySiril
app=Siril()       
workdir = '/Users/akrank/astro/images/M43_800'
process_dir = f'{workdir}/process'

try:
    cmd=Wrapper(app)    #2. its wrapper
    app.Open()          #2. ...and finally Siril
    
    #3. Set preferences
    cmd.set16bits()
    cmd.setext('fit')
    
    #4. Prepare master frames
    flatsdir=f'{workdir}/Flat'
    hasflats=True
    if not(os.path.isdir(flatsdir)) or (len(os.listdir(flatsdir) == 0): # flats folder does not contain any file or none is present in workdir
        hasflats=False
    
    if hasflats:
        master_bias(workdir+ '/Bias', process_dir)
        master_flat(workdir+ '/Flat', process_dir)
    
    master_dark(workdir+ '/Dark'  ,process_dir)  

    #5. Calibrate the light frames, register and stack them
    light(workdir+ '/Light' ,process_dir, hasflats)

except Exception as e :
    print("\n**** ERROR *** " +  str(e) + "\n" )    

#6. Closing Siril and deleting Siril instance
app.Close()
del app

#---------------
