# 🛡️ Top 20 Güvenli PLC Kodlama İlkeleri (Secure PLC Coding Practices)

![Endüstriyel PLC Kontrol Panosu](../assets/industrial_plc_control_panel.jpg)

Endüstriyel siber güvenlik tarih boyunca neredeyse tamamen ağ düzeyinde güvenlik duvarları, VPN'ler ve IDS/IPS sistemleri ile ele alınmıştır. Ancak ağ çeperi aşıldığında (veya USB gibi fiziksel yollarla bypass edildiğinde), kontrolörler (PLC/RTU) kendilerine gelen her komutu sorgusuz sualsiz çalıştırır.

**Top 20 Güvenli PLC Kodlama İlkeleri**, güvenliği doğrudan Seviye 1 mantıksal kontrolörün (PLC) kendi programlama döngüsüne (Ladder Logic, Structured Text, Fonksiyon Blokları) yerleştiren küresel bir inisiyatiftir.

---

## 📋 20 Temel İlke ve Türkçe Açıklamaları

### 1. PLC Çalışma Modunu Donanımsal Olarak Kilitleyin
- **Prensip:** Saha devreye alındıktan sonra PLC üzerindeki fiziksel anahtar (Key Switch) `REMOTE` konumundan çıkarılıp `RUN` moduna alınmalı ve anahtar panodan çıkarılarak kilitlenmelidir.
- **Güvenlik Kazancı:** Ağ üzerinden PLC'ye yetkisiz program yüklenmesi veya `CPU STOP` gönderilmesi donanımsal olarak engellenir.

### 2. Lojik Bütünlüğü PLC İçinde Denetleyin (Sanity Checks)
- **Prensip:** PLC kodu, değişkenlerin ve sensör okumalarının fiziksel dünyanın kurallarına uygunluğunu sürekli kontrol etmelidir.
- **Örnek:** Bir su deposunun su seviyesi sensörü 1 saniye içinde 0 metreden 10 metreye sıçrayamaz. Bu tür mantıksız değişimler siber manipülasyon veya donanım arızası olarak etiketlenmelidir.

### 3. Kullanılmayan Modbus / Ağ Fonksiyonlarını Engelleyin
- **Prensip:** Eğer PLC yalnızca telemetri okumak için kurulmuşsa, kod içerisinde `Write Coil` veya `Write Register` alanları lojik düzeyinde devre dışı bırakılmalıdır.

### 4. PLC Bellek Alanlarını Bölümlendirin (Memory Segregation)
- **Prensip:** HMI tarafından doğrudan erişilen veri blokları (DB'ler) ile kritik güvenlik/emniyet lojiğinin çalıştığı dahili hafıza bölgeleri birbirinden tamamen ayrılmalıdır. HMI asla kritik emniyet değişkenlerine doğrudan yazamamalıdır.

### 5. Girdi Verilerini Filtreleyin ve Doğrulayın (Input Clamping)
- **Prensip:** Operatör HMI üzerinden bir fırın hedef sıcaklığını 10.000°C girse bile, PLC lojiği bu değeri maksimum güvenli eşik olan örneğin 1.200°C ile sınırlamalıdır (Clamp).

### 6. Sahte / Yanıltıcı Telemetri Dedektörleri Ekleyin
- **Prensip:** Stuxnet saldırısında olduğu gibi, saldırganın operatör ekranlarına sahte "her şey normal" verisi göndermesini engellemek için, PLC içindeki sayaçlar ile gerçek zamanlı saatler (RTC) çapraz doğrulanmalıdır.

### 7. Güvenli Durum (Fail-Safe State) Mantığını Kodlayın
- **Prensip:** PLC kontrol sinyali koptuğunda veya sensör kablosu kesildiğinde sistem en tehlikesiz pozisyona geçmelidir (örneğin gaz vanaları kapanmalı, soğutma pompaları çalışmalıdır).

### 8. Zaman Damgalı Olay Günlüklerini PLC İçinde Saklayın
- **Prensip:** HMI veya SCADA sunucusu ele geçirilip loglar silinse bile, kritik durum değişiklikleri PLC'nin dahili kalıcı hafızasında (Retentive Memory) FIFO kuyruğu olarak tutulmalıdır.

### 9. Ağ İletişiminin Canlılığını Denetleyin (Heartbeat / Watchdog)
- **Prensip:** HMI veya SCADA ile PLC arasında sürekli artan bir sayaç (Heartbeat) dönmelidir. Eğer sayaç belirli bir süre (örneğin 3 saniye) güncellenmezse, PLC ağ bağlantısının koptuğunu varsayarak güvenli çalışma moduna geçmelidir.

### 10. Fiziksel Çıkışları Çapraz Doğrulayın (Feedback Loops)
- **Prensip:** PLC bir motoru çalıştırmak için röleye 24V çıkış verdiğinde, motorun gerçekten dönüp dönmediğini yardımcı kontaklardan (auxiliary contact) veya akım trafosundan okuyarak teyit etmelidir.

### 11. HMI Değişkenleri İçin İki Aşamalı Doğrulama Uygulayın
- **Prensip:** Kritik vanaları açmak gibi yüksek riskli işlemler için tek bir bitin `True` olması yetmemeli; iki farklı register'ın belirli bir sıra ile yazılması şart koşulmalıdır (Select-Before-Operate mantığı).

### 12. PLC Kodunun Sağlama Toplamını (Checksum / Hash) Doğrulayın
- **Prensip:** PLC lojiğinin hash değeri düzenli aralıklarla izlenmeli; lojik üzerinde beklenmeyen bir değişiklik olduğunda derhal alarm üretilmelidir.

### 13. Kullanılmayan Protokol ve Portları Kapatın
- **Prensip:** Kullanılmayan web sunucuları (HTTP/HTTPS yönetim panelleri), FTP, SNMP veya telnet servisleri denetleyici yapılandırmasından kapatılmalıdır.

### 14. Güvenli Başlangıç (Cold Start) Parametrelerini Tanımlayın
- **Prensip:** Elektrik kesintisinden sonra PLC yeniden başladığında tüm aktüatörler güvenli başlangıç konumunda kalmalı, kontrolsüz bir çalışma başlamamalıdır.

### 15. PLC Tarama Döngüsü (Scan Cycle) Süresini İzleyin
- **Prensip:** Aşırı ağ trafiği veya DoS saldırıları PLC işlemcisinin tarama döngüsünü uzatır. Tarama süresi izin verilen eşiği aştığında watchdog zamanlayıcısı alarm vermelidir.

### 16. Kayan Noktalı Sayı (Float) Taşmalarını Engelleyin
- **Prensip:** Sıfıra bölme veya NaN (Not a Number) üreten matematiksel hatalar kontrolörün çökmesine yol açabilir; tüm matematiksel hesaplamalardan önce sınır kontrolleri yapılmalıdır.

### 17. Doğrudan Bellek Adresleme Yerine Tanımlı Değişkenler Kullanın
- **Prensip:** Ham bellek adresleri (`%M0.0`, `%MW100`) yerine kesin tanımlı değişken yapıları (Struct / UDT) kullanılmalıdır.

### 18. Yetkisiz Mühendislik İstasyonu Bağlantılarını Kaydedin
- **Prensip:** PLC'ye yeni bir IP adresinden programlama bağlantısı açıldığında bu durum derhal SCADA alarmı olarak bildirilmelidir.

### 19. Donanım Hata Kodlarını (Diagnostic Buffer) Alarm Olarak Yayınlayın
- **Prensip:** PLC dahili donanım arıza kayıtları (örn. Siemens SZL teşhis arabelleği) SCADA ekranlarına otomatik düşürülmelidir.

### 20. Kod İçinde Sabit Parola veya Gizli Fonksiyon Bırakmayın
- **Prensip:** Test amacıyla açılmış arka kapılar, sabit kodlanmış şifreler veya gizli bayraklar canlıya alınmadan önce mutlaka temizlenmelidir.

---

> 🔗 Detaylı orijinal belge ve topluluk projeleri için: [top20.secure-plc-coding.com](https://top20.secure-plc-coding.com/)
