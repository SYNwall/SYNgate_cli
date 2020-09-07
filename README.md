# SYNgate cli

This tool is useful to configure SYNgate without changing manually the configuration file

# Usage

You need to run the script with a user that has read/write permissions on the SYNgate configuration file.

Run the script to open an interactive prompt:

    $ ./utils.py 
    Syngate configurator, type ? to list commands
    sg> ?
    
    Documented commands (type help <topic>):
    ========================================
    add  exit  getconf  help  list  remove  restart  save  setconf

Here you can visualize and modify the current configuration.

    sg> list
    #)      DSTNET  PSK     PRECISION       ENABLE_ANTISPOOF        ENABLE_UDP
    0)      10.0.0.0/8      xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx        10      0       1
    1)      10.5.0.0/16     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx        10      0       1
    2)      10.5.3.0/24     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx        10      0       1

# Requirements

You need python 3 and the jinja2 module
