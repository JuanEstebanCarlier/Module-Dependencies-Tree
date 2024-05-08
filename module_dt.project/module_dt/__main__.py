from module_dt import module_dt
def main():
    # Set to keep track of modules already parsed
    parsed_modules = set()

    # Parse command line arguments
    parser = module_dt.parse_command_line()

    # Capture the arguments provided in the command line into the Graph Config object
    args = parser.parse_args()
    graph_config = module_dt.GraphConfig(
    module_name         =   args.module_name,
    command             =   args.command,
    output_file         =   args.output,
    show_parsing        =   args.print,
    include_independent =   args.include,
    )
    
    module_dt.draw_graph(graph_config, parsed_modules)
    

if __name__ == "__main__":
    main()