#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security Lab
Modül: Simüle Edilmiş Su Deposu PLC'si (Modbus TCP Server)
Açıklama: Seviye 1 PLC davranışını taklit eden interaktif Modbus sunucusu.
          - Coil 0: Su Pompası (Açık/Kapalı)
          - Coil 1: Acil Boşaltma Vanası (Açık/Kapalı)
          - Holding Register 0: Tank Su Seviyesi (Litre)
          - Holding Register 1: Boru Basıncı (PSI)
=============================================================================
"""

import threading
import time
import logging
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def process_loop(context):
    """
    Fiziksel süreci simüle eden döngü:
    Pompa açıksa tank seviyesi artar, vana açıksa seviye düşer.
    """
    logging.info("[*] Siber-Fiziksel süreç simülasyonu başlatıldı...")
    slave_id = 0x00 # Varsayılan slave context (veya 1)
    
    while True:
        try:
            time.sleep(1.0)
            slave = context[slave_id]
            
            # Coil değerlerini oku (Coil 0: Pompa, Coil 1: Vana)
            coils = slave.getValues(1, 0, count=2)
            pump_on = coils[0]
            valve_open = coils[1]

            # Register değerlerini oku (Reg 0: Seviye, Reg 1: Basınç)
            regs = slave.getValues(3, 0, count=2)
            level = regs[0]
            pressure = regs[1]

            # Fiziksel dinamik hesaplaması
            if pump_on:
                level = min(1000, level + 15)
                pressure = min(150, pressure + 2)
            elif valve_open:
                level = max(0, level - 25)
                pressure = max(10, pressure - 3)
            else:
                level = max(0, level - 1)
                pressure = max(20, pressure - 1)

            # Güncellenmiş fiziksel değerleri PLC belleğine yaz
            slave.setValues(3, 0, [level, pressure])

            logging.info(f"[TELEMETRİ] Seviye: {level}L | Basınç: {pressure} PSI | Pompa: {pump_on} | Vana: {valve_open}")

        except Exception as e:
            logging.error(f"Simülasyon döngüsü hatası: {e}")
            time.sleep(2)

def run_server():
    # Başlangıç bellek durumu
    # Coils (0x01/0x05): [Pompa=False, Vana=False]
    # Discrete Inputs (0x02): [True, False]
    # Holding Registers (0x03/0x06/0x10): [Seviye=500L, Basınç=45 PSI]
    # Input Registers (0x04): [100, 200]
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [1] * 10),
        co=ModbusSequentialDataBlock(0, [0] * 10),
        hr=ModbusSequentialDataBlock(0, [500, 45, 0, 0, 0]),
        ir=ModbusSequentialDataBlock(0, [100, 200, 300])
    )
    context = ModbusServerContext(slaves=store, single=True)

    # Fiziksel süreci arka planda çalıştır
    sim_thread = threading.Thread(target=process_loop, args=(context,), daemon=True)
    sim_thread.start()

    logging.info("[+] Simüle Edilmiş Su Deposu Modbus TCP PLC başlatılıyor (Port 502)...")
    StartTcpServer(context=context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_server()
