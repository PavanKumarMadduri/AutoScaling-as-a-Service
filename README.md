# AutoScaling-as-a-Service
Deployed Virtual Private Cloud (VPC) and created AutoScaling-as-a-Service application that Scales-up/down Virtual Machines (or Containers) on-demand to maintain steady, predictable performance. Networking Infrastructure consists of Linux Bridges (NAT/DHCP and L2), Network Namespaces acting as Loadbalancers and Firewalls, and Controller Node for each Tenant. VPC is designed to achieve L2/L3 isolation among Tenants.

ISO Used: https://mirror.umd.edu/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-1908.iso

Packages in ISO: Collectd, DHCP

