---
title: "vCenter: Archive is full"
date: "2025-07-28T17:48:27"
lastmod: "2025-07-28T17:54:20"
slug: "vcenter-archive-is-full"
tags: ["VMware", "vCenter", "Sorun Giderme"]
draft: false
---
------------------------------------------------------------------------

### Problem?

Zaman zaman hepimizin karşılaştığı türden bir alarmla karşılaştım: vCenter sunucusunun `/storage/archive` diski %90 seviyelerindeydi. Normalde bu disk ara sıra dolar ve kendini temizlerdi, bu nedenle biraz kendi haline bırakıp gözlemlemek istedim ancak bu sefer hiç temizlemeye niyeti yoktu ve dolmaya devam ediyordu. Ben de bir yandan bu durumla ilgili Broadcom KB makalelerini incelemeye koyuldum.

Broadcom’un KB’lerini incelediğimde aşağıdaki önemli noktalar dikkat çekiyordu:

- vCenter’daki birçok dizin yüksek doluluk oranlarına çıkabilecek şekilde tasarlanmıştır. Çoğu durumda, bir bölüm %78-79 seviyesine ulaştığında, uyarıları tetiklemek için gereken %80’i aşabilir ve ardından daha düşük bir yüzdeye geri dönebilir.
- Benzer şekilde, %93’e ulaştığında, `vmware-vpxd` hizmetinin kapanmasını tetiklemek için gereken %95’i aşabilir ve ardından daha düşük bir yüzdeye geri dönebilir. Bu durumlar genellikle otomatik temizleme veya sistem davranışının bir parçasıdır.

**Archive Bölümünün Özelliği**

Diğer bölümlerden farklı olarak, sorun yaşadığımız `/storage/archive` bölümü **tasarım gereği dolu olabileceğinden** (evet, %100’e ulaşması da normal kabul ediliyor) **vCenter Server’ın herhangi bir işlemini etkilemiyor**. Bu birim, mümkün olduğunca çok WAL geçmişi depolar ve arşivleyici hizmeti tarafından en eski WAL segmentleri otomatik olarak kaldırılarak kendiliğinden temizlenir.

Bu birim özelinde vCenter Server 6.7 Update 1b’den itibaren alarmlar durumu oluşmamaktadır. Bu nedenle, yeni sürümlerde arşiv diski %100 dolu olsa bile VAMI’deki özet sekmesinin sağlık durumunda herhangi bir alarm oluşmayacaktır, çünkü bu tasarım gereğidir ve **vCenter’ın çalışması üzerinde herhangi bir etkisi yoktur.**

Broadcom makalesinde de bu bölüm özelinde problem **çözümünü(!)** aşağıdaki gibi adreslemiş:

| Filesystem                       | Mounted on         | Resolution                                                                                                                                                                                                  |
|----------------------------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/dev/mapper/archive_vg-archive` | `/storage/archive` | “Note: This partition being full is normal and expected in vCenter versions 6.7 and above” “File system /storage/archive is low on storage space” warning in vCenter Server Appliance 6.7/7.x/8.x (318803)  |

**Manuel Müdahale Edilebilir mi?**

Evet, Broadcom’un da belirttiği gibi bu bölüm %100 dolup kendini temizleyebiliyor. Ancak, benim vCenter sunucumda bu durum gün aşırı yaşandığından dolayı “false positive” alarmların oluşmasına sebebiyet veriyordu. Zaten kendileri de bazı yapılarda diskin yetersiz geldiği durumlarda diski genişletebileceğinizi belirtiyor.

Benim sunucumdaki path’i incelediğimde 3 günden fazla arşiv tutamadığını gördüm. Bu da çok kısa bir döngü olmasından dolayı disk genişletme kararı verdim. İSterseniz tek seferlik bir temizleme işlemi de yapabilirsiniz.

**Manuel Arşiv Temizleme**

Dilerseniz kendiniz manuel olarak da bu dizini temizleyebilirsiniz. Bu, disk genişletme yapmadan önce geçici bir çözüm veya anlık bir rahatlama sağlayabilir.

1.  **SSH ile vCenter Server Appliance’a bağlanıyoruz.**
2.  `shell` komutu ile `root`‘a geçiyoruz.
3.  **`/storage/archive/vpostgres` dizinine gidiyoruz.** `cd /storage/archive/vpostgres`
4.  **Belirli bir günden eski arşivleri listelemek için:**`find * -mtime +3 `komutunu kullanıyoruz. Bu komut bize üç günden eski arşiv dosyalarını listeleyecektir.
5.  **Listelediğimiz eski arşivleri temizlemek için:**`find *.* -mtime +3 | xargs rm `komutunu kullanıyoruz.
6.  **Temizleme sonrası `df -h` komutu ile kontrol ettiğinde archive dizininde bir rahatlama göreceksiniz.**

**Diskini Genişletme Adımları**

Ben, arşivlenebilen günün çok az olması nedeniyle disk genişletme işlemi yaptım. Bu işlem de sırasıyla şu şekildedir:

**Ön Hazırlıklar ve Dikkat Edilmesi Gerekenler:**

- **vCenter Server’ın yedeğini alın:** Kenarda bir yedeğinizin olması iyi olur. Alalım dursun kenarda 🙂
- **Mevcut Snapshot’ları Silin:** Disk genişletmeden önce vCenter VM üzerinde herhangi bir snapshot varsa silmemiz öneriliyor.

**1. Doğru Diski Tespit Etme:**

vCenter üzerinde 17 tane Virtual Disk bulunuyor. Öncelikle genişleteceğimiz `/storage/archive` diskinin SCSI bağlantısını tespit etmemiz ve ona uygun şekilde artırım yapmamız gerekiyor.

`lsblk -o NAME,HCTL,MOUNTPOINT,SIZE` komutu ile vCenter sunucumuzun disklerini ve mount pointlerini listeleyebiliriz.

``` text
root@vcsatst [ ~ ]# lsblk -o NAME,HCTL,MOUNTPOINT,SIZE
NAME                              HCTL       MOUNTPOINT             SIZE
sda                               2:0:0:0                          48.6G
├─sda1                                                                4M
├─sda2                                       /boot/efi               10M
├─sda3                                       /boot                  512M
└─sda4                                                               48G
  └─vg_root_0-lv_root_0                      /                       48G
sdb                               2:0:1:0                           7.2G
sdc                               2:0:2:0                            25G
└─swap_vg-swap1                              [SWAP]                  25G
sdd                               2:0:3:0                            50G
└─core_vg-core                               /storage/core           50G
sde                               2:0:4:0                            10G
└─log_vg-log                                 /storage/log            10G
sdf                               2:0:5:0                            10G
└─db_vg-db                                   /storage/db             10G
sdg                               2:0:6:0                            15G
└─dblog_vg-dblog                             /storage/dblog          15G
sdh                               2:0:8:0                           1.4T
└─seat_vg-seat                               /storage/seat          1.4T
sdi                               2:0:9:0                             1G
└─netdump_vg-netdump                         /storage/netdump      1016M
sdj                               2:0:10:0                           10G
└─autodeploy_vg-autodeploy                   /storage/autodeploy     10G
sdk                               2:0:11:0                           10G
└─imagebuilder_vg-imagebuilder               /storage/imagebuilder   10G
sdl                               2:0:12:0                          100G
└─updatemgr_vg-updatemgr                     /storage/updatemgr     100G
sdm                               2:0:13:0                          100G
└─archive_vg-archive                         /storage/archive       100G
sdn                               2:0:14:0                          1.4T
└─vtsdb_vg-vtsdb                             /storage/vtsdb         1.4T
sdo                               2:0:15:0                           15G
└─vtsdblog_vg-vtsdblog                       /storage/vtsdblog       15G
sdp                               3:0:0:0                           100G
└─lifecycle_vg-lifecycle                     /storage/lifecycle     100G
sr0                               0:0:0:0                          1024M
sdq                               3:0:1:0                          1000G
└─vg_lvm_snapshot-lv_lvm_snapshot            /storage/lvm_snapshot 1000G
```

Yukarıdaki çıktıda görüldüğü üzere`/storage/archive` diskimiz `sdm` olarak listelenmiş ve SCSI controller 0, Virtual Device Node SCSI(0:13) üzerinde yer alıyor.

**2. vCenter Üzerinden Sanal Diski Büyütme:**

vCenter arayüzü üzerinden vCenter VM’ine sağ tıklayıp “Edit Settings” seçeneğini seçerek `Hard disk 13` olarak görünen ve `/storage/archive`‘a karşılık gelen diskin boyutunu artırıyoruz.

vCenter sunucusuna SSH ile bağlanıyoruz ve shell komutu ile root’a geçiyoruz. Burada extend işlemini kolaylaştırmak için Broadcom’un yerleştirdiği bir script var. Onu çalıştırmamız yeterli olacak. `/usr/lib/applmgmt/support/scripts/autogrow.sh `komutu ile scripti çalışıtıyoruz.

Script bizim için extend işlemini gerçekleştirecektir. Scriptin çalışması tamamlandıktan sonra df -h komutu ile `/storage/archive` dizinine karşılık gelen `sdm` diskini kontrol edebilirsiniz.

**Böylelikle çok da sorun olmayan bir sorunun üstesinden gelmiş oluyoruz. Okuduğunuz için teşekkürler.**

**Referanslar**

**[vCenter Server Appliance disk space is full](https://knowledge.broadcom.com/external/article/318953/vcenter-server-appliance-disk-space-is-f.html)**

**[“File system /storage/archive is low on storage space” warning in vCenter Server Appliance 6.7/7.x/8.x](https://knowledge.broadcom.com/external/article/318803)**

**[Increasing the disk space for the vCenter Server Appliance in vSphere 6.5, 6.7, 7.0 and 8.0](https://knowledge.broadcom.com/external/article/316602)**

[How To Remove Old Archive Files in VMware vCenter Server Appliance  
](https://blogs.vmware.com/cloud-foundation/2023/04/06/how-to-remove-old-archive-files-in-vmware-vcenter-server-appliance/)
