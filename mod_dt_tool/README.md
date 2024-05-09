# Module-Dependencies-Tree (mod_dt)
A Python tool to list graph dependencies of modules in an HPCC environment utilizing Lmod.

## Installation

```bash
pip install mod_sd
```

## Usage

The Module Dependency Tree Tool (mod-dt) is used to list dependencies of modules in an HPCC environment. You can specify a particular module to show its dependencies or graph multiple modules using standard Lmod commands.

### Command-Line Arguments

- **`module_name`** (*optional*):  
  Name of the module to show dependencies for. Defaults to `None`.

- **`-h`, `--help`**:  
  Show the help message and exit.

- **`-c`, `--command`** (*optional*):  
  Use a standard Lmod command to graph (`list`, `avail`, `spider`). Defaults to `list`.  
  Example: `-c avail`

- **`-o`, `--output`** (*optional*):  
  Specify the output file name and format for the dependency graph (supported: `dot`, `png`, `svg`, `raw`). Defaults to `.raw` dot format.  
  Example: `-o tree.png`

- **`-p`, `--print`** (*optional*):  
  If set, print detailed parsing information of module dependencies.

- **`-i`, `--include`** (*optional*):  
  If set, include modules without dependencies in the output.

### Example Usage

1. **List All Modules with Default Graph Format (`.raw`):**
   ```bash
   mod-dt
   ```

2. **Graph Dependencies of a Specific Module (`exampleModule`):**
   ```bash
   mod-dt exampleModule -o tree.png
   ```

3. **Graph Using Lmod's `avail` Command:**
   ```bash
   mod-dt -c avail -o modules.svg
   ```

4. **Print Detailed Parsing Information and Include Independent Modules:**
   ```bash
   mod-dt -p -i
   ```

5. **Show Help Information:**
   ```bash
   mod-dt -h
   ```

### Examples in Context

- To list dependencies of all modules available using `list` and output in `png` format:
  ```bash
  mod-dt -c list -o all_modules.png
  ```

- To graph dependencies of a specific module named `science` in `dot` format:
  ```bash
  mod-dt science -o science.dot
  ```

- To graph modules with `spider` and include parsing details:
  ```bash
  mod-dt -c spider -p -o spider_tree.png
  ```
