# TODO LIST

3. when capsules update and reboot, it doesn't reset the AWS hostnames and stuff
5. convert gittemplatesync to git repo
6. set git templatesync settings to local dir
7. create PCI DSS policy
8. Create Host Collection
9. remote exec connect to ip
10. import git templates
11. change host interfaces to use internal ip
12. change remote exec user to ec2-user


1. api /api/operatingsystems/1/os_default_templates | jq
2. selectattr template_kind_name="user_data" | map(attribute='id') | first
3. api /api/operatingsystems/1/os_default_templates/5 -X PUT -d '{ "os_default_template": { "provisioning_template_id": 235 }
