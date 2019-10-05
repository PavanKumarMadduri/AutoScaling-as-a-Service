import  sys, paramiko, json


def best_hypervisor(tenant_name):
    free_memory=0
    with open('/home/vpmaddur/Project/'+tenant_name+'/hypervisor.json') as hypervisor_list:
        tenant_hyper_list=json.load(hypervisor_list)
    for ip in tenant_hyper_list[0]["ip_list"]:
        print(ip)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username='root',  key_filename='/root/.ssh/id_rsa')
        print(ip)
        stdin, stdout, stderr = ssh.exec_command('cat /proc/meminfo  | grep MemFree | awk \'{print $2}\'')
        hypervisor_memory=int(stdout.readlines()[0].strip())
        ssh.close()
        if hypervisor_memory > free_memory:
            free_memory=hypervisor_memory
            free_hyp=ip
    print(ip)
    return free_hyp
