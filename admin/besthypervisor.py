def best_hypervisor():
    free_memory=0
    for ip in tenant_hyper_list[0]["ip_list"]:
        print(ip)
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
