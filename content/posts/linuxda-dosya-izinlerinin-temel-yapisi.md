---
title: "Linux’da Dosya İzinlerinin Temel Yapısı"
date: "2025-02-28T23:56:54"
lastmod: "2025-02-28T23:56:55"
slug: "linuxda-dosya-izinlerinin-temel-yapisi"
tags: ["Linux"]
draft: false
---
Linux’ta dosya izinleri, dosyalara ve dizinlere kimlerin erişebileceğini ve bu erişimin nasıl olacağını belirler. Bu izinler, **owner, group ve others** için **read** **write** ve **execute** olmak üzere farklı kombinasyonlarla tanımlanabilir. Bu kombinasyonlar harflerle ya da rakamlarla yönetilebilmektedir. İlk bakışta karmaşık gibi görünse de oldukça basit ve anlaşılır bir düzen mevcuttur.

### **********1. **Harflerle İzinler**** –**Dosya İzinlerinin Sembolik Gösterimi Gösterimi**********

Linux’ta her dosya ve dizin için üç tür izin vardır:

- **Read (r):** Dosyanın içeriğini okuma veya dizindeki dosyaları listeleme izni.
- **Write (w):** Dosyaya veri yazma veya dizinde dosya oluşturma/silme izni.
- **Execute (x):** Dosyayı çalıştırma veya dizine erişme izni.

Bu izinler, üç farklı kullanıcı grubu için ayrı ayrı tanımlanır:

- **Owner (u):** Dosyanın sahibi olan kullanıcı.
- **Group (g)**: Dosyanın ait olduğu grup.
- **Others (o)**: Dosyanın sahibi veya grubunda olmayan diğer tüm kullanıcılar.

Sembolik gösterimde, izinler harflerle **(r, w, x)** ifade edilir. İzinleri eklemek veya kaldırmak için + ve – işaretleri kullanılır.

![](/wp-content/uploads/2025/02/WhatsApp-Gorsel-2025-02-28-saat-23.42.36_9cbbe11b-1024x242.jpg)

- **u+rwx            ** : Owner için **read**, **write** ve **execute** izni verir.
- **g+r                 ** : Group için **read** izni verir.
- **o-x                 ** : Others için **execute** iznini kaldırır.

**Örnekler**:

**Owner (kullanıcı) için tüm izinleri verme**:

``` text
chmod u+rwx /home/kemalb/test.txt
```

Bu komut, **user** için **okuma**, **yazma** ve **çalıştırma** izinleri verir.

    chmod g+r /home/kemalb/test.txt

Bu komut, dosyanın ait olduğu **gruba** okuma izni verir.

### ********2. Sayısal Gösterim (Rakamlarla İzinler)********

Sayısal gösterimde, izinler üç basamaklı bir sayı ile ifade edilir. Her basamak, sırasıyla **owner**, **group** ve **others** için izinleri belirtir. Her izin türü bir sayısal değere karşılık gelir:

- **Read (r)         ** : 4
- **Write (w)       ** : 2
- **Execute (x)     ** : 1

Bu değerler toplanarak her bir kullanıcı grubu için izinler belirlenir. Örneğin:

- **7 (4+2+1)       ** : Read, Write, Execute
- **6 (4+2)           ** : Read & Write.
- **5 (4+1)           ** : Read & Execute.
- **4                     ** : Read
- **0                     ** : Hiçbir izin yok.

**Örnekler:**

    chmod 777 /home/kemalb/test.txt

Herkese tam erişim verir (read, write, execute).

    chmod 660 /home/kemalb/test.txt

Owner ve group için read, write izni verir, diğerlerine hiçbir izin vermez.

### ******4. İzinlerin Uygulanması******

İzinleri düzenlemek için **chmod** komutu kullanılır. Bu komut, hem sembolik hem de sayısal gösterimle kullanılabilir.

- **Sembolik Gösterim**: chmod \[kim\]\[işlem\]\[izinler\] dosya
  - **Kim**: u (sahip), g (grup), o (diğerleri), a (hepsi)
  - **İşlem**: + (ekle), – (kaldır), = (ayarla)
  - **İzinler**: r (okuma), w (yazma), x (çalıştırma)
- **Sayısal Gösterim**: chmod \[izinler\] dosya
  - **İzinler**: Üç basamaklı sayı (örneğin, 755, 644, 750)

### ****5. Örnekler****

    chmod u+rwx,g+r-x,o-rwx /home/kemalb/test.txt

- Sahibe tam erişim verir.
- Gruba okuma izni verir, çalıştırma iznini kaldırır.
- Diğerlerinden tüm izinleri kaldırır.

&nbsp;

    chmod 750 /home/kemalb/test.txt

- Sahip: 7 (4+2+1) → Tam erişim.
- Grup: 5 (4+1) → Okuma ve çalıştırma.
- Diğerleri: 0 → Hiçbir izin yok.

### **6. Sonuç**

Linux’ta dosya izinleri, sistem güvenliği için kritik öneme sahiptir. İzinleri doğru şekilde yönetmek, yetkisiz erişimleri engeller ve sistemin güvenliğini artırır. Sembolik ve sayısal gösterimler, izinleri esnek bir şekilde yönetmemizi sağlar.
