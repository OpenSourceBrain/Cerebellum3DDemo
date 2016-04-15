python GenerateCerebellarCortex.py

jnml LEMS_Sim_CerebellarCortex.xml -neuron -run -nogui

pynml-povray -split CerebellarCortex.net.nml -split -scalez 4

python ~/pyNeuroML/pyneuroml/povray/OverlaySimulation.py CerebellarCortex.net LEMS_Sim_CerebellarCortex.xml -endTime 100 -rainbow

python ~/pyNeuroML/pyneuroml/povray/MakeMovie.py CerebellarCortex.net_T