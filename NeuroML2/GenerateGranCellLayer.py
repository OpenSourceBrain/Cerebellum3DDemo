#
#

from neuroml import NeuroMLDocument
from neuroml import Network
from neuroml import Population
from neuroml import Location
from neuroml import Instance
from neuroml import Projection
from neuroml import Property
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


def add_connection(projection, id, pre_pop, pre_component, pre_cell_id, pre_seg_id, post_pop, post_component, post_cell_id, post_seg_id):

    connection = Connection(id=id, \
                            pre_cell_id="../%s/%i/%s"%(pre_pop, pre_cell_id, pre_component), \
                            pre_segment_id=pre_seg_id, \
                            pre_fraction_along=0.5,
                            post_cell_id="../%s/%i/%s"%(post_pop, post_cell_id, post_component), \
                            post_segment_id=post_seg_id,
                            post_fraction_along=0.5)

    projection.connections.append(connection)
    

def add_probabilistic_projection(net, presynaptic_population, pre_component, postsynaptic_population, post_component, prefix, synapse, numCells_pre, numCells_post, connection_probability):
    
        if numCells_pre==0 or numCells_post==0:
            return None
        
        proj = Projection(id="%s_%s_%s"%(prefix,presynaptic_population, postsynaptic_population), 
                          presynaptic_population=presynaptic_population, 
                          postsynaptic_population=postsynaptic_population, 
                          synapse=synapse)
                          

        count = 0

        for i in range(0, numCells_pre):
            for j in range(0, numCells_post):
                if i != j:
                    if random() < connection_probability:
                        add_connection(proj, count, presynaptic_population, pre_component, i, 0, postsynaptic_population, post_component, j, 0)
                        
                    count+=1
                    
        net.projections.append(proj)
        
        return proj


def generate_granule_cell_layer(network_id,
                                x_size,     # um
                                y_size,     # um
                                z_size,     # um
                                numCells_mf,
                                numCells_grc,
                                numCells_gol,
                                mf_group_component = "MossyFiber",
                                grc_group_component = "Granule_98",
                                gol_group_component = "Golgi_98",
                                connections = True,
                                connection_probability_grc_gol =   0.2,
                                connection_probability_gol_grc =   0.1,
                                inputs = False,
                                input_firing_rate = 50, # Hz
                                num_inputs_per_mf = 4,
                                validate = True,
                                random_seed = 1234,
                                generate_lems_simulation = False,
                                duration = 500,  # ms
                                dt = 0.005,
                                temperature="32.0 degC"):

    seed(random_seed)

    nml_doc = NeuroMLDocument(id=network_id)

    net = Network(id = network_id, 
                  type = "networkWithTemperature",
                  temperature = temperature)
                  
    net.notes = "Network generated using libNeuroML v%s"%__version__
    nml_doc.networks.append(net)

    if numCells_mf>0:
        nml_doc.includes.append(IncludeType(href='%s.cell.nml'%mf_group_component))
    if numCells_grc>0:
        nml_doc.includes.append(IncludeType(href='%s.cell.nml'%grc_group_component))
    if numCells_gol>0:
        nml_doc.includes.append(IncludeType(href='%s.cell.nml'%gol_group_component))

    # The names of the groups/populations 
    mf_group = "MossyFibers" 
    grc_group = "Grans" 
    gol_group = "Golgis" 


    # The names of the synapse types (should match names at Cell Mechanism/Network tabs in neuroConstruct)=
    mf_grc_syn = "MF_AMPA"
    grc_gol_syn = "AMPA_GranGol"
    gol_grc_syn = "GABAA"

    for syn in [mf_grc_syn, grc_gol_syn, gol_grc_syn]:
        nml_doc.includes.append(IncludeType(href='%s.synapse.nml'%syn))


    # Generate Gran cells 
    if numCells_mf>0:
        mf_pop = Population(id=mf_group, component=mf_group_component, type="populationList", size=numCells_mf)
        mf_pop.properties.append(Property("color","0 0 1"))
        net.populations.append(mf_pop)

        for i in range(0, numCells_mf) :
                index = i
                inst = Instance(id=index)
                mf_pop.instances.append(inst)
                inst.location = Location(x=str(x_size*random()), y=str(y_size*random()), z=str(z_size*random()))

    # Generate Gran cells 
    if numCells_grc>0:
        grc_pop = Population(id=grc_group, component=grc_group_component, type="populationList", size=numCells_grc)
        grc_pop.properties.append(Property("color","1 0 0"))
        net.populations.append(grc_pop)

        for i in range(0, numCells_grc) :
                index = i
                inst = Instance(id=index)
                grc_pop.instances.append(inst)
                inst.location = Location(x=str(x_size*random()), y=str(y_size*random()), z=str(z_size*random()))

    # Generate Golgi cells
    if numCells_gol>0:
        gol_pop = Population(id=gol_group, component=gol_group_component, type="populationList", size=numCells_gol)
        gol_pop.properties.append(Property("color","0 1 0"))
        net.populations.append(gol_pop)

        for i in range(0, numCells_gol) :
                index = i
                inst = Instance(id=index)
                gol_pop.instances.append(inst)
                inst.location = Location(x=str(x_size*random()), y=str(y_size*random()), z=str(z_size*random()))

    if connections:

        add_probabilistic_projection(net, mf_group, mf_group_component, grc_group, grc_group_component, 'NetConn', mf_grc_syn, numCells_mf, numCells_grc, 1)
    
        add_probabilistic_projection(net, grc_group, grc_group_component, gol_group, gol_group_component, 'NetConn', grc_gol_syn, numCells_grc, numCells_gol, connection_probability_grc_gol)
        
        add_probabilistic_projection(net, gol_group, gol_group_component, grc_group, grc_group_component, 'NetConn', gol_grc_syn, numCells_gol, numCells_grc, connection_probability_gol_grc)
    

    if inputs:
        
        mf_input_syn = "MFSpikeSyn"
        nml_doc.includes.append(IncludeType(href='%s.synapse.nml'%mf_input_syn))
        
        rand_spiker_id = "input%sHz"%input_firing_rate
        
        
        #<poissonFiringSynapse id="Input_8" averageRate="50.0 per_s" synapse="MFSpikeSyn" spikeTarget="./MFSpikeSyn"/>
        pfs = PoissonFiringSynapse(id=rand_spiker_id,
                                   average_rate="%s per_s"%input_firing_rate,
                                   synapse=mf_input_syn,
                                   spike_target="./%s"%mf_input_syn)
                                   
        nml_doc.poisson_firing_synapses.append(pfs)
        
        input_list = InputList(id="Input_0",
                             component=rand_spiker_id,
                             populations=mf_group)
                             
        count = 0
        for i in range(0, numCells_mf):
            
            for j in range(num_inputs_per_mf):
                input = Input(id=count, 
                              target="../%s/%i/%s"%(mf_group, i, mf_group_component), 
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
        if numCells_mf>0:
            disp_mf = "display_mf"
            ls.create_display(disp_mf, "Voltages Mossy fibers", "-70", "10")

            of_mf = 'Volts_file_mf'
            ls.create_output_file(of_mf, "v_mf.dat")


            for i in range(numCells_mf):
                quantity = "%s/%i/%s/v"%(mf_group, i, mf_group_component)
                ls.add_line_to_display(disp_mf, "MF %i: Vm"%i, quantity, "1mV", pynml.get_next_hex_color())
                ls.add_column_to_output_file(of_mf, "v_%i"%i, quantity)

        # Specify Displays and Output Files
        if numCells_grc>0:
            disp_grc = "display_grc"
            ls.create_display(disp_grc, "Voltages Granule cells", "-75", "30")

            of_grc = 'Volts_file_grc'
            ls.create_output_file(of_grc, "v_grc.dat")


            for i in range(numCells_grc):
                quantity = "%s/%i/%s/v"%(grc_group, i, grc_group_component)
                ls.add_line_to_display(disp_grc, "GrC %i: Vm"%i, quantity, "1mV", pynml.get_next_hex_color())
                ls.add_column_to_output_file(of_grc, "v_%i"%i, quantity)
        
        if numCells_gol>0:
            disp_gol = "display_gol"
            ls.create_display(disp_gol, "Voltages Golgi cells", "-75", "30")

            of_gol = 'Volts_file_gol'
            ls.create_output_file(of_gol, "v_gol.dat")

            for i in range(numCells_gol):
                quantity = "%s/%i/%s/v"%(gol_group, i, gol_group_component)
                ls.add_line_to_display(disp_gol, "Golgi %i: Vm"%i, quantity, "1mV", pynml.get_next_hex_color())
                ls.add_column_to_output_file(of_gol, "v_%i"%i, quantity)

        # Save to LEMS XML file
        lems_file_name = ls.save_to_file()
    else:
        
        ls = None
        
    print "-----------------------------------"
    
    return nml_doc, ls


    
if __name__ == "__main__":
    
    
    generate_granule_cell_layer("Cerebellum3DDemo",
                                x_size = 1000,
                                y_size = 100, 
                                z_size = 1000,
                                numCells_mf = 40,
                                numCells_grc = 40,
                                numCells_gol = 20,
                                connections = True,
                                generate_lems_simulation = False)
                                
    x_size = 200
    y_size = 30
    z_size = 200
    numCells_mf = 4
    numCells_grc = 4
    numCells_gol = 4

    generate_granule_cell_layer("GCL_%sx%sx%s_%igrc_%igol"%(x_size, y_size, z_size, numCells_grc, numCells_gol),
                                x_size,
                                y_size, 
                                z_size,
                                numCells_mf,
                                numCells_grc,
                                numCells_gol,
                                connections = True,
                                connection_probability_grc_gol =   0.75,
                                connection_probability_gol_grc =   0.75,
                                inputs = True,
                                num_inputs_per_mf = 1,
                                input_firing_rate = 150, # Hz
                                generate_lems_simulation = True,
                                duration = 100,
                                dt = 0.01)

                                     






