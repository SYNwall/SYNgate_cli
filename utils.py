#!/usr/bin/python3
import copy
import ipaddress
import os
import re
import stat
from cmd import Cmd

import jinja2

DEFAULT_SYNGATE_CONF = '/etc/modprobe.d/SYNgate.conf'
TO_ADD = []
TO_REMOVE = set()
empty = {'psk_list': [], 'dstnet_list': [], 'precision_list': [], 'enable_antispoof_list': [], 'enable_udp_list': []}
OLD_CONFIGURATION = ''
OLD_TO_ADD = []
OLD_TO_REMOVE = set()


def parse_configuration_file(syngate_conf_path):

    content = ''

    try:
        with open(syngate_conf_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print('*** ERROR READING CONFIGURATION FILE: ', e)

    if content == '':
        return empty

    pattern = r'^options SYNgate psk_list=(?P<psk_list>.*?) dstnet_list=(?P<dstnet_list>.*?) precision_list=(?P<precision_list>.*?) enable_antispoof_list=(?P<enable_antispoof_list>.*?) enable_udp_list=(?P<enable_udp_list>.*)$'
    res = re.match(pattern, content)
    try:
        if res:
            res = res.groupdict()
            for k, v in res.items():
                v = v.split(',')
                res[k] = v if v != [''] else []
            return res
        else:
            print('*** ERROR PARSING CONFIGURATION FILE, CHECK FILE FORMAT')
            return None
    except Exception as e:
        print('*** ERROR PARSING CONFIGURATION FILE: ', e)
        return None


def print_table(content):
    print('#)\t{0:20} {1:45} {2:>10} {3:>10} {4:>10}'.format('DSTNET','PSK','PRECISION','ANTISPOOF','UDP'))
    i = 0
    while i < len(content['psk_list']):
        print('{0}{1:2})\t{2:20} {3:45} {4:>10} {5:>10} {6:>10}'.format('[remove]' if i in TO_REMOVE else '', i, content['dstnet_list'][i],
                                                 content['psk_list'][i], content['precision_list'][i],
                                                 content['enable_antispoof_list'][i], content['enable_udp_list'][i]))
        i += 1
    j = 0
    if TO_ADD:
        print('---------- TO ADD ----------')
    while j < len(TO_ADD):
        print('{0:2})\t{1:20} {2:45} {3:>10} {4:>10} {5:>10}'.format(i, TO_ADD[j][0], TO_ADD[j][1], TO_ADD[j][2], TO_ADD[j][3], TO_ADD[j][4]))
        i += 1
        j += 1


def check_values(net, psk, p, ea, eu):
    assert 32 <= len(psk) <= 1024, 'PSK LENGTH MUST BE BETWEEN 32 AND 1024'
    assert ea in ['0', '1'], 'ENABLE_ANTISPOOF MUST BE 0 OR 1'
    assert eu in ['0', '1'], 'ENABLE_UDP MUST BE 0 OR 1'

    try:
        p = int(p)
        assert 1 <= p <= 12, ''
    except:
        raise Exception('PRECISION MUST BE AN INTEGER BETWEEN 1 AND 12')

    try:
        ipaddress.IPv4Network(net)
    except:
        raise Exception('INVALID NETWORK')


def update_configuration_file(syngate_conf, syngate_conf_path):
    global OLD_CONFIGURATION
    try:
        OLD_CONFIGURATION = open(syngate_conf_path, 'w').read()
        pattern = r'options SYNgate psk_list={% for psk in psk_list %}{{ psk }}{{ "," if not loop.last }}{% endfor %} ' \
                  r'dstnet_list={% for dstnet in dstnet_list %}{{ dstnet }}{{ "," if not loop.last }}{% endfor %} ' \
                  r'precision_list={% for precision in precision_list %}{{ precision }}{{ "," if not loop.last }}{% endfor %} ' \
                  r'enable_antispoof_list={% for enable_antispoof in enable_antispoof_list %}{{ enable_antispoof }}{{ "," if not loop.last }}{% endfor %} ' \
                  r'enable_udp_list={% for enable_udp in enable_udp_list %}{{ enable_udp }}{{ "," if not loop.last }}{% endfor %}'
        configuration_template = jinja2.Template(pattern)
        syngate_configuration = configuration_template.render(syngate_conf)
        # TODO save copy and test new configuration
        with open(syngate_conf_path, 'w') as f:
            f.write(syngate_configuration)
        f.close()
        os.chmod(syngate_conf_path,stat.S_IRUSR | stat.S_IWUSR)
        return True
    except:
        OLD_CONFIGURATION = ''
        return None


def merge_old_and_new_configuration():
    global OLD_TO_REMOVE, OLD_TO_ADD
    content = parse_configuration_file(syngate_conf)
    new_content = copy.deepcopy(empty)
    OLD_TO_REMOVE = TO_REMOVE
    for i in range(0, len(content['psk_list'])):
        if i not in TO_REMOVE:
            new_content['psk_list'].append(content['psk_list'][i])
            new_content['dstnet_list'].append(content['dstnet_list'][i])
            new_content['precision_list'].append(content['precision_list'][i])
            new_content['enable_antispoof_list'].append(content['enable_antispoof_list'][i])
            new_content['enable_udp_list'].append(content['enable_udp_list'][i])
        else:
            TO_REMOVE.remove(i)
    OLD_TO_ADD = TO_ADD
    while TO_ADD:
        net, psk, p, ea, eu = TO_ADD.pop(0)
        new_content['psk_list'].append(psk)
        new_content['dstnet_list'].append(net)
        new_content['precision_list'].append(p)
        new_content['enable_antispoof_list'].append(ea)
        new_content['enable_udp_list'].append(eu)
    return new_content

def banner():
    print()
    print('      ^ ^')
    print('     |. o|')
    print('     \\ : /')
    print('      | |')
    print('    <#####>')
    print('  <#SYNwall#>')
    print('    <#####>')

class SyngateConfPrompt(Cmd):
    prompt = 'sg> '
    intro = "Syngate configurator, type ? to list commands"

    def do_list(self, inp):
        content = parse_configuration_file(syngate_conf)
        if content is not None:
            print_table(content)

    def help_list(self):
        print('List the content of the configuration file')

    def do_add(self, inp):
        try:
            net, psk, p, ea, eu = inp.split()
        except:
            print('*** MISSING ARGUMENTS: SEE HELP')
            return

        try:
            check_values(net, psk, p, ea, eu)
            TO_ADD.append(inp.split())
        except Exception as e:
            print('*** ERROR: ', e)

    def help_add(self):
        print('Add a new configuration (only in memory)\n'
              'Usage: add network psk precision enable_antispoof enable_udp\n'
              'Example: add 10.0.0.0/8 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 10 0 1')

    def do_exit(self, inp):
        os.chmod(DEFAULT_SYNGATE_CONF,stat.S_IRUSR | stat.S_IWUSR)
        if TO_ADD or TO_REMOVE:
            if input('You have unsaved work, want to exit anyway? (y): '):
                return True
        else:
            return True

    def help_exit(self):
        print('Check for unsaved work and exit')

    def do_save(self, inp):
        new_configuration = merge_old_and_new_configuration()
        update_configuration_file(new_configuration, syngate_conf)

    def help_save(self):
        print('Save new syngate configuration file')

    def do_remove(self, inp):
        try:
            inp = int(inp)
            if inp < 0:
                raise Exception()
        except:
            print('*** ERROR: ARGUMENT INVALID, MUST BE AN INTEGER >= 0')
            return

        content = parse_configuration_file(syngate_conf)
        if inp < len(content['psk_list']):
            TO_REMOVE.add(inp)
        elif inp < len(TO_ADD) + len(content['psk_list']):
            TO_ADD.pop(inp - len(content['psk_list']))
        else:
            print('*** ERROR: ARGUMENT TOO HIGH')

    def help_remove(self):
        print('Remove an element by its numeric position (use list)')

    def do_setconf(self, inp):
        global syngate_conf
        if os.path.isfile(inp):
            syngate_conf = inp
        else:
            print('*** ERROR: NOT A VALID FILE')

    def help_setconf(self):
        print('Set a new path for the syngate configuration file')

    def do_getconf(self, inp):
        print(syngate_conf)

    def help_getconf(self):
        print('Print the path of the syngate conf')

    def do_restart(self, inp):
        global TO_ADD
        global TO_REMOVE
        os.system('rmmod SYNgate')
        os.system('modprobe SYNgate')
        r = os.popen('cat /etc/services').read()
        if re.match(r'^SYNgate\s+\d+\s+\d+', r):
            print('successfully restarted')
        else:
            TO_REMOVE = OLD_TO_REMOVE
            TO_ADD = OLD_TO_ADD
            os.system('rmmod SYNgate')
            with open(syngate_conf, 'w') as f:
                f.write(OLD_CONFIGURATION)
            os.system('modprobe SYNgate')


    def help_restart(self):
        print('Save file and try to restart Syngate.'
              ' If the restart fails restores the old configuration and restarts again.'
              ' Needs superuser permissions')


if __name__ == '__main__':
    syngate_conf = DEFAULT_SYNGATE_CONF
    banner()
    SyngateConfPrompt().cmdloop()
