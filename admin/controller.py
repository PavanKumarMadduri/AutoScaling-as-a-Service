with open('/home/vpmaddur/Project/'+tenant_name+'/'+tenant_name+'.json') as json_input:
            tenant_input=json.load(json_input)

network=tenant_input[0]["Networks"]
######################DHCP File #######################################
for net in tenant['Networks']:
    dhcp_subnet=net["Subnet"]
    dhcp_netmask=net["netmask"]
    app_subnet=dhcp_subnet.split('.')
    dhcp_router=".".join(app_subnet[0:3])+str(.1)
    dhcp_low_range=".".join(app_subnet[0:3])+str(.2)
    dhcp_high_range=".".join(app_subnet[0:3])+str(.254)
    dhcp=open('/home/vpmaddur/Project/nokia/dhcpd.conf', 'a')
    dhcp.write('subnet '+dhcp_subnet+' netmask '+dhcp_netmask+' {\n')
    dhcp.write('        option routers                  '+dhcp_router+';\n')
    dhcp.write('        option subnet-mask              '+dhcp_netmask+';\n')
    dhcp.write('        option domain-name-servers      '+dhcp_router+';\n')
    dhcp.write('        range   '+dhcp_low_range+'   '+dhcp_high_range+';\n')
    dhcp.write('}\n\n')
    dhcp.close()


for net in network:
    if net["Name"]!="mgmt":
        for count in range(net["Min"]):
            bst_hyp=best_hypervisor()
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(bst_hyp, port=22, username='root' , key_filename='/root/.ssh/id_rsa')
            vm.vm_create(tenant_name, net, count, network,bst_hyp)
            stdin, stdout, stderr = ssh.exec_command('cp /home/vpmaddur/Project/admin/'+tenant_name+'.img /home/vpmaddur/Project/'+tenant_name+'/etc/'+tenant_name+'-'+net["Name"]+'-'+str(count)+'.img')
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
