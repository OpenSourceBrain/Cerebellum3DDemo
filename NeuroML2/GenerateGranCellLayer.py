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
from neuroml import InputList
from neuroml import Input
from neuroml import PoissonFiringSynapse

from neuroml import __version__

import neuroml.writers as writers

from pyneuroml import pynml
from pyneuroml.lems.LEMSSimulation import LEMSSimulation

from random import random
from random import seed


def generate_granule_cell_layer(network_id,
                                x_size,     # um
                                y_size,     # um
                                z_size,     # um
                                numCells_grc,
                                numCells_gol,
                                connections = True,
                                connection_probability_grc_gol =   0.2,
                                connection_probability_gol_grc =   0.1,
                                inputs = False,
                                input_firing_rate = 50, # Hz
                                num_inputs_per_grc = 4,
                                validate = True,
                                random_seed = 1234,
                                generate_lems_simulation = False,
                                duration = 500,  # ms
                                dt = 0.05,
                                temperature="32.0 degC"):

    seed(random_seed)

    nml_doc = NeuroMLDocument(id=network_id)

    net = Network(id = network_id, 
                  type = "networkWithTemperature",
                  temperature = temperature)
                  
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


        for i in range(0, numCells_grc):
            for j in range(0, numCells_gol):
                if i != j:
                    if random()<connection_probability_grc_gol:

                            add_connection(proj_grc_gol, count_grc_gol, grc_group, grc_group_component, i, 0, gol_group, gol_group_component, j, 0)
                    count_grc_gol+=1

                    if random()<connection_probability_gol_grc:

                            add_connection(proj_gol_grc, count_gol_grc, gol_group, gol_group_component, j, 0, grc_group, grc_group_component, i, 0)
                    count_gol_grc+=1

    if inputs:
        
        mf_input_syn = "MF_AMPA"
        nml_doc.includes.append(IncludeType(href='%s.synapse.nml'%mf_input_syn))
        
        rand_spiker_id = "input50Hz"
        
        
        #<poissonFiringSynapse id="Input_8" averageRate="50.0 per_s" synapse="MFSpikeSyn" spikeTarget="./MFSpikeSyn"/>
        pfs = PoissonFiringSynapse(id="input50Hz",
                                   average_rate="%s per_s"%input_firing_rate,
                                   synapse=mf_input_syn,
                                   spike_target="./%s"%mf_input_syn)
                                   
        nml_doc.poisson_firing_synapses.append(pfs)
        
        input_list = InputList(id="Input_0",
                             component=rand_spiker_id,
                             populations=grc_group)
                             
        count = 0
        for i in range(0, numCells_grc):
            
            for j in range(num_inputs_per_grc):
                input = Input(id=count, 
                              target="../%s/%i/%s"%(grc_group, i, grc_group_component), 
                              destination="synapses")  
                input_list.input.append(input)
            
            count += 1
                             
        net.input_lists.append(input_list)


    #######   Write to file  ######    

    print("Saving to file...")
    nml_file = network_id+'.net.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file)

    print("Written network file to: "+nml_file)


    if validate:

        ###### Validate the NeuroML ######    

        from neuroml.utils import validate_neuroml2
        validate_neuroml2(nml_file) 
        
    if generate_lems_simulation:
        # Create a LEMSSimulation to manage creation of LEMS file
        
        ls = LEMSSimulation("Sim_%s"%network_id, duration, dt)

        # Point to network as target of simulation
        ls.assign_simulation_target(net.id)
        
        # Include generated/existing NeuroML2 files
        ls.include_neuroml2_file('%s.cell.nml'%grc_group_component)
        ls.include_neuroml2_file('%s.cell.nml'%gol_group_component)
        ls.include_neuroml2_file(nml_file)
        

        # Specify Displays and Output Files
        disp_grc = "display_grc"
        ls.create_display(disp_grc, "Voltages Granule cells", "-95", "-38")

        of_grc = 'Volts_file_grc'
        ls.create_output_file(of_grc, "v_grc.dat")
        
        disp_gol = "display_gol"
        ls.create_display(disp_gol, "Voltages Golgi cells", "-95", "-38")

        of_gol = 'Volts_file_gol'
        ls.create_output_file(of_gol, "v_gol.dat")

        for i in range(numCells_grc):
            quantity = "%s/%i/%s/v"%(grc_group, i, grc_group_component)
            ls.add_line_to_display(disp_grc, "GrC %i: Vm"%i, quantity, "1mV", pynml.get_next_hex_color())
            ls.add_column_to_output_file(of_grc, "v_%i"%i, quantity)
            
        for i in range(numCells_gol):
            quantity = "%s/%i/%s/v"%(gol_group, i, gol_group_component)
            ls.add_line_to_display(disp_gol, "Golgi %i: Vm"%i, quantity, "1mV", pynml.get_next_hex_color())
            ls.add_column_to_output_file(of_gol, "v_%i"%i, quantity)

        # Save to LEMS XML file
        lems_file_name = ls.save_to_file()
        
    print "-----------------------------------"


    
if __name__ == "__main__":
    
    
    generate_granule_cell_layer("Cerebellum3DDemo",
                                x_size = 1000,
                                y_size = 100, 
                                z_size = 1000,
                                numCells_grc = 40,
                                numCells_gol = 20,
                                connections = True,
                                generate_lems_simulation = False)
                                
    x_size = 200
    y_size = 30
    z_size = 200
    numCells_grc = 4
    numCells_gol = 4

    generate_granule_cell_layer("GCL_%sx%sx%s_%igrc_%igol"%(x_size, y_size, z_size, numCells_grc, numCells_gol),
                                x_size,
                                y_size, 
                                z_size,
                                numCells_grc,
                                numCells_gol,
                                connections = True,
                                connection_probability_grc_gol =   0.75,
                                connection_probability_gol_grc =   0.75,
                                inputs = True,
                                num_inputs_per_grc = 12,
                                input_firing_rate = 150, # Hz
                                generate_lems_simulation = True,
                                duration = 100,
                                dt = 0.01)

                                     






