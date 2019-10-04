import paramiko, json, sys, subprocess, vm

tenant_name=sys.argv[1]
with open('/home/vpmaddur/Project/admin/'+tenant_name+'-hypervisor.json') as hypervisor_list:
    tenant_hyper_list=json.load(hypervisor_list)
###########Finding the Hypervisor with high free memory########################
def best_hypervisor():
#	with open('/home/vpmaddur/Project/admin/'+tenant_name+'-hypervisor.json') as hypervisor_list:
#		tenant_hyper_list=json.load(hypervisor_list)
	free_memory=0
	for ip in tenant_hyper_list[0]["ip_list"]:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(ip, port=22, username='root',  key_filename='/root/.ssh/id_rsa')
		stdin, stdout, stderr = ssh.exec_command('cat /proc/meminfo  | grep MemFree | awk \'{print $2}\'')
		hypervisor_memory=int(stdout.readlines()[0].strip())
		ssh.close()
		if hypervisor_memory > free_memory:
			free_memory=hypervisor_memory
			free_hyp=ip
	return ip
######################### Create Infrastrcuture in all Hypervisors#################
#with open('/home/admin/'+tenant_name+'/'+tenant_name+'-hypervisor.json') as hypervisor_list:
#	tenant_hyper_list=json.load(hypervisor_list)

with open('/home/vpmaddur/Project/'+tenant_name+'/'+tenant_name+'.json') as json_input:
	tenant_input=json.load(json_input)

for ip in tenant_hyper_list[0]["ip_list"]:
        print(ip)
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(ip)
	ssh.connect(ip, port=22, username='root', key_filename='/root/.ssh/id_rsa')
#	ssh.exec_command('mkdir /home/admin/'+tenant_name)
#	ssh.exec_command('mkdir /home/'+tenant_name)
#	ssh.exec_command('mkdir /home/'+tenant_name+'/etc')
#	ssh.exec_command('mkdir /home/'+tenant_name+'/var')
	ssh.exec_command('ip netns add '+tenant_name)
	ssh.exec_command('ip netns exec '+tenant_name+' brctl addbr '+tenant_name)
	ssh.exec_command('ip netns exec '+tenant_name+' ip link set '+tenant_name+' up')
	ssh.exec_command('ip netns exec '+tenant_name+' ip link set lo up')
	network=tenant_input[0]["Networks"]
	vxlan=40
	for net in network:
		ssh.exec_command('brctl addbr '+tenant_name+"-"+net["Name"]+'-br')
		ssh.exec_command('ip link set '+tenant_name+"-"+net["Name"]+'-br'+' up')
		ssh.exec_command('ip link add '+net["Name"]+' type veth peer name '+net["Name"]+'-'+tenant_name)
		ssh.exec_command('ip link set '+net["Name"]+'-'+tenant_name+' up')
		ssh.exec_command('brctl addif '+tenant_name+"-"+net["Name"]+'-br'+' '+net["Name"]+'-'+tenant_name)
		ssh.exec_command('ip link set '+net["Name"]+' netns '+tenant_name+' up')
		ssh.exec_command('ip netns exec '+tenant_name+' brctl addif '+tenant_name+' '+net["Name"])
		ssh.exec_command('ip link add name '+tenant_name+'-'+net["Name"]+'-vx type vxlan id '+str(vxlan)+' dev eth0 dstport 4789')
		ssh.exec_command('ip link set dev '+tenant_name+'-'+net["Name"]+'-vx up')
		ssh.exec_command('brctl addif '+tenant_name+"-"+net["Name"]+'-br'+' '+tenant_name+'-'+net["Name"]+'-vx')
		for vxlan_ip in tenant_hyper_list[0]["ip_list"]:
			if vxlan_ip!=ip:
				ssh.exec_command('bridge fdb append to 00:00:00:00:00:00 dst '+vxlan_ip+' dev '+net["Name"]+'-vx')
		vxlan+=1
	ssh.close()
##############################Create VMs################
for net in network:
	if net["Name"]!="mgmt":
		for count in range(net["Min"]):
			bst_hyp=best_hypervisor()
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(bst_hyp, port=22, username='root' , key_filename='/root/.ssh/id_rsa')
			vm.vm_create(tenant_name, net, count, network,bst_hyp)
                        stdin, stdout, stderr = ssh.exec_command('cp /home/vpmaddur/Project/admin/'+tenant_name+'.img /home/vpmaddur/Project/'+tenant_name+'/etc/'+tenant_name+'-'+net["Name"]+'-'+str(count)+'.img')
                        print(stderr.readlines())
                        vm.vm_start(tenant_name,net,bst_hyp,count,ssh)
			ssh.close()
	else:
		count=0
		bst_hyp=best_hypervisor()
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(bst_hyp, port=22, username='root',  key_filename='/root/.ssh/id_rsa' )
		vm.vm_create(tenant_name, net, count, network,bst_hyp)
		ssh.exec_command('cp /home/vpmaddur/Project/admin/'+tenant_name+'.img /home/vpmaddur/Project/'+tenant_name+'/etc/'+tenant_name+'-'+net["Name"]+'-'+str(count)+'.img')
		vm.vm_start(tenant_name,net,bst_hyp,count,ssh)
		ssh.close()
