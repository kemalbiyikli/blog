---
title: "vCenter Upgrade: Source vCenter has Duplicate Names in a Network Folder Hatası"
date: "2023-12-23T00:38:09"
lastmod: "2023-12-26T02:01:09"
slug: "vcenter-upgrade-source-vcenter-has-duplicate-names-in-a-network-folder-hatasi"
tags: ["VMware", "vCenter", "Upgrade", "Sorun Giderme"]
draft: false
---
![](/wp-content/uploads/2023/12/vcenter.jpg)

vCenter’ınızı upgrade etmek istediğinizde yukarıdaki gibi bir hatayla karşılaşıyorsanız büyük ihtimalle 6.5 öncesi bir sürümü upgrade etmeye çalışıyorsunuzdur. Bu hata vCenter üzerinde aynı isme sahip olan birden fazla Port Group’a sahip olmanızdan kaynaklanıyor.

Bu problem vCenter 6.5 ile giderildi, [Patch Note](https://docs.vmware.com/en/VMware-vSphere/6.5/rn/vsphere-vcenter-server-650b-release-notes.html)‘larını inceleyebilirsiniz.

Bu problemi mevcut sürümünüzde gidermek ve upgrade yapabilmeniz için VMware’in bir [KB](https://kb.vmware.com/s/article/2147547)‘si bulunuyor. Ancak KB’yi incelerseniz eğer vCenter Database’ine bağlanmanız, ilgili satır ve sütunları tespit ederek birtakım işlemler uygulamanız gerektiğini göreceksiniz. Ancak daha basit bir şekilde çözmek de mümkün.

Öncelikle bu hataya neden olan Port Group’ları tespit etmemiz gerekiyor. Eğer çok fazla Port Group yoksa bunu kendiniz vCenter üzerinde elle de yapabilirsiniz. Tespit ettiğiniz Port Group’ların isimlerini değiştirdiğinizde ya da sildiğinizde probleminiz çözülecektir. Peki ya benim gibi yüzlerce Port Group’unuz varsa?

Bunun için VMware’in önerdiği yöntemi tercih etmem bir seçenekti ancak ben farklı bir yoldan giderek ortamımın bir RVTools raporunu aldım, Excel’de duplicate hücreleri işaretleyerek aynı isimdeki Port Group’ları tespit ettim ve düzelttim.
