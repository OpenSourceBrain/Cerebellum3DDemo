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
from neuroml import __version__


import neuroml.writers as writers

from random import random
from random import seed


def generate_granule_cell_layer(network_id,
                                x_size,     # um
                                y_size,     # um
                                z_size,     # um
                                numCells_grc,
                                numCells_gol,
                                connections = True,
                                inputs = False,
                                validate = True,
                                random_seed = 1234):

    seed(random_seed)

    nml_doc = NeuroMLDocument(id=network_id)

    net = Network(id=network_id)
    net.notes = "Network generated using libNeuroML v%s"%__version__
    nml_doc.networks.append(net)

    # The names of the cell type/component used in the populations (Cell Type in neuroConstruct)
    grc_group_component = "Granule_98"
    gol_group_component = "Golgi_98"

    nml_doc.includes.append(IncludeType(href='%s.cell.nml'%grc_group_component))
    nml_doc.includes.append(IncludeType(href='%s.cell.nml'%gol_group_component))

    # The names of the Exc & Inh groups/populations (Cell Group in neuroConstruct)
    grc_group = "Grans" 
    gol_group = "Golgis" 

    # The names of the network connections 
    net_conn_grc_gol = "NetConn_Grans_Golgis"
    net_conn_gol_grc = "NetConn_Golgis_Grans"

    # The names of the synapse types (should match names at Cell Mechanism/Network tabs in neuroConstruct)
    grc_gol_syn = "AMPA_GranGol"
    gol_grc_syn = "GABAA"

    for syn in [grc_gol_syn, gol_grc_syn]:
        nml_doc.includes.append(IncludeType(href='%s.synapse.nml'%syn))





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

    if connections:

        # Connection probabilities (initial value)
        connection_probability_grc_gol =   0.2
        connection_probability_gol_grc =   0.1

        proj_grc_gol = Projection(id=net_conn_grc_gol, presynaptic_population=grc_group, postsynaptic_population=gol_group, synapse=grc_gol_syn)
        net.projections.append(proj_grc_gol)
        proj_gol_grc = Projection(id=net_conn_gol_grc, presynaptic_population=gol_group, postsynaptic_population=grc_group, synapse=gol_grc_syn)
        net.projections.append(proj_gol_grc)

        count_grc_gol = 0
        count_gol_grc = 0

        # Generate exc -> *  connections


        def add_connection(projection, id, pre_pop, pre_component, pre_cell_id, pre_seg_id, post_pop, post_component, post_cell_id, post_seg_id):

            connection = Connection(id=id, \
                                    pre_cell_id="../%s/%i/%s"%(pre_pop, pre_cell_id, pre_component), \
                                    pre_segment_id=pre_seg_id, \
                                    pre_fraction_along=0.5,
                                    post_cell_id="../%s/%i/%s"%(post_pop, post_cell_id, post_component), \
                                    post_segment_id=post_seg_id,
                                    post_fraction_along=0.5)

            projection.connections.append(connection)


        for i in range(0, numCells_grc) :
            for j in range(0, numCells_gol) :
                if i != j:
                    if random()<connection_probability_grc_gol:

                            add_connection(proj_grc_gol, count_grc_gol, grc_group, grc_group_component, i, 0, gol_group, gol_group_component, j, 0)
                    count_grc_gol+=1

                    if random()<connection_probability_gol_grc:

                            add_connection(proj_gol_grc, count_gol_grc, gol_group, gol_group_component, j, 0, grc_group, grc_group_component, i, 0)
                    count_gol_grc+=1



    #######   Write to file  ######    

    print("Saving to file...")
    nml_file = network_id+'.net.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file)

    print("Written network file to: "+nml_file)


    if validate:

        ###### Validate the NeuroML ######    

        from neuroml.utils import validate_neuroml2
        validate_neuroml2(nml_file) 
        print "-----------------------------------"


    
if __name__ == "__main__":
    
    
    generate_granule_cell_layer("Cerebellum3DDemo",
                                x_size = 1000,
                                y_size = 100, 
                                z_size = 1000,
                                numCells_grc = 40,
                                numCells_gol = 20,
                                connections = True)
                                
    x_size = 200
    y_size = 30
    z_size = 200
    numCells_grc = 20
    numCells_gol = 4

    generate_granule_cell_layer("GCL_%sx%sx%s_%igrc_%igol"%(x_size, y_size, z_size, numCells_grc, numCells_gol),
                                x_size,
                                y_size, 
                                z_size,
                                numCells_grc,
                                numCells_gol,
                                connections = False)

                                     






