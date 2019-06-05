# Overview

This charm allows for the configuration of systemd-networkd RoutingPolicyRule.

# Usage

    juju deploy cs:~xenefix/routingpolicyrule
    juju add-relation routingpolicyrule ubuntu-lxd
    juju config routingpolicyrule policyroutes='100.64.0.1 100.64.2.1 100.64.6.1'
