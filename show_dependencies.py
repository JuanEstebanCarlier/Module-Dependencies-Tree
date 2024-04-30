import argparse
import subprocess
import pydot
import re

#TODO regex function from list of strings (input lines) to list of dependencies (for module spider)
'''
def get_dependencies_list():
'''

def extract_dependencies(input_list):
    output_list = []
    
    # Iterate over each string in the input list
    for item in input_list:
        if item.strip().startswith("depends_on") or item.strip().starswith("load"):
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

# Run a specific command for module and return the list of modules
def get_module_list(method):
    try:
        result = subprocess.run('module --terse ' + method, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'module {method}': {e}")

    return result.stdout.split()

# display the dependencies of each module that was looked into
def print_module_dependencies(module_name, dependencies):
    if len(dependencies)>0:
        print(module_name, "depends on:")
        for dep in dependencies:
            print(f"- {dep}")
    else:
        print(module_name, "has no dependencies")
    print()

### GRAPH A SINGLE MODULE

def graph_module_dependencies(module_name, graph = None, recursive = True):
    # Create graph object from pydot library
    if graph == None:
        graph = pydot.Dot("dependency_tree " + module_name, graph_type="graph", bgcolor="white")

    # Execute the module show command
    try:
        result = subprocess.run('module show ' + module_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'module show {module_name}': {e}")
        return

    # Parse the output for dependencies
    lines = result.stdout.split("\n")
    dependencies = extract_dependencies(lines)

    # Add module to parsed_modules set
    parsed_modules.add(module_name)

    # Call print function to print dependencies list
    if show_parsing: print_module_dependencies(module_name, dependencies)

    if include_independent: graph.add_node(pydot.Node(module_name, shape="circle"))

    if len(dependencies) > 0:
        # Create node for the current module
        graph.add_node(pydot.Node(module_name, shape="circle"))
        for dep in dependencies:
            # Create node and edge from the dependency to the current module
            graph.add_node(pydot.Node(dep, shape="circle"))
            graph.add_edge(pydot.Edge(dep, module_name, color="black", dir="forward"))
            # Recursive Step: For each dependency call the function again
            if recursive and dep not in parsed_modules: graph_module_dependencies(dep, graph, True)
    return graph    

### GRAPH A SET OF MODULES

def graph_modules(method):
    # Create graph object from pydot library
    graph = pydot.Dot("dependency_tree_" + method, graph_type="graph", bgcolor="white")
    modules_list = get_module_list(method)
    for mod in modules_list:
        graph = graph_module_dependencies(mod, graph, False)
    return graph

### MAIN

def main():
    # Parse command line arguments
    global show_parsing
    global include_independent
    global parsed_modules
    parsed_modules = set()

    lmod_commands = ["list", "avail", "spider"]
    
    parser = argparse.ArgumentParser(
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
                    help='Use a lmod command to graph (list, avail, spider). Default is list. Example: -c avail')
    parser.add_argument('-o', '--output', type=str, nargs='?', default='raw',
                    help='Specify the output file format for the dependency graph (supported: raw, dot, png, svg). Default is raw dot format. Example: -o png')
    parser.add_argument('-p', '--print', action='store_true',
                    help='If set, print detailed parsing information of module dependencies.')
    parser.add_argument('-i', '--include', action='store_true',
                    help='If set, include modules without dependencies in the output.')

    # Capture the arguments provided in the command line into variables
    args = parser.parse_args()
    module_name =           args.module_name
    command =               args.command
    output_format =         args.output
    show_parsing =          args.print
    include_independent =   args.include
    
    # Call dependencies function according to the command line argument given
    if module_name == None:
        graph = graph_modules(command)
        # To give a name to the output file
        module_name = command
    # Otherwise, a module was selected
    else:
        graph = graph_module_dependencies(module_name, None, True)
        # Change format of module name to create an output file with its name
        module_name = module_name.replace("/","-")

    # Draw the graph with the respective format chosen 
    if output_format == "png": 
        graph.write_png(module_name + "_module_dependencies." + output_format)
    elif output_format == "svg":
        graph.write_svg(module_name + "_module_dependencies." + output_format)
    elif output_format == "dot":
        graph.write_dot(module_name + "_module_dependencies." + output_format)
    elif output_format ==  "raw":
        print(graph.to_string())
        

if __name__ == "__main__":
    main()
