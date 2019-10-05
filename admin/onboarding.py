import paramiko, json, sys, vm, mgmtnw, besthypervisor, controller

tenant_name=sys.argv[1]

with open('/home/vpmaddur/Project/'+tenant_name+'/hypervisor.json') as hypervisor_list:
    tenant_hyper_list=json.load(hypervisor_list)

with open('/home/vpmaddur/Project/'+tenant_name+'/'+tenant_name+'.json') as json_input:
    tenant_input=json.load(json_input)

####################Creating Management Network###################

bst_hyp=besthypervisor.best_hypervisor(tenant_name)
m_network=tenant_input[0]["Networks"][-1]["Subnet"]
m_netmask=tenant_input[0]["Networks"][-1]["netmask"]
mgmtnw.mgmt_network(m_netmask, bst_hyp, tenant_name, m_network)

######################### Create Infrastrcuture in all Hypervisors#################

for ip in tenant_hyper_list[0]["ip_list"]:
    print(ip)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(ip)
    ssh.connect(ip, port=22, username='root', key_filename='/root/.ssh/id_rsa')
#   ssh.exec_command('mkdir /home/admin/'+tenant_name)
#   ssh.exec_command('mkdir /home/'+tenant_name)
#   ssh.exec_command('mkdir /home/'+tenant_name+'/etc')
#   ssh.exec_command('mkdir /home/'+tenant_name+'/var')
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
                if net == "mgmt":
                    ssh.exec_command('ip link add '+net["Name"]+'-dhcp type veth peer name dhcp-'+net["Name"]+'-'+tenant_name)
                    ssh.exec_command('ip link set dhcp-'+net["Name"]+'-'+tenant_name+' up')
                    ssh.exec_command('ip link set '+net["Name"]+'-dhcp'+' up')
                    ssh.exec_command('brctl addif '+tenant_name+"-"+net["Name"]+'-br'+' '+net["Name"]+'-dhcp')
                    ssh.exec_command('brctl addif '+tenant_name+"-"+'-dhcp-mgmt'+' dhcp-'+net["Name"]+'-'+tenant_name)
    ssh.close()
    controller.create_controller(tenant_name)
