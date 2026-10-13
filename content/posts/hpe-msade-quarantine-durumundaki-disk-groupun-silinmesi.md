---
title: "HPE MSA’de Quarantine Durumundaki Disk Group’un Silinmesi"
date: "2026-08-19T00:00:00"
slug: "hpe-msade-quarantine-durumundaki-disk-groupun-silinmesi"
draft: true
---
**Önemli uyarı:** Bu işlem veri kaybına neden olur. Disk group, pool veya volume üzerindeki tüm veriler ve meta veriler silinir. Bu işlemler HPE MSA 2050 Modelinde gerçekleştirilmiştir. Storage’a eklenen ve önceden kullanılmış olan bir shelf’i yapılandırırken ortaya çıkan hata sonucunda bu yöntem izlenmiştir.

Bu yöntem yalnızca gerçekten kurtarılamayan disk group’lar için uygulanmalıdır. Normal işletim sırasında pool veya disk group silmek için kullanılmamalıdır. Yanlış kullanım, geri döndürülemeyen veri kaybına ve hizmet kesintisine yol açabilir.

## 1. Genel Bakış

HPE MSA serisi storage sistemlerinde disk shelf değişikliği veya ciddi bir sistem hatası sonrasında bir disk group **quarantine** durumuna geçebilir. Sistem, veri bütünlüğünü korumak amacıyla Disk Group’u karantinaya alır. Bu durumda GUI üzerinden işlem yapılamaz ve standart CLI komutları engellenebilir.

Bu yazıda, kurtarılamayan bir disk group’un gerekli yetkiler kullanılarak silinmesi ve işlem sonrasında sistemin çalışır hale getirilmesi açıklanmaktadır.

## 2. Sorunun Belirtileri

<!-- GÖRSEL EKSİK: Quarantine durumundaki disk group ekranı (orijinal görsel Atlassian/Confluence linkiydi, WordPress'te de açılmıyordu) -->

- Disk group durumu: `QTOF`
- Sağlık durumu: `Fault`
- Hata mesajı: `The disk group is quarantined`
- `remove disk-groups`, `delete pool` ve `dequarantine disk-group` gibi komutlar sistem tarafından engellenmektedir.
- Diğer pool, volume veya mapping nesnelerinde de değişiklik yapılamamaktadır.

## 3. İşlem Öncesi Kontroller

Aşağıdaki koşulları doğrulamadan silme işlemine başlamayın:

- Disk Group’un kurtarılabilir olmadığını ve verilerin artık kullanılmayacağını doğrulayın.
- Silinecek disk group ve pool adlarını dikkatlice doğrulayın. Örnek komutlarda `dgA06` ve `A` değerleri kullanılmıştır; kendi sisteminizdeki adlarla değiştirin.
- İşlemin veri kaybına yol açacağını bilerek işlemlere başlayın.

## 4. Diagnostic Rolüne Sahip Kullanıcı Oluşturma

Standart **admin** kullanıcısı diagnostic rolüne sahip değildir. Bu nedenle, gerekli komutları çalıştırabilmek için diagnostic rolü bulunan ayrı bir kullanıcı oluşturulur. Bu adım için mevcut admin kullanıcısıyla oturum açın.

<!-- GÖRSEL EKSİK: Diagnostic rolüne sahip kullanıcı oluşturma komutu -->

```text
create user roles monitor,manage,diagnostic HPE
```

Komutun ardından oluşturduğunuz kullanıcıyla storage sistemine **SSH** üzerinden bağlanın.

## 5. Pool Silme Korumasını Devre Dışı Bırakma

Quarantine durumundaki disk group’u silebilmek için HPE’nin pool silme korumasının devre dışı bırakılması gerekir.

<!-- GÖRSEL EKSİK: Pool silme erişimini etkinleştirme komutu -->

```text
set advanced-settings HPE-delete-pool-access enabled
```

**Dikkat:** Bu ayar uygulandıktan sonra 15 dk. boyunca geçerliliğini koruyacaktır. Bu süre içerisinde işlemin yapılması gerekmektedir.

## 6. Disk Group’u Kurtarılamaz Olarak İşaretleme

Silme yetkisi etkinleştirildikten sonra, sorunlu disk group’u **unrecoverable** olarak işaretleyin. Aşağıdaki örnekte disk group adı `dgA06` olarak verilmiştir. Bu komut, disk group’un kurtarılamaz olduğunu belirtir. Böylece controller, ilgili nesnede kurtarılabilir veri bulunmadığını değerlendirerek silme işlemine izin verir.

<!-- GÖRSEL EKSİK: remove disk-groups komutu çıktısı -->

```text
remove disk-groups dgA06 unrecoverable
```

## 7. Pool’u Silme

Disk group’u kurtarılamaz olarak işaretledikten sonra pool’u silebilirsiniz. Aşağıdaki örnekte pool adı `A` olarak kullanılmıştır.

```text
delete pool A
```

Silme işleminin süresi disk sayısına ve disklerin kapasitesine bağlıdır. İşlem yaklaşık 15 dakika süremektedir; bu süre boyunca sistemi ve controller durumunu izleyin.

## 8. İşlem Sonrası Doğrulama

Pool ve disk group durumlarını aşağıdaki komutlarla kontrol edin:

```text
show pools
show disk-groups
```

Çıktılarda silinen pool ve disk group’un artık listelenmediğini veya beklenen durumda olduğunu doğrulayın.
