import sys, json, onboarding

tenant_name=onboarding.sys.argv[1]

with open('/home/vpmaddur/Project/admin/'+tenant_name+'-hypervisor.json') as hypervisor_list:
    tenant_hyper_list=json.load(hypervisor_list)

with open('/home/vpmaddur/Project/'+tenant_name+'/'+tenant_name+'.json') as json_input:
    tenant_input=json.load(json_input)


