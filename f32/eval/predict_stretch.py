#!/usr/bin/env python3
import argparse
import numpy as np
from ase import Atoms
from ase.io import read, write, Trajectory
from ase.optimize import *
from NNCalculator.NNCalculator import *
from ase.visualize import view

'''
Script to calculate the potential energy H2CO along a C-H stretch
'''

#parse command line arguments
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser._action_groups.pop()
required = parser.add_argument_group("required arguments")
required.add_argument("-i", "--input",   type=str,   help="input xyz",  required=True)
optional = parser.add_argument_group("optional arguments")
optional.add_argument("--charge",  type=int, help="total charge", default=0)

args = parser.parse_args()
print("input ", args.input)

#read input file (molecular structure to predict) and create
#an atoms object
atoms = read(args.input)

#setup calculator object, which in this case is the NN calculator
#it is important that it is setup with the settings as used in the
#training procedure.
#setup calculator
calc = NNCalculator(
    checkpoint="models_f32/ch2o_mp2_avtz_3601_b", #load the model you want to used
    atoms=atoms,
    charge=args.charge,
    F=128,
    K=64,
    num_blocks=5,
    num_residual_atomic=2,
    num_residual_interaction=3,
    num_residual_output=1,
    sr_cut=6.0,
    use_electrostatic=True,
    use_dispersion=True,
    s6=1.0000,                    #s6 coefficient for d3 dispersion, by default is learned
    s8=2.3550,                    #s8 coefficient for d3 dispersion, by default is learned
    a1=0.5238,                    #a1 coefficient for d3 dispersion, by default is learned
    a2=3.5016)                   #a2 coefficient for d3 dispersion, by default is learned)

#attach the calculator object to the atoms object
atoms.set_calculator(calc)

#define name of the trajectory file to be saved
traj = Trajectory('dissociating_h_f32_h2co_mp2.traj', 'w', atoms)

#get all atomic positions
pos = atoms.get_positions()

#calculate vector pointing from O to H
vec = pos[2, :] - pos[0, :]
#normalize
vec = vec/np.linalg.norm(vec)

#define step size
eps = 0.00001

epot = []
r = []


for i in range(2000):
    pos = atoms.get_positions()
    pos[2, :] -= eps*vec
    atoms.set_positions(pos)
    

for i in range(5000):
    pos = atoms.get_positions()
    pos[2, :] += eps*vec
    atoms.set_positions(pos)
    
    epot.append(atoms.get_potential_energy())
    r.append(atoms.get_distance(2,0))

    traj.write(atoms)

np.savetxt('dissociating_h_f32_h2co_mp2.dat', np.c_[r, np.array(epot)*23.0605])



