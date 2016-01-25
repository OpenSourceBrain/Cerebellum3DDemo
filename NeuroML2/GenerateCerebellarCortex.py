#
#

from GenerateGranCellLayer import generate_granule_cell_layer
from neuroml import Connection
from neuroml import IncludeType
from neuroml import Input
from neuroml import InputList
from neuroml import Instance
from neuroml import Location
from neuroml import Network
from neuroml import NeuroMLDocument
from neuroml import PoissonFiringSynapse
from neuroml import Population
from neuroml import Projection
from neuroml import __version__
import neuroml.writers as writers
from pyneuroml import pynml
from pyneuroml.lems.LEMSSimulation import LEMSSimulation
from random import random
from random import seed


def generate_cerebellar_cortex(network_id,
                                x_size,     # um
                                grc_y_size,     # um
                                purk_y_size,     # um
                                z_size,     # um
                                numCells_grc,
                                numCells_gol,
                                numCells_purk,
                                connections = True,
                                connection_probability_grc_gol =   0.2,
                                connection_probability_gol_grc =   0.1,
                                inputs = False,
                                input_firing_rate = 200, # Hz
                                num_inputs_per_grc = 4,
                                validate = True,
                                random_seed = 1234,
                                generate_lems_simulation = False,
                                duration = 500,  # ms
                                dt = 0.01,
                                temperature="32.0 degC"):

    seed(random_seed)

    nml_doc, ls = generate_granule_cell_layer(network_id,
                                x_size,     # um
                                grc_y_size,     # um
                                z_size,     # um
                                numCells_grc,
                                numCells_gol,
                                connections = connections,
                                connection_probability_grc_gol =   connection_probability_grc_gol,
                                connection_probability_gol_grc =   connection_probability_gol_grc,
                                inputs = inputs,
                                input_firing_rate = input_firing_rate, 
                                num_inputs_per_grc = num_inputs_per_grc,
                                validate = validate,
                                random_seed = random_seed,
                                generate_lems_simulation = generate_lems_simulation,
                                duration = duration,  # ms
                                dt = dt,
                                temperature=temperature)
                                
    net = nml_doc.networks[0]
    
    purk_group_component = "purk2"

    purk_group = "Purkinjes" 


    # Generate excitatory cells 

    if numCells_purk>0:
        nml_doc.includes.append(IncludeType(href='%s.cell.nml'%purk_group_component))
        
        purk_pop = Population(id=purk_group, component=purk_group_component, type="populationList", size=numCells_purk)
        net.populations.append(purk_pop)

        for i in range(0, numCells_purk):
                index = i
                inst = Instance(id=index)
                purk_pop.instances.append(inst)
                inst.location = Location(x=str(x_size*random()), y=str(grc_y_size + purk_y_size*random()), z=str(z_size*random()))


    #######   Write to file  ######    

    print("Saving to file...")
    nml_file = network_id+'.net.nml'
    writers.NeuroMLWriter.write(nml_doc, nml_file)

    print("Written network file to: "+nml_file)
    
    
    ls.include_neuroml2_file('%s.cell.nml'%purk_group_component)
    
    lems_file_name = ls.save_to_file()
    
    return nml_doc, ls


    
if __name__ == "__main__":
    
    
    generate_cerebellar_cortex("CerebellarCortex",
                                random_seed = 123456,
                                x_size = 600,
                                grc_y_size = 100, 
                                purk_y_size = 30, 
                                z_size = 600,
                                numCells_grc = 200,
                                numCells_gol = 40,
                                numCells_purk = 4,
                                connections = True,
                                generate_lems_simulation = True,
                                inputs = True)
    large = False
    if large:
    
      generate_cerebellar_cortex( "CerebellarCortexLarge",
                                random_seed = 123,
                                x_size = 1000,
                                grc_y_size = 150, 
                                purk_y_size = 30, 
                                z_size = 1000,
                                numCells_grc = 2200,
                                numCells_gol = 400,
                                numCells_purk = 20,
                                connections = False,
                                generate_lems_simulation = True)


                                     






