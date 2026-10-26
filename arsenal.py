#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security
Modül: Ana Komuta ve Araç Cephaneliği Başlatıcısı (Awesome Arsenal CLI)
Açıklama: Depodaki tüm keşif, denetim, tehdit avcılığı ve laboratuvar araçlarını
          tek bir etkileşimli terminal menüsünden çalıştırmanızı sağlar.
=============================================================================
"""

import sys
import os
import subprocess

BANNER = r"""
  ██████╗ ████████╗    ███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗████████╗██╗   ██╗
 ██╔═══██╗╚══██╔══╝    ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
 ██║   ██║   ██║       ███████╗█████╗  ██║     ██║   ██║██████╔╝██║   ██║    ╚████╔╝ 
 ██║   ██║   ██║       ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║     ╚██╔╝  
 ╚██████╔╝   ██║       ███████║███████╗╚██████╗╚██████╔╝██║  ██║██║   ██║      ██║   
  ╚═════╝    ╚═╝       ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝   
       Operasyonel Teknolojiler & Endüstriyel Kontrol Sistemleri Cephaneliği
                         Geliştirici: Bahattin Yunus ÇETİN
"""

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_menu():
    print(BANNER)
    print("═" * 78)
    print("  [1]  Modbus TCP Güvenlik ve Bellek Denetimi (scripts/modbus_auditor.py)")
    print("  [2]  Siemens S7 PLC Keşif ve CPU Durum Tanılama (scripts/s7_recon.py)")
    print("  [3]  DNP3 Outstation Bağlantı ve Güvenlik Denetimi (scripts/dnp3_audit.py)")
    print("  [4]  OPC UA Sunucu ve Uç Nokta Güvenlik Tarayıcısı (scripts/opcua_scanner.py)")
    print("  [5]  IEC 61850 GOOSE Anomali ve Replay Analizörü (scripts/goose_analyzer.py)")
    print("  [6]  Çevrimdışı PCAP Tehdit Avcısı (scripts/ot_pcap_hunter.py)")
    print("  [7]  Sentetik OT Saldırı PCAP'i Üret (scripts/generate_sample_pcap.py)")
    print("  [8]  Docker Test Laboratuvarını Başlat (labs/docker-compose.yml)")
    print("  [9]  Docker Test Laboratuvarını Durdur (docker compose down)")
    print("  [0]  Çıkış")
    print("═" * 78)

def run_modbus():
    target = input("\nHedef PLC IP Adresi [127.0.0.1]: ").strip() or "127.0.0.1"
    port = input("Modbus Portu [5020]: ").strip() or "5020"
    test_write = input("Yetkisiz yazma zafiyeti testi yapılsın mı? (e/H): ").strip().lower() == "e"
    
    cmd = [sys.executable, "scripts/modbus_auditor.py", "-t", target, "-p", port]
    if test_write:
        cmd.append("--test-write")
    subprocess.run(cmd)

def run_s7():
    target = input("\nHedef Siemens PLC IP Adresi: ").strip()
    if not target:
        print("[-] Hedef IP boş bırakılamaz.")
        return
    slot = input("Slot Numarası (S7-300: 2, S7-1200/1500: 1) [2]: ").strip() or "2"
    subprocess.run([sys.executable, "scripts/s7_recon.py", "-t", target, "-s", slot])

def run_dnp3():
    target = input("\nHedef DNP3 Outstation IP Adresi: ").strip()
    if not target:
        print("[-] Hedef IP boş bırakılamaz.")
        return
    port = input("DNP3 Portu [20000]: ").strip() or "20000"
    subprocess.run([sys.executable, "scripts/dnp3_audit.py", "-t", target, "-p", port])

def run_opcua():
    target = input("\nHedef OPC UA Sunucu IP Adresi: ").strip()
    if not target:
        print("[-] Hedef IP boş bırakılamaz.")
        return
    port = input("OPC UA Portu [4840]: ").strip() or "4840"
    subprocess.run([sys.executable, "scripts/opcua_scanner.py", "-t", target, "-p", port])

def run_goose():
    pcap = input("\nİncelenecek PCAP dosyası [pcaps/ot_attack_sample.pcap]: ").strip() or "pcaps/ot_attack_sample.pcap"
    subprocess.run([sys.executable, "scripts/goose_analyzer.py", "-r", pcap])

def run_pcap_hunter():
    pcap = input("\nTaranacak PCAP dosyası [pcaps/ot_attack_sample.pcap]: ").strip() or "pcaps/ot_attack_sample.pcap"
    subprocess.run([sys.executable, "scripts/ot_pcap_hunter.py", "-r", pcap])

def run_pcap_generator():
    out = input("\nÇıktı PCAP Dosya Yolu [pcaps/ot_attack_sample.pcap]: ").strip() or "pcaps/ot_attack_sample.pcap"
    subprocess.run([sys.executable, "scripts/generate_sample_pcap.py", out])

def run_docker_up():
    print("\n[*] Docker Compose laboratuvarı başlatılıyor...")
    subprocess.run(["docker", "compose", "-f", "labs/docker-compose.yml", "up", "-d"])
    print("[+] Laboratuvar servisleri aktif!")
    print("    - Web SCADA HMI: http://localhost:8080")
    print("    - Modbus PLC   : localhost:5020")
    print("    - Conpot Honey : localhost:1020, 5021")

def run_docker_down():
    print("\n[*] Docker Compose laboratuvarı kapatılıyor...")
    subprocess.run(["docker", "compose", "-f", "labs/docker-compose.yml", "down"])

def main():
    while True:
        print_menu()
        choice = input("Seçiminiz (0-9): ").strip()
        
        if choice == "1":
            run_modbus()
        elif choice == "2":
            run_s7()
        elif choice == "3":
            run_dnp3()
        elif choice == "4":
            run_opcua()
        elif choice == "5":
            run_goose()
        elif choice == "6":
            run_pcap_hunter()
        elif choice == "7":
            run_pcap_generator()
        elif choice == "8":
            run_docker_up()
        elif choice == "9":
            run_docker_down()
        elif choice == "0":
            print("\n[*] Görüşmek üzere!")
            break
        else:
            print("[-] Geçersiz seçim, lütfen tekrar deneyin.")
        
        input("\nDevam etmek için [ENTER] tuşuna basın...")
        clear_screen()

if __name__ == "__main__":
    main()
