from __future__ import print_function
import os, sys,xml.etree.ElementTree as ET, paramiko, subprocess,libvirt, datetime

running={}

def vm_start(tenant_name,net,cpy_ip,count,ssh):
###############Definfing & starting a VM#################
	conn = libvirt.open('qemu+ssh://root@'+cpy_ip+'/system?keyfile=/root/.ssh/id_rsa')
	if conn == None:
		print('Failed to open connection to qemu:///system', file=sys.stderr)
		exit(1)

	xmlconfig=open('/home/vpmaddur/Project/'+tenant_name+'/etc/'+tenant_name+'-'+net["Name"]+'-'+str(count)+'.xml', 'r')
	xml=xmlconfig.read()
	dom=conn.defineXML(xml)
	if dom == None:
		print('Failed to define a domain from an XML definition.', file=sys.stderr)
		exit(1)
	if dom.create() < 0:
		print('Can not boot guest domain.', file=sys.stderr)
		exit(1)
	print('Guest '+dom.name()+' has booted', file=sys.stderr)
	ssh.exec_command('virsh dumpxml '+tenant_name+'-'+net["Name"]+'-'+str(count)+' > /home/vpmaddur/Project/'+tenant_name+'/etc/'+tenant_name+'-'+net["Name"]+'-'+str(count)+'.xml')
        running[net["Name"]]=[count, str(datetime.datetime.now())]
        conn.close()

        with open('/home/vpmaddur/Project/'+tenant_name+'/current.json', 'w') as outfile:
                json.dump(running, outfile)

def vm_create(tenant_name, net, vm, network,bst_hyp):
	tree = ET.parse('/home/vpmaddur/Project/'+tenant_name+'/'+tenant_name+'-vm.xml')
	root = tree.getroot()
#######Changing VM Name###########
	vm_name=root.find('name')
	vm_name.text=tenant_name+'-'+net["Name"]+'-'+str(vm)
##########Configuration#############
	vm_vcpu=root.find('vcpu')
	vm_vcpu.text=str(net["vcpu"])
	vm_mem=root.find('memory')
	vm_mem.text=str(net["memory(in KB)"])
	current_mem=root.find("currentMemory")
	root.remove(current_mem)
######Deleting UUID Tag##########
	ide=root.find('uuid')
	root.remove(ide)
#####Changing the Source File Attribute#########
	def img_source():
		dev = root.find('devices')
		for dsk in dev.findall('disk'):
			if dsk.attrib['device'] == 'disk':
				src = dsk.find('source')
				src.attrib["file"] = str('/home/vpmaddur/Project/'+tenant_name+'/etc/'+tenant_name+'-'+net["Name"]+'-'+str(vm)+'.img')
	img_source()
######Attaching the interfaces######
	def attach_interface(net):
		dev = root.find('devices')
		if net["Name"] != "mgmt":
			face = ET.SubElement(dev, 'interface',attrib={'type':'bridge'})
			nw = ET.SubElement(face, 'source',attrib={'bridge':tenant_name+"-"+net["Name"]+'-br'})
			mod=ET.SubElement(face, 'model',attrib={'type':'virtio'})
			face = ET.SubElement(dev, 'interface',attrib={'type':'bridge'})
			nw = ET.SubElement(face, 'source',attrib={'bridge':tenant_name+'-mgmt-br'})
			mod=ET.SubElement(face, 'model',attrib={'type':'virtio'})
		else:
			for netwrk in network:
				face = ET.SubElement(dev, 'interface',attrib={'type':'bridge'})
                		nw = ET.SubElement(face, 'source',attrib={'bridge':tenant_name+"-"+netwrk["Name"]+'-br'})
                		mod=ET.SubElement(face, 'model',attrib={'type':'virtio'})
	attach_interface(net)
######Creating New XML######################
	tree.write('/home/vpmaddur/Project/'+tenant_name+'/etc/'+tenant_name+'-'+net["Name"]+'-'+str(vm)+'.xml')
	subprocess.call('scp -o StrictHostKeyChecking=no /home/vpmaddur/Project/'+tenant_name+'/etc/'+tenant_name+'-'+net["Name"]+'-'+str(vm)+'.xml root@'+bst_hyp+':/home/vpmaddur/Project/'+tenant_name+'/etc/', shell=True)
