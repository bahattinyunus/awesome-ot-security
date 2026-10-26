#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security
Modül: IEC 61850 GOOSE Protokol Analizörü ve Anomali Dedektörü
Açıklama: Ethernet Seviye 2 üzerinde çalışan GOOSE (Generic Object Oriented
          Substation Events) trafo merkezi koruma mesajlarını dinler.
          Durum (stNum) ve Sıra (sqNum) numaralarını takip ederek Replay,
          Enjeksiyon ve Paket Taşkını (Flooding) anomalilerini yakalar.
=============================================================================
"""

import argparse
import sys
import time

try:
    from scapy.all import sniff, Ether, Raw
except ImportError:
    print("[!] Hata: 'scapy' kütüphanesi bulunamadı.")
    print("    Lütfen yükleyin: pip install scapy")
    sys.exit(1)

GOOSE_ETHERTYPE = 0x88B8

# Global durum takip yapısı: { (src_mac, app_id): {"stNum": X, "sqNum": Y, "last_time": Z} }
tracker = {}

def banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║       IEC 61850 GOOSE Analizörü & Anomali Dedektörü          ║
    ║        Awesome OT Security Toolkit - bahattinyunus           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def parse_goose_payload(raw_bytes):
    """
    GOOSE PDU (ASN.1 BER) içerisinden APPID, stNum ve sqNum alanlarını çıkarır.
    """
    parsed = {"appid": 0, "stNum": None, "sqNum": None}
    if len(raw_bytes) < 8:
        return parsed
    
    # İlk 2 bayt APPID (Big-endian)
    parsed["appid"] = int.from_bytes(raw_bytes[0:2], byteorder="big")
    
    # Basit ASN.1 BER etiket araması (0x85 = stNum, 0x86 = sqNum)
    idx = 2
    length = len(raw_bytes)
    while idx < length - 2:
        tag = raw_bytes[idx]
        val_len = raw_bytes[idx + 1]
        if tag == 0x85 and idx + 2 + val_len <= length: # stNum
            parsed["stNum"] = int.from_bytes(raw_bytes[idx+2 : idx+2+val_len], byteorder="big")
        elif tag == 0x86 and idx + 2 + val_len <= length: # sqNum
            parsed["sqNum"] = int.from_bytes(raw_bytes[idx+2 : idx+2+val_len], byteorder="big")
        idx += 2 + val_len
    return parsed

def analyze_packet(packet):
    if not packet.haslayer(Ether):
        return
    if packet[Ether].type != GOOSE_ETHERTYPE:
        return

    src_mac = packet[Ether].src
    dst_mac = packet[Ether].dst
    raw_payload = bytes(packet[Raw]) if packet.haslayer(Raw) else bytes(packet[Ether].payload)

    goose_data = parse_goose_payload(raw_payload)
    app_id = goose_data["appid"]
    st_num = goose_data["stNum"]
    sq_num = goose_data["sqNum"]
    curr_time = time.time()

    stream_key = (src_mac, app_id)

    print(f"\n[+] GOOSE Çerçevesi: {src_mac} -> {dst_mac} | APPID: 0x{app_id:04X} | Boyut: {len(packet)}B")
    if st_num is not None and sq_num is not None:
        print(f"    [*] stNum (Durum No): {st_num} | sqNum (Sıra No): {sq_num}")

        # Anomali Analizi
        if stream_key in tracker:
            prev = tracker[stream_key]
            prev_st = prev["stNum"]
            prev_sq = prev["sqNum"]
            time_diff = curr_time - prev["last_time"]

            # 1. Replay Saldırısı Tespiti: stNum aynıyken sqNum geriye düşerse
            if st_num == prev_st and sq_num < prev_sq:
                print(f"    [!] KRİTİK UYARI: Olası REPLAY Saldırısı! (sqNum geriledi: {prev_sq} -> {sq_num})")
            
            # 2. Fiziksel Değişim: stNum artarsa (Şalter/kesici açıldı veya kapandı)
            elif st_num > prev_st:
                print(f"    [★] SÜREÇ DEĞİŞİMİ: Yeni fiziksel olay bildirildi! (stNum: {prev_st} -> {st_num})")
                if sq_num != 0:
                    print(f"    [!] UYARI: Yeni stNum sıfır sqNum ile başlamadı! (sqNum={sq_num})")

            # 3. Paket Taşkını (Flooding / DoS): Çok kısa sürede (< 1ms) çok sayıda paket
            if time_diff < 0.001 and sq_num == prev_sq:
                print(f"    [!] UYARI: Anormal paket frekansı tespit edildi (Flooding şüphesi)!")

        tracker[stream_key] = {"stNum": st_num, "sqNum": sq_num, "last_time": curr_time}

def main():
    banner()
    parser = argparse.ArgumentParser(description="IEC 61850 GOOSE Anomali Analizörü")
    parser.add_argument("-i", "--interface", default=None, help="Dinlenecek ağ arayüzü (örn: eth0)")
    parser.add_argument("-r", "--pcap", default=None, help="Çevrimdışı PCAP dosyası analiz et")
    args = parser.parse_args()

    if args.pcap:
        print(f"[*] PCAP dosyası inceleniyor: {args.pcap}")
        sniff(offline=args.pcap, filter="ether proto 0x88b8", prn=analyze_packet, store=0)
        print("\n[*] PCAP analizi tamamlandı.")
    elif args.interface:
        print(f"[*] Canlı arayüz dinleniyor: {args.interface} (Filtre: ether proto 0x88b8)...")
        sniff(iface=args.interface, filter="ether proto 0x88b8", prn=analyze_packet, store=0)
    else:
        print("[-] Lütfen bir arayüz (-i) veya PCAP dosyası (-r) belirtin.")
        sys.exit(1)

if __name__ == "__main__":
    main()
