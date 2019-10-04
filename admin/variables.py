import sys, json, onboarding

with open('/home/vpmaddur/Project/admin/'+onboarding.tenant_name+'-hypervisor.json') as hypervisor_list:
    tenant_hyper_list=json.load(hypervisor_list)

with open('/home/vpmaddur/Project/'+onboarding.tenant_name+'/'+onboarding.tenant_name+'.json') as json_input:
    tenant_input=json.load(json_input)


