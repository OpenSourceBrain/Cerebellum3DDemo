#
#


from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Location
from neuroml import Instance
from neuroml import Projection
from neuroml import Connection
from neuroml import IncludeType

import math
from random import random

import neuroml.writers as writers

network_id = "Cerebellum3DDemo"

nml_doc = NeuroMLDocument(id=network_id)

net = Network(id=network_id)
nml_doc.networks.append(net)

# The names of the cell type/component used in the populations (Cell Type in neuroConstruct)
grc_group_component = "Granule_98"
gol_group_component = "Golgi_98"

nml_doc.includes.append(IncludeType(href='%s.cell.nml'%grc_group_component))
nml_doc.includes.append(IncludeType(href='%s.cell.nml'%gol_group_component))

# The names of the Exc & Inh groups/populations (Cell Group in neuroConstruct)
grc_group = "Grcs" 
gol_group = "Golgis" 

# The names of the network connections 
net_conn_grc_gol = "net_conn_grc_gol"
net_conn_gol_grc = "net_conn_gol_grc"

# The names of the synapse types (should match names at Cell Mechanism/Network tabs in neuroConstruct)
grc_gol_syns = ["AMPA_GranGol"]
gol_grc_syns = ["GABAA"]

for syn in grc_gol_syns+gol_grc_syns:
	nml_doc.includes.append(IncludeType(href='%s.synapse.nml'%syn))


# Volume
x_size = 200
y_size = 50
z_size = 200



numCells_grc = 400
numCells_gol = 20

# Connection probabilities (initial value)
connection_probability_grc_gol =   0.5
connection_probability_gol_grc =   0.1


# Generate excitatory cells 

grc_pop = Population(id=grc_group, component=grc_group_component, type="populationList", size=numCells_grc)
net.populations.append(grc_pop)

for i in range(0, numCells_grc) :
        index = i
        inst = Instance(id=index)
        grc_pop.instances.append(inst)
        inst.location = Location(x=str(x_size*random()), y=str(y_size*random()), z=str(z_size*random()))

# Generate inhibitory cells
gol_pop = Population(id=gol_group, component=gol_group_component, type="populationList", size=numCells_gol)
net.populations.append(gol_pop)

for i in range(0, numCells_gol) :
        index = i
        inst = Instance(id=index)
        gol_pop.instances.append(inst)
        inst.location = Location(x=str(x_size*random()), y=str(y_size*random()), z=str(z_size*random()))
    
'''
# Generate inhibitory cells

inh_pop = Population(id=gol_group, component=gol_group_component, type="populationList", size=XSCALE_inh*ZSCALE_inh)
net.populations.append(inh_pop)

for i in range(0, XSCALE_inh) :
    for j in range(0, ZSCALE_inh):
        # create cells
        x = i*xSpacing_inh
        z = j*zSpacing_inh
        index = i*ZSCALE_inh + j 

        inst = Instance(id=index)
        inh_pop.instances.append(inst)

        inst.location = Location(x=x, y=0, z=z)



proj_grc_exc = Projection(id=net_conn_grc_exc, presynaptic_population=grc_group, postsynaptic_population=grc_group, synapse=grc_grc_syn)
net.projections.append(proj_grc_exc)
proj_grc_inh = Projection(id=net_conn_grc_inh, presynaptic_population=grc_group, postsynaptic_population=gol_group, synapse=grc_inh_syn)
net.projections.append(proj_grc_inh)
proj_inh_exc = Projection(id=net_conn_inh_exc, presynaptic_population=gol_group, postsynaptic_population=grc_group, synapse=inh_grc_syn)
net.projections.append(proj_inh_exc)
proj_inh_inh = Projection(id=net_conn_inh_inh, presynaptic_population=gol_group, postsynaptic_population=gol_group, synapse=inh_inh_syn)
net.projections.append(proj_inh_inh)


# Generate exc -> *  connections

grc_grc_conn_number =  [[0 for x in xrange(ZSCALE_ex)] for x in xrange(XSCALE_ex)]
grc_inh_conn_number =  [[0 for x in xrange(ZSCALE_ex)] for x in xrange(XSCALE_ex)]
count_grc_exc = 0
count_grc_inh = 0
count_inh_exc = 0
count_inh_inh = 0


def add_connection(projection, id, pre_pop, pre_component, pre_cell_id, pre_seg_id, post_pop, post_component, post_cell_id, post_seg_id):
    
    connection = Connection(id=id, \
                            pre_cell_id="../%s/%i/%s"%(pre_pop, pre_cell_id, pre_component), \
                            pre_segment_id=pre_seg_id, \
                            pre_fraction_along=0.5,
                            post_cell_id="../%s/%i/%s"%(post_pop, post_cell_id, post_component), \
                            post_segment_id=post_seg_id,
                            post_fraction_along=0.5)

    projection.connections.append(connection)


'''



#######   Write to file  ######    

print("Saving to file...")
nml_file = network_id+'.net.nml'
writers.NeuroMLWriter.write(nml_doc, nml_file)

print("Written network file to: "+nml_file)



###### Validate the NeuroML ######    

from neuroml.utils import validate_neuroml2
validate_neuroml2(nml_file) 
print "-----------------------------------"


print
quit()



                                     






