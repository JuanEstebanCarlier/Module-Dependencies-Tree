import argparse
import subprocess
import pydot

class GraphConfig:
    def __init__(self, module_name, command, output_file, show_parsing, include_independent):
        self.module_name = module_name
        self.command = command
        self.recursive = bool(module_name != None)
        self.output_file = output_file
        self.show_parsing = show_parsing
        self.include_independent = include_independent

def parse_command_line():
    parser = argparse.ArgumentParser(
    prog = 'Module Dependency Tree Tool',
    description='List dependencies of a module in an HPCC environment.',
    epilog='''
    Examples:
    %(prog)s                              # Lists dependencies of all modules in default format.
    %(prog)s exampleModule -o png         # Outputs the dependencies of 'exampleModule' in PNG format.
    %(prog)s -p -i                        # Prints parsing details and includes modules without dependencies.
    '''
    )
    parser.add_argument('module_name', type=str, nargs='?', default=None,
                    help='Name of the module to show dependencies for. Defaults to None.')
    parser.add_argument('-c', '--command', type=str, nargs='?', default='list',
                    help='Use a standard lmod command to graph (list, avail, spider). Default is list. Example: -c avail')
    parser.add_argument('-o', '--output', type=str, nargs='?', default='.raw',
                    help='Specify the output file name and format for the dependency graph (supported: dot, png, svg). Default is .raw dot format. Example usage: -o tree.png')
    parser.add_argument('-p', '--print', action='store_true',
                    help='If set, print detailed parsing information of module dependencies.')
    parser.add_argument('-i', '--include', action='store_true',
                    help='If set, include modules without dependencies in the output.')
    return parser

def extract_dependencies(input_list):
    depend_prefix = ["depends_on", "load", "always_load", "prereq"] 
    output_list = []
    
    # Iterate over each string in the input list
    for item in input_list:
        start = item.find('(')
        if (item[:start] in depend_prefix) and (start != -1):
            # Find the starting and ending position of the argument(s) inside depends_on()
            start = item.find('(') + 1
            end = item.rfind(')')
            
            # Extract the argument(s) as a single string
            arguments_str = item[start:end]
            
            # Split the arguments by comma and strip the quotation marks
            arguments = [arg.strip('"') for arg in arguments_str.split(',')]
            
            # Add the extracted arguments to the output list
            output_list.extend(arguments)
    
    return output_list

def get_dependencies_list(module_name):
    # Execute the module show command
    init_script = "/etc/profile.d/lmod.sh.dpkg-dist"
    command = f"bash -c 'source {init_script} && module --raw show {module_name}'"
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'module --raw show {module_name}': {e}")
        return []

    # Parse the output for dependencies and strip 
    lines = result.stdout.split("\n")
    stripped_lines = []
    for line in lines:
        stripped_lines.append(line.strip())
    return extract_dependencies(stripped_lines)

# Run a specific command for module and return the list of modules
def get_module_list(method):
    init_script = "/etc/profile.d/lmod.sh.dpkg-dist"
    command = f"bash -c 'source {init_script} && module --terse {method}'"
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'module --terse {method}': {e}")
    return result.stdout.split()

# display the dependencies of each module that was looked into
def print_module_dependencies(module_name, dependencies):
    if len(dependencies) > 0:
        print(module_name, "depends on:")
        for dep in dependencies:
            print(f"- {dep}")
    else:
        print(module_name, "has no dependencies")
    print()

### GRAPH A SINGLE MODULE

def graph_module_dependencies(graph_config, parsed_modules, graph = None):
    # Create graph object from pydot library
    if graph == None:
        graph = pydot.Dot(f'dependency_tree {graph_config.module_name}', graph_type="graph", bgcolor="white")

    dependencies = get_dependencies_list(graph_config.module_name)

    # Add module to parsed_modules set
    parsed_modules.add(graph_config.module_name)

    # Call print function to print dependencies list
    if graph_config.show_parsing: print_module_dependencies(graph_config.module_name, dependencies)

    if graph_config.include_independent: graph.add_node(pydot.Node(graph_config.module_name, shape="circle"))

    if len(dependencies) > 0:
        # Create node for the current module
        graph.add_node(pydot.Node(graph_config.module_name, shape="circle"))
        for dep in dependencies:
            # Create node and edge from the dependency to the current module
            graph.add_node(pydot.Node(dep, shape="circle"))
            graph.add_edge(pydot.Edge(dep, graph_config.module_name, color="black", dir="forward"))
            # Recursive Step: For each dependency call the function again
            graph_config.module_name = dep
            if graph_config.recursive and dep not in parsed_modules: graph_module_dependencies(graph_config, parsed_modules, graph)
    return graph

### GRAPH A SET OF MODULES

def graph_modules(graph_config, parsed_modules):
    # Create graph object from pydot library
    graph = pydot.Dot(f'dependency_tree_{graph_config.command}', graph_type="graph", bgcolor="white")
    modules_list = get_module_list(graph_config.command)
    for mod in modules_list:
        graph_config.module_name = mod
        graph = graph_module_dependencies(graph_config, parsed_modules, graph)
    return graph

def draw_graph(graph_config, parsed_modules):
    # Call dependencies function according to the command line argument given
    if graph_config.module_name == None:
        graph = graph_modules(graph_config, parsed_modules)
        # To give a name to the output file
        graph_config.module_name = graph_config.command
    # Otherwise, a module was selected
    else:
        graph = graph_module_dependencies(graph_config, parsed_modules)
        # Change format of module name to create an output file with its name
        graph_config.module_name = graph_config.module_name.replace("/","-")

    # Draw the graph with the respective format chosen
    valid_formats = ["png", "svg", "dot", "raw"]
    period = graph_config.output_file.find(".")
    output_format = graph_config.output_file[period+1:]
    if (output_format not in valid_formats) or (period == -1):
        print("Output file format not valid. Default to raw")
        output_format = "raw"

    if output_format == "png":
        graph.write_png(graph_config.output_file)
    elif output_format == "svg":
        graph.write_svg(graph_config.output_file)
    elif output_format == "dot":
        graph.write_dot(graph_config.output_file)
    elif output_format ==  "raw":
        print(graph.to_string())

def main():
    # Set to keep track of modules already parsed
    parsed_modules = set()

    # Parse command line arguments
    parser = parse_command_line()

    # Capture the arguments provided in the command line into the Graph Config object
    args = parser.parse_args()
    graph_config = GraphConfig(
    module_name         =   args.module_name,
    command             =   args.command,
    output_file         =   args.output,
    show_parsing        =   args.print,
    include_independent =   args.include,
    )
    
    draw_graph(graph_config, parsed_modules)
    

if __name__ == "__main__":
    main()