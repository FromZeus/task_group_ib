#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import facts


DOCUMENTATION = '''
---
module: host_ib
short_description: Gather some host information
'''

EXAMPLES = '''
- name: Get info
  host_ib:
    installed_memory: True
    promisc_count: True
    vpn_adapters: True
  register: info
- name: Get tag
  set_fact:
    repo_tag: "{{ mem_tags[info.meta.installed_memory] }}"
- name: Pull configuration
  git:
    repo: https://github.com/FromZeus/ib_task_resources.git
    dest: /tmp/ib_configuration
    version: "{{ repo_tag }}"
- name: Configure
  shell: cp -r /tmp/ib_configuration/etc/ib_conf /etc/
- debug: var=repo_tag
'''


def form_result(data):
    result = dict.fromkeys(data)

    if data["installed_memory"]:
        result["installed_memory"] = facts.ansible_facts(
            module, ["hardware"])["memtotal_mb"]
    if data["promisc_count"]:
        result["promisc_count"] = 0
        for el in facts.ansible_facts(module, ["network"]):
            if "promisc" in el and el["promisc"]:
                result["promisc_count"] += 1
    if data["vpn_adapters"]:
        result["vpn_adapters"] = [el for el in facts.ansible_facts(
            module, ["network"])["interfaces"] if el.startswith("tun")]

    return False, result


def main():
    global module
    fields = {
        "installed_memory": {"default": False, "type": "bool"},
        "promisc_count": {"default": False, "type": "bool"},
        "vpn_adapters": {"default": False, "type": "bool"}
    }

    module = AnsibleModule(argument_spec=fields)
    has_changed, response = form_result(module.params)
    module.exit_json(changed=has_changed, meta=response)

if __name__ == '__main__':
    main()
