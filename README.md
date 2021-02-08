# SYNgate CLI

This tool is useful to configure SYNgate without changing manually the configuration file

# Usage

You need to run the script with a user that has read/write permissions on the SYNgate configuration file.

Run the script to open an interactive prompt:

    > sudo ./sg_shell.py 
    
          ^ ^
         |. o|
         \ : /
          | |
        <#####>
      <#SYNwall#>
        <#####>
    SYNgate configurator, type ? to list commands
    sg> ?
    
    Documented commands (use 'help -v' for verbose/'help <topic>' for details):
    ===========================================================================
    add    exit     history  py      restart       save     shell    
    alias  getconf  list     quit    run_pyscript  set      shortcuts
    edit   help     macro    remove  run_script    setconf
    
    sg>

Here you can visualize and modify the current configuration.

    sg> list
    #)	DSTNET               PSK                                            PRECISION  ANTISPOOF        UDP
     0)	192.168.1.0/24       XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX           10          0          0
     1)	10.0.0.0/24          XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX           10          0          0
     2)	192.168.20.1/32      XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX           10          0          1

# Requirements

You need Python3 with cmd2 and jinja modules.
