import sys
import os

from pysiril.siril import *
from pysiril.wrapper import *
from pysiril.addons import Addons

def master_bias(bias_dir, process_dir):
    cmd.cd(bias_dir)
    cmd.convert("bias", out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.stack("bias", type="rej", sigma_low=3, sigma_high=3, norm="no")

def master_flat(flat_dir, process_dir):
    cmd.cd(flat_dir)
    cmd.convert("flat", out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.preprocess("flat", bias="bias_stacked")
    cmd.stack("pp_flat", type="rej", sigma_low=3, sigma_high=3, norm="mul")

def master_dark(dark_dir, process_dir):
    cmd.cd(dark_dir)
    cmd.convert("dark", out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.stack("dark", type="rej", sigma_low=3, sigma_high=3, norm="no")

def light(light_dir, process_dir, has_flats=True):
    cmd.cd(light_dir)
    cmd.convert("light", out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    if has_flats:
        cmd.preprocess(
            "light",
            dark="dark_stacked",
            flat="pp_flat_stacked",
            cfa=True,
            equalize_cfa=True,
            debayer=True,
        )
    else:
        cmd.preprocess("light", dark="dark_stacked", cfa=True, debayer=True)
    cmd.register("pp_light")
    cmd.stack(
        "r_pp_light",
        type="rej",
        sigma_low=3,
        sigma_high=3,
        norm="addscale",
        output_norm=True,
        out="../result",
    )
    cmd.close()


import argparse

parser = argparse.ArgumentParser(description='Convert images via SiriL')
parser.add_argument('work_dir', nargs='+', help='work directory')
parser.add_argument('--bias', help='bias directory')
parser.add_argument('--dark', help='dark directory')
parser.add_argument('--flat', help='flat directory')
parser.add_argument('--light', help='light directory')
parser.add_argument('--process', help='process directory')
#args = parser.parse_args(["--target", "t", "editorial_dashboard_playlist", "editorial_dashboard_station", "editorial_song_cms", "music_activity", "music_audioclip", "music_audioclipset", "music_brand", "music_broadcaststation", "music_itunesbrand", "music_rottingplaylist", "music_rottingsong", "music_station", "music_stationset", "music_uploaded_content"])
args = parser.parse_args()
if not(args.work_dir):
    parser.print_usage()
    sys.exit(1)

work_dir = os.path.abspath(args.work_dir[0]) if args.work_dir[0] else os.path.abspath(".")
process_dir = os.path.abspath(f"{work_dir}/process")
flat_dir = args.flat or f"{work_dir}/Flat"
bias_dir = args.bias or f"{work_dir}/Bias"
dark_dir = args.dark or f"{work_dir}/Dark"
light_dir = args.light or f"{work_dir}/Light"

print(args, flat_dir, bias_dir, dark_dir, light_dir)
# sys.exit(1)
app = Siril()

try:
    cmd = Wrapper(app) 
    app.Open()
    process_dir = os.path.abspath(f"{work_dir}/process")
    os.mkdir(process_dir)
    cmd.set16bits()
    cmd.setext("fit")
    # flats folder does not contain any file or none is present in work_dir
    has_flats = (os.path.isdir(flat_dir) and len(os.listdir(flat_dir)) > 1)
    if has_flats:
        master_bias(bias_dir, process_dir)
        master_flat(flat_dir, process_dir)
    master_dark(dark_dir, process_dir)
    light(light_dir, process_dir, has_flats)
except Exception as e:
    print(f"\n**** ERROR *** {str(e)}\n")
app.Close()
del app
