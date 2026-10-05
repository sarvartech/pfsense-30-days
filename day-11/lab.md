# 🛠️ [KUN-11] LAB: OpenVPN Site-to-Site Tunneling va CSO Amaliyoti

**Mavzu:** HQ va Filial o'rtasida to'liq marshrutlangan L3 tunnel qurish  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyaning Toshkentdagi Bosh ofisida yagona 1C ERP va fayl serveri joylashgan. Samarqanddagi yangi ochilgan filial xodimlari ushbu serverga kira olmayapti. Filialda oq IP manzil yo'q (mobil provayder NAT ortida). Shunday tunnel qurish kerakki, filial xodimlari 1C serverga to'g'ridan-to'g'ri `10.10.20.50` lokal IP si orqali ulanishsin va filialdagi IP kameralarni Bosh ofis xavfsizlik xizmati ko'ra olsin.

---

## 🗺️ 2. Topologiya va IP Rejasi

| Lokatsiya | Router Nomi | WAN IP | LAN Subnet | Tunnel IP |
|---|---|---|---|---|
| **Bosh Ofis** | `pfSense-HQ` | `192.168.100.10` (Static) | `10.10.0.0/16` | `10.250.0.1/24` |
| **Filial** | `pfSense-Branch` | DHCP (NAT ortida) | `10.20.0.0/16` | `10.250.0.2/24` |

---

## ⚙️ 3. Qadam-baqadam Sozlash

### 1-Qadam: Bosh Ofisda (HQ) PKI va Sertifikatlarni Tayyorlash
1. `System -> Cert. Manager -> Certificates` ga kiring.
2. Server sertifikatini yarating: `HQ_S2S_Server_Cert` (Type: Server Certificate).
3. Filial uchun alohida mijoz sertifikatini yarating:
   * Common Name: `branch-samarkand` (KRITIK: bu nom CSO da kerak bo'ladi!).
   * Type: User Certificate.

### 2-Qadam: HQ da OpenVPN Serverini Sozlash
1. `VPN -> OpenVPN -> Servers` -> **Add**:
   * Server Mode: `Peer to Peer (SSL/TLS)`
   * Protocol: `UDP on IPv4`, Interface: `WAN`, Port: `1195`
   * Server Certificate: `HQ_S2S_Server_Cert`
   * IPv4 Tunnel Network: `10.250.0.0/24`
   * IPv4 Local Network/s: `10.10.0.0/16`
   * IPv4 Remote Network/s: *Bo'sh qoldiring* (chunki bir nechta filial bo'ladi).
2. Saqlang.

### 3-Qadam: HQ da Client Specific Overrides (CSO) Yaratish
1. `VPN -> OpenVPN -> Client Specific Overrides` yorlig'iga o'ting, **Add** bosing:
   * Common Name: `branch-samarkand` (Mijoz sertifikati bilan 100% bir xil bo'lishi shart!).
   * IPv4 Remote Network/s: `10.20.0.0/16` (Filialning ichki LAN tarmog'i).
2. Saqlang.

### 4-Qadam: Filialda (Branch) Mijozni Sozlash
1. Filial pfSense siga HQ ning `Corp_Internal_CA` Root sertifikatini va `branch-samarkand` mijoz sertifikatini import qiling (`System -> Cert. Manager`).
2. `VPN -> OpenVPN -> Clients` -> **Add**:
   * Server Mode: `Peer to Peer (SSL/TLS)`
   * Server host or address: HQ ning WAN IP si (`192.168.100.10`).
   * Server port: `1195`
   * Client Certificate: `branch-samarkand`
   * IPv4 Tunnel Network: `10.250.0.0/24`
   * IPv4 Remote Network/s: `10.10.0.0/16` (Bosh ofis tarmog'i).
3. Saqlang.

### 5-Qadam: Firewall Qoidalarini Ochish
* Ikkala pfSense da ham `Firewall -> Rules -> OpenVPN` interfeysiga kirib, `Pass Any to Any` qoidasini qo'shing.
* HQ WAN interfeysida UDP port 1195 ga ruxsat bering.

---

## 🧪 4. Verifikatsiya va Sinovlar

1. **Tunnel Holati:**
   * Ikkala routerda ham `Status -> OpenVPN` sahifasiga kiring. Holat yashil **up** bo'lishi va tunnel IP lari (`10.250.0.1` va `10.250.0.2`) ko'rinishi lozim.
2. **Filialdan Bosh Ofisga Ping:**
   Filial LAN kompyuteridan (`10.20.0.50`):
   ```bash
   ping 10.10.20.50
   tracert 10.10.20.50
   ```
   *Paketlar VPN tunnel orqali o'tib Bosh ofis serveriga yetib borishi kerak.*
3. **Bosh Ofisdan Filialga Ping (Ikki Tomonlama Aloqa):**
   Bosh ofis serveridan (`10.10.20.50`):
   ```bash
   ping 10.20.0.50
   ```
   *Agar javob kelsa, demak `iroute` va CSO 100% to'g'ri ishladi!*

---

## 🚨 5. Troubleshooting
* ⚠️ **Muammo: Filialdan HQ ga ping boradi, lekin HQ dan filialga bormayapti.**  
  *Yechim:* Bu eng mashhur xato. HQ da CSO yaratilmagan yoki Common Name maydonidagi nom sertifikat nomi (`branch-samarkand`) bilan mos kelmagan. Shuningdek, HQ Routing jadvalida `netstat -rn` orqali 10.20.0.0/16 yo'nalishi bor-yo'qligini tekshiring.
