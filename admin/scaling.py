from __future__ import print_function
import json, datetime, libvirt, time, paramiko, sys, subprocess, re, xml.etree.ElementTree as ET, stat, shutil, os
#nw=sys.argv[1]
#no=sys.argv[2]
def hypervisor():
	with open('/home/PK/ASS/admin/hypervisor.json', 'r') as hyper:
		hyper_dict=json.load(hyper)
		mem_list=[]
		mem_dict={}
	for ip in hyper_dict:
		for mgmt_ip in ip["ip_list"]:
			hyp,vm=mgmt_ip.split(':')
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(hyp, port=22, username='ece792', password='EcE792net!')
                        vmtransport = ssh.get_transport()
			dest_addr = (vm, 22)
			local_addr = (hyp, 22)
			vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
			dhost = paramiko.SSHClient()
                        dhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        dhost.connect(vm, port=22, username='ece792', password='EcE792net!', sock=vmchannel)
			stdin, stdout, stderr = dhost.exec_command('cat /proc/meminfo  | grep MemFree | awk \'{print $2}\'')
			mem=stdout.readlines()
			dhost.close()
			ssh.close()
			mem_dict[mgmt_ip]=mem[0].strip()
			mem_list.append(dict(mem_dict))
	final_hyp=mem_list[0]
	return final_hyp

def vm_sup(vm):
	with open('/home/PK/ASS/etc/nokia/nokia.json', 'r') as input:
		input_dict = json.load(input)
###################Setting up infrastructure(Bridges & Veth Pairs)####################
	for tenant in input_dict:
		tenant_name = tenant["Name"]
		for net1 in tenant['Networks']:
			if net1['Name']=='dns':
				net=net1
				print(net)

	vm=vm+1
	tree = ET.parse('/home/PK/ASS/etc/nokia/nokia-sample.xml')
	root = tree.getroot()
########Creating a copy of img file#######
	shutil.copy2('/home/PK/ASS/etc/nokia/nokia-sample.img', '/home/PK/ASS/etc/nokia/nokia-'+net["Name"]+'-'+str(vm)+'.img')
#######Preserving the File Permissions#########
	st = os.stat('/home/PK/ASS/etc/nokia/nokia-sample.img')
	os.chown('/home/PK/ASS/etc/nokia/nokia-'+net["Name"]+'-'+str(vm)+'.img', st[stat.ST_UID], st[stat.ST_GID])
#######Changing VM Name###########
	vm_name=root.find('name')
	vm_name.text='nokia-'+net["Name"]+'-'+str(vm)
##########Configuration#############
	vm_vcpu=root.find('vcpu')
	vm_vcpu.text=str(net["vcpu"])
	vm_mem=root.find('memory')
	vm_mem.text=str(net["memory(in KB)"])
	current_mem=root.find("currentMemory")
	root.remove(current_mem)
######Deleting UUID Tag##########
	id=root.find('uuid')
	root.remove(id)
#####Changing the Source File Attribute#########
	def img_source():
		dev = root.find('devices')
		for dsk in dev.findall('disk'):
			if dsk.attrib['device'] == 'disk':
				src = dsk.find('source')
				src.attrib["file"] = str('/home/PK/ASS/etc/nokia/nokia-'+net["Name"]+'-'+str(vm)+'.img')
	img_source()
######Attaching the interfaces######
	def attach_interface(net):
		dev = root.find('devices')
		if net["Name"] != "mgmt":
			face = ET.SubElement(dev, 'interface',attrib={'type':'bridge'})
			nw = ET.SubElement(face, 'source',attrib={'bridge':tenant_name+"-"+net["Name"]})
			mod=ET.SubElement(face, 'model',attrib={'type':'virtio'})
			face = ET.SubElement(dev, 'interface',attrib={'type':'network'})
			nw = ET.SubElement(face, 'source',attrib={'network':tenant_name+'-'+'mgmt'})
			mod=ET.SubElement(face, 'model',attrib={'type':'virtio'})
		else:
			for net in tenant['Networks']:
				face = ET.SubElement(dev, 'interface',attrib={'type':'bridge'})
                		nw = ET.SubElement(face, 'source',attrib={'bridge':tenant_name+"-"+net["Name"]})
                		mod=ET.SubElement(face, 'model',attrib={'type':'virtio'})
	attach_interface(net)
######Creating New XML######################
	tree.write('/home/PK/ASS/etc/nokia/nokia-'+net["Name"]+'-'+str(vm)+'.xml')

###############Definfing & starting a VM#################
	conn = libvirt.open('qemu:///system')
	if conn == None:
		print('Failed to open connection to qemu:///system', file=sys.stderr)
		exit(1)

	xmlconfig=open('/home/PK/ASS/etc/nokia/nokia-'+net["Name"]+'-'+str(vm)+'.xml', 'r')
	xml=xmlconfig.read()
	dom=conn.defineXML(xml)
	if dom == None:
		print('Failed to define a domain from an XML definition.', file=sys.stderr)
		exit(1)
	if dom.create() < 0:
		print('Can not boot guest domain.', file=sys.stderr)
		exit(1)
	print('Guest '+dom.name()+' has booted', file=sys.stderr)
	subprocess.call('virsh dumpxml nokia-'+net["Name"]+'-'+str(vm)+' > /home/PK/ASS/etc/nokia/nokia-'+net["Name"]+'-'+str(vm)+'.xml', shell=True)
	conn.close()

def scalingup():
	hyper=hypervisor()
	hype,vme=list(hyper.keys())[0].split(':')
	with open('/home/PK/ASS/etc/nokia/run1.json', 'r') as run1:
		run_dict=json.load(run1)
		#print(run_dict)
	hyp_list=[]
	for json2 in run_dict:
	        hyp_list.append(json2['hip'].strip())
	index=hyp_list.index(vme)
	count=subprocess.call('cat dns | wc -l', shell=True)
	if vme in hyp_list:
		print("HIP already present")
		vm_sup(count)
		
	else:
		vm_dict={"hip":vme, "networks":[]}
		run_dict.append(dict(vm_dict))
#		print(run_dict)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hype, port=22, username='ece792', password='EcE792net!')
               	vmtransport = ssh.get_transport()
               	dest_addr = (vme, 22)
               	local_addr = (hype, 22)
                vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
                dhost = paramiko.SSHClient()
                dhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                dhost.connect(vme, port=22, username='ece792', password='EcE792net!', sock=vmchannel)
                with open('/home/PK/ASS/etc/nokia/nokia.json') as input1:
			input_dict=json.load(input1)
		for bridge in input_dict:
			tenant_name=bridge['Name']
			stdin, stdout, stderr = dhost.exec_command('ip netns add '+tenant_name)
			stdin, stdout, stderr = dhost.exec_command('ip netns exec '+tenant_name+' brctl addbr '+tenant_name)
			stdin, stdout, stderr = dhost.exec_command('ip netns exec '+tenant_name+' ip link set '+tenant_name+' up')
			stdin, stdout, stderr = dhost.exec_command('ip netns exec '+tenant_name+' ip link set lo up')
			for br in bridge["Networks"]:
				stdin, stdout, stderr = dhost.exec_command('brctl addbr '+tenant_name+"-"+br["Name"])
				stdin, stdout, stderr = dhost.exec_command('ip link set '+tenant_name+"-"+br["Name"]+' up')
				stdin, stdout, stderr = dhost.exec_command('ip link add '+br["Name"]+' type veth peer name '+br["Name"]+'-'+tenant_name)
                       		stdin, stdout, stderr = dhost.exec_command('ip link set '+br["Name"]+'-'+tenant_name+' up')
                       		stdin, stdout, stderr = dhost.exec_command('brctl addif '+tenant_name+"-"+br["Name"]+' '+br["Name"]+'-'+tenant_name)
                       		stdin, stdout, stderr = dhost.exec_command('ip link set '+br["Name"]+' netns '+tenant_name+' up')
                       		stdin, stdout, stderr = dhost.exec_command('ip netns exec '+tenant_name+' brctl addif '+tenant_name+' '+br["Name"])
				nw_dict={br["Name"]:[]}
				run_dict[-1]['networks'].append(dict(nw_dict))
		dhost.close()
		ssh.close()
#		print(run_dict)
		vm_sup(count)
scalingup()