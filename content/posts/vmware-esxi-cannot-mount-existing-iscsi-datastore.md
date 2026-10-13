---
title: "VMware ESXi – Cannot Mount Existing iSCSI Datastore"
date: "2025-06-25T00:43:49"
lastmod: "2025-07-30T09:47:14"
slug: "vmware-esxi-cannot-mount-existing-iscsi-datastore"
categories: ["HPE", "Storage", "vSphere"]
tags: ["HPE", "Storage", "vSphere"]
draft: false
---
Geçtiğimiz hafta sanallaştırma altyapımıza yeni bir sunucu ekledim. Her şey yolunda gidiyor derken MSA2060 üzerindeki bir Volume’ü sunucuya mount edemedim. Neden oldu, nasıl çözeriz derken aşağıdaki gibi bir süreç gelişti.

------------------------------------------------------------------------

## İş Senaryosu

- Hali hazırda MSA2060 storage’ımızda aktif olarak kullanılan 2 adet LUN var.
- Yeni bir ESXi host vCenter ortamına eklendi.
- Bu hosta storage iSCSI ile bağlandı.
- LUN’lardan biri datastore olarak başarıyla mount edildi.
- Ancak bir LUN datastore listesinde yok ve mount edilemiyor.
- “Storage Devices” altında LUN görünüyor, ama **“Not Consumed”** durumu var.

------------------------------------------------------------------------

## Tanılama Aşaması

ÖProblemi tespit etmek için aşağıdaki kontroller yapıldı.

- Tüm iSCSI initiator’leri ve bağlantılarını kontrol edildi.
- Hostumuzun VMKernel ve iSCSI konfigürasyonları kontrol edildi.
- Storage üzerinde Volume Groups ve Host Groups bölümlerini ve mappingleri kontrol ediyoruz.
- Tüm LUN’ların hostlara aynı id’ler ile bağlı olup olmadığı kontrol edildi.

Öncelikle tüm fiziksel bağlantı ve konfigürasyonların doğruluğundan emin olduktan sonra sorunu storage üzerinde aradım. Çünkü hostlarıma bağlı olan diğer storage’larla hiçbir sorun yaşamazken bu storage’da LUN’lardan birini bağlarken diğerini bağlayamamış olmam beni storage tarafını kontrol etmeye itti.

HPE ile yapılandırmayı kontrol ettik. Onlar’da herhangi bir yapılandırma hatası göremedi ve ticket’ı L2 mühendise eskale ettiler. Logları ve problemi inceleyen mühendis çözüm için Controller’ları sıra ile restart etmemi önerdi. Ancak bu yöntemi canlı sistemleri etkileme riskinden dolayı son seçenek olarak kenara koydum.

Bu aşamada internetten durumu araştırınca bu konuyla ilgili bazı KB ve forum yorumlarına denk geldim. Nitekim çözümü de storage üzerinde değil de esxi üzerinde buldum. Şimdi kısaca bu durumun neden gerçekleştiğine bakalım:

ESXi hostlar, üzerinde başka bir host tarafından formatlanmış bir VMFS volume varsa, bunu otomatik olarak mount etmez.(Aslında bazı durumlarda edilebiliyor ama çok değişkenli bir fonksiyon gibi bir durum var. Her ihtimali şu an yazmak kafa karıştırıcı olacaktır, refernas linkini veriyorum.) Bunun sebebi veri kaybı riskidir. ESXi bu LUN’u “foreign VMFS” olarak algılar ve sizin manuel olarak mount etmenizi ister. Bu noktada New Datastore diye eklediğinizde o volume’ü görürsünüz ve devam etmek istediğinizde de bak dostum böyle bir bölüm var ben bunu koruyarak eski isim ve id’si ile ekleyeyim mi dye sorar.

Buraya kadar herşey normal, ancak ben bu volume’ü yeni bir datastore ekler gibi eklemek istediğimde de göremiyordum. Bu durumun ESXi, yeni eklenen bir LUN’da mevcut VMFS imzası görürse, veri kaybı riskini önlemek için tasarım gereği volume’u snapshot olarak algılamasından kaynaklanıyor.

[Troubleshooting LUNs detected as snapshot LUNs in vSphere](https://knowledge.broadcom.com/external/article/323142/troubleshooting-luns-detected-as-snapsho.html)

Bu durumda force mount ile problemi çözebiliriz ancak bunun da beraberinde getireceği bazı problemler var. Kısaca özetlemek gerekirse:

**Force mount:** Datastore’u herhangi bir kesinti yaşatmadan mount eder, UUID değişmediği için ileride GUI üzerinden genişletme yapamazsınız, ve yeni hostlarda mount edilme problemi tekrar yaşanabilir.

**Resignature:** Yeni UUID ile datastore yeni bir imza kazanır. Böylece koruma mekanizması devre dışı kalır, ama yeniden mount edilirken GUI kısıtlamaları azalır. Ancak bu işlemi yapabilmek için datastore’u maintenance modeuna almak gerekiyor.

------------------------------------------------------------------------

## Çözüm Adımları

Exsi’a SSH ile bağlanarak aşağıdaki komutu çalıştırıyoruz. Bu komut, sistem tarafından algılanmış ama mount edilmemiş VMFS volume’ları listeler.

``` text
esxcli storage vmfs snapshot list
```

**Örnek çıktı:**

``` text
66759913-1a8be7cc-960f-0800691800c8
  Volume Name: MSA2022_Pool01
  VMFS UUID: 66759913-1a8be7cc-960f-0800691800c8
  Can mount: true
  Reason for un-mountability:
  Can resignature: false
  Reason for non-resignaturability: the volume is being actively used
  Unresolved Extent Count: 1
```

**Volume Mount Durumu**

- **Can mount: true** ise mount edilebilir.
- **Can resignature: false** ve “actively used” ibaresi varsa, bu volume başka host tarafından zaten kullanılıyor.
- Bu durumda resignature işlemi yapmak isteiğimizde hata verecektir. Zorla yapmaya çalışırsak eğer de veri kaybı yaşayacağız.
- Bu nedenle datastore’u resignature yapmadan herhangi bir değişiklik yapmadan mount edeceğiz.

``` text
esxcli storage vmfs snapshot mount -u 66759913-1a8be7cc-960f-0800691800c8
```

------------------------------------------------------------------------

## Sonuç

Problemimi şu an için force mount ile gidermek iş sürekliliği açısından en efektif çözümdü ancak ileride datastore extend gibi işlemleri gui üzerinden yapabilmek ya da yeni hostlar bağladığımda benzer problemleri yaşamamak adına resignature ile datastore’u tekrar bağlamak en sağlıklı yol olacaktır.
