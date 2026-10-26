# 🧪 İnteraktif OT / ICS Güvenlik Test Laboratuvarı (Docker Lab)

![Lab Mimarisi](../assets/lab-topology.svg)

Bu laboratuvar, bilgisayarınızda herhangi bir fiziksel PLC donanımına ihtiyaç duymadan, siber-fiziksel süreçleri, endüstriyel protokol manipülasyonlarını ve tespit mekanizmalarını test etmeniz için tasarlanmış izole bir Docker ortamıdır.

---

## 🏗️ Laboratuvar Mimarisi

```text
               +-------------------------------------------------------+
               |                  Docker Host (Köprü Ağ)               |
               |                     172.28.0.0/16                     |
               +-------------------------------------------------------+
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         │                                 │                                 │
         ▼                                 ▼                                 ▼
+-----------------------+       +-----------------------+       +-----------------------+
|  Simüle Su Deposu     |       |  Conpot Honeypot      |       |  OT Güvenlik İstemcisi|
|      (PLC)            |       |  (S7 / Modbus / BAC)  |       |     (Auditor)         |
|  172.28.0.10:502      |       |  172.28.0.20          |       |  172.28.0.30          |
|  (Host Port: 5020)    |       |  (Host Port: 1020)    |       |  (Test Scriptleri)    |
+-----------------------+       +-----------------------+       +-----------------------+
```

1. **`ot_modbus_plc` (172.28.0.10):**
   - Python ve PyModbus ile yazılmış gerçekçi bir Su Deposu Süreç PLC'si.
   - Pompa (Coil 0) ve Vana (Coil 1) durumuna göre tank seviyesini dinamik olarak hesaplar ve telemetri logları üretir.
2. **`ot_conpot_honeypot` (172.28.0.20):**
   - İnternet ortamındaki saldırganları aldatmak ve keşif girişimlerini yakalamak için çalışan popüler endüstriyel honeypot.
3. **`ot_security_auditor` (172.28.0.30):**
   - `scripts/` dizinindeki tüm denetim araçlarını çalıştırabileceğiniz hazır ortam.

---

## 🚀 Başlangıç

### 1. Laboratuvarı Başlatma

Docker ve Docker Compose yüklü olmalıdır:

```bash
cd labs
docker compose up -d
```

Konteynerlerin durumunu kontrol edin:
```bash
docker compose ps
```

---

## 🎯 Uygulamalı Test Senaryoları

### Senaryo 1: PLC Süreç Telemetrisini İzleme
Simüle edilmiş su deposunun loglarını canlı takip edin:
```bash
docker logs -f ot_modbus_plc
```
*(Tank seviyesinin, basıncın ve pompa durumunun 1 saniyelik tarama periyotlarında aktığını göreceksiniz).*

---

### Senaryo 2: İstemci Üzerinden Modbus Denetimi Yapma
Denetim konteynerine giriş yapın ve `modbus_auditor.py` betiğini çalıştırın:

```bash
docker exec -it ot_security_auditor bash

# PLC bellek haritasını oku (172.28.0.10:502)
python modbus_auditor.py -t 172.28.0.10 -p 502

# Yetkisiz Coil yazma zafiyeti testi uygula (Pompayı veya vanayı aç)
python modbus_auditor.py -t 172.28.0.10 -p 502 --test-write
```

---

### Senaryo 3: Conpot Honeypot Taraması
Honeypot üzerindeki servisleri yerel ağdan veya auditor konteynerinden keşfedin:

```bash
# S7comm servisini sorgula (Port 102)
python s7_recon.py -t 172.28.0.20 -s 2

# Nmap ile endüstriyel servis taraması
nmap -Pn -sT -p 102,502 172.28.0.20 --script s7-info,modbus-discover
```

---

## 🛑 Laboratuvarı Durdurma

Testleriniz bittiğinde tüm laboratuvarı temizlemek için:

```bash
docker compose down -v
```
