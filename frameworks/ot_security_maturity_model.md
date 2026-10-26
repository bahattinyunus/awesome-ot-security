# 📈 Endüstriyel Siber Güvenlik Olgunluk Modeli ve Değerlendirme Çerçevesi (OT-CMM)

Bu çerçeve; enerji santralleri, su arıtma tesisleri, rafineriler ve üretim fabrikalarının siber dayanıklılık seviyelerini ölçmek ve kademeli bir yol haritası (Roadmap) çizmek üzere NIST SP 800-82, CISA CPGs ve ISA/IEC 62443 standartları harmanlanarak hazırlanmış 5 aşamalı bir öz-değerlendirme modelidir.

---

## 🎯 5 Aşamalı Olgunluk Seviyeleri (Maturity Levels)

```text
Seviye 5: Optimizasyon & Sıfır Güven (Zero Trust & Kriptografik Savunma)
   ▲
Seviye 4: Dayanıklılık & Ölçülebilirlik (Resilient, Veri Diyotları, Tatbikatlar)
   ▲
Seviye 3: Görünürlük & Yönetim (Pasif NDR, MFA Jump Host, Top 20 PLC Kodlama)
   ▲
Seviye 2: Temel Segmentasyon (Purdue IDMZ, Ayrı Alt Ağlar, Varlık Envanteri)
   ▲
Seviye 1: Başlangıç / Düzensiz (Ad-hoc, Varsayılan Şifreler, Doğrudan IT-OT Geçişi)
```

---

## 📋 Olgunluk Seviyeleri Detaylı Kontrol Listesi

### Seviye 1: Başlangıç / Düzensiz (Ad-hoc)
- [ ] Saha cihazlarında (PLC, HMI, Gateway) üretici varsayılan parolaları (`admin/admin`, `1111`) kullanılmaktadır.
- [ ] Kurumsal ağ ile saha kontrol ağı arasında güvenlik duvarı bulunmamakta veya tek bir basit yönlendirici ile bağlıdır.
- [ ] Bakım için harici tedarikçilere açık TeamViewer, AnyDesk veya kontrolsüz doğrudan VPN erişimi verilmektedir.
- [ ] Tesisin güncel bir OT donanım ve yazılım varlık envanteri (Asset Inventory) bulunmamaktadır.
- [ ] Sahada düzenli bir yedekleme (PLC ladder logic, SCADA projesi) rutini yoktur.

---

### Seviye 2: Temel Segmentasyon (Defined & Segmented)
- [ ] **Purdue Modeli:** Kurumsal ağ (Seviye 4) ile Saha ağı (Seviye 3) arasına Seviye 3.5 Endüstriyel DMZ (IDMZ) konumlandırılmıştır.
- [ ] Seviye 4'ten Seviye 1 (PLC/RTU) kontrolörlerine doğrudan erişim tamamen engellenmiştir.
- [ ] Tüm saha cihazlarının IP, MAC, model ve firmware sürümlerini içeren bir varlık envanteri çıkarılmıştır.
- [ ] Tüm varsayılan şifreler güçlü kurumsal parolalarla değiştirilmiştir.
- [ ] PLC programları ve SCADA konfigürasyonları haftalık veya aylık periyotlarla güvenli çevrimdışı ortamlara yedeklenmektedir.

---

### Seviye 3: Görünürlük ve Süreç Güvenliği (Managed & Monitored)
- [ ] **Pasif Ağ İzleme:** Sahadaki ağ anahtarlarından (SPAN/TAP) alınan trafik Zeek, Malcolm veya ticari NDR (Nozomi, Claroty, Dragos) sensörleri ile pasif olarak incelenmektedir.
- [ ] **Güvenli Uzaktan Erişim (SRA):** Dış bakım erişimleri yalnızca Seviye 3.5 IDMZ üzerindeki Çok Faktörlü Kimlik Doğrulama (MFA) korumalı Jump Box üzerinden sağlanmaktadır.
- [ ] **PLC Kod Güvenliği:** PLC programcıları *"Top 20 Güvenli PLC Kodlama İlkeleri"*ne (fiziksel limit kısıtlama, sanity check) uygun kod geliştirmektedir.
- [ ] Mühendislik istasyonlarında (EWS) ve HMI bilgisayarlarında USB port kısıtlaması ve Uygulama Beyaz Listeleme (Application Whitelisting) aktiftir.

---

### Seviye 4: Dayanıklılık ve Süreç Bütünlüğü (Resilient & Measured)
- [ ] **Fiziksel İzolasyon:** Kritik Seviye 3 SCADA sunucularından kurumsal ağa veri aktarımı tek yönlü donanımsal **Veri Diyotları (Data Diodes)** üzerinden gerçekleştirilmektedir.
- [ ] **ICS Olay Müdahale Planı:** Yıllık masaüstü siber kriz tatbikatları (Tabletop Exercises) ve "Island Mode" (manuel mekanik kontrole geçiş) testleri icra edilmektedir.
- [ ] **IEC 62443 Uyumluluğu:** Tesis içindeki üretim hatları Bölge ve İletim Kanalları (Zones & Conduits) metodolojisine göre mikro-segmente edilmiştir.
- [ ] PLC'lerin fiziksel `RUN` anahtarları kilitlenmiş, anahtarlar fiziksel kilitli panolarda muhafaza edilmektedir.

---

### Seviye 5: Optimizasyon ve Sıfır Güven (Zero Trust & Optimized)
- [ ] **Kriptografik Protokoller:** Sahada çalışan endüstriyel protokoller şifreli ve kimlik doğrulamalı varyantlara dönüştürülmüştür (CIP Security, Modbus Security, IEC 62351, OPC UA Basic256Sha256).
- [ ] **Süreç Tabanlı Anomali Tespiti:** Yalnızca ağ anomalileri değil; kimyasal formül sapmaları, türbin devir frekansı tutarsızlıkları ve fiziksel telemetri anomalileri makine öğrenimi modelleriyle gerçek zamanlı izlenmektedir.
- [ ] PLC firmware ve lojik sağlama toplamları (Hash) kriptografik olarak sürekli doğrulanmaktadır.
- [ ] Tedarik zinciri bileşenleri (Secure Development Lifecycle - IEC 62443-4-1) denetiminden geçmektedir.

---

## 🛠️ Uygulama Yol Haritası Önerisi

1. **İlk 30 Gün (Hızlı Kazanımlar):** Varsayılan şifreleri değiştirin, internete açık tüm RDP/TeamViewer oturumlarını kapatın, PLC kod yedeklerini alın.
2. **90 Gün (Mimari Sağlamlaştırma):** Purdue IDMZ kurun, MFA Jump Box devreye alın, pasif SPAN port dinlemesini başlatın.
3. **180 Gün (Olgunluk Artışı):** Top 20 PLC kodlama ilkelerini devreye alın, masaüstü kriz tatbikatı yapın, IEC 62443 zone ayrımını tamamlayın.
