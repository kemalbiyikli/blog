---
title: "Hyper-V to vSphere Migration"
date: "2024-01-23T22:56:59"
lastmod: "2024-01-23T23:11:53"
slug: "hyper-v-to-vsphere-migration"
categories: ["Veeam", "vSphere"]
tags: ["convert", "Migration", "vCenter", "vSphere"]
draft: false
---
Geçtiğimiz aylarda bir firmayı oldukça eski bir Hyper-V ortamından güncel bir VMware ortamına geçirmemiz gerekti. Bu işlemi en pürüzsüz şekilde nasıl yaparım diye araştırırken en başta aklıma vCenter Converter geldi. Kurulumunu yaptım ve çeşitli testler yaptım, adım adım hataları giderdim ancak ne olursa olsun bu işlem hayallerinizdeki gibi gerçekleşmiyor. Her zaman ufak tefek de olsa bir yerlerde sorun çıkıyor. Sunucunun UUID değiştiği için bazı servisler bozulabiliyor, güvenlikle ilgili Group Policy’lere takılabiliyor, network kartını tanımıyor, taşıyacağınız her sunucuda güvenlik yazılımlarını disable etmeniz gerekiyor, bu da sürecin uzamasına neden oluyor. Bu ve benzeri sorunlarla uğraştığınızda da bu sürecin istediğiniz gibi gerçekleşmeyeceğini anlıyorsunuz. Bu noktada alternatif çözümleri araştırdıktan sonra bu geçiş sürecinde veeam kullanmaya karar verdim.

**Öncelikle neden Veeam’de karar kıldığımı aktarayım.**

1- Sunucularımın UUID’si değişmediği için olası bir çok sorunun da önüne geçmiş oldum.  
2- Backup restore mantığında bir taşıma olacağı için sunucudaki uygulamalar veya policy’lerle ilgili bir işlem yapmam gerekmiyor.

**Kurulum ve Yapılandırma**

1- Yeni kurduğum VMware ortamında sanal sunucu olarak Veeam kurulumunu gerçekleştirdim. Dilerseniz fiziksel bir proxy sunucusu da konumlandırarak backupları SAN üzerinden de alabilirsiniz. Bu sizin network ve storage alt yapınıza göre tercih edeceğiniz bir durum. Benim Hyper-V ve VMware ortamımdaki management network’um 10G olduğu için network üzerinden backup almayı tercih ettim.

2- Backup Repository’leri için sunucuya sanallaştırma ortamında yeni bir disk verdim ve bu diski Windows ortamında REFS olarak yapılandırdım. Devamında bu diski Veeam’de backup repository olarak yapılandırdım.

3- Sunucunun networkünü 10G olarak yapılandırdım. Sunucuyu VMware ortamına geçirirken migration işlemini network üzerinden yapacağımız için sunucuya esxi hostlarımın vMotion Network’ü ile aynı IP bloğundan bir IP adresi verdim.

4- Eski Hyper-V Failover Cluster ortamımı ve yeni VMware ortamımı Veeam’e Hyper-V Failover Cluster olarak ekledim. Bir Hyper-V Failover Cluster ortamınızı Veeam’e eklemek istediğiniz Access Denied hatası ile karşılaşabilirsiniz. Keza ben de aynı şekilde access denied hatasıyla karşılaştım. Genelde birçok insan bu aşamada hata aldığı için her bir node’u ayrı olarak ekleme yoluna gitmiş. Ancak Windows update’lerini eksiksiz bir şekilde yaptığınızda bu hatadan kurtulabilirsiniz.

5- Taşıma işlemi aynı site ve network yapısı içerisinde olacağı için herhangi bir Proxy sunucusu yapılandırmadım.

**Sunucu Migration**

İşlemi iki farklı senaryoda gerçekleştirebiliriz. Sunucuyu kapatma ile ilgili bir sorununuz yoksa direk kapatıp Full Backup alıp işlemlere başlayabilirsiniz. Ya da benim senaryomda olduğu gibi minimum kesintiye ihtiyaç duyuyorsanız eğer Full Backup aldıktan sonra taşıma yapacağınız saatte sunucuyu kapatıp Incremental Backup aldıktan sonra taşımayı gerçekleştirebilirsiniz. Benimki gibi bir senaryoda sırası ile aşağıdaki adımları gerçekleştirebilirsiniz.

Öncelikle aşağıdaki gibi **Instant Recovery** kullanarak sunucumuzu convert ediyoruz.

1- Taşınacak sunucu için bir Backup Job oluşturuyoruz ve Full Backup başlatıyoruz.

![](/wp-content/uploads/2024/01/image-14.png)

![](/wp-content/uploads/2024/01/image-13.png)

![](/wp-content/uploads/2024/01/image-5.png)

2- Full backup işlemi tamamlandıktan sonra taşıma işlemini gerçekleştireceğimiz esnada data kaybı olmaması için sunucuyu kapatıp Incremental Backup başlatıyorum.

3- Backup işlemi tamamlandıktan sonra Instant Recovery işlemini başlatıyorum. Burada sunucuyu Backup diski üzerinden VMware ortamınıza deploy edecektir, isterseniz sunucuyu Power On yapabilirsiniz. Ancak sunucuyu açtığınızda Migration işlemi daha da uzayacaktır. Bu nedenle Instant Recovery tamamlandıktan sonra sağ tıklayıp Migrate to Production seçeneğini seçiyorum.

![](/wp-content/uploads/2024/01/image-4.png)

![](/wp-content/uploads/2024/01/image-3.png)

4- Destination bölümünde Instant Recovery işlemini yapacağımız sunucumuzun ismini, taşıyacağımız hostumuzu, networkümüzü belirliyoruz. Bu aşamada networkü seçmiş olsak dahi taşıma işleminin ardından sunucumuz networkle haberleşmeyecektir. Taşıma işlemi sonrasında network kartını yeniden vmxnet3 olarak ekleyip tanıtmanız gerekiyor. (Bu durum her koşulda bir zorunluluk, mevcutta kullandığınız Hyper-V network adapter VMware ile çalışmayacağı için yeni bir adapter ekleyip config yapmak icap ediyor.)

![](/wp-content/uploads/2024/01/image-1.png)

5- Finish diyerek Instant Recovery işlemini başlatıyoruz. Bu aşamada yukarıda da belirttiğim gibi migration tamamlanmadan VM’i power on yapmıyorum. Aksi halde migration aşaması oldukça uzuyor.

![](/wp-content/uploads/2024/01/image-8.png)

6- Instant Recovery işlemini yaptıktan sonra artık sunucuyu vSphere ortamınızda görebilirsiniz. Sunucumuz şu an Veeam tarafından vSphere üzerinde çalıştırılabilir şekilde convert edildi. Ancak henüz taşıma işlemini gerçekleştirmedik.

![](/wp-content/uploads/2024/01/image-9.png)

7- Taşıma işlemini tamamlamak için **Migrate to Production** seçeneğini kullanıyoruz. Böylelikle Veeam Repository’imiz üzerindeki VM’imizi vSphere ortamına taşımaya başlıyoruz.

![](/wp-content/uploads/2024/01/image-10.png)

8- Destination bölümünde sunucumuzu migrate edeceğimiz host ve datastore’u seçiyoruz.

![](/wp-content/uploads/2024/01/image-11.png)

9- Transfer bölümünde proxy kullanıyorsak eğer proxy sunucularımızı seçiyoruz ve finish diyerek taşıma işlemini başlatıyoruz.

Bu aşmada taşıma işlemimiz tamamlanmış oluyor. Artık Hyper-V üzerinde çalışan sanal sunucumuz vSphere üzerinde çalışmabilecek şekilde convert edildi.

Bu nokta yapmamız gereken tek bir işlem kalıyor. Sunucumuz daha önceden Hyper-V sürücüleri ile çalıştığı için convert sonrasında network kartımız çalışmaz hale geliyor. Sunucumuza VMXNET 3 olarak yeni bir network kartı ekliyoruz Web Console üzerinden bağlanarak VMware Tools kurulumu yapıyoruz. Sunucumuza restart attıktan sonra Windows üzerinden IP Subnet gibi ayarları tekrar yaptıktan sonra geçmiş olsun diyoruz.
