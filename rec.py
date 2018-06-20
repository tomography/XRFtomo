#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TomoPy example script to reconstruct a single data set.
"""

from __future__ import print_function

import os
import sys
import json
import argparse
import collections

import h5py
import tomopy
import tomopy.util.dtype as dtype
import dxchange

import numpy as np

def restricted_float(x):

    x = float(x)
    if x < 0.0 or x >= 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
    return x

       

def find_index(a_list, element):
    try:
        return a_list.tolist().index(element)
    except ValueError:
        return None

def read_elements(h5fname):
    return(dxchange.read_hdf5(h5fname, "MAPS/channel_names"))

def read_projection(fname, element):

    projections = dxchange.read_hdf5(fname, "MAPS/XRF_roi")
    elements = read_elements(fname)
    print (elements)
    print (projections.shape)
    print(element, find_index(elements, element))

#print ("ERROR: this element is not in the file")

def main(arg):

    parser = argparse.ArgumentParser()
    parser.add_argument("fname", help="Directory containing multiple datasets or file name of a single dataset: /data/ or /data/sample.h5")
    parser.add_argument("--start", nargs='?', type=float, default=0.0, help="Angle first projection (default 0.0)")
    parser.add_argument("--end", nargs='?', type=float, default=180.0, help="Angle last projection (default 180.0)")
    parser.add_argument("--element", nargs='?', type=str, default="Si", help="Select the element to recontruct (default Si)")
    parser.add_argument("--axis", nargs='?', type=str, default="0", help="Rotation axis location (pixel): 1024.0 (default 1/2 image horizontal size)")
    parser.add_argument("--bin", nargs='?', type=int, default=0, help="Reconstruction binning factor as power(2, choice) (default 0, no binning)")
    parser.add_argument("--method", nargs='?', type=str, default="gridrec", help="Reconstruction algorithm: sirtfbp (default gridrec)")
    parser.add_argument("--type", nargs='?', type=str, default="slice", help="Reconstruction type: full, slice, try (default slice)")
    parser.add_argument("--csw", nargs='?', type=int, default=10, help="+/- center search width (pixel): 10 (default 10). Search is in 0.5 pixel increments")
    parser.add_argument("--nsino", nargs='?', type=restricted_float, default=0.5, help="Location of the sinogram to reconstruct (0 top, 1 bottom): 0.5 (default 0.5)")

    args = parser.parse_args()

    # Set path to the micro-CT data to reconstruct.
    fname = args.fname
    algorithm = args.method
    rot_center = float(args.axis)
    binning = int(args.bin)

    nsino = float(args.nsino)
    angle_start = float(args.start)
    angle_end = float(args.end)
    element = args.element
    rec_type = args.type
    center_search_width = args.csw

    if os.path.isfile(fname):    

        elements = read_elements(fname)
        for i, e in enumerate(elements):
            print ('%d:  %s' % (i, e))
        
        read_projection(fname, element)

    elif os.path.isdir(fname):
        # Add a trailing slash if missing
        top = os.path.join(fname, '')

        h5_file_list = list(filter(lambda x: x.endswith(('.h5', '.hdf')), os.listdir(top)))

        print(len(h5_file_list))
        print((angle_end - angle_start)/len(h5_file_list))

        # Create theta
        theta = []
        for i, f in enumerate(h5_file_list):
            #print(i*(angle_end - angle_start)/len(h5_file_list))

            angle = i*(angle_end - angle_start)/len(h5_file_list) 
            #print ('%d:  %s at %d' % (i, f, theta[i]))
            theta.append(angle)
            print ('%d, %f deg: %s' % (i, theta[i], f))

    else:
        print("Directory or File Name does not exist: ", fname)

if __name__ == "__main__":
    main(sys.argv[1:])

