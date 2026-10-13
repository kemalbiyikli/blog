#!/usr/bin/env python3
"""Kategorileri kaldırır, yazılara tek tip 'Konular' (tags) atar."""
import json, os, re

TAGS = {
    "apache-guacamole-kurulumu": ["Linux", "Guacamole"],
    "cannot-increase-disk-size-due-to-old-replication-participation-hatasi-ve-cozumu": ["VMware", "vCenter", "ESXi", "Sorun Giderme"],
    "dell-emc-dd6300-firmware-upgrade": ["Dell EMC", "Data Domain", "Backup", "Upgrade"],
    "esxi-cli-upgrade": ["VMware", "ESXi", "Upgrade", "CLI"],
    "hpe-msade-quarantine-durumundaki-disk-groupun-silinmesi": ["Storage", "HPE MSA", "CLI", "Sorun Giderme"],
    "hyper-v-to-vsphere-migration": ["VMware", "Hyper-V", "Veeam", "Migration"],
    "linuxda-dosya-izinlerinin-temel-yapisi": ["Linux"],
    "lvm-ile-linux-sunucuda-disk-genisletme": ["Linux", "LVM", "Storage"],
    "ubuntu-server-uzerinde-redis-cluster-kurulumu": ["Linux", "Ubuntu", "Redis"],
    "vcenter-archive-is-full": ["VMware", "vCenter", "Sorun Giderme"],
    "vcenter-upgrade-source-vcenter-has-duplicate-names-in-a-network-folder-hatasi": ["VMware", "vCenter", "Upgrade", "Sorun Giderme"],
    "vmware-esxi-cannot-mount-existing-iscsi-datastore": ["VMware", "ESXi", "Storage", "HPE MSA", "iSCSI", "Sorun Giderme"],
    "zabbix-ile-vcenter-monitoring-hangi-kullanici-hangi-gruplarda-olmali": ["VMware", "vCenter", "Zabbix", "Monitoring"],
}

d = "content/posts"
for name in sorted(os.listdir(d)):
    slug = name[:-3]
    p = os.path.join(d, name)
    text = open(p, encoding="utf-8").read()
    _, fm, body = text.split("---\n", 2)
    lines = [l for l in fm.splitlines() if not l.startswith(("categories:", "tags:"))]
    if slug in TAGS:
        i = next(i for i, l in enumerate(lines) if l.startswith("slug:")) + 1
        lines.insert(i, "tags: " + json.dumps(TAGS[slug], ensure_ascii=False))
    else:
        print("ETIKETSIZ:", slug)
    open(p, "w", encoding="utf-8").write("---\n" + "\n".join(lines) + "\n---\n" + body)
    print("ok", slug)

os.makedirs("content/tags", exist_ok=True)
open("content/tags/_index.md", "w", encoding="utf-8").write('---\ntitle: "Konular"\n---\n')
