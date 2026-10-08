#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 14:34:19 2021

@author: kendrick shepherd
"""

import sys

# determine if the bar is statically determinate (and belongs to a truss)
def StaticallyDeterminate(nodes,bars):                 
    # Determine the number of nodes in the truss
    n_nodes = len(nodes)
    n_bars = len(bars)
    
    # Determine number of (valid) reactions supported by nodes of the truss
    n_reactions = 0
    for node in nodes:
        if(any(node.ConstraintType())):
            if(2 in node.ConstraintType()):
                sys.exit("Truss cannot support a moment reaction force")
            elif(-1 in node.ConstraintType()):
                sys.exit("Invalid constraint type specified for the truss")
            else:
                n_reactions += len(node.ConstraintType())
    
    # Compute if b + r = 2j (Equation 3-1 of the textbook)
    if(n_bars + n_reactions < 2*n_nodes):
        sys.exit("The truss is unstable; did you input all of the reaction constraints correctly?")
    elif(n_bars + n_reactions > 2*n_nodes):
        sys.exit("The truss is statically indeterminate, and cannot be resolved using method of joints")
    else:
        return True
 
def ComputeReactions(nodes):
    # assume that there is one pin and one roller for our statically determinate structure
    n_pins = 0
    n_roller = 0
    for node in nodes:
        if(node.constraint=="pin"):
            pin_node = node
            n_pins += 1
        elif(node.constraint=="roller_no_xdisp"):
            roller_node = node
            n_roller += 1
        elif(node.constraint=="roller_no_ydisp"):
            roller_node = node
            n_roller += 1
    
    if(n_pins != 1 or n_roller != 1):
        sys.exit("A more clever way must be found to compute the reaction forces")
    
    # Continue from here
    # Sum of moments about the pin
    # THIS FIRST GETS THE X AND Y COORDINATE OF THE NODE CORRESPONDING TO THE PIN AND GETS THE X AND Y COORDINATE OF THE NODE ASSOCIATED WITH THE ROLLER
    [pin_x, pin_y] = pin_node.location
    [roller_x, roller_y] = roller_node.location

    roller_reaction = 0
    for node in nodes:
        [node_x, node_y] = node.location
        # contributions in the y direction
        roller_reaction += node.yforce_external * (node_x - pin_x)
        #contributiond in the x direction
        roller_reaction += node.xforce_external * (pin_y - node_y)
    if(roller_node.constraint=="roller_no_xdisp"):
        roller_reaction = -roller_reaction/(pin_y - roller_y)
        roller_node.AddReactionXForce(roller_reaction)
    elif(roller_node.constraint=="roller_no_ydisp"):
        roller_reaction = -roller_reaction/(roller_x - pin_x)
        roller_node.AddReactionYForce(roller_reaction)

    # Sum all of the external forces acting in the x and y direction
    sum_x_forces = 0
    sum_y_forces = 0
    for node in nodes:
        sum_x_forces += node.xforce_external
        sum_y_forces += node.yforce_external

   # Calculate the pin's x reaction using the sum of forces in the x direction
    if(roller_node.constraint=="roller_no_xdisp"):
        pin_reaction_x = -sum_x_forces - roller_node.xforce_reaction
    else:
        pin_reaction_x = -sum_x_forces

    # Calculate the pin's y reaction using the sum of forces in the y direction
    if(roller_node.constraint=="roller_no_ydisp"):
        pin_reaction_y = -sum_y_forces - roller_node.yforce_reaction
    else:
        pin_reaction_y = -sum_y_forces

    # Add the calculated x and y reactions to the pin node
    pin_node.AddReactionXForce(pin_reaction_x)
    pin_node.AddReactionYForce(pin_reaction_y)
    
    
