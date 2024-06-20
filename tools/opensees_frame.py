import numpy as np
import matplotlib.pyplot as plt
from sys import platform
import openseespy.opensees as ops
import opsvis as opsv
import sys
from tools import opensees_deformation as deform
from tools import opensees_secforces as forces
from pprint import pprint

# Euler-bernoulli elements. Does not account for shear deformation
# P-delta effects included.


def opensees_mom_frame(clear_height, height, span, beam_E, beam_A, beam_Ix, post_E, post_A, post_Ix, load_lat, load_vert):
    """
    Calls Opensees to evaluate frame. Full fixity assumed at beam-post connections. Base has full freedom of rotation.
    Returns maximum moment, shear, and deflection in each frame element (left to right)
    All values in kips or in
    """

    # Clean up, set 2D structure, set 3 DOFs per node
    ops.wipe()
    ops.model('basic', '-ndm', 2, '-ndf', 3)
    
    # Create nodes array at end of beams and at post tops
    nodes = []

    # For node creation, order of arguments is tag, x, y

    # Node at base of initial post  
    ops.node(0, 0, 0)
    ops.fix(0, 1, 1, 0)
    
    # Node at top of initial post
    ops.node(1, 0, clear_height)
    
    # Node at base of 2nd post
    ops.node(2, span, 0)
    ops.fix(2, 1, 1, 0)

    # Node at top of 2nd post
    ops.node(3, span, clear_height)

    # Node at 1st beam start
    ops.node(4, 0, clear_height)

    # Node at second beam end
    ops.node(5, span, clear_height)

    # Node at 1st beam end (peak)
    ops.node(6, span/2, height)

    # Node at 2nd beam start (peak)
    ops.node(7, span/2, height)

    # Assign constraints between beam end nodes and column nodes (RIgid beam column connections)
    ops.equalDOF(1, 4, 1,2,3)
    ops.equalDOF(3, 5, 1,2,3)
    ops.equalDOF(6, 7, 1,2,3)
   
    # Create time series with tag
    # 'Constant' type indicates load is applied constantly throughout time interval
    ops.timeSeries('Constant', 0)

    # All loads below will be added to pattern
    ops.pattern('Plain', 0, 0)

    # Create coordinate transfromation object
    ops.geomTransf('Linear', 0)

    # Add roof beam elements
    beam_ele_args = [beam_A, beam_E, beam_Ix, 0]

    # Based on order of node creation, the first beam will span from nodes 1 to 4, and the second will span nodes 3 to 4
    ele_nodes = [4, 6]
    ops.element('elasticBeamColumn', 0, *ele_nodes, *beam_ele_args)

    ele_nodes = [7, 5]
    ops.element('elasticBeamColumn', 1, *ele_nodes, *beam_ele_args)

    # Add post elements
    post_ele_args = [post_A, post_E, post_Ix, 0]

    # The first post will span from nodes 0 to 1 and the second will span nodes 2 to 3
    ele_nodes = [0, 1]
    ops.element('elasticBeamColumn', 2, *ele_nodes, *post_ele_args)

    ele_nodes = [2, 3]
    ops.element('elasticBeamColumn', 3, *ele_nodes, *post_ele_args)

    # Add lateral load to node 1
    ops.load(1, load_lat, 0., 0.)

    # Add gravity loads to beams
    ops.eleLoad('-ele', 0, '-type', '-beamUniform', load_vert, 0.)
    ops.eleLoad('-ele', 1, '-type', '-beamUniform', load_vert, 0.)
    
    # ------------------------------
    # Start of analysis generation
    # ------------------------------

    ops.constraints('Plain')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    ops.test('NormDispIncr', 1.0e-6, 6, 2)
    ops.algorithm('Linear')
    ops.integrator('LoadControl', 1)
    ops.analysis('Static')
    ops.analyze(1) 

    opsv.plot_model()
    plt.title('plot_model after defining elements')
    opsv.plot_loads_2d(sfac = 1)

    _, defl_ax, min_defl, max_defl, x_defl, y_defl = deform.plot_defo(sfac = 1)
    defl = []
    for ind, i in enumerate(x_defl):
        defl.append([])
        for index, j in enumerate(i):
            defl[ind].append([x_defl[ind][index], y_defl[ind][index]])

    # 4. plot N, V, M forces diagrams

    sfacV, sfacM = 1, 1

    opsv.section_force_diagram_2d('T', sfacV)
    _, _, ax_shear, nep_shear, shear_force = forces.section_force_diagram_2d('T', sfacV)
    plt.title('Shear force distribution')
    shear = []
    for ind, i in enumerate(nep_shear):
        shear.append([])
        for index, j in enumerate(i):
            shear[ind].append([nep_shear[ind][index], shear_force[ind][index]])

    opsv.section_force_diagram_2d('N', 1)

    _, _, ax, nep_mom, mom_force = forces.section_force_diagram_2d('M', sfacM)
    plt.title('Bending moment distribution')
    plt.pause(0.001)
    mom = []
    for ind, i in enumerate(nep_mom):
        mom.append([])
        for index, j in enumerate(i):
            mom[ind].append([nep_mom[ind][index], mom_force[ind][index]])
    ops.reactions()
    try0 = ops.basicForce(0)
    try1 = ops.basicForce(1)
    try2 = ops.eleForce(2)
    try3 = ops.eleForce(3)
    plt.show()