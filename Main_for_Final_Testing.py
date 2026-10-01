#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 08:51:30 2021

@author: kendrick shepherd
"""

import sys

from ImportCSVData import LoadData

# Structure_Operations and Method_of_Joints are imported inside the functions
# that use them, so each test file depends only on the code it tests:
#   Geometry_Operations tests  -> LoadCSV                  (no student code)
#   Structure_Operations tests -> LoadAndComputeReactions  (Structure_Operations)
#   Method_of_Joints tests     -> MethodOfJoints           (all three files)

# load the input data only
def LoadCSV(input_geometry):
    [nodes, bars] = LoadData(input_geometry)
    return nodes,bars

def LoadAndComputeReactions(input_geometry):
    from Structure_Operations import StaticallyDeterminate
    from Structure_Operations import ComputeReactions

    # load the input data
    [nodes, bars] = LoadCSV(input_geometry)

    # determine if the truss is statically determinate barring parallel or
    # concurrent reactions
    if not StaticallyDeterminate(nodes,bars):
        sys.exit("Cannot operate on a truss that is not statically determinate")

    # Compute reaction forces at the supports from external loads
    ComputeReactions(nodes)

    return nodes,bars

# perform the method of joints on a statically
# determinate truss
def MethodOfJoints(input_geometry):
    from Method_of_Joints import IterateUsingMethodOfJoints

    # load the input data and compute reaction forces at the supports
    [nodes, bars] = LoadAndComputeReactions(input_geometry)

    # Iterate through all bars using the method of joints
    # to compute internal member loads
    IterateUsingMethodOfJoints(nodes,bars)

    # return the answer
    return [nodes, bars]
