# 📊 pfSense 30 Kunlik O'zlashtirish va Maqolalar Jadvali (Progress Tracker)

Ushbu jadval orqali siz har kuni bajargan ishlaringizni, laboratoriya testlarini va GitHub maqolalaringiz holatini kuzatib borasiz. Ushbu jadvalni to'g'ridan-to'g'ri nusxalab Google Sheets yoki Excel ga ham joylashtirishingiz mumkin.

| Kun | Mavzu | Lab Muhiti (VMware/Proxmox) | Test / Verifikatsiya | Maqola Holati | Sana | Havola (Article Link) |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| **01** | pfSense & FreeBSD Arxitekturasi, Lab Topology | [ ] VMware [ ] Proxmox | Virtual Switch / Bridge ping | [ ] Yozilmoqda [ ] Tayyor | | [01-lab-setup.md](docs/01-architecture-and-lab-setup.md) |
| **02** | O'rnatish, ZFS, Konsol va WebGUI Hardening | [ ] VMware [ ] Proxmox | SSH Public Key, HTTPS cert | [ ] Yozilmoqda [ ] Tayyor | | docs/02-... |
| **03** | DHCP Server, Static Mappings, Options (PXE/NTP) | [ ] VMware [ ] Proxmox | DHCP Lease, Wireshark bootp | [ ] Yozilmoqda [ ] Tayyor | | docs/03-... |
| **04** | Unbound DNS chuqur tahlili, DoT & DNSSEC | [ ] VMware [ ] Proxmox | `dig`, `drill` DNSSEC valid | [ ] Yozilmoqda [ ] Tayyor | | docs/04-... |
| **05** | 802.1Q VLANlar va Inter-VLAN Routing | [ ] VMware [ ] Proxmox | Subnetlararo ping va izolyatsiya | [ ] Yozilmoqda [ ] Tayyor | | docs/05-... |
| **06** | Firewall Qoidalari, State Table va Aliaslar | [ ] VMware [ ] Proxmox | `pfctl -sr`, Alias URL update | [ ] Yozilmoqda [ ] Tayyor | | docs/06-... |
| **07** | NAT Turlari: Port Forward, Outbound, 1:1, Loopback | [ ] VMware [ ] Proxmox | `curl` tashqi va ichki IP orqali | [ ] Yozilmoqda [ ] Tayyor | | docs/07-... |
| **08** | Multi-WAN: Dual ISP Failover & Load Balancing | [ ] VMware [ ] Proxmox | WAN1 ni o'chirib failover sinovi | [ ] Yozilmoqda [ ] Tayyor | | docs/08-... |
| **09** | Dinamik Marshrutlash: FRR paketi (OSPF & BGP) | [ ] VMware [ ] Proxmox | `vtysh -c "show ip ospf route"` | [ ] Yozilmoqda [ ] Tayyor | | docs/09-... |
| **10** | OpenVPN Remote Access (CA, TLS-Crypt, RoadWarrior) | [ ] VMware [ ] Proxmox | Windows/Telefon client ulanishi | [ ] Yozilmoqda [ ] Tayyor | | docs/10-... |
| **11** | OpenVPN Site-to-Site Tunneling & CSO | [ ] VMware [ ] Proxmox | 2 ta filial subnetlari pingi | [ ] Yozilmoqda [ ] Tayyor | | docs/11-... |
| **12** | WireGuard: Zamonaviy High-Speed VPN | [ ] VMware [ ] Proxmox | `wg show`, `iperf3` benchmark | [ ] Yozilmoqda [ ] Tayyor | | docs/12-... |
| **13** | IPsec IKEv2 Enterprise Site-to-Site (VTI) | [ ] VMware [ ] Proxmox | Phase 1 & 2 SA, VTI traffic | [ ] Yozilmoqda [ ] Tayyor | | docs/13-... |
| **14** | IPsec IKEv2 Mobile Client (Native Windows/macOS) | [ ] VMware [ ] Proxmox | Windows VPN ulanishi ilovasiz | [ ] Yozilmoqda [ ] Tayyor | | docs/14-... |
| **15** | Zero-Trust & Mesh: Tailscale Subnet Router | [ ] VMware [ ] Proxmox | CGNAT ortidagi tarmoqqa kirish | [ ] Yozilmoqda [ ] Tayyor | | docs/15-... |
| **16** | pfBlockerNG-devel: DNSBL, GeoIP & AdBlock | [ ] VMware [ ] Proxmox | Reklama va GeoIP blok sinovi | [ ] Yozilmoqda [ ] Tayyor | | docs/16-... |
| **17** | IDS/IPS: Suricata Inline Mode & ET Rules | [ ] VMware [ ] Proxmox | `testmyids.com` hujum simulyatsiyasi | [ ] Yozilmoqda [ ] Tayyor | | docs/17-... |
| **18** | Traffic Shaping & QoS: FQ-CoDel Bufferbloat Fix | [ ] VMware [ ] Proxmox | Waveform Bufferbloat Test (A+) | [ ] Yozilmoqda [ ] Tayyor | | docs/18-... |
| **19** | High Availability (CARP): L2 Sync & Promiscuous | [ ] VMware [ ] Proxmox | CARP VIP master/backup holati | [ ] Yozilmoqda [ ] Tayyor | | docs/19-... |
| **20** | High Availability (CARP): pfsync & Zero-Downtime | [ ] VMware [ ] Proxmox | Master o'chirilganda uzilish 0s | [ ] Yozilmoqda [ ] Tayyor | | docs/20-... |
| **21** | HAProxy: Reverse Proxy, SSL Offloading, Healthcheck| [ ] VMware [ ] Proxmox | Backend serverlarga load balance | [ ] Yozilmoqda [ ] Tayyor | | docs/21-... |
| **22** | ACME (Let's Encrypt) Wildcard SSL & Cloudflare API | [ ] VMware [ ] Proxmox | Haqiqiy SSL sertifikat chiqarish | [ ] Yozilmoqda [ ] Tayyor | | docs/22-... |
| **23** | Squid Proxy & Kesh, Antivirus ClamAV | [ ] VMware [ ] Proxmox | EICAR test virusini tutib qolish | [ ] Yozilmoqda [ ] Tayyor | | docs/23-... |
| **24** | Centralized Logging: Syslog, Graylog / ELK | [ ] VMware [ ] Proxmox | Log oqimi va tahlil paneli | [ ] Yozilmoqda [ ] Tayyor | | docs/24-... |
| **25** | Monitoring: Telegraf + InfluxDB + Grafana Dashboard | [ ] VMware [ ] Proxmox | Real-time Grafana grafikalari | [ ] Yozilmoqda [ ] Tayyor | | docs/25-... |
| **26** | Enterprise Auth: Active Directory / LDAP / RADIUS | [ ] VMware [ ] Proxmox | Domain user bilan pfSense login | [ ] Yozilmoqda [ ] Tayyor | | docs/26-... |
| **27** | Backup, ACB va Disaster Recovery Mashqi | [ ] VMware [ ] Proxmox | Noldan 5 minutda to'liq tiklash | [ ] Yozilmoqda [ ] Tayyor | | docs/27-... |
| **28** | Cloud pfSense Arxitekturasi: AWS, GCP, Linode | [ ] Nazariya [ ] CLI | Cloud VPC & Route Table reja | [ ] Yozilmoqda [ ] Tayyor | | docs/28-... |
| **29** | pfSense Cloud Deployment (Real Cloud Instance) | [ ] AWS [ ] GCP [ ] Linode | Public IP, WebGUI, Cloud NAT | [ ] Yozilmoqda [ ] Tayyor | | docs/29-... |
| **30** | Grand Finale: Hybrid Cloud IPsec Tunnel & Portfolio | [ ] Proxmox ⇄ Cloud | On-prem to Cloud to'liq marshrut | [ ] Yozilmoqda [ ] Tayyor | | docs/30-... |
