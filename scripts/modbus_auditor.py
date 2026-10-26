#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security
Modül: Modbus TCP Güvenlik ve Denetim Aracı (Modbus Auditor)
Açıklama: Modbus TCP protokolünü konuşan Seviye 1/2 cihazların (PLC, RTU vb.)
          kimlik bilgilerini sorgular, register/coil alanlarını haritalandırır
          ve yetkilendirme eksikliklerini test eder.
UYARI: Yalnızca yetkili laboratuvar ortamlarında test amacıyla kullanılmalıdır.
=============================================================================
"""

import argparse
import sys
import json
import time

try:
    from pymodbus.client import ModbusTcpClient
    from pymodbus.exceptions import ModbusException
except ImportError:
    print("[!] Hata: 'pymodbus' kütüphanesi bulunamadı.")
    print("    Lütfen yükleyin: pip install pymodbus")
    sys.exit(1)

def banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║        Modbus TCP Güvenlik ve Denetim Aracı v1.0.0          ║
    ║        Awesome OT Security Toolkit - bahattinyunus           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def scan_unit_ids(client, max_id=10):
    """Cevap veren Unit ID (Slave ID) adreslerini tespit eder."""
    print(f"[*] Unit ID (Slave ID) keşfi başlatılıyor (1 - {max_id})...")
    active_units = []
    for uid in range(1, max_id + 1):
        try:
            # 0. adresten 1 holding register okuyarak canlılık testi
            rr = client.read_holding_registers(address=0, count=1, slave=uid)
            if not rr.isError():
                print(f"    [+] Yanıt alındı -> Unit ID: {uid}")
                active_units.append(uid)
        except Exception:
            continue
    if not active_units:
        print("    [-] Belirtilen aralıkta cevap veren Unit ID bulunamadı (Varsayılan 1 denenecek).")
        return [1]
    return active_units

def read_device_info(client, slave_id=1):
    """MEI (Modbus Encapsulated Interface) üzerinden cihaz kimliğini sorgular."""
    print(f"[*] Cihaz kimlik bilgileri sorgulanıyor (MEI Read Device Identification - Unit ID: {slave_id})...")
    info = {}
    try:
        # MEI Read Device Identification genellikle Read Device ID fonksiyonunu destekler
        # Kütüphane sürümüne göre raw paket veya pdu üzerinden de çekilebilir
        pass
    except Exception as e:
        print(f"    [-] Kimlik okunamadı: {e}")
    return info

def audit_memory_map(client, slave_id=1, count=10):
    """Temel Modbus bellek bloklarını okuyarak durum haritasını çıkarır."""
    print(f"\n[*] Bellek Haritası Taraması (İlk {count} kayıt - Unit ID: {slave_id}):")
    report = {
        "coils": [],
        "discrete_inputs": [],
        "holding_registers": [],
        "input_registers": []
    }

    # 1. Coils (00001 - 09999) - Read/Write Bits
    try:
        rr = client.read_coils(address=0, count=count, slave=slave_id)
        if not rr.isError():
            report["coils"] = rr.bits[:count]
            print(f"    [+] Coils (Bobinler)        : {report['coils']}")
        else:
            print(f"    [-] Coils Okunamadı         : {rr}")
    except Exception as e:
        print(f"    [-] Coils Hatası            : {e}")

    # 2. Discrete Inputs (10001 - 19999) - Read-Only Bits
    try:
        rr = client.read_discrete_inputs(address=0, count=count, slave=slave_id)
        if not rr.isError():
            report["discrete_inputs"] = rr.bits[:count]
            print(f"    [+] Discrete Inputs (Giriş) : {report['discrete_inputs']}")
        else:
            print(f"    [-] Discrete Inputs Hatası  : {rr}")
    except Exception as e:
        print(f"    [-] Discrete Inputs Hatası  : {e}")

    # 3. Holding Registers (40001 - 49999) - Read/Write 16-bit Words
    try:
        rr = client.read_holding_registers(address=0, count=count, slave=slave_id)
        if not rr.isError():
            report["holding_registers"] = rr.registers[:count]
            print(f"    [+] Holding Registers (Kayıt): {report['holding_registers']}")
        else:
            print(f"    [-] Holding Regs Hatası     : {rr}")
    except Exception as e:
        print(f"    [-] Holding Regs Hatası     : {e}")

    # 4. Input Registers (30001 - 39999) - Read-Only 16-bit Words
    try:
        rr = client.read_input_registers(address=0, count=count, slave=slave_id)
        if not rr.isError():
            report["input_registers"] = rr.registers[:count]
            print(f"    [+] Input Registers (Giriş) : {report['input_registers']}")
        else:
            print(f"    [-] Input Regs Hatası       : {rr}")
    except Exception as e:
        print(f"    [-] Input Regs Hatası       : {e}")

    return report

def test_unauthorized_write(client, address=0, slave_id=1):
    """Yetkisiz yazma zafiyetini (No-Auth Write) test eder."""
    print(f"\n[!] Yetkilendirme Denetimi: Adres {address} Coil'ine test yazması deneniyor...")
    try:
        # Mevcut durumu al
        curr = client.read_coils(address=address, count=1, slave=slave_id)
        if curr.isError():
            print("    [-] Mevcut bobin durumu okunamadı, test atlanıyor.")
            return False

        orig_val = curr.bits[0]
        test_val = not orig_val
        print(f"    [*] Mevcut Değer: {orig_val} -> Test Değeri Enjekte Ediliyor: {test_val}")

        wr = client.write_coil(address=address, value=test_val, slave=slave_id)
        if wr.isError():
            print(f"    [+] Güvenli: Yazma işlemi reddedildi ({wr}).")
            return False
        else:
            print("    [!] KRİTİK ZAFİYET: Yazma başarılı! Ağda hiçbir kimlik doğrulama bulunmuyor.")
            # Güvenlik amacıyla orijinal değeri hemen geri yükle
            time.sleep(0.5)
            client.write_coil(address=address, value=orig_val, slave=slave_id)
            print(f"    [*] Orijinal değer ({orig_val}) tekrar geri yüklendi.")
            return True
    except Exception as e:
        print(f"    [-] Test sırasında hata: {e}")
        return False

def main():
    banner()
    parser = argparse.ArgumentParser(description="Modbus TCP Güvenlik Denetim Aracı")
    parser.add_argument("-t", "--target", required=True, help="Hedef PLC / Cihaz IP adresi")
    parser.add_argument("-p", "--port", type=int, default=502, help="Modbus TCP Portu (Varsayılan: 502)")
    parser.add_argument("-u", "--unit", type=int, default=None, help="Spesifik Unit ID (Belirtilmezse taranır)")
    parser.add_argument("-c", "--count", type=int, default=10, help="Okunacak adres sayısı (Varsayılan: 10)")
    parser.add_argument("--test-write", action="store_true", help="Yetkisiz yazma zafiyeti testi uygula (Lab ortamı!)")
    parser.add_argument("-o", "--output", help="Sonuçları JSON dosyasına kaydet")

    args = parser.parse_args()

    print(f"[*] Hedef: {args.target}:{args.port}")
    client = ModbusTcpClient(args.target, port=args.port, timeout=4)

    if not client.connect():
        print("[-] HATA: Hedef cihaza TCP bağlantısı kurulamadı. Port kapalı veya cihaz erişilemez!")
        sys.exit(1)

    print("[+] TCP bağlantısı başarılı.")

    # Unit ID tespiti
    if args.unit is not None:
        target_units = [args.unit]
    else:
        target_units = scan_unit_ids(client, max_id=5)

    full_report = {
        "target": args.target,
        "port": args.port,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "units": {}
    }

    for uid in target_units:
        mem_data = audit_memory_map(client, slave_id=uid, count=args.count)
        write_vulnerable = False
        if args.test_write:
            write_vulnerable = test_unauthorized_write(client, address=0, slave_id=uid)
        
        full_report["units"][uid] = {
            "memory": mem_data,
            "unauthorized_write_vulnerable": write_vulnerable
        }

    client.close()
    print("\n[*] Denetim tamamlandı, bağlantı sonlandırıldı.")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        print(f"[+] Rapor kaydedildi: {args.output}")

if __name__ == "__main__":
    main()
