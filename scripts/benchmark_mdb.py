import os
import re
import sys
import socket
import subprocess
import time

QUERIES_FILE  = sys.argv[1]
PATH_SEMANTIC = sys.argv[2] # ANY|SIMPLE|TRAILS|ALL|ALL_COUNT
PATH_MODE     = sys.argv[3] # bfs|dfs
INDEX_MODE    = sys.argv[4] # cache|naive
INDEX_TYPE    = sys.argv[5] # btree|trie

# !!!!!!!!!!!!!!!! MAKE SURE THIS PATHS AND PARAMS ARE CORRECT !!!!!!!!!!!!!!!!
MDB_PATH = f'/home/user/MillenniumDB' # where you cloned MillenniumDB repo
OUTPUT_PATH = f'/home/user/results'   # results and logs will be written here, folder must exist
MDB_DB_FOLDER_PATH = f'{MDB_PATH}/tests/dbs/wikidata' # database folder

# Buffer used by MillenniumDB 8388608 pages(4kB) == 32GB
# this is only for the buffer manager (B+Tree pages),
# MillenniumDB will use more RAM for other things (tries/visited hashmaps)
MDB_BUFFER_SIZE = 8388608
LIMIT = 100000
TIMEOUT = 60 # Max time per query in seconds
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

MDB_PORT = 8080

MDB_CMD = ['./build/Release/bin/server',
           MDB_DB_FOLDER_PATH,
           '-b', str(MDB_BUFFER_SIZE),
           '--timeout', str(TIMEOUT),
           '--path-mode', PATH_MODE,
           '--index-mode', INDEX_MODE,
           '--index-type', INDEX_TYPE
           ]

SUFFIX = f'{PATH_SEMANTIC}_{PATH_MODE}_{INDEX_MODE}_{INDEX_TYPE}'

# Path to needed output and input files #
MDB_QUERY_FILE   = f'{MDB_PATH}/.query_file.tmp'
MDB_RESULTS_FILE = f'{MDB_PATH}/.results.tmp'
RESUME_FILE      = f'{OUTPUT_PATH}/mdb_paths_{SUFFIX}.csv'
SERVER_LOG_FILE  = f'{OUTPUT_PATH}/mdb_paths_{SUFFIX}.log'


# Does not return a string, it writes the query in MDB_QUERY_FILE
# Designed to work for WDBench queries, not a generic SPARQL property path
def parse_to_millenniumdb(query):
    query_parts   = query.strip().split(' ')
    from_string   = query_parts[0]
    property_path = " ".join(query_parts[1:len(query_parts) - 1])
    end_string    = query_parts[len(query_parts) - 1]

    if '?x' in from_string and '?x' in end_string:
        print('Queries with two variables are not supported')
        print(query)

    # Parse subject
    if '?x' in from_string:
        from_string = f'(?x)=[{PATH_SEMANTIC} ?p '
    else:
        from_string = '(' + from_string.split('/')[-1].replace('>', '') + f')=[{PATH_SEMANTIC} ?p '

    # Parse object
    if '?x' in end_string:
        end_string  = ']=>(?x)'
    else:
        end_string  = ']=>(' + end_string.split('/')[-1].replace('>', '') + ')'

    # Parse SPARQL property path
    pattern = r"\<[a-zA-Z0-9\/\.\:\#]*\>"
    path_edges = re.findall(pattern, property_path)
    clean_property_path = property_path

    for path in path_edges:
        clean_path          = ':' + path.split('/')[-1].replace('>', '')
        clean_property_path = re.sub(path, clean_path, clean_property_path, flags=re.MULTILINE)

    with open(MDB_QUERY_FILE, 'w') as file:
        file.write(f'MATCH {from_string}{clean_property_path}{end_string} RETURN *')
        if LIMIT:
            file.write(f' LIMIT {LIMIT}')


def start_server():
    global server_process
    os.chdir(MDB_PATH)
    print('starting server...')

    server_log.write("[start server]\n")
    server_process = subprocess.Popen(MDB_CMD, stdout=server_log, stderr=server_log)
    print(f'pid: {server_process.pid}')

    # Sleep to wait server start
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = ("127.0.0.1", MDB_PORT)
    while s.connect_ex(location) != 0:
        time.sleep(1)

    print(f'done')


def kill_server():
    global server_process
    print(f'killing server[{server_process.pid}]...')
    server_log.write("[kill server]\n")
    server_process.kill()
    server_process.wait()
    print('done')


def query_millennium(query, query_number):
    parse_to_millenniumdb(query)
    start_time = time.time()
    with open(MDB_RESULTS_FILE, 'w') as results_file, open(MDB_QUERY_FILE, 'r') as query_file:
        query_execution = subprocess.Popen(
            ['./build/Release/bin/query'],
            stdin=query_file,
            stdout=results_file,
            stderr=subprocess.DEVNULL)
    exit_code = query_execution.wait()
    elapsed_time = int((time.time() - start_time) * 1000)
    p = subprocess.Popen(['wc', '-l', MDB_RESULTS_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, _ = p.communicate()
    results_count = int(result.strip().split()[0]) - 6 # 1 line from header + 2 for separators + 3 for stats

    mem_cmd = f'grep ^VmRSS /proc/{server_process.pid}/status'.split(' ')
    process = subprocess.Popen(mem_cmd, universal_newlines=True, stdout=subprocess.PIPE)
    out_cmd, err_cmd = process.communicate()
    out_cmd = out_cmd.strip().split()[1]

    with open(RESUME_FILE, 'a') as file:
        if exit_code == 0:
            file.write(f'{query_number},{results_count},OK,{elapsed_time},{out_cmd}\n')
        else:
            if elapsed_time >= TIMEOUT:
                file.write(f'{query_number},{results_count},TIMEOUT,{elapsed_time},{out_cmd}\n')
            else:
                file.write(f'{query_number},0,ERROR,{elapsed_time},{out_cmd}\n')


def check_port_available():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = ("127.0.0.1", MDB_PORT)
    # Check if port is already in use
    if s.connect_ex(location) == 0:
        raise Exception("server port already in use")


# Send query to server
def execute_queries():
    with open(QUERIES_FILE) as queries_file:
        for line in queries_file:
            query_number, query = line.split(',')
            print(f'Executing query {query_number}')
            query_millennium(query, query_number)


########################## BEGIN BENCHMARK EXECUTION ##########################
server_log = open(SERVER_LOG_FILE, 'w')
server_process = None

check_port_available()

# Check if output file already exists
if os.path.exists(RESUME_FILE):
    print(f'File {RESUME_FILE} already exists.')
    sys.exit()

with open(RESUME_FILE, 'w') as file:
    file.write('query_number,results,status,time,mem[kB]\n')

print('TIMEOUT', TIMEOUT, 'seconds')
start_server()
execute_queries()

# Delete temp file
subprocess.Popen(['rm', MDB_RESULTS_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.Popen(['rm', MDB_QUERY_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if server_process is not None:
    max_mem_cmd = f'grep ^VmHWM /proc/{server_process.pid}/status'.split(' ')
    process = subprocess.Popen(max_mem_cmd, universal_newlines=True, stdout=subprocess.PIPE)
    out, err = process.communicate()
    print(out)
    kill_server()

server_log.close()
