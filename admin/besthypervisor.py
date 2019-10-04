import  sys, paramiko, onboarding, logging

def best_hypervisor():
    free_memory=0
    for ip in onboarding.tenant_hyper_list[0]["ip_list"]:
        print(ip)
        logging.basicConfig()
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        paramiko.util.log_to_file("./paramiko.log")
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
    return ip
