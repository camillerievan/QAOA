Main program is ex09_x.py

Use the settings.yaml file to set the parameters of the program

execution_ref: 'XTEST'                      # a reference for your test
load_graphs: ''                             # a list of ready made graphs: 'ge8c.g6', 'ge10c.g6','12a.hyper'
internal_graph_indexes: ['q8']              # if load_graphs='' then set a path or cyclic graph in the format of qN for path or qNc for cyclic, where N=number of qubites, example: q4, q5, q6, e9, q12, q13, q15, q4c
save_to_db: true                            # true to save the resultant data in an SQLite database
console_to_file: false                      # true to save the console text to a file
action: 'MAXIMIZE'                          # objective of the QAOA: MAXIMIZE or MINIMIZE
layer_range: [1,2,3]                        # range of layers to run
classical_optimizer_loop: ['BFGS']          # classical optimiser to use: BFGS or POWELL
angle_study_loop: ['default']               # 'multi_angle', 'automorphism_global', 'ka', 'polynomial', 'default', automorphism_local' : default is single angle (sa)
try_all_initial_angles: false               # (deprecated)
initial_angles_loop: ['one_p']              # initial angles to try: 'one_p', 'tqa075', 'random0_to_2pi_p', 'random0_to_1_p', 'tqa100', 'tenth_p', 'one_p2'
optimization_loop: ['QUBO',]                # PUBO or QUBO
orbit_library: 'generic'                    # graph automorphism library: igraph, nauty, generic
build_circuit: true                         # true to build the circuit
show_circuit: true                          # true to display the circuit visually
build_in_qiskit: false                      # true builds the circuit in Qulacs and Qiskit, else it builds it only in Qulacs
run_qaoa: true                              # execute the QAOA circuit                  
folder: 'C:...\%REF%_output_%Y%m%d_%H%M%S'  # folder to save data
