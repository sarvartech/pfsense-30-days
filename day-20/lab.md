# 🛠️ [KUN-20] LAB: pfsync va XML-RPC Sinxronizatsiyasi bilan Zero-Downtime Failover Mashqi

**Mavzu:** Jonli klasterda konfiguratsiyani sinxronlash va Master o'chirilganda 0s uzilish testi  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Rahbariyat Zoom orqali muhim xalqaro investorlar bilan video konferentsiya o'tkazmoqda. Shu vaqtda asosiy firewall apparatida quvvat bloki portlab o'chib qoldi. Tizim shunday sozlangan bo'lishi kerakki, video qo'ng'iroq bir soniyaga ham to'xtamasin va investorlar nosozlik yuz berganini umuman sezmasin (Zero-Downtime).

---

## ⚙️ 2. Qadam-baqadam Sozlash

### 1-Qadam: FW-01 (Master) da High Availability Sync Sozlash
1. `System -> High Avail. Sync` bo'limiga kiring.
2. **State Synchronization Settings (pfsync):**
   * Synchronize States: **Katakchani yoqing**.
   * Synchronize Interface: `SYNC`
   * Synchronize Peer IP: `192.168.99.2` (FW-02 SYNC IP si).
3. **Configuration Synchronization Settings (XMLRPC Sync):**
   * Synchronize Config to IP: `192.168.99.2`
   * Remote System Username: `admin`
   * Remote System Password: *(FW-02 ning admin paroli)*
   * Sinxronlanadigan qismlarni belgilang:
     * [x] Synchronize Firewall Rules
     * [x] Synchronize Firewall Aliases
     * [x] Synchronize NAT
     * [x] Synchronize Virtual IPs
     * [x] Synchronize Certificates
     * [x] Synchronize OpenVPN
4. Saqlang.

### 2-Qadam: FW-02 (Backup) da pfsync ni Yoqish
1. FW-02 da: `System -> High Avail. Sync` ga kiring.
2. Synchronize States: **Katakchani yoqing**.
3. Synchronize Interface: `SYNC`.
4. Synchronize Peer IP: `192.168.99.1` (FW-01 SYNC IP si).
5. **DIQQAT:** XMLRPC Sync bo'limidagi barcha katakchalarni **BO'SH** qoldiring! (Backup router Masterga hech qachon konfiguratsiya yozmasligi kerak). Saqlang.

---

## 🧪 3. Verifikatsiya va Zero-Downtime Sinovi

### 1. XML-RPC Sinovi:
1. FW-01 (Master) da yangi Firewall Alias yarating: Name: `Test_Sync_Alias`, Type: `Host`, IP: `1.2.3.4`. Saqlang va Apply qiling.
2. FW-02 (Backup) ga o'ting va `Firewall -> Aliases` sahifasini yangilang.
*Natija:* `Test_Sync_Alias` 1 soniya ichida FW-02 da avtomatik paydo bo'lishi kerak!

### 2. State Table (Sessiyalar) Sinovi:
1. FW-01 da konsol oching: `pfctl -ss | wc -l`
2. FW-02 da konsol oching: `pfctl -ss | wc -l`
*Natija:* Ikkala routerda ham ochiq sessiyalar soni bir xil bo'lishi lozim!

### 3. Falokat va Zero-Downtime Sinovi (Grand Test):
1. Mijoz kompyuterida uzluksiz ping yoki SSH ulanishini yoqing:
```bash
ping -t 10.10.10.1
```
2. Boshqa terminalda YouTube yoki Zoom qo'ng'irog'ini ishga tushiring.
3. **FW-01 (Master) ning elektrini birdaniga o'chiring (Power Off / Pull plug)!**
4. Mijoz kompyuteridagi ping oynasiga va video qo'ng'iroqqa qarang:
* **Natija:** Bitta ham ping yo'qolmaydi! Video qo'ng'iroq uzilmaydi! FW-02 soniyaning ulushlarida MASTER ga aylanadi va barcha sessiyalarni o'z zimmasiga oladi.
