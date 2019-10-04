with open('/home/vpmaddur/Project/'+tenant_name+'/'+tenant_name+'.json') as json_input:
                tenant_input=json.load(json_input)

                network=tenant_input[0]["Networks"]

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
