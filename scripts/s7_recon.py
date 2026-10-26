#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security
Modül: Siemens S7comm / S7comm-plus Keşif Aracı (S7 Recon)
Açıklama: Siemens Simatic PLC'leri (S7-300/400/1200/1500) ISO-on-TCP (Port 102)
          üzerinden keşfeder, donanım sipariş kodu (MLFB), firmware versiyonu
          ve CPU çalışma durumunu (RUN/STOP) tespit eder.
UYARI: Yalnızca yetkili laboratuvar ortamlarında test amacıyla kullanılmalıdır.
=============================================================================
"""

import argparse
import sys
import json
import time

try:
    import snap7
    from snap7.snap7types import S7CpuStatusRun, S7CpuStatusStop, S7CpuStatusUnknown
except ImportError:
    print("[!] Hata: 'python-snap7' kütüphanesi bulunamadı.")
    print("    Lütfen yükleyin: pip install python-snap7")
    sys.exit(1)

def banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║       Siemens S7 PLC Keşif ve Tanılama Aracı v1.0.0          ║
    ║        Awesome OT Security Toolkit - bahattinyunus           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def scan_s7_target(target_ip, rack=0, slot=2, timeout_sec=3):
    client = snap7.client.Client()
    print(f"[*] Hedef taranıyor: {target_ip} (Rack={rack}, Slot={slot})...")
    
    result = {
        "ip": target_ip,
        "rack": rack,
        "slot": slot,
        "connected": False,
        "cpu_state": "Unknown",
        "order_code": None,
        "module_name": None,
        "serial_number": None,
        "as_name": None,
        "module_type": None
    }

    try:
        client.connect(target_ip, rack, slot)
        if client.get_connected():
            result["connected"] = True
            print(f"[+] Başarılı: {target_ip} ile S7 oturumu kuruldu!")

            # 1. CPU Çalışma Durumu
            try:
                state = client.get_cpu_state()
                result["cpu_state"] = str(state)
                print(f"    [*] CPU Çalışma Durumu  : {state}")
            except Exception as e:
                print(f"    [-] CPU durumu alınamadı: {e}")

            # 2. Sipariş Kodu (Order Code - MLFB)
            try:
                order_code = client.get_order_code()
                clean_code = order_code.Code.decode('utf-8', errors='ignore').strip()
                result["order_code"] = clean_code
                print(f"    [+] Donanım Kodu (MLFB) : {clean_code}")
            except Exception as e:
                print(f"    [-] Donanım kodu alınamadı: {e}")

            # 3. CPU / Modül Ayrıntıları
            try:
                info = client.get_cpu_info()
                result["module_name"] = info.ModuleName.decode('utf-8', errors='ignore').strip()
                result["serial_number"] = info.SerialNumber.decode('utf-8', errors='ignore').strip()
                result["as_name"] = info.ASName.decode('utf-8', errors='ignore').strip()
                result["module_type"] = info.ModuleTypeName.decode('utf-8', errors='ignore').strip()

                print(f"    [+] Modül Adı           : {result['module_name']}")
                print(f"    [+] Modül Tipi          : {result['module_type']}")
                print(f"    [+] AS Adı              : {result['as_name']}")
                print(f"    [+] Seri Numarası       : {result['serial_number']}")
            except Exception as e:
                print(f"    [-] CPU bilgileri alınamadı: {e}")

        else:
            print(f"[-] Bağlantı başarısız: {target_ip}")
    except Exception as e:
        print(f"[-] İletişim hatası ({target_ip}): {e}")
    finally:
        try:
            client.disconnect()
            client.destroy()
        except Exception:
            pass

    return result

def main():
    banner()
    parser = argparse.ArgumentParser(description="Siemens S7comm PLC Keşif Aracı")
    parser.add_argument("-t", "--target", required=True, help="Hedef Siemens PLC IP adresi")
    parser.add_argument("-r", "--rack", type=int, default=0, help="Rack numarası (Varsayılan: 0)")
    parser.add_argument("-s", "--slot", type=int, default=2, help="Slot numarası (S7-300 için 2, S7-1200/1500 için 1)")
    parser.add_argument("-o", "--output", help="Sonuçları JSON dosyasına yaz")

    args = parser.parse_args()
    data = scan_s7_target(args.target, rack=args.rack, slot=args.slot)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Rapor kaydedildi: {args.output}")

if __name__ == "__main__":
    main()
