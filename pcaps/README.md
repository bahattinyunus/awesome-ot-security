# 📦 Endüstriyel Ağ Trafiği ve Saldırı PCAP Deposu (Sample OT PCAPs)

Bu dizin, endüstriyel kontrol sistemleri protokollerini ve siber saldırı kalıplarını Wireshark, Snort/Suricata, Zeek veya bu depodaki tehdit avcısı scriptleri ile test edebilmeniz için hazırlanmış örnek paket dökümlerini içerir.

---

## 🎯 Paket İçeriği: `ot_attack_sample.pcap`

| Paket No | Protokol | Akış | Fonksiyon / Detay | Tehdit Seviyesi |
| :--- | :--- | :--- | :--- | :--- |
| **#1** | **Modbus TCP** | `192.168.1.10:49152` -> `192.168.1.50:502` | `FC 03` (Read Holding Registers - Telemetri Okuma) | 🟢 Normal |
| **#2** | **Modbus TCP** | `192.168.1.199:55555` -> `192.168.1.50:502` | `FC 05` (Write Single Coil - Pompa / Vana Açma) | 🔴 **YÜKSEK (Yetkisiz Yazma)** |
| **#3** | **Siemens S7comm** | `192.168.1.199:55556` -> `192.168.1.100:102` | `0x29` (PLC CPU STOP Durdurma Komutu) | 🚨 **KRİTİK (Hizmet Engelleme)** |
| **#4** | **IEC 61850 GOOSE** | `00:24:D7:11:22:33` -> `01:0C:CD:01:00:01` | L2 EtherType `0x88B8` (Trafo Röle Durum Bildirimi) | 🟡 **İzleme (L2 Koruma)** |

---

## 🚀 Nasıl Test Edilir?

### 1. Bu Depodaki Tehdit Avcısı ile Tarama:
```bash
python scripts/ot_pcap_hunter.py -r pcaps/ot_attack_sample.pcap
```

### 2. Wireshark veya Tshark ile İnceleme:
```bash
# Modbus yazma saldırısını görüntüle:
tshark -r pcaps/ot_attack_sample.pcap -Y "modbus.func_code == 5"

# Siemens S7 CPU durdurma komutunu görüntüle:
tshark -r pcaps/ot_attack_sample.pcap -Y "s7comm.param.func == 0x29"
```

### 3. Yeni PCAP Üretme:
`scripts/generate_sample_pcap.py` aracını çalıştırarak istediğiniz zaman temiz veya özel senaryolu yeni paket dökümleri sentezleyebilirsiniz:
```bash
python scripts/generate_sample_pcap.py pcaps/yeni_senaryo.pcap
```
