from __future__ import print_function
import os, sys,xml.etree.ElementTree as ET, paramiko, subprocess,libvir

def mgmt_network(nw_netmask, ip, tenant_name, nw_subnet):
    conn = libvirt.open('qemu+ssh://root@'+ip+'/system?keyfile=/root/.ssh/id_rsa')
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)
    nwtree=ET.parse('/home/vpmaddur/Project/'+tenant_name+'/etc/nokia-network-sample.xml')
    nwroot=nwtree.getroot()
    nw_name=nwroot.find('name')
    nw_name.text=tenant_name+"-dhcp-mgmt"
    id=nwroot.find('uuid')
    nwroot.remove(id)
    br_name=nwroot.find('bridge')
    br_name.attrib['name']=nw_name.text
    macaddr=nwroot.find('mac')
    nwroot.remove(macaddr)
    ipa=nwroot.find('ip')
    nw1 = nw_subnet.split(".")
    nw_subnet = ".".join(nw1[0:3])
    ipa.attrib['address']=nw_subnet+str(.1)
    ipa.attrib['netmask']=str(nw_netmask)
    dhc=ipa.find('dhcp')
    rang=dhc.find('range')
    rang.attrib['start']=nw_subnet+str(.2)
    rang.attrib['end']=nw_subnet+str(.254)
    nwtree.write('/home/vpmaddur/Project/'+tenant_name+'/etc/mgmt-network.xml')
    nwconfig=open('/home/vpmaddur/Project/'+tenant_name+'/etc/mgmt-network.xml', 'r')
    nwxml=nwconfig.read()
###############Create a persistent virtual network#################
    network = conn.networkCreateXML(nwxml)
    if network == None:
        print('Failed to create a virtual network', file=sys.stderr)
        exit(1)
    nwconfig.close()
    conn.close()
