import os
import sys
import argparse
import re

## sort images into Type/ISO/secs

parser = argparse.ArgumentParser(description='Sort images')
parser.add_argument('work_dir', nargs='+', help='work directory')
parser.add_argument('--dest', help='destination directory')
parser.add_argument('--final', help='final directory for stacked images')
parser.add_argument('--flat', help='flat file to use')
parser.add_argument('--type', help='type of images')
#args = parser.parse_args(["--target", "t", "editorial_dashboard_playlist", "editorial_dashboard_station", "editorial_song_cms", "music_activity", "music_audioclip", "music_audioclipset", "music_brand", "music_broadcaststation", "music_itunesbrand", "music_rottingplaylist", "music_rottingsong", "music_station", "music_stationset", "music_uploaded_content"])
args = parser.parse_args()
if not(args.work_dir):
    parser.print_usage()
    sys.exit(1)
work_dir = os.path.abspath(args.work_dir[0]) if args.work_dir[0] else os.path.abspath(".")
dest_dir = os.path.abspath(args.dest) if args.dest else os.path.abspath("sorted")
final_dir = os.path.abspath(args.final) if args.final else os.path.abspath("final")
process_dir = os.path.abspath(f"./process")
final_type = args.type or 'dark'
flat_name = os.path.abspath(args.flat) if args.final else None # os.path.abspath(f"../flats/pp_flat_250_0.100_stacked.fit") 

def master_dark(dark_dir, name, process_dir):
    cmd.cd(dark_dir)
    cmd.convert(name, out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.stack(f"{name}", type="rej", sigma_low=3, sigma_high=3, norm="no")

def master_bias(bias_dir, name, process_dir):
    cmd.cd(bias_dir)
    cmd.convert(name, out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.stack(f"{name}", type="rej", sigma_low=3, sigma_high=3, norm="no")

def master_flat(flat_dir, name, process_dir):
    cmd.cd(flat_dir)
    cmd.convert(name, out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.preprocess(name, bias=f"{process_dir}/../master_bias/bias_master.fit")
    cmd.stack(f"pp_{name}", type="rej", sigma_low=3, sigma_high=3, norm="mul")

def light(light_dir, iso, secs, process_dir, flat_name=None):
    name = f"light_{iso}_{secs}"
    dark_name = f"../master_darks/dark_{iso}_{secs}_stacked.fit"
    cmd.cd(light_dir)
    cmd.convert(name, out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    if flat_name:
        cmd.preprocess(
            name,
            dark=dark_name,
            flat=flat_name,
            cfa=True,
            equalize_cfa=True,
            debayer=True,
        )
    else:
        cmd.preprocess(name, dark=dark_name, cfa=True, debayer=True)
    cmd.register(f"pp_{name}")
    cmd.stack(
        f"r_pp_{name}",
        type="rej",
        sigma_low=3,
        sigma_high=3,
        norm="addscale",
        output_norm=True,
        out=f"final_{name}_stacked",
    )
    cmd.savetif(f"final_{name}_stacked")
    cmd.close()

from pysiril.siril import *
from pysiril.wrapper import *
from pysiril.addons import Addons

# sys.exit(1)
app = Siril()

def clean_dir(dir):
    os.makedirs(dir, exist_ok=True)
    for existing in os.listdir(dir):
        try:
            os.remove(f"{dir}/{existing}")
        except:
            pass

def process():
    process_dir = os.path.abspath(f"./process")

    images = {}
    for name in os.listdir(work_dir):
        try:
            if re.match(r'.*?\.(cr2|fits|fit)$', name):
                parts = name.split("_")
                if len(parts) > 5:
                    parts = parts[1:]
                iso, type, secs, ignored1, num_extension = parts
                images[iso] = images.get(iso) or {}
                images[iso][secs] =  images[iso].get(secs) or []
                images[iso][secs].append(name)
        except Exception as e:
            print("********ERROR processing: {name}: {e}")
    os.makedirs(f"{dest_dir}", exist_ok=True)
    for iso in list(images.keys()):
        os.makedirs(f"{dest_dir}/{iso}", exist_ok=True)
        for secs in list(images[iso].keys()):
            sorted_dir = f"{dest_dir}/{iso}/{secs}"
            try:
                clean_dir(sorted_dir)
                clean_dir(process_dir)
                for name in images[iso][secs]:
                    try:
                        os.link(f"{work_dir}/{name}", f"{sorted_dir}/{name}")
                    except:
                        pass
                final_name = f"{final_type}_{iso}_{secs}"
                if final_type == 'dark':
                    master_dark(sorted_dir, final_name, process_dir)
                elif final_type == 'bias':
                    master_bias(sorted_dir, final_name, process_dir)
                elif final_type == 'flat':
                    master_flat(sorted_dir, final_name, process_dir)
                    final_name = f"pp_{final_name}"
                elif final_type == 'light':
                    light(sorted_dir, iso, secs, process_dir)
                    final_name = f"final_{final_name}"
                try:
                    os.remove(f"{final_dir}/{final_name}_stacked.fit")
                except:
                    pass
                os.link(f"{process_dir}/{final_name}_stacked.fit", f"{final_dir}/{final_name}_stacked.fit")
            except Exception as e:
                print("********ERROR processing: {sorted_dir}: {e}")
                pass
            #sys.exit(0)

from pysiril.siril import *
from pysiril.wrapper import *
from pysiril.addons import Addons

try:
    cmd = Wrapper(app) 
    app.Open()
    try:
        sys.exec(f"rm -Rf '{process_dir}' '{dest_dir}'")
    except:
        pass
    os.makedirs(f"{process_dir}", exist_ok=True)
    os.makedirs(f"final", exist_ok=True)
    cmd.set16bits()
    cmd.setext("fit")

    process()
except Exception as e:
    print(f"\n**** ERROR *** {str(e)}\n")
app.Close()
del app
