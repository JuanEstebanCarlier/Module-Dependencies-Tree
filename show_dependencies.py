import argparse
import subprocess
import pydot
import re

#TODO regex function from list of strings (input lines) to list of dependencies (ideally for both module spider and module avail)
def get_dependencies_list():
    print()

def extract_dependencies(input_list):
    output_list = []
    
    # Iterate over each string in the input list
    for item in input_list:
        if item.strip().startswith("depends_on"):
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

def get_active_module_list():
    try:
        result = subprocess.run('module tablelist', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'module show {module_name}': {e}")

    tablelist_pattern = r'\["(.*?)"\] = "(.*?)"'

    # Find all matches of the pattern and turn them into a list
    matches = re.findall(tablelist_pattern, result.stdout)
    active_module_list = [key+'/'+value for key, value in matches]

    return active_module_list 

def get_avail_module_list():
    try:
        result = subprocess.run('module avail', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'module show {module_name}': {e}")

    avail_module_list = []
    lines = result.stdout.split()
    for potential in lines:
        if ((potential.count("/") == 1) or potential.startswith("quartus")) and (not potential.startswith("foo")):
            avail_module_list.append(potential)
    return avail_module_list

# TODO try using module spider
'''
def get_full_modules_list():
    try:
        result = subprocess.run('module spider', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'module show {module_name}': {e}")

    full_modules = []
    lines = result.stdout.split()
    for potential in lines:
        if ((potential.count("/") == 1) or potential.startswith("quartus")) and (not potential.startswith("foo")):
            full_modules.append(potential)
    return full_modules
'''

def print_module_dependencies(module_name, dependencies):
    if len(dependencies)>0:
        print(module_name, "depends on:")
        for dep in dependencies:
            print(f"- {dep}")
    else:
        print(module_name, "has no dependencies")

def graph_module_dependencies(module_name, graph = None, recursive = True):
    # Create graph object from pydot library
    if graph == None:
        graph = pydot.Dot("dependency_tree"+ " " + module_name, graph_type="graph", bgcolor="white")

    # Execute the module show command
    try:
        result = subprocess.run('module show' + " " + module_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'module show {module_name}': {e}")
        return

    # Parse the output for dependencies
    lines = result.stdout.split("\n")
    dependencies = extract_dependencies(lines)

    # Call print function to print dependencies list
    print_module_dependencies(module_name, dependencies)

    if len(dependencies) > 0:
        # Create node for the current module
        graph.add_node(pydot.Node(module_name, shape="circle"))
        for dep in dependencies:
            # Create node and edge from the dependency to the current module
            graph.add_node(pydot.Node(dep, shape="circle"))
            graph.add_edge(pydot.Edge(dep, module_name, color="black", dir="forward"))
            # Recursive Step: For each dependency call the function again
            if recursive:
                graph_module_dependencies(dep, graph, True)
    return graph    

def graph_module_available():
    # Create graph object from pydot library
    graph = pydot.Dot("dependency_tree_avail", graph_type="graph", bgcolor="white")
    available_list_modules = get_avail_module_list()
    for mod in available_list_modules:
        graph = graph_module_dependencies(mod, graph, False)
    return graph

def graph_module_active():
    # Create graph object from pydot library
    graph = pydot.Dot("dependency_tree_active", graph_type="graph", bgcolor="white")
    available_list_modules = get_active_module_list()
    for mod in available_list_modules:
        graph = graph_module_dependencies(mod, graph, False)
    return graph

def graph_module_all():
    # Create graph object from pydot library
    graph = pydot.Dot("dependency_tree_all", graph_type="graph", bgcolor="white")
    full_modules_list = get_full_modules_list()
    for mod in full_list_modules:
        graph = graph_module_dependencies(mod, graph, False)
    return graph   

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='List dependencies of a module in an HPCC environment.')
    parser.add_argument('module_name', type=str, nargs='?', default='active', help='Name of the module to show dependencies for. If not provided, will default to active modules.')
    parser.add_argument('image_format', type=str, nargs='?', default='.svg', help='Type of output file for creating the graph. If not provided, will default to .svg.')
    
    # Parse and store the arguments provided in the command line
    args = parser.parse_args()
    module_name = args.module_name
    image_format = args.image_format
    
    # Call dependencies function according to the command line argument chosen
    if module_name == "active":
        graph = graph_module_active()
    elif module_name == "available":
        graph = graph_module_available()
    elif module_name == "all":
        graph = graph_module_all()
    # Specific module was selected
    else:
        graph = graph_module_dependencies(module_name)
        # Make it possible to create a file with its name
        module_name = module_name.replace("/","-")

    # Draw the graph with the respective format chosen 
    if image_format == ".png": 
        graph.write_png(module_name + "_module_dependencies" + image_format)
    elif image_format == ".svg":
        graph.write_svg(module_name + "_module_dependencies" + image_format)
        

if __name__ == "__main__":
    main()
