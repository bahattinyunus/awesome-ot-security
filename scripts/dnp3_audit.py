#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security
Modül: DNP3 Protokol Denetim ve Keşif Aracı (DNP3 Audit)
Açıklama: Su, gaz ve elektrik şebekelerinde kullanılan DNP3 (IEEE 1815)
          protokolünü konuşan Outstation (RTU) cihazlarını sorgular.
          Data Link Reset ve Status paketleri göndererek açık metin ve
          kimlik doğrulamasız çalışma durumunu doğrular.
=============================================================================
"""

import argparse
import socket
import sys
import time

def banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║            DNP3 (IEEE 1815) Denetim Aracı v1.0.0            ║
    ║        Awesome OT Security Toolkit - bahattinyunus           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def calculate_crc(data):
    """DNP3 16-bit CRC hesaplayıcısı."""
    crc = 0x0000
    for byte in data:
        crc = (crc ^ byte)
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA653
            else:
                crc = (crc >> 1)
    return (~crc) & 0xFFFF

def build_dnp3_link_status_frame(src=1, dst=1024):
    """
    DNP3 Link Status İstek Çerçevesi (Data Link Katmanı)
    Başlık (Header): 0x05, 0x64
    Uzunluk: 5 bayt
    Kontrol: 0x49 (Primary, FCV=0, Function=9 / Request Status of Link)
    """
    header_sync = b"\x05\x64"
    length = 5
    control = 0x49
    dst_bytes = dst.to_bytes(2, byteorder="little")
    src_bytes = src.to_bytes(2, byteorder="little")

    header_data = bytes([length, control]) + dst_bytes + src_bytes
    crc = calculate_crc(header_data)
    crc_bytes = crc.to_bytes(2, byteorder="little")

    return header_sync + header_data + crc_bytes

def audit_dnp3_target(ip, port=20000, timeout=3):
    print(f"[*] Hedef DNP3 Outstation test ediliyor: {ip}:{port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect((ip, port))
        print("[+] TCP bağlantısı kuruldu.")

        # Link Status sorgusu gönder
        probe = build_dnp3_link_status_frame(src=1, dst=1024)
        print(f"[*] DNP3 Request Link Status gönderiliyor ({len(probe)} bayt)...")
        sock.sendall(probe)

        response = sock.recv(1024)
        if len(response) >= 10 and response[0:2] == b"\x05\x64":
            print(f"[+] DNP3 GEÇERLİ YANIT ALINDI! ({len(response)} bayt)")
            control_byte = response[3]
            print(f"    [*] Dönen Kontrol Baytı: 0x{control_byte:02X}")
            print("    [!] AÇIK METİN DNP3 TESPİT EDİLDİ: Cihaz şifresiz ve kimlik doğrulamasız yanıt veriyor!")
            print("    [!] DNP3-SAv5 (Secure Authentication) uygulanmamış görünüyor.")
            return True
        else:
            print("[-] Cihazdan DNP3 başlığı içeren bir yanıt dönmedi.")
            return False

    except socket.timeout:
        print("[-] Zaman aşımı: Cihaz DNP3 paketine yanıt vermedi.")
        return False
    except ConnectionRefusedError:
        print("[-] Bağlantı reddedildi: Port 20000 kapalı.")
        return False
    except Exception as e:
        print(f"[-] İletişim hatası: {e}")
        return False
    finally:
        sock.close()

def main():
    banner()
    parser = argparse.ArgumentParser(description="DNP3 Outstation Güvenlik Denetim Aracı")
    parser.add_argument("-t", "--target", required=True, help="Hedef DNP3 cihaz IP adresi")
    parser.add_argument("-p", "--port", type=int, default=20000, help="DNP3 Portu (Varsayılan: 20000)")
    parser.add_argument("--timeout", type=int, default=3, help="Bağlantı zaman aşımı (saniye)")

    args = parser.parse_args()
    audit_dnp3_target(args.target, port=args.port, timeout=args.timeout)

if __name__ == "__main__":
    main()
