# AutoScaling-as-a-Service
Deployed Virtual Private Cloud (VPC) and created AutoScaling-as-a-Service application that Scales-up/down Virtual Machines (or Containers) on-demand to maintain steady, predictable performance. Networking Infrastructure consists of Linux Bridges (NAT/DHCP and L2), Network Namespaces acting as Loadbalancers and Firewalls, and Controller Node for each Tenant. VPC is designed to achieve L2/L3 isolation among Tenants.

ISO Used: https://mirror.umd.edu/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-1908.iso

Packages in ISO: Collectd, DHCP

* Update the list of Hypervisors in JSON file
* Generate SSH keys of manager node and add SSH Keys into all Hypervisors
* Find the best hypervisor and create management network
* Create namespaces, bridges, veth pairs, and VxLANs
* Create Controller node in the best hypervisor
* Create DHCP file and Collectd server file

* Configure DHCP and Collectd in server

* Create application VMs and update the running JSON file
* Reboot the VMs to change the hostname

* Push collectd files into all VMs

* Collect all the ip addresses of VMs and Create IP tables
* Push iptables into the best hypervisor namespace

* Scale up/down logic
