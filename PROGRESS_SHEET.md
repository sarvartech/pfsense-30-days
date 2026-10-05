# 📊 pfSense 30 Kunlik O'zlashtirish va Maqolalar Jadvali (Progress Tracker)

Ushbu jadval orqali siz har kuni bajargan ishlaringizni, laboratoriya testlarini va GitHub maqolalaringiz holatini kuzatib borasiz. Ushbu jadvalni to'g'ridan-to'g'ri nusxalab Google Sheets yoki Excel ga ham joylashtirishingiz mumkin.

| Kun | Mavzu | Lab Muhiti (Hardware/Virtual) | Test / Verifikatsiya | Maqola Holati | Sana | Dars & Lab Havolasi |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| **01** | pfSense va FreeBSD Arxitekturasi, Dual Lab (Hardware & Virtual) Muhitini Qurish | [ ] Hardware [ ] Virtual | `ping 10.10.10.1` | [x] Tayyor | | 📖 [Lecture](day-01/lecture.md) · 🛠️ [Lab Guide](day-01/lab.md) |
| **02** | O'rnatish, ZFS Fayl Tizimi, Konsol Menyusi va Production Hardening | [ ] Hardware [ ] Virtual | `ssh -p 2222 -i id_ed25519 secadmin@10.10.10.1` | [x] Tayyor | | 📖 [Lecture](day-02/lecture.md) · 🛠️ [Lab Guide](day-02/lab.md) |
| **03** | DHCP Server, Static Mappings, DHCP Options (PXE/NTP) va DHCP Relay | [ ] Hardware [ ] Virtual | `Status -> DHCP Leases` | [x] Tayyor | | 📖 [Lecture](day-03/lecture.md) · 🛠️ [Lab Guide](day-03/lab.md) |
| **04** | Unbound DNS chuqur tahlili, DNSSEC, DoT (DNS over TLS) va Split-Horizon DNS | [ ] Hardware [ ] Virtual | `drill -D sigok.verteiltesysteme.net @10.10.10.1` | [x] Tayyor | | 📖 [Lecture](day-04/lecture.md) · 🛠️ [Lab Guide](day-04/lab.md) |
| **05** | 802.1Q VLANlar va Inter-VLAN Marshrutlash (Router-on-a-Stick) | [ ] Hardware [ ] Virtual | `ifconfig -a` | [x] Tayyor | | 📖 [Lecture](day-05/lecture.md) · 🛠️ [Lab Guide](day-05/lab.md) |
| **06** | Firewall Qoidalari, State Table Internals, Floating Rules va Aliases | [ ] Hardware [ ] Virtual | `pfctl -sr` | [x] Tayyor | | 📖 [Lecture](day-06/lecture.md) · 🛠️ [Lab Guide](day-06/lab.md) |
| **07** | NAT Masterclass | [ ] Hardware [ ] Virtual | `Tashqi kompyuterdan: curl http://<WAN_IP>:8080` | [x] Tayyor | | 📖 [Lecture](day-07/lecture.md) · 🛠️ [Lab Guide](day-07/lab.md) |
| **08** | Multi-WAN | [ ] Hardware [ ] Virtual | `Status -> Gateways` | [x] Tayyor | | 📖 [Lecture](day-08/lecture.md) · 🛠️ [Lab Guide](day-08/lab.md) |
| **09** | Dinamik Marshrutlash | [ ] Hardware [ ] Virtual | `vtysh -c 'show ip ospf neighbor'` | [x] Tayyor | | 📖 [Lecture](day-09/lecture.md) · 🛠️ [Lab Guide](day-09/lab.md) |
| **10** | OpenVPN Remote Access (Road Warrior), PKI/CA va Client Export | [ ] Hardware [ ] Virtual | `Mijoz qurilmasida OpenVPN Connect dasturini ishga tushirib, yuklab olingan profil bilan ulanish` | [x] Tayyor | | 📖 [Lecture](day-10/lecture.md) · 🛠️ [Lab Guide](day-10/lab.md) |
| **11** | OpenVPN Site-to-Site Tunneling va Client Specific Overrides (CSO) | [ ] Hardware [ ] Virtual | `Status -> OpenVPN` | [x] Tayyor | | 📖 [Lecture](day-11/lecture.md) · 🛠️ [Lab Guide](day-11/lab.md) |
| **12** | WireGuard High-Performance VPN | [ ] Hardware [ ] Virtual | `Status -> WireGuard` | [x] Tayyor | | 📖 [Lecture](day-12/lecture.md) · 🛠️ [Lab Guide](day-12/lab.md) |
| **13** | Enterprise IPsec IKEv2 Site-to-Site Tunnel va Routed VTI | [ ] Hardware [ ] Virtual | `Status -> IPsec` | [x] Tayyor | | 📖 [Lecture](day-13/lecture.md) · 🛠️ [Lab Guide](day-13/lab.md) |
| **14** | Mobile IPsec IKEv2 (Native Windows, macOS va iOS ilovasiz ulanishi) | [ ] Hardware [ ] Virtual | `Windows tizim sozlamalaridan` | [x] Tayyor | | 📖 [Lecture](day-14/lecture.md) · 🛠️ [Lab Guide](day-14/lab.md) |
| **15** | Zero-Trust va Overlay Network | [ ] Hardware [ ] Virtual | `tailscale status` | [x] Tayyor | | 📖 [Lecture](day-15/lecture.md) · 🛠️ [Lab Guide](day-15/lab.md) |
| **16** | pfBlockerNG-devel | [ ] Hardware [ ] Virtual | `Mijoz brauzeridan: reklama ko'p saytlarga` | [x] Tayyor | | 📖 [Lecture](day-16/lecture.md) · 🛠️ [Lab Guide](day-16/lab.md) |
| **17** | IDS/IPS chuqur tahlili | [ ] Hardware [ ] Virtual | `Mijoz kompyuterdan IDS test hujumini simulyatsiya qilish: curl http://testmyids.com` | [x] Tayyor | | 📖 [Lecture](day-17/lecture.md) · 🛠️ [Lab Guide](day-17/lab.md) |
| **18** | Traffic Shaping va QoS | [ ] Hardware [ ] Virtual | `Waveform Bufferbloat Test` | [x] Tayyor | | 📖 [Lecture](day-18/lecture.md) · 🛠️ [Lab Guide](day-18/lab.md) |
| **19** | High Availability (CARP) Klasteri — 1-Qism | [ ] Hardware [ ] Virtual | `Status -> CARP` | [x] Tayyor | | 📖 [Lecture](day-19/lecture.md) · 🛠️ [Lab Guide](day-19/lab.md) |
| **20** | High Availability (CARP) — 2-Qism | [ ] Hardware [ ] Virtual | `pfSense konsolida: pfctl -ss` | [x] Tayyor | | 📖 [Lecture](day-20/lecture.md) · 🛠️ [Lab Guide](day-20/lab.md) |
| **21** | HAProxy Reverse Proxy | [ ] Hardware [ ] Virtual | `Status -> HAProxy` | [x] Tayyor | | 📖 [Lecture](day-21/lecture.md) · 🛠️ [Lab Guide](day-21/lab.md) |
| **22** | ACME (Let's Encrypt) Avtomatizatsiyasi va Cloudflare DNS API | [ ] Hardware [ ] Virtual | `pfSense WebGUI ga domeningiz orqali kirish` | [x] Tayyor | | 📖 [Lecture](day-22/lecture.md) · 🛠️ [Lab Guide](day-22/lab.md) |
| **23** | Squid Proxy, Kesh Arxitekturasi va ClamAV Antivirus Filtratsiyasi | [ ] Hardware [ ] Virtual | `tail -f /var/log/squid/access.log` | [x] Tayyor | | 📖 [Lecture](day-23/lecture.md) · 🛠️ [Lab Guide](day-23/lab.md) |
| **24** | Centralized Logging | [ ] Hardware [ ] Virtual | `tcpdump -i vtnet1 -n udp port 514` | [x] Tayyor | | 📖 [Lecture](day-24/lecture.md) · 🛠️ [Lab Guide](day-24/lab.md) |
| **25** | Telemetriya va Monitoring | [ ] Hardware [ ] Virtual | `Status -> Services` | [x] Tayyor | | 📖 [Lecture](day-25/lecture.md) · 🛠️ [Lab Guide](day-25/lab.md) |
| **26** | Korxona Autentifikatsiyasi | [ ] Hardware [ ] Virtual | `Diagnostics -> Authentication` | [x] Tayyor | | 📖 [Lecture](day-26/lecture.md) · 🛠️ [Lab Guide](day-26/lab.md) |
| **27** | Avtomatlashtirish, AutoConfigBackup (ACB) va 5-Daqiqalik Disaster Recovery Mashqi | [ ] Hardware [ ] Virtual | `Zaxiradan tiklangan yangi serverda barcha qoidalar va sertifikatlar o'z joyida ekanini ko'rish` | [x] Tayyor | | 📖 [Lecture](day-27/lecture.md) · 🛠️ [Lab Guide](day-27/lab.md) |
| **28** | Cloud Muhitlar Arxitekturasi | [ ] Hardware [ ] Virtual | `AWS VPC Dashboard da barcha subnetlar va yo'nalishlar xaritasi` | [x] Tayyor | | 📖 [Lecture](day-28/lecture.md) · 🛠️ [Lab Guide](day-28/lab.md) |
| **29** | pfSense Cloud Deployment | [ ] Hardware [ ] Virtual | `Bulutdagi pfSense WebGUI ga xavfsiz ulanishni tasdiqlash` | [x] Tayyor | | 📖 [Lecture](day-29/lecture.md) · 🛠️ [Lab Guide](day-29/lab.md) |
| **30** | Katta Final — Hybrid Cloud Production Project | [ ] Hardware [ ] Virtual | `Mahalliy ofis kompyuteridan: ping 172.31.2.50` | [x] Tayyor | | 📖 [Lecture](day-30/lecture.md) · 🛠️ [Lab Guide](day-30/lab.md) |

