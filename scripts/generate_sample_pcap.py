#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security
Modül: Sentetik OT / ICS Saldırı ve Trafik Üreteci (Zero-Dependency PCAP Generator)
Açıklama: Herhangi bir harici kütüphaneye (Scapy vb.) ihtiyaç duymadan,
          saf Python ile standart PCAP ikili formatında endüstriyel saldırı
          ve telemetri paketleri üretir.
          İçerik:
          1. Normal Modbus TCP Okuma (Port 502 / FC 03)
          2. Yetkisiz Modbus TCP Tekli Bobin Yazma Saldırısı (Port 502 / FC 05)
          3. Siemens S7comm CPU STOP Durdurma Saldırısı (Port 102 / 0x29)
          4. IEC 61850 GOOSE L2 Trafo Koruma Çerçevesi (EtherType 0x88B8)
=============================================================================
"""

import struct
import time
import os
import sys

def ip_checksum(data):
    """IPv4 başlık checksum hesaplayıcısı."""
    if len(data) % 2 == 1:
        data += b"\x00"
    s = sum(struct.unpack(f"!{len(data)//2}H", data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return (~s) & 0xFFFF

def build_eth_header(src_mac, dst_mac, eth_type):
    src_bytes = bytes.fromhex(src_mac.replace(":", ""))
    dst_bytes = bytes.fromhex(dst_mac.replace(":", ""))
    return dst_bytes + src_bytes + struct.pack("!H", eth_type)

def build_ipv4_packet(src_ip, dst_ip, proto, payload):
    version_ihl = (4 << 4) | 5
    dscp_ecn = 0
    total_len = 20 + len(payload)
    ident = 0x1234
    flags_fragment = 0x4000  # Don't fragment
    ttl = 64
    checksum = 0

    src_bytes = bytes(map(int, src_ip.split(".")))
    dst_bytes = bytes(map(int, dst_ip.split(".")))

    header_without_checksum = struct.pack(
        "!BBHHHBBH4s4s",
        version_ihl, dscp_ecn, total_len, ident, flags_fragment,
        ttl, proto, 0, src_bytes, dst_bytes
    )
    chk = ip_checksum(header_without_checksum)
    header = struct.pack(
        "!BBHHHBBH4s4s",
        version_ihl, dscp_ecn, total_len, ident, flags_fragment,
        ttl, proto, chk, src_bytes, dst_bytes
    )
    return header + payload

def build_tcp_packet(sport, dport, seq, ack, flags, payload):
    offset_res = (5 << 4)  # 20 bytes header
    window = 64240
    checksum = 0 # Basit analiz için opsiyonel
    urgent_ptr = 0
    return struct.pack("!HHIIBBHHH", sport, dport, seq, ack, offset_res, flags, window, checksum, urgent_ptr) + payload

def generate_ot_pcap(output_file="pcaps/ot_attack_sample.pcap"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    print(f"[*] Saf Python (Zero-Dependency) ile OT PCAP üretiliyor: {output_file}...")

    # PCAP Global Header (24 bytes)
    # Magic: 0xa1b2c3d4, Major: 2, Minor: 4, Zone: 0, Sigfigs: 0, Snaplen: 65535, Network: 1 (Ethernet)
    global_header = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)

    packets_raw = []
    base_ts = int(time.time()) - 3600

    # 1. Normal Modbus TCP Okuma (HMI 192.168.1.10 -> PLC 192.168.1.50)
    # MBAP: TransID: 0x0001, ProtoID: 0x0000, Len: 0x0006, UnitID: 0x01 | FC: 0x03, Start: 0x0000, Count: 0x0002
    mb_read_pdu = b"\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x02"
    tcp1 = build_tcp_packet(49152, 502, 1000, 1, 0x18, mb_read_pdu) # PSH, ACK
    ip1 = build_ipv4_packet("192.168.1.10", "192.168.1.50", 6, tcp1)
    eth1 = build_eth_header("00:1A:2B:3C:4D:5E", "00:50:56:A1:B2:C3", 0x0800) + ip1
    packets_raw.append((base_ts, 100000, eth1))

    # 2. Yetkisiz Modbus TCP Bobin Yazma Saldırısı (Attacker 192.168.1.199 -> PLC 192.168.1.50)
    # FC: 0x05 (Force Single Coil), Addr: 0x0000, Value: 0xFF00 (Zorla Aç)
    mb_attack_pdu = b"\x00\x02\x00\x00\x00\x06\x01\x05\x00\x00\xff\x00"
    tcp2 = build_tcp_packet(55555, 502, 2000, 1, 0x18, mb_attack_pdu)
    ip2 = build_ipv4_packet("192.168.1.199", "192.168.1.50", 6, tcp2)
    eth2 = build_eth_header("DE:AD:BE:EF:00:01", "00:50:56:A1:B2:C3", 0x0800) + ip2
    packets_raw.append((base_ts + 2, 250000, eth2))

    # 3. Siemens S7comm CPU STOP Durdurma Saldırısı (Attacker 192.168.1.199 -> Siemens PLC 192.168.1.100)
    # TPKT (4B) + COTP (3B) + S7comm Header (0x32, Parameter 0x29 CPU Stop)
    s7_stop_payload = b"\x03\x00\x00\x21" + \
                      b"\x02\xf0\x80" + \
                      b"\x32\x01\x00\x00\x00\x01\x00\x0e\x00\x00" + \
                      b"\x29\x00\x00\x00\x00\x00\x09\x50\x5f\x50\x52\x4f\x47\x52\x41\x4d"
    tcp3 = build_tcp_packet(55556, 102, 3000, 1, 0x18, s7_stop_payload)
    ip3 = build_ipv4_packet("192.168.1.199", "192.168.1.100", 6, tcp3)
    eth3 = build_eth_header("DE:AD:BE:EF:00:01", "00:1B:1B:5A:6C:7D", 0x0800) + ip3
    packets_raw.append((base_ts + 4, 500000, eth3))

    # 4. IEC 61850 GOOSE L2 Trafo Koruma Çerçevesi (Multicast L2 0x88B8)
    goose_payload = b"\x00\x01\x00\x18\x00\x00\x00\x00\x85\x01\x01\x86\x01\x00"
    eth4 = build_eth_header("00:24:D7:11:22:33", "01:0C:CD:01:00:01", 0x88B8) + goose_payload
    packets_raw.append((base_ts + 6, 750000, eth4))

    # Dosyaya PCAP formatında yaz
    with open(output_file, "wb") as f:
        f.write(global_header)
        for ts_sec, ts_usec, pkt_bytes in packets_raw:
            pkt_len = len(pkt_bytes)
            # Packet header (16 bytes): ts_sec, ts_usec, incl_len, orig_len
            pkt_hdr = struct.pack("<IIII", ts_sec, ts_usec, pkt_len, pkt_len)
            f.write(pkt_hdr + pkt_bytes)

    print(f"[+] Başarılı: {len(packets_raw)} adet sentetik OT çerçevesi oluşturuldu: {output_file}")
    print(f"    Dosya boyutu: {os.path.getsize(output_file)} bayt")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "pcaps/ot_attack_sample.pcap"
    generate_ot_pcap(out)
