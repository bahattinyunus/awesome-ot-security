# 🦈 Wireshark Endüstriyel Protokol Filtreleri & Paket Analizi Hile Tablosu (Cheat Sheet)

Bu rehber, ağ izleme (SOC/NOC/OT-SOC), olay müdahalesi (DFIR) veya sızma testleri sırasında Wireshark veya `tshark` kullanarak endüstriyel ağ trafiğini filtrelemek için kapsamlı bir başvuru kılavuzudur.

---

## 1. Modbus TCP (Port 502)

| Amaç | Ekran Filtresi (Display Filter) | Açıklama |
| :--- | :--- | :--- |
| **Tüm Modbus Trafiği** | `modbus` | Tüm Modbus paketlerini listeler |
| **Yazma İşlemleri (Write)** | `modbus.func_code == 5 || modbus.func_code == 6 || modbus.func_code == 15 || modbus.func_code == 16` | Tekli/Çoklu bobin ve register yazma |
| **Tekil Bobin Yazma** | `modbus.func_code == 5` | Force Single Coil (Motor aç/kapa vb.) |
| **Holding Register Yazma** | `modbus.func_code == 6 || modbus.func_code == 16` | Süreç parametresi manipülasyonu |
| **İstisna / Hata Yanıtları** | `modbus.exception_code` | Hata dönen paketler (Fuzzing/Tarama işareti) |
| **Spesifik Unit ID** | `modbus.unit_id == 1` | Belirli bir slave cihazın trafiği |
| **Cihaz Tanıma (MEI)** | `modbus.mei` | Read Device Identification sorguları |

---

## 2. Siemens S7comm & S7comm-plus (Port 102 / RFC 1006)

| Amaç | Ekran Filtresi (Display Filter) | Açıklama |
| :--- | :--- | :--- |
| **Tüm S7 Trafiği** | `s7comm` | Tüm ISO-on-TCP ve S7 iletişimleri |
| **CPU STOP Komutu** | `s7comm.param.func == 0x29` | **KRİTİK:** PLC'yi durduran komut |
| **CPU START Komutu** | `s7comm.param.func == 0x28` | PLC'yi başlatan komut |
| **Bellek Yazma (Write)** | `s7comm.param.func == 0x05` | DB veya Merker bellek yazma istekleri |
| **SZL Okuma (Sistem Durumu)**| `s7comm.param.func == 0x00 && s7comm.param.subfunc == 0x01` | Donanım modeli ve teşhis bilgisi sorgusu |
| **Program Yükleme** | `s7comm.param.func == 0x1A` | Request download (Yeni lojik indirme) |
| **S7comm-plus Trafiği** | `s7comm-plus` | S7-1200 / S7-1500 modern oturumları |

---

## 3. DNP3 (Port 20000 / IEEE 1815)

| Amaç | Ekran Filtresi (Display Filter) | Açıklama |
| :--- | :--- | :--- |
| **Tüm DNP3 Trafiği** | `dnp3` | DNP3 trafiğini görüntüler |
| **Soğuk Başlatma (Restart)** | `dnp3.al.func == 18` | **KRİTİK:** Cold Restart (Cihazı yeniden başlat) |
| **Sıcak Başlatma** | `dnp3.al.func == 19` | Warm Restart komutu |
| **Doğrudan İşlet (Direct Operate)**| `dnp3.al.func == 5` | Kesici veya vana tetikleme |
| **Seç ve İşlet (Select-Before-Operate)**| `dnp3.al.func == 3 || dnp3.al.func == 4` | İki aşamalı güvenli kontrol komutları |
| **DNP3 Hata Yanıtı** | `dnp3.al.iin` | Internal Indication bayrakları |

---

## 4. IEC 60870-5-104 (Port 2404 - Telecontrol)

| Amaç | Ekran Filtresi (Display Filter) | Açıklama |
| :--- | :--- | :--- |
| **Tüm IEC-104 Trafiği** | `104asdu || 104apci` | Tüm telekontrol mesajları |
| **Tek Komut (Single Command)** | `104asdu.typeid == 45` | Şalt kesicisi açma/kapama |
| **Çift Komut (Double Command)** | `104asdu.typeid == 46` | Yüksek gerilim ayırıcı/kesici kontrolü |
| **Test Komutu** | `104asdu.typeid == 107` | Hat canlılık test komutu |
| **Genel Sorgulama (Interrogation)**| `104asdu.typeid == 100` | SCADA'nın tüm sahadan veri talep etmesi |
| **STARTDT (Oturum Başlatma)**| `104apci.type == 0x07` | Bağlantı aktivasyon çerçevesi |

---

## 5. IEC 61850 Trafo Otomasyonu (GOOSE, SV, MMS)

| Amaç | Ekran Filtresi (Display Filter) | Açıklama |
| :--- | :--- | :--- |
| **GOOSE Mesajları (L2)** | `goose` veya `eth.type == 0x88b8` | Trafo hızlı koruma mesajları |
| **Sampled Values (SV - L2)**| `sv` veya `eth.type == 0x88ba` | Dijital akım/gerilim dalga formu paketleri |
| **MMS Kontrol Trafiği** | `mms` | SCADA ile koruma rölesi Seviye 7 iletişimi |
| **GOOSE Replay Tespiti** | `goose.sqNum` | Sıra numaralarının anormal değişimi |
| **GOOSE Durum Değişimi** | `goose.stNum` | Kesici açılması gibi fiziksel olay bildirimi |

---

## 6. Rockwell EtherNet/IP & CIP (Port 44818 / 2222)

| Amaç | Ekran Filtresi (Display Filter) | Açıklama |
| :--- | :--- | :--- |
| **Tüm EtherNet/IP Trafiği** | `enip` | TCP 44818 ve UDP 2222 paketleri |
| **Oturum Açma** | `enip.command == 0x0065` | Register Session |
| **CIP İletişimi** | `cip` | Common Industrial Protocol uygulama katmanı |
| **Forward Open (Bağlantı Kur)**| `cip.cm_service == 0x54` | I/O veya mesajlaşma oturumu açma |
| **Etiket / Tag Yazma** | `cip.service == 0x4D` | PLC içindeki Tag değişkenine yazma |

---

## 7. Bina Otomasyonu (BACnet - UDP 47808)

| Amaç | Ekran Filtresi (Display Filter) | Açıklama |
| :--- | :--- | :--- |
| **Tüm BACnet Trafiği** | `bacnet` | Bina otomasyonu paketleri |
| **Özellik Yazma (Write Property)**| `bacnet.service == 15` | İklimlendirme veya kilit durumunu değiştirme |
| **Cihaz Keşfi (Who-Is)** | `bacnet.service == 8` | Ağdaki BACnet cihazlarını tarama |
| **Cihaz Yanıtı (I-Am)** | `bacnet.service == 0` | Cihazın kimlik yanıtı |

---

## 💡 Pratik Tshark (CLI) Komutları

Çevrimdışı PCAP dosyalarını komut satırından hızlıca taramak için:

```bash
# PCAP içindeki tüm Modbus yazma komutlarını listele
tshark -r capture.pcap -Y "modbus.func_code == 5 || modbus.func_code == 16" -T fields -e ip.src -e ip.dst -e modbus.func_code

# Siemens S7 CPU STOP komutunu ara
tshark -r capture.pcap -Y "s7comm.param.func == 0x29"

# IEC 61850 GOOSE çerçevelerini kaynak MAC ve stNum ile dök
tshark -r capture.pcap -Y "goose" -T fields -e eth.src -e goose.stNum -e goose.sqNum
```
