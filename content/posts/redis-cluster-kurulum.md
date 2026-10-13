---
title: "Ubuntu Server Üzerinde Redis Cluster Kurulumu"
date: "2025-03-02T01:29:01"
lastmod: "2025-03-02T01:36:31"
slug: "ubuntu-server-uzerinde-redis-cluster-kurulumu"
tags: ["Linux", "Ubuntu", "Redis"]
draft: false
---
### **Redis Nedir?**

Redis, verileri RAM üzerinde tutarak yüksek hızda okuma ve yazma işlemleri gerçekleştiren bir anahtar-değer (key-value) veri deposudur. Genellikle bir önbellek veya mesaj kuyruğu olarak kullanılır. Geleneksel veritabanlarına kıyasla çok daha hızlı çalıştığı için, performans gerektiren birçok uygulamada tercih edilmektedir.

#### **Redis’in Kullanım Alanları**

- **Önbellekleme (caching):** Web uygulamalarında sık kullanılan verilerin hızlı erişilebilir olmasını sağlar.
- **Gerçek zamanlı analiz:** Örneğin, leaderboard veya sayfa görüntüleme sayaçları gibi işlemlerde kullanılır.
- **Mesaj kuyruğu:** Verileri geçici olarak saklayarak dağıtık sistemlerde mesajlaşma altyapısı sağlar.
- **Oturum yönetimi:** Kullanıcı oturumlarını verimli bir şekilde saklayarak performansı artırır.

#### **Hangi İşletim Sistemlerinde Çalışır?**

Redis, **en stabil ve performanslı şekilde Linux ortamında** çalışmaktadır. Ancak farklı platformlarda da belirli yöntemlerle kullanılabilir:

- **Linux:** Resmi olarak desteklenir ve production ortamları için önerilen işletim sistemidir.
- **macOS:** Geliştirme ve test süreçlerinde kullanılabilir ancak production ortamları için önerilmez.
- **Windows:** Resmi bir Redis desteği bulunmamaktadır. Ancak WSL2 veya üçüncü taraf çözümlerle çalıştırmak mümkündür.

**Üretim ortamları için daima Linux tercih edilmelidir.** Genellikle **Ubuntu, Debian veya CentOS/Rocky Linux** gibi dağıtımlar tercih edilmektedir.

## **Redis Cluster Nedir, Nasıl Kurulur?**

Redis Cluster, **yüksek erişilebilirlik ve ölçeklenebilirlik** sağlamak amacıyla geliştirilmiş bir yapılandırmadır. Verileri **shard’lara** bölerek birden fazla sunucuya dağıtır. Bu sayede:

- **Performans artırılır,** çünkü yük birden fazla node’a dağıtılır.
- **Tek bir sunucu devre dışı kalsa bile** sistem çalışmaya devam eder.
- **Otomatik failover** mekanizması sayesinde veri bütünlüğü korunur.

### **1. Redis Cluster Tasarımı**

Redis Cluster’ın sağlıklı çalışabilmesi için **minimum 6 node’lu bir yapı** önerilmektedir:

- **3 Master, 3 Replica olmak üzere toplamda 6** node kullanılır.
- **Master node’lar veriyi saklarken, Replica node’lar yedekleme ve failover işlemlerini üstlenir.**
- **Bir Master node devre dışı kaldığında, ilgili Replica otomatik olarak Master rolünü devralır.**
- **Veriler, sharding yöntemi ile tüm node’lar arasında dengeli bir şekilde dağıtılır.**

Bu yapılandırma, Redis’in **yüksek erişilebilirlik ve ölçeklenebilirlik** sunmasını sağlar.

### **Kurulum Adımları (Ubuntu Server)**

Örnek olarak 6 Redis Node’u kuruyoruz. Her bir sunucu için benzersiz ip adresleri ve hostname’ler veriyoruz. Şimdi bunları bir cluster’a çevireceğiz.

- **Sunucu 1**: redis01 \> 10.10.0.101 \> **Master 1**
- **Sunucu 2**: redis02 \> 10.10.0.102 \> **Master 2**
- **Sunucu 3**: redis03 \> 10.10.0.103 \> **Master 3**

- **Sunucu 4**: redis04 \> 10.10.0.104 \> **Replica 1**
- **Sunucu 5**: redis05 \> 10.10.0.105 \> **Replica 2**
- **Sunucu 6**: redis06 \> 10.10.0.106 \> **Replica 3**

#### **1. Redis’in Yüklenmesi**

Tüm sunucularda Redis kurulumunu gerçekleştirelim:

    sudo apt update -y
    sudo apt install redis -y

Yükleme tamamlandıktan sonra redis servisini kontrol ediyoruz.

    systemctl status redis

#### **2. Redis Konfigürasyon Dosyası**

Redis’i tüm sunuculara yükledikten sonra Cluster kurabilmek için tüm sunucularda konfigürasyon dosyasını da düzenlememiz gerekiyor. Aşağıdaki komut ile redisin varsayılan konfigürasyon dosyasına ulaşabilirsiniz.

    nano /etc/redis/redis.conf

#### **Redis Yapılandırma Ayarları**

Redis’in verimli ve güvenilir çalışabilmesi için bazı temel yapılandırma ayarlarının yapılması gerekmektedir. Bu ayarların her biri, Redis’in dayanıklılığını, performansını ve ölçeklenebilirliğini artırmak için kritik öneme sahiptir.

##### **1. Veri Kaybını Önlemek İçin: `appendonly yes`**

Redis, **RAM** tabanlı çalıştığı için ani bir sunucu çökmesi durumunda tüm verilerin kaybolma riski vardır. Bu durumu önlemek için **kalıcı veri saklama (persistence) mekanizmaları** kullanılmalıdır. Redis’te iki farklı yöntem bulunmaktadır:

- **RDB (Redis Database Snapshot):** Belirli aralıklarla tüm veritabanının anlık görüntüsünü (snapshot) alır ve diske yazar.
- **AOF (Append-Only File):** Yapılan tüm işlemleri log dosyasına sürekli olarak kaydeder.

**Önerilen Ayar:**`appendonly yes`

Bu ayar etkinleştirildiğinde Redis, her değişikliği disk üzerinde loglayarak ani çökme durumlarında veri kaybını en aza indirir.

##### **2. Timeout Ayarları: `cluster-node-timeout 5000`**

Redis Cluster yapısında, düğümler (nodes) arasındaki iletişim kritik bir konudur. `cluster-node-timeout` parametresi, bir düğümün diğer düğümlerle iletişim kuramadığında ne kadar süre içinde başarısız (failed) olarak işaretleneceğini belirler.

- **Düşük bir değer (örneğin 1000 ms) kullanılırsa:** Küçük ağ gecikmeleri bile düğümlerin başarısız olarak algılanmasına neden olabilir. Bu durum gereksiz failover işlemlerine yol açarak cluster’ın istikrarsız hale gelmesine sebep olabilir.
- **Çok yüksek bir değer kullanılırsa:** Gerçekten çöken bir düğümün fark edilmesi gecikeceği için failover süreci uzar ve hizmet kesintileri yaşanabilir.

**Önerilen Ayar:**`cluster-node-timeout 5000`

Genellikle **3-5 saniye arası** ideal bir değerdir. Eğer ağ altyapınızda gecikmeler yaşanıyorsa, değeri biraz daha yükseltebilirsiniz.

##### **3. Bellek Yönetimi: `maxmemory` ve `maxmemory-policy`**

Redis, tüm verileri RAM üzerinde tuttuğu için bellek yönetimi büyük önem taşır. Eğer bellek sınırı belirlenmezse, iki önemli risk ortaya çıkabilir:

1.  **Sistem belleği tamamen dolar ve Redis süreci çöker.** Bu durumda Redis, sistem tarafından sonlandırılabilir.
2.  **Yeni veri eklenemez, uygulamalar hata verebilir.** Bu da performans problemlerine ve beklenmeyen kesintilere yol açabilir.

Bu riskleri önlemek için aşağıdaki iki temel ayarın yapılandırılması gerekmektedir:

#### **a) `maxmemory`: Redis’in Kullanabileceği Maksimum Bellek**

Redis’e ne kadar bellek kullanabileceğini belirtmek için `maxmemory` ayarı kullanılır. Örneğin, Redis’in **2 GB bellek kullanmasını** istiyorsak: `maxmemory 2gb`

#### **b) `maxmemory-policy`: Bellek Dolduğunda Uygulanacak Strateji**

Bellek sınırına ulaşıldığında hangi verilerin silineceğini belirlemek için `maxmemory-policy` ayarı kullanılır. Yaygın olarak kullanılan ve önerilen politika şudur: `allkeys-lru`

Bu ayar etkinleştirildiğinde, **en az kullanılan eski veriler (LRU – Least Recently Used) bellekten temizlenerek** yeni veriler için yer açılır.

#### **4. Diğer Önemli Yapılandırmalar**

Bazı ek ayarlar, Redis’in doğru şekilde çalışmasını sağlamak için gereklidir:

**`cluster-config-file nodes.conf` → Cluster yapılandırma dosyasını tanımlar**

Redis, cluster’daki düğümleri ve bağlantı durumlarını bu dosyada saklar.

**`bind 0.0.0.0` → Tüm IP’lerden erişime izin verir**

Varsayılan olarak Redis, sadece localhost üzerinden erişime açıktır. Eğer Redis’e dış ağdan bağlantı sağlanacaksa bu ayarın değiştirilmesi gerekir.

**`cluster-enabled yes` → Cluster modunu aktif hale getirir**

Redis’in dağıtık mimaride çalışabilmesi için bu ayarın etkinleştirilmesi gerekir.

#### 5. Konfigürasyon Dosyasının Düzenlenmesi

Konfigürasyon dosyasını açıp yukarıda paylaştığım konfigürasyonları eklemek istediğinizde bu neymiş be! diyebilirsiniz. Burada redisle ilgili birçok bilgiyi içeren bilgilerle birlikte kullanmayacağımız birçok ayar da bulunuyor. Bu nedenle yeni ve sade bir konfigürasyon dosyası oluşturmak daha kolay olacaktır. Aşağıdaki komut ile mevcut konfigürasyon dosyasının adını değiştirerek aynı klasör altında **redis.conf.backup** olarak tutuyoruz.

    mv /etc/redis/redis.conf /etc/redis/redis.conf.backup

Eski konfigürasyon dosyasını yedekledikten sonra Aşağıdaki komut ile yeni dosyayı oluşturup aşağıdaki konfigürasyonu içine yazarak kaydediyoruz.

    nano /etc/redis/redis.conf

##### Örnek Konfigürasyon Dosyası

    # Redis Cluster Konfigurasyonu

    # Temel Ayarlar
    port 6379
    bind 0.0.0.0
    protected-mode no

    # Cluster Ayarları
    cluster-enabled yes
    cluster-config-file nodes.conf
    cluster-node-timeout 5000
    cluster-require-full-coverage no

    # Bellek Yönetimi
    maxmemory 2gb
    maxmemory-policy allkeys-lru

    # Disk Kalıcılığı
    appendonly yes
    appendfsync everysec

    dbfilename dump.rdb
    dir /var/lib/redis/

Dosyamızı **tüm sunucularda** oluşturup içeriği kaydettikten sonra **redis servisini restart ediyoruz**.

    systemctl restart redis

## 3. Cluster Kurulumu

Master ve Replica’ları belirleyerek Cluster’ı oluşturuyoruz:

    redis-cli --cluster create 10.10.0.101:6379 10.10.0.102:6379 10.10.0.103:6379 \
    10.10.0.104:6379 10.10.0.105:6379 10.10.0.106:6379 --cluster-replicas 1

Komutu çalıştırdıktan sonra aşağıdaki gibi bir çıktı elde ettiğimizde cluster kurulumu tamamlanmıştır

Bu komut: **İlk 3 Node’u Master** yapar, sonraki **3 Node’u onların Replica’sı** olarak ayarlar.

    root@redis01:~# redis-cli --cluster create 10.10.0.101:6379 10.10.0.102:6379 10.10.0.103:6379 10.10.0.104:6379 10.10.0.105:6379 10.10.0.106:6379 --cluster-replicas 1
    >>> Performing hash slots allocation on 6 nodes...
    Master[0] -> Slots 0 - 5460
    Master[1] -> Slots 5461 - 10922
    Master[2] -> Slots 10923 - 16383
    Adding replica 10.10.0.105:6379 to 10.10.0.101:6379
    Adding replica 10.10.0.106:6379 to 10.10.0.102:6379
    Adding replica 10.10.0.104:6379 to 10.10.0.103:6379
    M: d8710299ca28d14163ea3ecb0427441245a77019 10.10.0.101:6379
       slots:[0-5460] (5461 slots) master
    M: f56239df411d0a16a848444c7558fc275fdfb8f3 10.10.0.102:6379
       slots:[5461-10922] (5462 slots) master
    M: 3681759047207adbb2dc8bd3cf821c525016b82e 10.10.0.103:6379
       slots:[10923-16383] (5461 slots) master
    S: 3d93d577776d88aea8276779ef772cbae2aea2af 10.10.0.104:6379
       replicates 3681759047207adbb2dc8bd3cf821c525016b82e
    S: f756af3c4dbf8e22b9fae6fbf749593d70f1b592 10.10.0.105:6379
       replicates d8710299ca28d14163ea3ecb0427441245a77019
    S: a39b1062bc97ef86d9b192676752122e7922fb19 10.10.0.106:6379
       replicates f56239df411d0a16a848444c7558fc275fdfb8f3
    Can I set the above configuration? (type 'yes' to accept): yes
    >>> Nodes configuration updated
    >>> Assign a different config epoch to each node
    >>> Sending CLUSTER MEET messages to join the cluster
    Waiting for the cluster to join
    ...
    >>> Performing Cluster Check (using node 10.10.0.101:6379)
    M: d8710299ca28d14163ea3ecb0427441245a77019 10.10.0.101:6379
       slots:[0-5460] (5461 slots) master
       1 additional replica(s)
    S: f756af3c4dbf8e22b9fae6fbf749593d70f1b592 10.10.0.105:6379
       slots: (0 slots) slave
       replicates d8710299ca28d14163ea3ecb0427441245a77019
    S: 3d93d577776d88aea8276779ef772cbae2aea2af 10.10.0.104:6379
       slots: (0 slots) slave
       replicates 3681759047207adbb2dc8bd3cf821c525016b82e
    M: f56239df411d0a16a848444c7558fc275fdfb8f3 10.10.0.102:6379
       slots:[5461-10922] (5462 slots) master
       1 additional replica(s)
    M: 3681759047207adbb2dc8bd3cf821c525016b82e 10.10.0.103:6379
       slots:[10923-16383] (5461 slots) master
       1 additional replica(s)
    S: a39b1062bc97ef86d9b192676752122e7922fb19 10.10.0.106:6379
       slots: (0 slots) slave
       replicates f56239df411d0a16a848444c7558fc275fdfb8f3
    [OK] All nodes agree about slots configuration.
    >>> Check for open slots...
    >>> Check slots coverage...
    [OK] All 16384 slots covered.

Cluster kurulumu tamamlandıktan sonra Cluster durumunu kontrol ediyoruz.

    redis-cli -c -p 6379 cluster nodes

Her şey düzgünce yapıladırıldıysa aşağıdaki şekilde **“Master/Slave”** eşleşmeleri görünecektir.

    root@redis01:~# redis-cli -c -p 6379 cluster nodes
    a39b1062bc97ef86d9b192676752122e7922fb19 10.10.0.106:6379@16379 slave f56239df411d0a16a848444c7558fc275fdfb8f3 0 1740867669000 2 connected
    3d93d577776d88aea8276779ef772cbae2aea2af 10.10.0.104:6379@16379 slave 3681759047207adbb2dc8bd3cf821c525016b82e 0 1740867670571 3 connected
    f56239df411d0a16a848444c7558fc275fdfb8f3 10.10.0.102:6379@16379 master - 0 1740867670000 2 connected 5461-10922
    d8710299ca28d14163ea3ecb0427441245a77019 10.10.0.101:6379@16379 myself,master - 0 1740867669000 1 connected 0-5460
    f756af3c4dbf8e22b9fae6fbf749593d70f1b592 10.10.0.105:6379@16379 slave d8710299ca28d14163ea3ecb0427441245a77019 0 1740867670571 1 connected
    3681759047207adbb2dc8bd3cf821c525016b82e 10.10.0.103:6379@16379 master - 0 1740867669867 3 connected 10923-16383
