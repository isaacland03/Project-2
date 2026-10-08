#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 12:37:32 2021

@author: kendrick shepherd
"""

import sys

import Geometry_Operations as geom

# Determine the unknown bars next to this node
def UnknownBars(node):
    bars_next_to_this_node = node.bars
    unknown_bars = []
    for bar in bars_next_to_this_node:
        if not bar.is_computed:
            unknown_bars.append(bar)

    return unknown_bars

# Determine if a node if "viable" or not
def NodeIsViable(node):
    unk_bars = UnknownBars(node)
    if 0 < len(unk_bars) and len(unk_bars) <= 2:
        return True
    else:
        return False
    
# Compute unknown force in bar due to sum of the
# forces in the x direction
def SumOfForcesInLocalX(node, local_x_bar):
    local_x_vec = geom.BarNodeToVector(node, local_x_bar)

    local_x_length = geom.VectorTwoNorm(local_x_vec)

    local_x_node_force = (
        node.GetNetXForce() * local_x_vec[0]
        + node.GetNetYForce() * local_x_vec[1]
    ) / local_x_length

    sum_known_forces = local_x_node_force

    for bar in node.bars:
        if bar != local_x_bar and bar.is_computed:
            sum_known_forces += (
                bar.axial_load * geom.CosineBars(local_x_bar, bar)
            )

    unknown_force = -sum_known_forces
    return unknown_force

# Compute unknown force in bar due to sum of the 
# forces in the y direction
def SumOfForcesInLocalY(node, unknown_bars):

    local_x_bar = unknown_bars[0]

    other_bar = unknown_bars[1]

    local_x_vec = geom.BarNodeToVector(node, local_x_bar)

    local_x_length = geom.VectorTwoNorm(local_x_vec)

    local_y_node_force = (
        node.GetNetXForce() * (-local_x_vec[1])
        + node.GetNetYForce() * local_x_vec[0]
    ) / local_x_length

    sum_known_forces = local_y_node_force

    for bar in node.bars:
        if bar.is_computed:
            sum_known_forces += (
                bar.axial_load * geom.SineBars(local_x_bar, bar)
            )

    other_bar_sine = geom.SineBars(local_x_bar, other_bar)

    if abs(other_bar_sine) < 1e-12:
        sys.exit("Cannot solve node: the two unknown bars are collinear.")

    unknown_force = -sum_known_forces / other_bar_sine

    return unknown_force
    
# Perform the method of joints on the structure
def IterateUsingMethodOfJoints(nodes,bars):

    while True:

        if all(bar.is_computed for bar in bars):
            return

        progress = False

        for node in nodes:

            unknown_bars = UnknownBars(node)

            if len(unknown_bars) ==1:

                force = SumOfForcesInLocalX(
                    node,
                    unknown_bars[0]
                )

                unknown_bars[0].SetAxialLoad(force)

                unknown_bars[0].is_computed = True

                progress = True

            elif len(unknown_bars) == 2:

                force_y = SumOfForcesInLocalY(
                    node,
                    unknown_bars
                )

                unknown_bars[1].SetAxialLoad(force_y)

                unknown_bars[1].is_computed = True

                force_x = SumOfForcesInLocalX(
                    node,
                    unknown_bars[0]
                )

                unknown_bars[0].SetAxialLoad(force_x)

                unknown_bars[0].is_computed = True

                progress = True

        if not progress:
            sys.exit(
                "Method of joints could not solve the remaining bars."
            )