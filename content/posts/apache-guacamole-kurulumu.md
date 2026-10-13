---
title: "Apache Guacamole Kurulumu"
date: "2025-03-08T03:52:09"
lastmod: "2025-03-08T16:45:31"
slug: "apache-guacamole-kurulumu"
tags: ["Linux", "Guacamole"]
draft: false
---
### **Giriş**

**Guacamole**, istemci gerektirmeden tarayıcı üzerinden uzak masaüstü bağlantıları yapmanıza olanak tanıyan, **açık kaynaklı** bir **remote desktop gateway** çözümüdür. **RDP, VNC ve SSH** gibi protokolleri destekleyerek çok yönlü kullanım imkanı sunar. Guacamole doğrudan bir sunucuya kurulabilir, ancak bağımlılıklar, güncellemeler, taşınabilirlik açısından Docker ile kurulum yapmak daha pratik ve avantajlıdır. Bu yazımda, Guacamole’un Docker üzerinde nasıl kurulacağını ve yapılandırılacağını adım adım aktarmaya çalışacağım.

### **1. Docker Kurulumu Yapıyoruz**

Docker ve Docker Compose’un kurulumunu aşağıdaki komutlarla gerçekleştiriyoruz.

``` text
sudo apt update
sudo apt install -y docker.io docker-compose
```

Kurulum tamamlandıktan sonra, Docker’ın çalışıp çalışmadığını kontrol ediyoruz. Aşağıdakine benzer bir çıktı görmemiz gerekiyor.

    root@guacamole:~# docker --version
    Docker version 26.1.3, build 26.1.3-0ubuntu1~24.04.1
    root@guacamole:~# docker-compose --version
    docker-compose version 1.29.2, build unknown

### **2. Guacamole ve PostgreSQL için Docker Compose Dosyası Oluşturuyoruz**

Guacamole’un çalışması için **3 ana bileşene** ihtiyacımız var:

1.  `guacd` Guacamole Daemon servisi
2.  `postgres` Kullanıcı ve Bağlantılar için kullanacağımız veritabanı
3.  `guacamole` Uygulamanın web arayüzü

Bu üç bileşenin docker üzerinde kurulumu için öncelikle terminalde şu komutları çalıştırarak bir klasör ve konfigürasyon dosyası oluşturuyoruz.

    root@guacamole:~# mkdir guacamole-docker
    root@guacamole:~# cd guacamole-docker
    root@guacamole:~/guacamole-docker# nano docker-compose.yml

##### **Docker Compose içeriğinde neler var?**

Açılan `docker-compose.yml` dosyasına servislerin kurulumu için gerekli olan içeriği ekliyoruz. Dosyanın içeriği ile ilgili tanımlar şu şekilde.

- `guacd`: Guacamole’un temel servisi.
- `postgres`: PostgreSQL veritabanı servisi.
- `guacamole`: Web arayüzünü sağlayan servis.
- `volumes`: PostgreSQL’in verilerini kalıcı hale getirmek için kullanılıyor.

``` text
version: '3'
services:
  guacd:
    image: guacamole/guacd
    container_name: guacd
    restart: always

  postgres:
    image: postgres:13
    container_name: guac-postgres
    restart: always
    environment:
      POSTGRES_DB: guacamole_db
      POSTGRES_USER: guacuser
      POSTGRES_PASSWORD: guacpass
    volumes:
      - guac-postgres-data:/var/lib/postgresql/data

  guacamole:
    image: guacamole/guacamole
    container_name: guacamole
    restart: always
    depends_on:
      - guacd
      - postgres
    ports:
      - "8080:8080"
    environment:
      GUACD_HOSTNAME: guacd
      POSTGRES_HOSTNAME: postgres
      POSTGRES_DATABASE: guacamole_db
      POSTGRES_USER: guacuser
      POSTGRES_PASSWORD: guacpass

volumes:
  guac-postgres-data:
```

### **3. Docker Servislerini Çalıştırıyoruz**

Hazırladığımız `docker-compose.yml` dosyası ile aşağıdaki komutu kullanarak konteynerleri başlatıyoruz.

    docker-compose up -d

Çalışan konteynerleri kontrol etmek için `docker ps` komutunu kullanıyoruz.

    root@guacamole:~/guacamole-docker# docker ps
    CONTAINER ID   IMAGE                 COMMAND                  CREATED        STATUS                            PORTS                                       NAMES
    3320aed26c8c   guacamole/guacamole   "/opt/guacamole/bin/…"   23 hours ago   Up 3 minutes                      0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   guacamole
    9599dface8ac   guacamole/guacd       "/bin/sh -c '/opt/gu…"   23 hours ago   Up 3 minutes (health: starting)   4822/tcp                                    guacd
    c90d178d512d   postgres:13           "docker-entrypoint.s…"   23 hours ago   Up 3 minutes                      5432/tcp                                    guac-postgres

### **4. PostgreSQL için Veritabanını Yapılandırıyoruz**

**Guacamole** bağlantı yönetimi, kullanıcı yönetimi gibi işlemleri veri tabanı üzerinden yapmaktadır. Veri tabanında bu verileri barındıracağımız tablolar için PostgreSQL içine bir şema yüklememiz gerekiyor. Şemayı yüklemek için öncelikle bir klasör oluşturuyoruz ve gerekli şemaları klasörün altına indiriyoruz.

    root@guacamole:~# mkdir init-sql
    root@guacamole:~# cd init-sql
    root@guacamole:~/init-sql# wget https://raw.githubusercontent.com/apache/guacamole-client/master/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema/001-create-schema.sql
    root@guacamole:~/init-sql# wget https://raw.githubusercontent.com/apache/guacamole-client/master/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema/002-create-admin-user.sql
    root@guacamole:~/init-sql# cd ..

### **Veritabanı Şemalarını Yüklüyoruz**

Şema yükleme işlemini yapmadan önce indirdiğimiz şema dosyalarını taşımamız gerekiyor. Şu anda dosyalarınız **host makinenizde** `/init-sql/` dizini altında bulunuyor. Bu dosyaları Host makinenizdeki `/init-sql/` klasörünü PostgreSQL konteynerinizin `/init-sql/` dizinine kopyalamak için şu komutu çalıştırıyoruz.

``` text
docker cp init-sql/ guac-postgres:/init-sql/
```

Şimdi PostgreSQL konteynerine giriş yapıyoruz.

``` text
docker exec -it guac-postgres bash
```

Konteyner içinde `init-sql` klasörünün geldiğini doğrulamak için ls komutu ile klasörün içeriğini kontrol ediyoruz.

``` text
ls /init-sql/
```

Eğer `001-create-schema.sql` ve `002-create-admin-user.sql` dosyalarını görüyorsak kopyalama işlemi başarılı olmuş demektir.

Şimdi şema dosyalarını yüklemek için PostgreSQL’e giriş yapıyoruz.

``` text
psql -U guacuser -d guacamole_db
```

PostgreSQL’e giriş yaptıktan sonra sırasıyla şu komutları çalıştırarak şema dosyalarını içe aktarıyoruz.

``` text
\i /init-sql/001-create-schema.sql;
\i /init-sql/002-create-admin-user.sql;
```

`CREATE TABLE`, `INSERT`, gibi mesajlar gördüğümüzde işlem başarılı olmuş demektir. `exit` diyerek PostgreSQL’den çıkış yapıyoruz ve `docker-compose.yml` olduğu dizine geri gidiyoruz.

Eğer `docker-compose.yml` dosyanızın olduğu dizinde değilseniz, hatayla karşılaşırsınız. Önce doğru dizine gidin:

``` text
cd /guacamole-docker
```

Sonrasında konteynerleri tekrar başlatıyoruz.

``` text
docker-compose up -d
```

Artık Guacamole’ tarayıcımızdan erişebiliriz. (`localhost `yerine sunucumuzun ip adresini yazıyoruz.)  
**Adres:** `http://localhost:8080/guacamole`  
**Kullanıcı:** `guacadmin`  
**Parola:** `guacadmin`

Uygulamaya giriş yaptıktan sonra sağ üstteki menüden `settings `altına gelerek kullanıcı, grup ve bağlantılar gibi seçenekleri yapılandırıyoruz.

![](/wp-content/uploads/2025/03/image-1-1024x330.png)

Örnek olarak connection tabına gelerek bir sunucu ekliyorum.

1.  Sunucu için bir isim ve kullanacağımız ve yapacağımız bağlantı şeklini belirliyoruz.
2.  Sunucumuzun ip adresi ve bağlantıyı gerçekleştireceğimiz portu belirliyoruz.
3.  Sunucuya login olmak için gerekli olan kullanıcı bilgilerini yazıyoruz.

![](/wp-content/uploads/2025/03/image-2-1024x1018.png)

Bağlantıyı oluşturduktan sonra sağ üstteki menüden `Home`‘a gidiyoruz ve bağlantımızı seçerek çift tıklayıp sunucuya bağlantı işlemini gerçekleştiriyoruz.

![](/wp-content/uploads/2025/03/image-3-1024x231.png)

![](/wp-content/uploads/2025/03/image-4-1024x212.png)

### Sonuç

- Guacamole **RDP** **SSH** ve **VNC** gibi ihtiyaç duyacağımız birçok protokolü desteklemektedir.
- **Herhangi bir istemciye ihtiyaç duymadan** tarayıcı üzerinden çalıştığı için esnek bir kullanım alanına sahiptir.
- **LDAP, RADIUS, OpenID** ve **CAS** gibi kimlik doğrulama mekanizmalarıyla birlikte grup bazlı yönetimi de destekler. Bu sayede yönetimsel kolaylıkla birlikte ekstra güvenlik katmanı sağlar.
- **Dosya transferi kopyala-yapıştır** gibi özellikleri de barındırmaktadır.
- Kullanıcıların gerçekleştirdiği oturumların **video kaydını** almanıza imkan tanır.
- Bir sonraki yazımda oturumların video kaydının harici bir nfs sunucu üzerine nasıl yapıldığını ele alacağım.
