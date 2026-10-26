# 🛠️ OT / ICS Güvenlik Araç Kiti (Scripts & Tools)

Bu dizin, Operasyonel Teknolojiler (OT) ve Endüstriyel Kontrol Sistemleri (ICS) ağlarında güvenlik denetimi, keşif, anomali tespiti ve tehdit avcılığı yapmak üzere Python ile geliştirilmiş açık kaynaklı araç setini içerir.

---

## 📦 Kurulum

Gerekli Python kütüphanelerini yükleyin:

```bash
cd scripts
pip install -r requirements.txt
```

---

## 🚀 Araçlar ve Kullanım Senaryoları

### 1. `modbus_auditor.py` — Modbus TCP Güvenlik ve Denetim Aracı
Modbus TCP (Port 502) kullanan PLC veya RTU cihazlarını sorgular, slave unit ID keşfi yapar, register ve coil bellek haritasını çıkarır ve yetkisiz yazma (unauthorized write) açıklığını test eder.

```bash
# Canlı PLC bellek haritasını tara
python modbus_auditor.py -t 192.168.1.50 -p 502

# Yetkisiz bobin yazma testi gerçekleştir ve JSON raporu oluştur
python modbus_auditor.py -t 192.168.1.50 -p 502 --test-write -o modbus_audit_report.json
```

---

### 2. `s7_recon.py` — Siemens S7 PLC Keşif ve Tanılama Aracı
Siemens S7-300, S7-400, S7-1200 ve S7-1500 PLC'lere ISO-on-TCP (Port 102) üzerinden bağlanarak donanım sipariş kodunu (MLFB), modül tipini, seri numarasını ve CPU çalışma durumunu (RUN/STOP) tespit eder.

```bash
# S7-300 / S7-400 PLC sorgulama (Slot 2)
python s7_recon.py -t 192.168.1.100 -r 0 -s 2

# S7-1200 / S7-1500 PLC sorgulama (Slot 1)
python s7_recon.py -t 192.168.1.100 -r 0 -s 1 -o s7_report.json
```

---

### 3. `goose_analyzer.py` — IEC 61850 GOOSE Anomali Analizörü
Modern dijital trafo merkezlerinde Seviye 2 Ethernet (EtherType `0x88B8`) üzerinde taşınan GOOSE koruma mesajlarını dinler. Durum numarası (`stNum`) ve sıra numarası (`sqNum`) takibi yaparak olası Replay ve Paket Taşkını (Flooding) saldırılarını tespit eder.

```bash
# Canlı ağ arayüzünü dinleme (Linux: eth0)
sudo python goose_analyzer.py -i eth0

# Kaydedilmiş bir PCAP dosyasını analiz etme
python goose_analyzer.py -r trafo_trafigi.pcap
```

---

### 4. `dnp3_audit.py` — DNP3 Outstation Denetim Aracı
Enerji ve su dağıtım şebekelerinde kullanılan DNP3 (IEEE 1815 - Port 20000) cihazlarına Data Link Status istekleri göndererek cihazın açık metin yanıt verip vermediğini ve DNP3-SAv5 kriptografik doğrulamasının eksikliğini denetler.

```bash
python dnp3_audit.py -t 192.168.1.75 -p 20000
```

---

### 5. `ot_pcap_hunter.py` — Çevrimdışı PCAP Tehdit Avcısı
Ağ güvenlik sensörlerinden veya Wireshark'tan alınmış PCAP paket dökümlerini inceler. Modbus coil/register manipülasyonlarını, Siemens CPU STOP komutlarını ve anormal trafik artışlarını raporlar.

```bash
python ot_pcap_hunter.py -r saha_saldiri_kaydi.pcap
```

---

> [!WARNING]
> **Yasal Uyarı:** Bu araçlar yalnızca izinli eğitim ortamları, meşru güvenlik araştırmaları ve yasal yetkili sızma testleri için geliştirilmiştir. İzin alınmamış üretim sahalarında veya kamu şebekelerinde kullanılması kanunen suçtur.
