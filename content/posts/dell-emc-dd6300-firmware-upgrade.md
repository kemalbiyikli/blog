---
title: "DELL EMC DD6300 Firmware Upgrade"
date: "2024-01-02T19:29:36"
lastmod: "2024-01-19T23:59:58"
slug: "dell-emc-dd6300-firmware-upgrade"
categories: ["DELL EMC"]
tags: ["Backup", "DataDomain", "Dell", "Upgrade"]
draft: false
---
Bu yazımda **DELL EMC Data Domain 6300**‘ün firmware upgrade işleminden söz edeceğim.

Upgrade işlemini yapacağım ürün oldukça eski bir sürümde kalmış. Bu nedenle son sürüm olan 7.13.0.20’ye geçebilmem için cihazımın minimum 6.2 sürümünde olması gerekiyor. Bu yüzden önce 6.2 sürümüne ardından da 7.0.13 sürümüne upgrade işlemi gerçekleştireceğim.

İşlemlerin sırası ile nasıl yapıldığına geçmeden önce belirtmem gereken bazı maddeler var.

Bu işlem tamamlandıktan sonra otomatik reboot işlemi gerçekleşecektir ve bu süre bende her bir upgrade işlemi için yaklaşık 40 dk. kadar sürdü. Bu nedenle kesinti için bir planlama yapmanız gerekebilir.

Upgrade esnasında herhangi bir problemle karşılaşmadım, karşılaşsam da ürünü tamamen sıfırladığım ve içi boş olduğu için zarar görecek kritik bir veri bulunmuyordu. Bu nedenle olası bir problem benim açımdan bir sorun teşkil etmiyordu. Ancak sizler ürünü hali hazırda kritik verileriniz ile kullanıyorsanız profesyonel bir yardım almanız yararınıza olacaktır.

Gelelim upgrade işlemnine

Öncelikle [ürünün sayfasından](https://www.dell.com/support/home/tr-tr/product-support/product/dd6300-appliance/drivers) ihtiyacımız olan paketleri download ediyoruz.

![](/wp-content/uploads/2024/01/WhatsApp-Gorsel-2024-01-02-saat-19.14.23_2c0af5d0.jpg)

Ben ihtiyacım olan 6.2.1.110 ve 7.13.0.20 sürümlerini download ediyorum.

![](/wp-content/uploads/2024/01/dd6300-0-1024x487.png)

İndirdiğimiz paketleri de web arayüzünden yüklememiz gerekiyor ancak ben bu aşamada aşağıdaki hatayı aldım.

![](/wp-content/uploads/2024/01/dd6300-0-1-1024x484.png)

Bu aşamada internette çeşitli araştırmalar yaptım ancak hata ile ilgili spesifik bir çözüme ulaşamadım. [Shamistan ARZIMANLI](https://www.linkedin.com/pulse/dell-emc-data-domain-upgrade-file-upload-failed-error-arzimanli/?originalSubdomain=tr)‘nın bir yazısında aynı hatayla karşılaştığını ve alternatif olarak FTP kullandığını gördüm. Ben de aynı şekilde upgrade dosylarını FTP ile atma yolunu tercih ettim. Bu işlem için de WinSCP uygulamasını kullandım.

WinSCP ile DataDomain’e **FTP** protokolü ile bağlandım. rpm dosyalarını Data Domain’in ***root/releases*** dizinine kopyaladım.

![](/wp-content/uploads/2024/01/dd6300-3-1024x560.png)

Kopyalama işlemi tamamlandıktan sonra web arayüzünde Maintenance/System altında aşağıdaki gibi paketinizi görüntüleyebilirsiniz.

![](/wp-content/uploads/2024/01/dd6300-4-1024x487.png)

Upgrade öncesinde dosyamızı işaretleyip UPGRADE-PRECHECK seçeneğini seçiyoruz ve paketimiz eksiksiz ve uygun olup olmadığını kontrol ediyoruz.

![](/wp-content/uploads/2024/01/dd6300-6-1024x486.png)

Precheck işlemi sorunsuz bir şekilde tamamlandıktan sonra **PERFORM SYSTEM UPGRADE** butonu ile upgrade işlemine başlayabiliriz.

![](/wp-content/uploads/2024/01/dd6300-7-1024x487.png)

![](/wp-content/uploads/2024/01/dd6300-8-1024x485.png)

Upgrade’in yüklenmesi hızlıca bitiyor ancak reboot işlemi yazının başında da belirttiğim gibi biraz zaman alıyor. Upgrade işlemi tamamlandığında yeni sürümümüz bizleri karşılıyor.

![](/wp-content/uploads/2024/01/dd6300-9-1024x487.png)

Bir sonraki aşamada 7.13.0.20 sürüme upgrade yapıyorum. Bu işlem için de süreç aynı işliyor.
