# -*- coding: utf-8 -*-

import os
import pyarts
import numpy as np

def run(ws, working_dir, show_diff):
    ws.Wigner6Init()
    ws.isotopologue_ratiosInitFromBuiltin()
    pyarts.cat.linemixing.init_ecs(ws)
    
    qid = pyarts.arts.QuantumIdentifier('O2-66 S 1 1 Lambda 0 0 v 0 0 ElecStateLabel X X')
    
    orig_fn = os.path.join(working_dir, "O2-66.xml")
    assert os.path.exists(orig_fn), f"Cannot find> {orig_fn}"
    
    ws.ReadXML(ws.abs_lines, orig_fn)
    
    if 'abs_lines_tmp__' not in dir(ws):
        ws.create_variable("ArrayOfAbsorptionLines", 'abs_lines_tmp__')
    ws.Copy(ws.abs_lines_tmp__, ws.abs_lines)
    
    pyarts.cat.select.select(ws, ws.abs_lines_tmp__, qid, 40e9, 130e9, 0)
    ws.abs_linesSetPopulation(ws.abs_lines_tmp__, "ByMakarovFullRelmat")
    print("Adapting oxygen band with ", len(ws.abs_lines_tmp__.value[0].lines), " lines")
    
    pyarts.cat.linemixing.adapt_lines(ws, ws.abs_lines_tmp__,
                                      t_grid=np.linspace(150, 350),
                                      pressure=1e5, order=1, robust=1,
                                      rosenkranz_adaptation=0)
    
    ws.abs_linesReplaceLines(ws.abs_lines, ws.abs_lines_tmp__)
    
    if show_diff:
        diffout = os.path.join(working_dir, "O2-66.xml.OxygenLM.diff.txt")
        print(f"Generating diff log at: {diffout}")
        ws.abs_lines.value.savexml(orig_fn+'.tmp')
        os.system(f'diff {orig_fn}.tmp {orig_fn} > {diffout}')
        os.system(f'mv {orig_fn}.tmp {orig_fn}')
    else:
        ws.abs_lines.value.savexml(orig_fn)
    