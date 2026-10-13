#!/usr/bin/env python3
"""Yazı dosyalarını kısa adlara çevirir, görselleri static/images/<kisa-ad>/ altına taşır.
URL'ler değişmez (front matter'daki slug korunur). Tek seferlik iş bitince kendini ve eski scriptleri siler."""
import os, re, shutil, subprocess

NAMES = {
    "apache-guacamole-kurulumu": "guacamole-kurulum",
    "cannot-increase-disk-size-due-to-old-replication-participation-hatasi-ve-cozumu": "vcenter-disk-genisletme-hatasi",
    "dell-emc-dd6300-firmware-upgrade": "dd6300-firmware",
    "esxi-cli-upgrade": "esxi-cli-upgrade",
    "hpe-msade-quarantine-durumundaki-disk-groupun-silinmesi": "msa-quarantine-diskgroup",
    "hyper-v-to-vsphere-migration": "hyperv-vsphere-gecis",
    "linuxda-dosya-izinlerinin-temel-yapisi": "linux-dosya-izinleri",
    "lvm-ile-linux-sunucuda-disk-genisletme": "lvm-disk-genisletme",
    "ubuntu-server-uzerinde-redis-cluster-kurulumu": "redis-cluster-kurulum",
    "vcenter-archive-is-full": "vcenter-archive-full",
    "vcenter-upgrade-source-vcenter-has-duplicate-names-in-a-network-folder-hatasi": "vcenter-duplicate-names",
    "vmware-esxi-cannot-mount-existing-iscsi-datastore": "esxi-iscsi-mount",
    "zabbix-ile-vcenter-monitoring-hangi-kullanici-hangi-gruplarda-olmali": "zabbix-vcenter-yetkiler",
}
IMG = re.compile(r"/wp-content/uploads/[^\s)\"'>]+")
moved = {}

def git(*a):
    subprocess.run(["git", *a], check=True)

def relocate(md_path, short):
    text = open(md_path, encoding="utf-8").read()
    n = 0
    for old in dict.fromkeys(IMG.findall(text)):
        if old not in moved:
            src = "static" + old
            if not os.path.exists(src):
                print("  YOK:", src); continue
            n += 1
            ext = os.path.splitext(old)[1].lower()
            new = f"/images/{short}/{short}-{n}{ext}"
            os.makedirs(os.path.dirname("static" + new), exist_ok=True)
            git("mv", src, "static" + new)
            moved[old] = new
        text = text.replace(old, moved[old])
    open(md_path, "w", encoding="utf-8").write(text)
    return n

for old, short in NAMES.items():
    src = f"content/posts/{old}.md"
    if not os.path.exists(src):
        print("atlandi:", old); continue
    print(f"{old} -> {short} ({relocate(src, short)} gorsel)")
    if old != short:
        git("mv", src, f"content/posts/{short}.md")

for f in os.listdir("content"):
    p = os.path.join("content", f)
    if f.endswith(".md") and os.path.isfile(p):
        k = relocate(p, f[:-3])
        if k: print(f"{f}: {k} gorsel")

# Hiçbir yazıda kullanılmayan eski görseller
if os.path.isdir("static/wp-content"):
    left = [os.path.join(r, x) for r, _, fs in os.walk("static/wp-content") for x in fs]
    print("kullanilmayan:", left)
    if left: git("rm", "-q", *left)
    shutil.rmtree("static/wp-content", ignore_errors=True)

# Tek seferlik araçları temizle
for f in ["scripts/wp_import.py", "scripts/retag.py", "scripts/rename.py"]:
    if os.path.exists(f): git("rm", "-q", f)
