# -*- coding: utf-8 -*-

import os
import tqdm
import pyarts

def run(ws, infile, tmpdir):
    if not os.path.exists(infile): raise RuntimeError(f"Cannot find {infile}")
    
    a = open(infile, 'r').readlines()
    test = {}
    for line in tqdm.tqdm(a, ascii=True, desc="Reading and splitting lines"):
        key = line[:3]
        fname = os.path.join(tmpdir, key)
        
        if key not in test:
            test[key] = open(fname, 'w')
        test[key].write(line)
    
    for key in test:
        fname = os.path.join(tmpdir, key)
        test[key].close()
        
        print(f"Reading filename {fname} and printing to {tmpdir + '/'}")
        ws.abs_linesWriteSpeciesSplitXML("ascii", pyarts.cat.hitran.read(ws, fname), tmpdir + '/')
        os.remove(fname)
