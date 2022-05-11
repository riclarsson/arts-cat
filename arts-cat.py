# -*- coding: utf-8 -*-

import os
import pyarts
import argparse
import importlib
import Hitran

def check_done_or_return_step(steps):
    if len(steps) == 0:
        print("No more steps")
        
        print ("Trying to read all the lines")
        ws = pyarts.workspace.Workspace()
        ws.abs_speciesDefineAll()
        print ("The following is the tags read: ", ws.abs_species.value)
        
        # Read all available lines (ignore if no lines exist for some Arts species with robust=1)
        ws.abs_lines_per_speciesReadSpeciesSplitCatalog(basename=working_dir,
                                                        robust=1)
        print ("Can read all!")

        print ("Exit with success!")
        exit(0)
    return steps.pop(0)

all_steps = [
    "DownloadHitran",
    "ReadHitran",
    "Water183",
    "Zeeman",
    "OxygenLM",
    ]
all_steps_h = " ".join([f"{x}" for x in all_steps])

parser = argparse.ArgumentParser(description='Run all required updates for the Artscat')
parser.add_argument('-w', '--working_dir', type=str, help='The path to be generated where generated data is stored', default='./tmp')
parser.add_argument('-s', '--steps', nargs="+", help=f'Steps to create the catalog (options: [{all_steps_h}])', default=all_steps)
parser.add_argument('-f', "--hitran_file", type=str, help="Hitran file (created in the working dir if 'DownloadHitran' is an option; never deleted)", default="hitfile")
parser.add_argument('--hitran_api', type=str, help='Your personal Hitran API key', default=None)

# Trigger options
parser.add_argument('-d', '--show_diff',action='store_true', help='Show what the update did')
parser.add_argument('-c', '--cleanup',action='store_false', help='Remove all non-xml files from the working directory when finished')

args = parser.parse_args()

# create local variables
hitran_file = args.hitran_file
working_dir = os.path.abspath(args.working_dir)
show_diff = True if args.show_diff else False
cleanup = False if args.cleanup else True
steps = args.steps
hitran_api = args.hitran_api

# create temporary work directory
if not os.path.exists(working_dir):
    print (f"Attempting to create the working directory: {working_dir}")
    os.mkdir(working_dir)
    print ("Created the working directory.  Note, this will not be removed at the end of the run, though several files might be.")
else:
    assert os.path.isdir(working_dir)
    print (f"Using the working directory: {working_dir}")

ws = pyarts.workspace.Workspace()

# Will we download hitran?
step = check_done_or_return_step(steps)
if step == "DownloadHitran":
    hitran_file = os.path.abspath(os.path.join(working_dir, hitran_file))
    print (f"Attempting to download Hitran data to: {hitran_file}")
    Hitran.download.run(hitran_file, hitran_api)
    step = check_done_or_return_step(steps)  # must update step!
else:
    print ("Attempting to use already prepared Hitran data from the temporary directory")

# Will we read hitran?
hitran_file = os.path.abspath(hitran_file)
if step == "ReadHitran":
    print (f"Attempting to read Hitran data from: {hitran_file}")
    Hitran.read.run(ws, hitran_file, working_dir)
    step = check_done_or_return_step(steps)  # must update step!
else:
    print ("Attempting to use already prepared Hitran data from the temporary directory")

while True:
    print(f"Importing step: {step}")
    importlib.import_module(step).run(ws, working_dir, show_diff)
    print(f"Completed step: {step}")
    
    step = check_done_or_return_step(steps)

if cleanup:
    for f in os.listdir(working_dir):
        if not f.endswith('.xml'):
            os.remove(os.path.join(working_dir, f))
