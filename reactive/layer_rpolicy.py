import subprocess

from charmhelpers.core.hookenv import (application_version_set, config, log,
                                        status_set)
from charmhelpers.core.host import mkdir
from charmhelpers.fetch import get_upstream_version
from charms.reactive import set_flag, when, when_not
from netaddr import IPAddress, IPNetwork
from ruamel import yaml

yaml = yaml.YAML()

@when('config.set.policyroutes')
def set_message_policy():
    policyRoutes = config('policyroutes')
    table = 101
    yaml.preserve_quotes = True
    try:
        with open('/etc/netplan/99-juju.yaml') as fp:
            data = yaml.load(fp)
    except FileNotFoundError:
        with open('/etc/netplan/50-cloud-init.yaml') as fp:
            data = yaml.load(fp)

    fp.close()

    policyRoutes_list = []
    for gateway4_policy in str.split(policyRoutes, " "):
        policyRoutes_list.append(IPAddress(gateway4_policy))

    for elem in data['network']['ethernets']:
        try:
            del data['network']['ethernets'][elem]['gateway4']
        except TypeError:
            pass
        except KeyError:
            pass
        for address in data['network']['ethernets'][elem]['addresses']:
            cidr = str(IPNetwork(address).cidr)
            for policyRoutes in policyRoutes_list:
                if policyRoutes in IPNetwork(address):
                    data['network']['ethernets'][elem]['routes'] = [{'to': '0.0.0.0/0', 'via': str(policyRoutes), 'table': table}]
                    data['network']['ethernets'][elem]['routing-policy'] = [{'from': cidr, 'priority': 100, 'table': table},{'from': cidr, 'to': cidr, 'table': 0}]
                    table += 1
                    break
            break
        try:
            del data['network']['ethernets'][elem]['addresses']
        except KeyError:
            pass
        try:
            del data['network']['ethernets'][elem]['mtu']
        except KeyError:
            pass
        try:
            del data['network']['ethernets'][elem]['set-name']
        except KeyError:
            pass
        try:
            del data['network']['ethernets'][elem]['nameservers']
        except KeyError:
            pass

    f= open("/etc/netplan/48-routingpolicy.yaml","w+")
    yaml.dump(data, f)
    f.close()

    cmd = 'netplan generate --debug'
    netplan_generate = subprocess.check_output(cmd, shell=True)
    log(netplan_generate)
    cmd = 'netplan apply --debug'
    netplan_apply = subprocess.check_output(cmd, shell=True)
    log(netplan_apply)
    status_set('active', 'RoutingPolicyRule applied' )