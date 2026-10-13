---
title: "VMware ESXi CLI Upgrade 7.0>8.0"
date: "2023-12-01T22:29:14"
lastmod: "2023-12-26T02:01:41"
slug: "esxi-cli-upgrade"
tags: ["VMware", "ESXi", "Upgrade", "CLI"]
draft: false
---
ESXi upgrade işlemi birden fazla yöntemle yapılabilmektedir, bu yazımda cli üzerinden esxi upgrade işleminin nasıl yapılacağını aktaracağım.

Bunun için aşağıdaki adımları takip etmemiz gerekmektedir. Öncelikle offline bundle paketini [customerconnect.vmware.com](http://customerconnect.vmware.com) adresinden download ediyoruz. Download ederken custom bir esxi sürümü mü standart bir esxi sürümü mü kullandığımıza dikkat etmemiz gerekiyor. Ben standart sürüm kullandığım için standart sürümü tercih ediyorum.

![](/images/esxi-cli-upgrade/esxi-cli-upgrade-1.png)

Uygun sürümü download ettikten sonra upgrade işlemini yapacağız esxi hosta bağlı olan bir datastore’a upload ediyoruz.

![](/images/esxi-cli-upgrade/esxi-cli-upgrade-2.png)

Ardından hostumuzda SSH’ı aktif ediyoruz.

Hostumuzu maintenance moda almadan önce dikkat etmemiz gereken bazı noktalar var.

- Eğer hostumuz standalone çalışıyorsa maintenace mod aktif olduğunda sunucularımız power off duruma geçecektir.
- Host bir vCenter ortamında yönetiliyor ve clustera dahil ise üzerindeki sunucuları vMotion ile diğer sunuculara dağılacaktır. Ancak sunucuları diğer hostlara manuel olarak taşımak oluşabilecek migration hatalarının önüne geçmemizi sağlayacaktır.

Kontrollerimizi yaptıktan sonra putty vb. bir programla hostumuza bağlanıyoruz.

Hostumuzu maintenace moda almak için de aşağıdaki komutu çalıştırıyoruz.

``` text
vim-cmd hostsvc/maintenance_mode_enter
```

Hostumuzu maintenance moda aldıktan sonra update komutunu çalıştırabilmek için upgrade dosyasının profil bilgisine ihtiyacımız. Bu bilgiyi elde etmek için aşağıdaki komutu çalıştırıyoruz. Komut büyük küçük harfe karşı duyarlı. Bu nedenle datastore ismini ve dosya ismini yazarken dikkat etmek gerekiyor.

``` text
esxcli software sources profile list -d /vmfs/volumes/DATASTORE01/VMware-ESXi-8.0-20513097-depot.zip
```

Komutu çalıştırdıktan sonra aşağıdaki görselde gördüğümüz profil bilgisini kopyalıyoruz ve upgrade komutunu aşağıdaki şekilde düzenliyoruz.(Resim 3)

``` text
esxcli software profile update -p ESXi-8.0.0-20513097-standard -d /vmfs/volumes/DATASTORE01/VMware-ESXi-8.0-20513097-depot.zip
```

![](/images/esxi-cli-upgrade/esxi-cli-upgrade-3.png)

Yukarıda düzenlediğimiz komutu çalıştıyoruz ve upgrade işlemini gerçekleştiriyoruz. Upgrade sonrasında bizden restart isteyecektir. Hostumuzu aşağıdaki komutla maintenance modundan çıkartıp restart ederek ve upgrade işlemi tamamlıyoruz.

``` text
vim-cmd hostsvc/maintenance_mode_exit
```

![](/images/esxi-cli-upgrade/esxi-cli-upgrade-4.png)
