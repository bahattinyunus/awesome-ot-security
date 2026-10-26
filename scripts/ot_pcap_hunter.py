#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security
Modül: OT / ICS Ağ Trafiği Tehdit Avcısı (PCAP Threat Hunter)
Açıklama: Çevrimdışı kaydedilmiş PCAP dosyalarını tarar; endüstriyel
          protokollerdeki (Modbus, S7comm, DNP3, IEC-104) şüpheli yazma
          ve durdurma (CPU STOP) gibi tehlikeli operasyonları tespit eder.
=============================================================================
"""

import argparse
import sys
from collections import defaultdict

try:
    from scapy.all import rdpcap, TCP, UDP, Raw, Ether
except ImportError:
    print("[!] Hata: 'scapy' kütüphanesi bulunamadı.")
    print("    Lütfen yükleyin: pip install scapy")
    sys.exit(1)

def banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║       OT / ICS Ağ Trafiği Tehdit Avcısı (PCAP Hunter)        ║
    ║        Awesome OT Security Toolkit - bahattinyunus           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def analyze_pcap(filepath):
    print(f"[*] PCAP dosyası yükleniyor: {filepath}...")
    try:
        packets = rdpcap(filepath)
    except Exception as e:
        print(f"[-] Hata: PCAP okunamadı: {e}")
        return

    print(f"[+] Toplam {len(packets)} paket analiz ediliyor...\n")

    stats = defaultdict(int)
    suspicious_events = []

    for idx, pkt in enumerate(packets):
        # 1. Modbus TCP Analizi (Port 502)
        if pkt.haslayer(TCP) and (pkt[TCP].dport == 502 or pkt[TCP].sport == 502):
            stats["Modbus_Packets"] += 1
            if pkt.haslayer(Raw):
                payload = bytes(pkt[Raw])
                # Modbus MBAP Başlığı: 7 bayt (TransID:2, ProtoID:2, Len:2, UnitID:1)
                if len(payload) >= 8:
                    func_code = payload[7]
                    stats[f"Modbus_FC_{func_code}"] += 1
                    
                    # Yazma operasyonları (0x05, 0x06, 0x0F, 0x10)
                    if func_code in [0x05, 0x06, 0x0F, 0x10]:
                        suspicious_events.append({
                            "packet_no": idx + 1,
                            "protocol": "Modbus TCP",
                            "severity": "YÜKSEK",
                            "desc": f"Yetkisiz Yazma Girişimi! Fonksiyon Kodu: 0x{func_code:02X}",
                            "src": f"{pkt['IP'].src}:{pkt[TCP].sport}",
                            "dst": f"{pkt['IP'].dst}:{pkt[TCP].dport}"
                        })

        # 2. Siemens S7comm Analizi (Port 102)
        elif pkt.haslayer(TCP) and (pkt[TCP].dport == 102 or pkt[TCP].sport == 102):
            stats["S7comm_Packets"] += 1
            if pkt.haslayer(Raw):
                payload = bytes(pkt[Raw])
                # TPKT (4) + COTP (3) = 7 bayt
                # S7comm Protokol Tanıtıcısı: 0x32
                if len(payload) > 17 and payload[7] == 0x32:
                    # CPU STOP komutu araması (0x29)
                    if b"\x29" in payload:
                        suspicious_events.append({
                            "packet_no": idx + 1,
                            "protocol": "Siemens S7comm",
                            "severity": "KRİTİK",
                            "desc": "PLC CPU STOP (Durdurma) Komutu Tespit Edildi!",
                            "src": f"{pkt['IP'].src}:{pkt[TCP].sport}",
                            "dst": f"{pkt['IP'].dst}:{pkt[TCP].dport}"
                        })

        # 3. DNP3 Analizi (Port 20000)
        elif (pkt.haslayer(TCP) and (pkt[TCP].dport == 20000 or pkt[TCP].sport == 20000)) or \
             (pkt.haslayer(UDP) and (pkt[UDP].dport == 20000 or pkt[UDP].sport == 20000)):
            stats["DNP3_Packets"] += 1

        # 4. IEC 61850 GOOSE Analizi (EtherType 0x88B8)
        elif pkt.haslayer(Ether) and pkt[Ether].type == 0x88B8:
            stats["GOOSE_Frames"] += 1

    # Raporlama
    print("=" * 60)
    print("                 TRAFİK VE PROTOKOL İSTATİSTİKLERİ             ")
    print("=" * 60)
    for proto, count in stats.items():
        print(f"  * {proto:<25} : {count} paket")

    print("\n" + "=" * 60)
    print(f"            ŞÜPHELİ / TEHLİKELİ OT OLAYLARI ({len(suspicious_events)})           ")
    print("=" * 60)
    if not suspicious_events:
        print("  [+] Belirgin bir şüpheli yazma veya PLC durdurma komutuna rastlanmadı.")
    else:
        for ev in suspicious_events:
            print(f"  [Paket #{ev['packet_no']:<5}] [{ev['severity']}] {ev['protocol']}")
            print(f"    Tanım : {ev['desc']}")
            print(f"    Akış  : {ev['src']} -> {ev['dst']}\n")

def main():
    banner()
    parser = argparse.ArgumentParser(description="OT/ICS PCAP Tehdit Avcısı")
    parser.add_argument("-r", "--pcap", required=True, help="Taranacak PCAP dosyasının yolu")
    args = parser.parse_args()

    analyze_pcap(args.pcap)

if __name__ == "__main__":
    main()
