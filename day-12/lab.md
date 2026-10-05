# 🛠️ [KUN-12] LAB: WireGuard High-Performance VPN va iperf3 Benchmark Sinovi

**Mavzu:** WireGuard tunnelini sozlash, Peerlarni bog'lash va OpenVPN bilan tezlikni solishtirish  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyada dizaynerlar va video montajchilar katta hajmdagi (5-10 GB) video fayllarni masofadan serverga yuklamoqda. Mavjud OpenVPN tüneli 100 Mbps dan oshmayapti va fayllarni yuklash soatlab vaqt olyapti. Kompaniya rahbariyati optik kanalning to'liq 1 Gbps tezligidan foydalana oladigan zamonaviy WireGuard VPN infratuzilmasini joriy etishni talab qildi.

---

## ⚙️ 2. Qadam-baqadam Sozlash

### 1-Qadam: WireGuard Paketini O'rnatish
1. `System -> Package Manager -> Available Packages` ga kiring.
2. `WireGuard` paketini o'rnating.

### 2-Qadam: WireGuard Tunnelini Yaratish
1. `VPN -> WireGuard -> Tunnels` ga kiring, **Add Tunnel** bosing:
   * Description: `WG_ENTERPRISE`
   * Listen Port: `51820`
   * Interface Keys: **Generate** tugmasini bosing (Public va Private Key yaratiladi).
2. Saqlang va **Apply Changes** qiling.

### 3-Qadam: WireGuard Interfeysini pfSense ga Biriktirish
1. `Interfaces -> Assignments` bo'limiga o'ting.
2. `Available network ports` dan `tun_wg0` ni tanlab, **Add** bosing.
3. Yangi paydo bo'lgan `OPT` interfeysiga kiring:
   * Enable: Yoqing
   * Description: `WIREGUARD`
   * IPv4 Configuration: `Static IPv4`
   * IPv4 Address: `10.200.0.1/24`
4. Saqlang va Apply qiling.

### 4-Qadam: Peer (Mijoz) Qo'shish
1. `VPN -> WireGuard -> Peers` yorlig'iga o'ting, **Add Peer** bosing:
   * Tunnel: `tun_wg0 (WG_ENTERPRISE)`
   * Description: `Engineer_Laptop`
   * Public Key: *(Mijoz noutbukidagi WireGuard yaratgan Public Key)*
   * Allowed IPs: `10.200.0.2/32`
2. Saqlang va Apply qiling.

### 5-Qadam: Mijoz Qurilmasini Sozlash (Windows / macOS / Linux)
Mijozda rasmiy WireGuard ilovasida yangi profil oching:
```ini
[Interface]
PrivateKey = <Mijozning_Shaxsiy_Private_Key>
Address = 10.200.0.2/24
DNS = 10.10.10.1

[Peer]
PublicKey = <pfSense_WireGuard_Public_Key>
Endpoint = <pfSense_WAN_IP>:51820
AllowedIPs = 10.10.0.0/16
PersistentKeepalive = 25
```

### 6-Qadam: Firewall Qoidalarini Ochish
1. `Firewall -> Rules -> WAN`:
   * Action: `Pass`, Protocol: `UDP`, Destination: `WAN address`, Port: `51820`.
2. `Firewall -> Rules -> WIREGUARD`:
   * Action: `Pass`, Protocol: `Any`, Source: `WIREGUARD net`, Destination: `Any`.

---

## 🧪 3. Verifikatsiya va iperf3 Benchmark

1. Mijozda WireGuard da **Activate** tugmasini bosing.
2. `Status -> WireGuard` da qarang: **Latest Handshake** soniyalari ko'rinishi lozim.
3. **CLI da tekshirish:**
```bash
wg show
```
4. **iperf3 orqali tezlikni o'lchash:**
   * pfSense ichki serverida iperf3 serverni yoqing:
   ```bash
   iperf3 -s
   ```
   * Mijoz noutbukidan VPN orqali sinov o'tkazing:
   ```bash
   iperf3 -c 10.10.20.80 -P 4
   ```
5. Natijani OpenVPN tezligi bilan solishtiring (WireGuard tezligi bir necha barobar yuqori chiqishini guvohi bo'lasiz).
