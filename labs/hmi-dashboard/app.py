#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Proje: Awesome OT & ICS Security Lab
Modül: Web SCADA HMI Kontrol ve İzleme Paneli (Web HMI Dashboard)
Açıklama: Modbus TCP sunucusuna (Seviye 1 PLC) bağlanarak su deposu telemetrisini
          (seviye, basınç, pompa, vana) web arayüzünde canlı görselleştirir.
          Aynı zamanda HMI üzerinden açma/kapama komutları göndermeye olanak tanır.
=============================================================================
"""

import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    print("[!] 'pymodbus' bulunamadı. Lütfen yükleyin: pip install pymodbus")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MODBUS_HOST = os.environ.get("MODBUS_HOST", "127.0.0.1")
MODBUS_PORT = int(os.environ.get("MODBUS_PORT", "5020"))
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8080"))

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SCADA HMI - Su Deposu Süreç Kontrol Paneli</title>
  <style>
    :root {
      --bg-main: #0b1120;
      --card-bg: #1e293b;
      --accent-cyan: #38bdf8;
      --accent-green: #10b981;
      --accent-red: #ef4444;
      --accent-amber: #f59e0b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
    body { background: var(--bg-main); color: var(--text-main); min-height: 100vh; padding: 20px; }
    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 15px; margin-bottom: 25px; }
    .header h1 { font-size: 22px; font-weight: 700; color: var(--accent-cyan); display: flex; align-items: center; gap: 10px; }
    .badge-status { padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; background: #064e3b; color: #34d399; border: 1px solid #059669; }
    .alarm-banner { padding: 12px 20px; border-radius: 8px; margin-bottom: 25px; font-weight: 600; display: none; }
    .alarm-critical { background: rgba(239, 68, 68, 0.2); border: 1px solid var(--accent-red); color: #fca5a5; display: block; }
    .alarm-warning { background: rgba(245, 158, 11, 0.2); border: 1px solid var(--accent-amber); color: #fde047; display: block; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .card { background: var(--card-bg); border: 1px solid #334155; border-radius: 12px; padding: 20px; }
    .card-title { font-size: 14px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }
    
    /* Tank Visual */
    .tank-container { width: 140px; height: 200px; border: 3px solid #64748b; border-radius: 0 0 16px 16px; margin: 0 auto; position: relative; background: #0f172a; overflow: hidden; }
    .tank-water { position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(180deg, #38bdf8, #0284c7); transition: height 0.8s ease-in-out; }
    .tank-label { text-align: center; margin-top: 15px; font-size: 24px; font-weight: 700; color: var(--accent-cyan); }

    /* Pressure Gauge */
    .gauge-val { font-size: 42px; font-weight: 800; text-align: center; margin: 30px 0 10px 0; color: #f8fafc; }
    .gauge-unit { font-size: 14px; color: var(--text-muted); text-align: center; }

    /* Switches */
    .control-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #334155; }
    .control-row:last-child { border: none; }
    .btn { padding: 8px 18px; border-radius: 6px; font-weight: 700; cursor: pointer; border: none; transition: 0.2s; font-size: 13px; }
    .btn-on { background: var(--accent-green); color: white; }
    .btn-off { background: #475569; color: #cbd5e1; }
    .btn:hover { opacity: 0.85; }

    /* Event Logs */
    .log-box { height: 180px; overflow-y: auto; background: #0f172a; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 11px; color: #94a3b8; }
    .log-entry { margin-bottom: 6px; }
    .log-time { color: var(--accent-cyan); margin-right: 6px; }
  </style>
</head>
<body>
  <div class="header">
    <h1><span>🏭</span> SCADA HMI Operatör Konsolu (Purdue Seviye 2)</h1>
    <div class="badge-status" id="conn-badge">PLC BAĞLANTISI: CANLI</div>
  </div>

  <div class="alarm-banner" id="alarm-box"></div>

  <div class="grid">
    <!-- Card 1: Tank Seviyesi -->
    <div class="card">
      <div class="card-title">Tank Su Seviyesi (Holding Reg 0)</div>
      <div class="tank-container">
        <div class="tank-water" id="tank-water" style="height: 50%;"></div>
      </div>
      <div class="tank-label" id="level-text">500 L</div>
    </div>

    <!-- Card 2: Boru Basıncı -->
    <div class="card">
      <div class="card-title">Boru Hattı Basıncı (Holding Reg 1)</div>
      <div class="gauge-val" id="pressure-text">45</div>
      <div class="gauge-unit">PSI (Maksimum Güvenli Eşik: 100 PSI)</div>
    </div>

    <!-- Card 3: Aktüatör Kontrolleri -->
    <div class="card">
      <div class="card-title">Saha Aktüatörleri (Coil Yazma)</div>
      <div class="control-row">
        <div>
          <div style="font-weight: 600;">Su Giriş Pompası</div>
          <div style="font-size: 11px; color: var(--text-muted);">Coil Adresi: 0x0000</div>
        </div>
        <button class="btn btn-off" id="btn-pump" onclick="toggleCoil(0)">KAPALI</button>
      </div>
      <div class="control-row">
        <div>
          <div style="font-weight: 600;">Acil Tahliye Vanası</div>
          <div style="font-size: 11px; color: var(--text-muted);">Coil Adresi: 0x0001</div>
        </div>
        <button class="btn btn-off" id="btn-valve" onclick="toggleCoil(1)">KAPALI</button>
      </div>
    </div>

    <!-- Card 4: SCADA Olay Günlüğü -->
    <div class="card">
      <div class="card-title">SCADA Telemetri &amp; Olay Kaydı</div>
      <div class="log-box" id="log-box"></div>
    </div>
  </div>

  <script>
    let pumpState = false;
    let valveState = false;

    function addLog(msg) {
      const box = document.getElementById('log-box');
      const time = new Date().toLocaleTimeString();
      const div = document.createElement('div');
      div.className = 'log-entry';
      div.innerHTML = `<span class="log-time">[${time}]</span> ${msg}`;
      box.prepend(div);
      if (box.children.length > 30) box.removeChild(box.lastChild);
    }

    async function fetchTelemetry() {
      try {
        const res = await fetch('/api/telemetry');
        if (!res.ok) throw new Error('İletişim hatası');
        const data = await res.json();
        
        document.getElementById('conn-badge').textContent = 'PLC BAĞLANTISI: CANLI (Port ' + data.port + ')';
        document.getElementById('conn-badge').style.background = '#064e3b';

        // Tank Seviyesi
        const pct = Math.min(100, Math.max(0, (data.level / 1000) * 100));
        document.getElementById('tank-water').style.height = pct + '%';
        document.getElementById('level-text').textContent = data.level + ' L (%' + Math.round(pct) + ')';

        // Basınç
        document.getElementById('pressure-text').textContent = data.pressure;

        // Alarmlar
        const alarmBox = document.getElementById('alarm-box');
        if (data.pressure > 100) {
          alarmBox.className = 'alarm-banner alarm-critical';
          alarmBox.textContent = '🚨 KRİTİK ALARM: Aşırı Boru Basıncı Algılandı! (' + data.pressure + ' PSI > 100 PSI Limit)';
        } else if (data.level > 900) {
          alarmBox.className = 'alarm-banner alarm-warning';
          alarmBox.textContent = '⚠️ UYARI: Su Deposu Taşma Eşiğinde (%' + Math.round(pct) + ')';
        } else {
          alarmBox.className = 'alarm-banner';
          alarmBox.style.display = 'none';
        }

        // Buton durumları
        pumpState = data.pump;
        valveState = data.valve;
        
        const btnPump = document.getElementById('btn-pump');
        btnPump.className = pumpState ? 'btn btn-on' : 'btn btn-off';
        btnPump.textContent = pumpState ? 'AÇIK' : 'KAPALI';

        const btnValve = document.getElementById('btn-valve');
        btnValve.className = valveState ? 'btn btn-on' : 'btn btn-off';
        btnValve.textContent = valveState ? 'AÇIK' : 'KAPALI';

      } catch (err) {
        document.getElementById('conn-badge').textContent = 'PLC BAĞLANTISI KOPTU!';
        document.getElementById('conn-badge').style.background = '#7f1d1d';
      }
    }

    async function toggleCoil(addr) {
      const targetState = addr === 0 ? !pumpState : !valveState;
      const deviceName = addr === 0 ? 'Su Pompası' : 'Tahliye Vanası';
      addLog(`[KOMUT] ${deviceName} için Coil 0x000${addr} -> ${targetState} yazılıyor...`);
      
      try {
        const res = await fetch(`/api/control?coil=${addr}&val=${targetState ? 1 : 0}`);
        const result = await res.json();
        if (result.success) {
          addLog(`[ONAY] ${deviceName} durumu başarıyla güncellendi.`);
          fetchTelemetry();
        } else {
          addLog(`[HATA] Yazma reddedildi: ${result.error}`);
        }
      } catch (e) {
        addLog(`[HATA] İletişim koptu: ${e}`);
      }
    }

    setInterval(fetchTelemetry, 1000);
    fetchTelemetry();
    addLog('SCADA HMI Web Konsolu başlatıldı. Telemetri dinleniyor...');
  </script>
</body>
</html>
"""

def query_modbus_telemetry():
    """Modbus PLC'den mevcut telemetriyi okur."""
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT, timeout=2)
    telemetry = {
        "host": MODBUS_HOST,
        "port": MODBUS_PORT,
        "level": 0,
        "pressure": 0,
        "pump": False,
        "valve": False
    }

    if not client.connect():
        client.close()
        return telemetry, False

    try:
        # Coils 0 & 1 oku
        rc = client.read_coils(address=0, count=2)
        if not rc.isError():
            telemetry["pump"] = bool(rc.bits[0])
            telemetry["valve"] = bool(rc.bits[1])

        # Holding Regs 0 & 1 oku
        rr = client.read_holding_registers(address=0, count=2)
        if not rr.isError():
            telemetry["level"] = rr.registers[0]
            telemetry["pressure"] = rr.registers[1]
        
        client.close()
        return telemetry, True
    except Exception as e:
        logging.error(f"Modbus okuma hatası: {e}")
        client.close()
        return telemetry, False

def write_modbus_coil(address, value):
    """Modbus PLC'ye tekli coil komutu yazar."""
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT, timeout=2)
    if not client.connect():
        client.close()
        return False, "TCP bağlantısı kurulamadı"
    try:
        wr = client.write_coil(address=address, value=value)
        client.close()
        if wr.isError():
            return False, str(wr)
        return True, "Başarılı"
    except Exception as e:
        client.close()
        return False, str(e)

class ScadaHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))

        elif parsed.path == "/api/telemetry":
            data, ok = query_modbus_telemetry()
            self.send_response(200 if ok else 503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))

        elif parsed.path == "/api/control":
            params = parse_qs(parsed.query)
            coil = int(params.get("coil", [0])[0])
            val = bool(int(params.get("val", [0])[0]))
            
            ok, msg = write_modbus_coil(coil, val)
            self.send_response(200 if ok else 500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": ok, "message": msg}).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

def run_hmi():
    logging.info(f"[+] SCADA HMI Web Sunucusu başlatılıyor: http://0.0.0.0:{HTTP_PORT}")
    logging.info(f"[*] Hedef Modbus PLC: {MODBUS_HOST}:{MODBUS_PORT}")
    server = HTTPServer(("0.0.0.0", HTTP_PORT), ScadaHttpHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

if __name__ == "__main__":
    run_hmi()
