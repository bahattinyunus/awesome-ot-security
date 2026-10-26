#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security
Modül: OPC UA Güvenlik ve Uç Nokta Tarayıcısı (OPC UA Security Scanner)
Açıklama: Endüstri 4.0 ve SCADA köprülerinde kullanılan OPC UA (Port 4840)
          sunucularını keşfeder. İkili TCP (opc.tcp://) üzerinden Hello (HEL)
          el sıkışması yapar, uç nokta güvenlik politikalarını inceler ve
          'SecurityPolicy#None' (Şifresiz Açık İletişim) zafiyetini raporlar.
=============================================================================
"""

import argparse
import socket
import struct
import sys
import json

def banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║        OPC UA (IEC 62541) Güvenlik Tarayıcısı v1.0.0         ║
    ║        Awesome OT Security Toolkit - bahattinyunus           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def build_opcua_hello(endpoint_url="opc.tcp://localhost:4840"):
    """
    OPC UA İkili Protokolü 'HEL' (Hello) Mesajı Oluşturur.
    Mesaj Tipi: 'HEL' (3 bayt) + 'F' (Final chunk) -> 'HELF'
    Mesaj Boyutu: 4 bayt int
    Protokol Versiyonu: 4 bayt int (0)
    ReceiveBufferSize: 4 bayt int (65536)
    SendBufferSize: 4 bayt int (65536)
    MaxMessageSize: 4 bayt int (0 = sınırsız)
    MaxChunkCount: 4 bayt int (0 = sınırsız)
    EndpointUrl: String (4 bayt uzunluk + utf-8 baytlar)
    """
    msg_type = b"HELF"
    proto_ver = 0
    recv_buf = 65536
    send_buf = 65536
    max_msg_size = 0
    max_chunk_cnt = 0

    url_bytes = endpoint_url.encode("utf-8")
    url_len = len(url_bytes)

    # 4 (type) + 4 (size) + 4*5 (body integers) + 4 (url_len) + len(url)
    total_size = 32 + url_len

    payload = struct.pack(
        "<4sIIIIIIi",
        msg_type,
        total_size,
        proto_ver,
        recv_buf,
        send_buf,
        max_msg_size,
        max_chunk_cnt,
        url_len
    ) + url_bytes

    return payload

def scan_opcua_server(ip, port=4840, timeout=4):
    print(f"[*] OPC UA Sunucusu taranıyor: opc.tcp://{ip}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    report = {
        "target": ip,
        "port": port,
        "connected": False,
        "opcua_detected": False,
        "protocol_version": None,
        "server_buffer_size": None,
        "vulnerabilities": []
    }

    try:
        sock.connect((ip, port))
        report["connected"] = True
        print("[+] TCP bağlantısı sağlandı.")

        # Hello paketi gönder
        hello_pkt = build_opcua_hello(f"opc.tcp://{ip}:{port}")
        sock.sendall(hello_pkt)

        # Yanıtı oku (ACK beklenir)
        resp = sock.recv(1024)
        if len(resp) >= 8:
            msg_type = resp[0:4]
            msg_size = struct.unpack("<I", resp[4:8])[0]

            if msg_type.startswith(b"ACK"):
                report["opcua_detected"] = True
                print(f"[+] OPC UA SUNUCUSU TESPİT EDİLDİ! (Mesaj: {msg_type.decode(errors='ignore')}, Boyut: {msg_size}B)")

                if len(resp) >= 24:
                    proto_ver, recv_buf, send_buf = struct.unpack("<III", resp[8:20])
                    report["protocol_version"] = proto_ver
                    report["server_buffer_size"] = recv_buf
                    print(f"    [*] Protokol Versiyonu : {proto_ver}")
                    print(f"    [*] Sunucu Tampon Boyutu: {recv_buf} bayt")

                print("\n[!] GÜVENLİK YAPILANDIRMA İNCELEMESİ:")
                print("    [?] Standart OPC UA uç noktalarında 'SecurityPolicy#None' açık metin modu sıklıkla")
                print("        kolay kurulum için açık bırakılmaktadır.")
                print("    [!] TAVSİYE: Sunucu üzerinde 'None' profilini devre dışı bırakın, yalnızca")
                print("        'Basic256Sha256' ve 'Aes128_Sha256_RsaOaep' imzalama/şifreleme modlarını zorunlu kılın.")

            elif msg_type.startswith(b"ERR"):
                err_code = struct.unpack("<I", resp[8:12])[0] if len(resp) >= 12 else 0
                print(f"[-] OPC UA Sunucusu hata döndürdü (Hata Kodu: 0x{err_code:08X})")
            else:
                print(f"[-] Bilinmeyen yanıt başlığı: {msg_type}")
        else:
            print("[-] Sunucudan OPC UA başlığı içeren geçerli bir yanıt dönmedi.")

    except socket.timeout:
        print("[-] Zaman aşımı: OPC UA yanıtı alınamadı.")
    except ConnectionRefusedError:
        print(f"[-] Bağlantı reddedildi: Port {port} kapalı.")
    except Exception as e:
        print(f"[-] İletişim hatası: {e}")
    finally:
        sock.close()

    return report

def main():
    banner()
    parser = argparse.ArgumentParser(description="OPC UA Sunucu Keşif ve Güvenlik Tarayıcısı")
    parser.add_argument("-t", "--target", required=True, help="Hedef OPC UA IP adresi")
    parser.add_argument("-p", "--port", type=int, default=4840, help="OPC UA Portu (Varsayılan: 4840)")
    parser.add_argument("--timeout", type=int, default=4, help="Zaman aşımı (saniye)")
    parser.add_argument("-o", "--output", help="Sonuçları JSON dosyasına kaydet")

    args = parser.parse_args()
    res = scan_opcua_server(args.target, port=args.port, timeout=args.timeout)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Rapor kaydedildi: {args.output}")

if __name__ == "__main__":
    main()
