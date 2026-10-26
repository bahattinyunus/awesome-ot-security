# 🎯 MITRE ATT&CK for ICS Derinlemesine Tehdit ve Savunma Matrisi

MITRE ATT&CK for ICS, siber saldırganların endüstriyel otomasyon sistemlerine, enerji iletim şebekelerine, su tesislerine ve üretim hatlarına yönelik operasyonlarında sergiledikleri taktik, teknik ve prosedürleri (TTP) belgeleyen uluslararası referans kütüphanesidir.

---

## 🧭 Taktiksel Saldırı Yaşam Döngüsü

```text
[1. Initial Access] ──> [2. Execution] ──> [3. Persistence] ──> [4. Privilege Escalation]
         │
         ├──> [5. Evasion] ──> [6. Discovery] ──> [7. Lateral Movement]
                   │
                   └──> [8. Collection] ──> [9. Command & Control]
                             │
                             ├──> [10. Inhibit Response Function] (Savunmayı/Emniyeti Felç Et)
                             │
                             ├──> [11. Impair Process Control] (Fiziksel Süreci Boz)
                             │
                             └──> [12. Impact] (Tahribat / Kesinti / Can Kaybı)
```

---

## 🔍 Kritik ICS Teknikleri ve Savunma Stratejileri

### 1. T0843 - Program Download (Yetkisiz Lojik Yükleme)
- **Açıklama:** Saldırganın PLC/RTU kontrolörüne yeni Ladder Logic veya C lojiği yükleyerek cihazın fiziksel çalışma parametrelerini değiştirmesi.
- **Tarihi Örnek:** *Stuxnet* (Natanz santrifüj frekans konvertörlerine yeni kod indirdi).
- **Tespit ve Savunma:**
  - PLC fiziksel anahtarlarını donanımsal olarak `RUN` modunda kilitlemek.
  - Ağ üzerinde mühendislik protokollerinde (S7comm, CIP, Modbus) `Download` fonksiyon kodlarını tespit eden IDS kuralları (Suricata/Zeek) çalıştırmak.
  - PLC kod sağlama toplamlarını (Checksum/Hash) düzenli olarak sorgulamak.

---

### 2. T0855 - Unauthorized Command Message (Yetkisiz Komut Enjeksiyonu)
- **Açıklama:** Saldırganın endüstriyel ağa sahte protokol mesajları basarak vanaları açması, pompaları durdurması veya elektrik kesicilerini tetiklemesi.
- **Tarihi Örnek:** *Industroyer* (Kiev trafo merkezinde IEC-104 ASDU Type 45 komutları ile yüksek gerilim kesicilerini açtı).
- **Tespit ve Savunma:**
  - Protokol düzeyinde kimlik doğrulama (IEC 62351, DNP3-SAv5 veya CIP Security) kullanmak.
  - Ağ segmentasyonu ile Seviye 1 kontrolörlerine erişebilecek kaynak IP adreslerini sıkı güvenlik duvarı kurallarıyla kısıtlamak.

---

### 3. T0836 - Modify Parameter (Süreç Parametresi Değiştirme)
- **Açıklama:** Kimyasal konsantrasyon sınırlarının, fırın sıcaklık limitlerinin veya basınç eşik değerlerinin tehlikeli seviyelere çekilmesi.
- **Tarihi Örnek:** *Oldsmar Su Arıtma Olayı* (Sodyum hidroksit konsantrasyonu 100 ppm'den 11.100 ppm'e çıkarıldı).
- **Tespit ve Savunma:**
  - Top 20 PLC kodlama ilkelerinden *Input Clamping* (Girdi Kısıtlama) uygulamak: PLC lojiği HMI'dan gelen parametreleri fiziksel emniyet eşikleriyle sınırlandırmalıdır.

---

### 4. T0858 - Change Operating Mode (Çalışma Modunu Değiştirme)
- **Açıklama:** PLC'nin çalışma modunu `RUN` durumundan `PROGRAM` veya `STOP` durumuna çekerek kontrol döngüsünü tamamen durdurmak.
- **Tarihi Örnek:** *Industroyer* ve *INCONTROLLER / PIPEDREAM* modülleri.
- **Tespit ve Savunma:**
  - `s7comm.param.func == 0x29` (CPU STOP) gibi komutları tespit eden IDS uyarıları üretmek.

---

### 5. T0880 - Loss of Safety (Fonksiyonel Emniyet Kaybı)
- **Açıklama:** Tesisin patlamasını veya zehirli gaz sızdırmasını engelleyen Emniyet Enstrümanlı Sistemlerin (SIS - Safety Instrumented Systems) devreden çıkarılması.
- **Tarihi Örnek:** *TRITON / TRISIS* (Schneider Electric Triconex SIS kontrolörlerini hedef aldı).
- **Tespit ve Savunma:**
  - Emniyet ağlarını (Safety Network) genel proses ağından (DCS/SCADA) tamamen izole ve hava boşluklu tutmak.
  - SIS kontrolörlerine uzaktan firmware veya lojik güncellemesini fiziksel olarak yasaklamak.
