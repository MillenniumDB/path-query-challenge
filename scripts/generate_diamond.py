import sys

scale_param = int(sys.argv[1])
output_type = sys.argv[2].lower()

if output_type == 'nt':
    with open(f"diamond_{scale_param}.nt", mode="w")  as nt_output:
        for i in range(0, 3*scale_param, 3):
            nt_output.write(f'<http://e.cl/N{i  }> <http://e.cl/A> <http://e.cl/N{i+1}> .\n')
            nt_output.write(f'<http://e.cl/N{i  }> <http://e.cl/A> <http://e.cl/N{i+2}> .\n')
            nt_output.write(f'<http://e.cl/N{i+1}> <http://e.cl/A> <http://e.cl/N{i+3}> .\n')
            nt_output.write(f'<http://e.cl/N{i+2}> <http://e.cl/A> <http://e.cl/N{i+3}> .\n')

elif output_type == 'mdb':
    with open(f"diamond_{scale_param}.mdb", mode="w") as mdb_output:
        for i in range(0, 3*scale_param, 3):
            mdb_output.write(f'N{i  }->N{i+1} :A\n')
            mdb_output.write(f'N{i  }->N{i+2} :A\n')
            mdb_output.write(f'N{i+1}->N{i+3} :A\n')
            mdb_output.write(f'N{i+2}->N{i+3} :A\n')

elif output_type == 'neo4j':
    with open(f"diamond_{scale_param}_neo4j_nodes.csv", mode="w")  as neo4j_nodes_output, \
         open(f"diamond_{scale_param}_neo4j_edges.csv", mode="w")  as neo4j_edges_output:
        neo4j_nodes_output.write(":ID,id:STRING\n")
        neo4j_edges_output.write(":START_ID,:END_ID,:TYPE\n")

        neo4j_nodes_output.write(f'0,"N0"\n')
        for i in range(0, 3*scale_param, 3):
            neo4j_nodes_output.write(f"{i+1},\"N{i+1}\"\n")
            neo4j_nodes_output.write(f"{i+2},\"N{i+2}\"\n")
            neo4j_nodes_output.write(f"{i+3},\"N{i+3}\"\n")

            neo4j_edges_output.write(f'{i  },{i+1},A\n')
            neo4j_edges_output.write(f'{i  },{i+2},A\n')
            neo4j_edges_output.write(f'{i+1},{i+3},A\n')
            neo4j_edges_output.write(f'{i+2},{i+3},A\n')
else:
    print(f'Output type "{output_type}" not recognized.')
