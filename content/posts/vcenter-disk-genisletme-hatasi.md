---
title: "“Cannot increase disk size due to old replication participation” hatası ve çözümü"
date: "2024-01-13T00:37:32"
lastmod: "2024-02-03T02:30:59"
slug: "cannot-increase-disk-size-due-to-old-replication-participation-hatasi-ve-cozumu"
tags: ["VMware", "vCenter", "ESXi", "Sorun Giderme"]
draft: false
---
VMware vSphere site to site replication’dan bir sunucuyu kaldırdığınızda ya da VSRM sunucusunu kaybettiğinizde ve replikasyonlarınız dağıldığında VM’leriniz olduğu gibi çalışacaktır. Ancak sunucularınızda disk artırmak istediğinizde **`Cannot increase disk size due to old replication participation `** hatası ile karşılaşmanız muhtemel.

Sunucuda power on veya power off fark etmeksizin disk kapasitesini artırmak istediğinizde fail olacaktır. Bu problemin çözümünü araştırdığımda ise VMware’in KB’lerini incelediğimde de bir çözüme ulaşamadım. Forumlarda çeşitli çözümler okudum, sizlerle de başarılı olduğum bir çözümü çözümü paylaşmak istiyorum.

Yaygın olarak iki çözümle karşılaştım.

Bunlardan birincisi;

1.  Sunucuyu power off yapıyoruz.
2.  Delete form inventory ile sunucuyu vCenter’dan kaldırıyoruz.
3.  Datastore’da sunucunun dosyalarının olduğu dizine gidiyoruz ve RDID dosyasını siliyoruz.
4.  Sunucuyu .vmx dosyasından tekrar register ediyoruz.

Bu yöntemde hem sunucuda kesinti yapmanız gerekiyor. Ek olarak bu yöntem maalesef bende problemi gidermedi.

İkinci yöntem;

Bu yöntemde sanal sunucuyu kapatmamız gerekmiyor ve yapacağımız işlemler herhangi bir kesintiye de sebep olmuyor. İşlemleri aşağıdaki sıralama ile gerçekleştiriyoruz.

1.  Sanal sunucunun bulunduğu esxi host’da SSH’ı aktif ediyoruz.
2.  Ardından host’a SSH ile bağlanıyoruz ve aşağıdaki komutları sırası ile çalıştırıyoruz.
3.  **`vim-cmd vmsvc/getallvms`** Bu komut ile host üzerinde bulunan sanal sunucuları listeliyoruz. En soldaki sütun sanal sunucunun VM ID’sini göstermektedir.
4.  Listeden sorun yaşadığımız sanal sunucuyu buluyoruz ve ID’sini bir kenara not ediyoruz. Benim sunucu ID’im **219**
5.   **`vim-cmd hbrsvc/vmreplica.getConfig 219`** Komutunu çalıştırarak sanal sunucuda replikasyonun aktif durumda olduğunu görüyoruz.
6.  **`vim-cmd hbrsvc/vmreplica.disable 219`** Komutunu çalıştırarak bu sunucu için replikasyonu disable ediyoruz.
7.  İşlemi tamamladıktan sonra **`vim-cmd hbrsvc/vmreplica.getConfig 219`** komutu ile replikasyonun disable olduğunu görebilirisiniz.

Bu işlemlerin ardından sunucunuzda disk artırımını gerçekleştirebilirsiniz.
