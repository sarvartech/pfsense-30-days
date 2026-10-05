# -*- coding: utf-8 -*-
"""
pfSense 30-Day Curriculum Generator
Creates day-01 to day-30 folders with rich lecture.md and lab.md files.
Takes into account both Real Hardware and Virtualized (Proxmox / VMware) setups.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DAYS_DATA = [
    {
        "day": 1,
        "title": "pfSense va FreeBSD Arxitekturasi, Dual Lab (Hardware & Virtual) Muhitini Qurish",
        "category": "1-Hafta: Baza va Virtualizatsiya",
        "problem": "Korxonada xavfsizlik devori yo'qligi sababli tarmoq nazoratsiz, xavfsizlik zaif va izolyatsiya qilinmagan. Shuningdek, talabalar laboratoriya amaliyotini ham fizik mini-PC (hardware), ham virtual serverlar (Proxmox / VMware) da xatosiz o'rnatish poydevorini qurishi lozim.",
        "theory_points": [
            "pfSense tarixi, Netgate ekotizimi va nima uchun Linux (iptables) emas, FreeBSD yadrosi tanlangan?",
            "OpenBSD `pf` (Packet Filter) mexanizmi: holatli paket tahlili (Stateful Inspection), qoidalar tartibi va State Table.",
            "FreeBSD Tarmoq Steki: Monolit arxitektura, Zero-Copy paket marshrutlash, kqueue, mbuf xotira boshqaruvi va 10G/40G unumdorlik.",
            "ZFS (Zettabyte File System) afzalliklari: Copy-on-Write, to'satdan tok uzilganda fayllar buzilmasligi (Crash-resilience), Boot Environments (BE).",
            "Jismoniy Tarmoq Kartalari (Hardware NICs): Intel I210/I225/I350 (igb, igc) drayverlari vs Realtek (re) drayverlari va ularning farqi."
        ],
        "hardware_guide": """* **Qurilma:** 2 yoki undan ortiq tarmoq kartasiga ega x86-64 mini-PC yoki eski kompyuter (Intel i3/i5, kamida 4GB RAM, 64GB SSD).
* **Fizik ulanish:**
  * `WAN` porti (masalan, `igb0`): Internet provayder modemi yoki tashqi routerdan kelgan kabel.
  * `LAN` porti (masalan, `igb1`): Boshqaruv noutbuki yoki jismoniy switch (Cisco, TP-Link, MikroTik) ga RJ45 patch-cord orqali.
* **Konsol ulanishi:** Agar monitor/klaviatura ulasangiz HDMI/VGA; agar headless bo'lsa RS-232 COM / RJ45-to-USB konsol kabel (Baud rate: `115200`, 8N1).
* **BIOS Sozlamalari:** Intel VT-x faol, 'Restore on AC Power Loss' -> Last State yoki Power On, CSM Legacy yoki UEFI native boot.""",
        "virtual_guide": """* **Proxmox VE:**
  * `vmbr0` (WAN): Tashqi internetga chiquvchi Bridge (Gateway bilan).
  * `vmbr1` (LAN): Alohida ichki Linux Bridge (VLAN-aware yoqilgan, IP berilmagan).
  * pfSense VM: 2 vCPU (Host type), 2-4GB RAM, 32GB VirtIO SCSI disk, 2x VirtIO Network (`vmbr0` va `vmbr1`).
* **VMware Workstation Pro:**
  * `VMnet0` (Bridged) yoki `VMnet8` (NAT) -> WAN uchun.
  * `VMnet1` / `VMnet2` (Host-Only) -> LAN ichki izolyatsiyalangan tarmoq uchun.
  * Network Adapter 1: WAN, Network Adapter 2: LAN.""",
        "lab_steps": [
            "pfSense Community Edition (CE) 2.7.2 x86-64 DVD ISO tasvirini yuklab olish va tekshirish (SHA256).",
            "Hardware foydalanuvchilari uchun Rufus yoki BalenaEtcher orqali Bootable USB tayyorlash; Virtual foydalanuvchilar uchun ISO ni Proxmox `local` storage ga yoki VMware ga yuklash.",
            "Tizimni ZFS (Auto ZFS, stripe, pool name: `pfSense`, swap: 2GB) bilan o'rnatish.",
            "Konsolda interfeyslarni aniqlash: WAN (`igb0` yoki `vtnet0`), LAN (`igb1` yoki `vtnet1`), VLAN hozircha talab qilinmaydi (`N`).",
            "LAN interfeysiga `10.10.10.1/24` (yoki standart `192.168.1.1/24`) IP tayinlash va DHCP serverni yoqish.",
            "Mijoz kompyuterni LAN ga ulab, brauzer orqali `https://10.10.10.1` ga kirish (Standard login: `admin` / `pfsense`)."
        ],
        "verification": [
            "ping 10.10.10.1 (Mijoz kompyuterdan pfSense LAN shlyuziga)",
            "pfctl -s info (FreeBSD konsolida pf holati va ish vaqtini tekshirish)",
            "ifconfig -a (Interfeyslar MTU, media status (active/no carrier) va IP manzillarini ko'rish)",
            "curl -k https://10.10.10.1 (WebGUI HTTPS javobini tekshirish)"
        ],
        "troubleshooting": [
            "Muammo: LAN mijoz IP olmayapti. Yechim: Jismoniy kabel ulangan portni tekshiring (Link LED yonishi kerak), Proxmoxda esa vmbr1 to'g'ri biriktirilganini va VM tarmoq adapteri 'Connected' holatdaligini tasdiqlang.",
            "Muammo: WebGUI ochilmayapti. Yechim: pfSense konsolida 16-band (Restart PHP-FPM) yoki 11-band (Restart webConfigurator) ni tanlang.",
            "Muammo: Realtek kartalarida tarmoq uzilib qolmoqda. Yechim: System > Advanced > Networking bo'limida Hardware Checksum Offload, Hardware TCP Segmentation Offloading (TSO) va Hardware Large Receive Offloading (LRO) larni 'Disable' qilib qo'ying."
        ],
        "homework": "pfSense konsoli orqali ping va traceroute buyruqlarini ishlatib, 8.8.8.8 va google.com ga yo'lni tekshiring. ZFS pool holatini konsolda `zpool status` buyrug'i orqali ko'rib, xotira tuzilishini tahlil qiling."
    },
    {
        "day": 2,
        "title": "O'rnatish, ZFS Fayl Tizimi, Konsol Menyusi va Production Hardening",
        "category": "1-Hafta: Baza va Virtualizatsiya",
        "problem": "Standart sozlamalardagi pfSense da `admin:pfsense` default paroli, ochiq HTTP porti, standart 22-portdagi SSH va konsolga cheklovlarsiz kirish imkoniyati mavjud. Hujumchi birinchi urinishdayoq shlyuzni egallab olishi mumkin.",
        "theory_points": [
            "Defense-in-Depth (Ko'p qatlamli himoya) konsepsiyasi: Firewall faqat tashqi perimetr emas, uning o'zi ham eng mustahkam himoyalangan tugun bo'lishi shart.",
            "ZFS Snapshot va Boot Environments: Tizim yangilanishi (upgrade) muvaffaqiyatsiz tugaganda 10 soniyada oldingi stabil holatga qaytish mexanizmi.",
            "Kriptografik HTTPS va TLS konfiguratsiyasi: Self-signed sertifikatlar, TLS 1.3 qat'iy talablari va HTTP -> HTTPS avtomat yo'naltirish.",
            "SSH xavfsizligi: Parol orqali autentifikatsiyani taqiqlash, faqat Ed25519 ochiq kalitlari (Public Key Auth) orqali kirish va portni 2222 ga o'zgartirish.",
            "Console Password Protection: Jismoniy yoki virtual konsol oldiga borgan har qanday begona shaxs menyudan IP larni o'zgartira olmasligi uchun parollash."
        ],
        "hardware_guide": """* **Hardware:** Fizik serverda BIOS paroli o'rnatilgan bo'lishi lozim (begonalar USB orqali yuklanmasligi uchun).
* **Konsol:** Serial konsol (COM port) orqali ulanganda ham konsol menyusi parol so'rashi shart.
* **Elektr:** UPS (uzluksiz quvvat manbai) ga ulangan bo'lsa, pfSense ga `nut` yoki `apcupsd` paketini qo'shish rejalashtiriladi.""",
        "virtual_guide": """* **Proxmox / VMware:** Virtual Machine Console (noVNC / Remote Console) ga cheklov o'rnatish.
* **ZFS Snapshot:** Proxmox darajasidagi backupdan tashqari, pfSense ichida ham ZFS snapshot olish imkoniyatini sinash.""",
        "lab_steps": [
            "WebGUI ga kirish: `System` -> `User Manager` bo'limida yangi `secadmin` nomli superuser foydalanuvchisini yaratish va o'ta kuchli (16+ belgili) parol berish.",
            "`admin` standart foydalanuvchisini o'chirib qo'yish (Disable).",
            "`System` -> `Advanced` -> `Admin Access`: Protocol -> `HTTPS`, TCP Port -> `8443` deb belgilash.",
            "`Secure Shell` (SSH) ni yoqish, portni `2222` ga o'zgartirish, `Password Authentication` ni o'chirib, foydalanuvchiga SSH Ed25519 Public Key yuklash.",
            "`Password protect the console menu` bandini yoqish (konsolga kirganda ham login/parol so'rashi uchun).",
            "`System` -> `Advanced` -> `Firewall & NAT`: Maximum table entries sonini 400000 ga ko'tarish."
        ],
        "verification": [
            "ssh -p 2222 -i id_ed25519 secadmin@10.10.10.1 (Faqat kalit bilan kirishni tekshirish)",
            "ssh -p 2222 admin@10.10.10.1 (Admin foydalanuvchisi rad etilishini tekshirish)",
            "curl -I http://10.10.10.1 (HTTP avtomatik 8443 HTTPS ga yo'naltirilishini tekshirish)",
            "pfSense konsoliga ulanib, menyu chiqishidan oldin login/parol so'ralayotganini ko'rish"
        ],
        "troubleshooting": [
            "Muammo: Port 8443 ga o'tgach WebGUI ga kirib bo'lmay qoldi. Yechim: Brauzerda https://10.10.10.1:8443 deb portni aniq yozing.",
            "Muammo: SSH kalit bilan ulanishda 'Permission denied (publickey)' xatosi. Yechim: Kalit huquqi mijozda `chmod 600 id_ed25519` ekanini va pfSense User Manager da kalit to'liq kiritilganini tekshiring."
        ],
        "homework": "pfSense konsoli orqali `zfs list` va `zfs snapshot pfSense/ROOT/default@day2_hardening` buyrug'i yordamida qo'lda snapshot oling va o'zgarishlarni tekshiring."
    },
    {
        "day": 3,
        "title": "DHCP Server, Static Mappings, DHCP Options (PXE/NTP) va DHCP Relay",
        "category": "1-Hafta: Baza va Virtualizatsiya",
        "problem": "Korxonada yangi ulangan printerlar va serverlar IP manzili har rebootda o'zgarib ketmoqda, bu esa servislar to'xtashiga sabab bo'lmoqda. Shu bilan birga tarmoqda vaqt sinxronizatsiyasi (NTP) buzilgan va tarmoq orqali OS o'rnatish (PXE Boot) yo'lga qo'yilmagan.",
        "theory_points": [
            "DHCP (Dynamic Host Configuration Protocol) 4 bosqichi: DORA (Discover, Offer, Request, Acknowledge) UDP 67/68 portlarida.",
            "Static DHCP Mapping (MAC Reservation): IP manzillarini MAC adresga bog'lash va nima uchun serverlarga statik emas, aynan DHCP reservation berish afzalroq?",
            "DHCP Options arxitekturasi: Option 42 (NTP server), Option 66/67 (PXE TFTP Server va Bootfile), Option 43 (UniFi / Aruba Access Point Controller IP).",
            "DHCP Relay Agent (RFC 3046): Router boshqa broadcast domenidagi DHCP so'rovlarni markaziy DHCP serverga Unicast qilib yetkazishi.",
            "IP Conflict Detection: ARP probing va bepul manzillarni tekshirish (Ping check before offer)."
        ],
        "hardware_guide": """* **Hardware:** Fizik tarmoqda bir nechta qurilma (noutbuk, telefon, Wi-Fi AP) ni switchga ulang.
* Wi-Fi Access Point (masalan Ubiquiti UniFi yoki MikroTik) ulangan bo'lsa, pfSense DHCP Option 43 orqali AP ga kontrollerni avtomat taniting.""",
        "virtual_guide": """* **Proxmox / VMware:** Ichki LAN (vmbr1 yoki VMnet1) da ikkita VM ishga tushiring: 1 ta Ubuntu Server, 1 ta Alpine Linux.
* Ularning MAC manzillarini virtual mashina sozlamalaridan aniqlab oling.""",
        "lab_steps": [
            "`Services` -> `DHCP Server` -> `LAN` ga kirish. Subnet: `10.10.10.0/24`, Range: `10.10.10.100` dan `10.10.10.200` gacha belgilash.",
            "Gateway: `10.10.10.1`, DNS Server: `10.10.10.1` (pfSense o'zi).",
            "NTP Server maydoniga `10.10.10.1` manzilini kiritish (Option 42).",
            "`DHCP Static Mappings` bo'limida serveringiz MAC manzilini kiritib, unga qat'iy `10.10.10.20` IP sini va `srv-master.local` hostname berish.",
            "`Services` -> `NTP` sozlamalariga kirib, pfSense NTP serverini yoqish va tashqi hovuz sifatida `pool.ntp.org` ni belgilash.",
            "Mijoz VM yoki kompyuterda IP manzilni yangilash (`dhclient -v` yoki `ipconfig /renew`)."
        ],
        "verification": [
            "Status -> DHCP Leases (Aktiv ijaralarni va statik bog'lanishlarni ko'rish)",
            "ntpdate -q 10.10.10.1 (Mijoz kompyuterdan pfSense NTP serveri ishlayotganini tekshirish)",
            "tcpdump -i vtnet1 -n port 67 or port 68 (pfSense konsolida DORA jarayonini tutib ko'rish)",
            "ping srv-master.local (Statik xostnomi DNS orqali yechilayotganini tekshirish)"
        ],
        "troubleshooting": [
            "Muammo: Mijoz boshqa IP olmoqda (masalan 192.168.x.x). Yechim: Tarmoqda 'Rogue DHCP' (ikkilamchi DHCP server, masalan uy routeri) bor-yo'qligini tekshiring.",
            "Muammo: Static mapping IP diapazon ichida bo'lsa xato beradi. Yechim: pfSense qoidasi bo'yicha Static IP diapazondan (100-200) tashqarida bo'lishi kerak (masalan 10.10.10.20)."
        ],
        "homework": "DHCP Option 66 (TFTP Server: 10.10.10.50) va Option 67 (Bootfile: pxelinux.0) parametrlarini sozlang va Wireshark orqali DHCP Offer paketida ushbu optionlar kelganini tekshiring."
    },
    {
        "day": 4,
        "title": "Unbound DNS chuqur tahlili, DNSSEC, DoT (DNS over TLS) va Split-Horizon DNS",
        "category": "1-Hafta: Baza va Virtualizatsiya",
        "problem": "Internet provayder (ISP) foydalanuvchilar qaysi saytlarga kirayotganini shifrlanmagan DNS port 53 orqali kuzatmoqda (DNS Snooping), soxta javoblar qaytarish (DNS Spoofing) xavfi mavjud, va korxonaning ichki `crm.corp.local` servislari tashqi dunyoga ochilmasdan xavfsiz ichki DNS orqali yechilishi lozim.",
        "theory_points": [
            "DNS daraxti arxitekturasi: Root Servers (13 ta harf), TLD (.com, .uz), Authoritative Nameservers vs Recursive Resolvers.",
            "Unbound DNS Resolver: pfSense ning standart rekursiv rezolveri. Iterative lookup (bevosita ildizdan so'rash) va Forwarding Mode farqi.",
            "DNSSEC (Domain Name System Security Extensions): Kriptografik RRSIG, DNSKEY, DS yozuvlari orqali javob buzilmaganligini (Integrity) kafolatlash.",
            "DNS over TLS (DoT - RFC 7858, Port 853): DNS so'rovlarni Cloudflare (1.1.1.1) yoki Quad9 (9.9.9.9) ga TLS shifrlash orqali jo'natish — ISP monitoringini butkul to'xtatish.",
            "Split-Horizon (Split-Brain) DNS: Bitta domen nomi (masalan `portal.company.com`) ofis ichida lokal IP ga (`10.10.20.10`), ofis tashqarisida esa Public IP ga yechilishi mantig'i."
        ],
        "hardware_guide": """* **Hardware:** WAN porti internetga to'g'ri ulanganini va provayder DNS port 853 ni bloklamaganini tekshiring.
* Agar ichki xususiy Active Directory DNS server bo'lsa, 'Domain Overrides' orqali `.corp` so'rovlarini AD ga yo'naltirish sozlanadi.""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense VM orqali chiquvchi TCP port 853 ruxsat berilgan bo'lishi kerak.
* Test mijoz VM (Ubuntu) da `systemd-resolved` o'rniga DNS sifatida to'g'ridan-to'g'ri pfSense IP sini ko'rsating.""",
        "lab_steps": [
            "`Services` -> `DNS Resolver` -> `General Settings` ga kirish. Port: `53`, Network Interfaces: `ALL` (yoki LAN/Localhost), Outgoing: `WAN`.",
            "`Enable DNSSEC Support` katakchasini yoqish.",
            "`DNS Query Forwarding`: 'Enable Forwarding Mode' va 'Use SSL/TLS for outgoing queries' ni faollashtirish.",
            "`System` -> `General Setup`: DNS Serverlar ro'yxatiga `1.1.1.1` (Hostname: `cloudflare-dns.com`) va `9.9.9.9` (Hostname: `dns.quad9.net`) ni kiritish.",
            "`Services` -> `DNS Resolver`: Eng pastida `Host Overrides` ga kirish. Yangi yozuv: Host: `crm`, Domain: `corp.lan`, IP: `10.10.20.50` kiritish.",
            "Ichki mijozlardan DNS so'rovlar faqat pfSense ga borishi uchun port 53 ni NAT Port Forward orqali pfSense ga majburiy tutib qolish (Redirect DNS)."
        ],
        "verification": [
            "drill -D sigok.verteiltesysteme.net @10.10.10.1 (DNSSEC to'g'ri ishlashini tasdiqlash: rrsig bayrog'i bo'lishi kerak)",
            "drill -D sigfail.verteiltesysteme.net @10.10.10.1 (DNSSEC xato domenini Unbound SERVFAIL qaytarib bloklashi kerak)",
            "tcpdump -i vtnet0 -n port 853 (Tashqi interfeysda barcha DNS so'rovlar TLS orqali shifrlanganini ko'rish)",
            "nslookup crm.corp.lan 10.10.10.1 (Host override natijasi 10.10.20.50 chiqishi kerak)"
        ],
        "troubleshooting": [
            "Muammo: DoT yoqilgach internetda saytlar ochilmay qoldi. Yechim: System > General Setup da Cloudflare IP si yonidagi 'Hostname' (cloudflare-dns.com) to'g'ri yozilganini tekshiring, TLS sertifikat tekshiruvida hostname shart.",
            "Muammo: Ba'zi mijozlar Google DNS (8.8.8.8) ni qo'lda kiritib qoidani chetlab o'tyapti. Yechim: Port Forward NAT qoidasi tuzib, har qanday tashqi port 53/853 ga boruvchi so'rovni pfSense (127.0.0.1) ga burib qo'ying."
        ],
        "homework": "Domain Overrides bo'limidan foydalanib, barcha `.internal` so'rovlarini maxsus ichki serverga (10.10.10.250) yo'naltiruvchi qoida yarating va test qiling."
    },
    {
        "day": 5,
        "title": "802.1Q VLANlar va Inter-VLAN Marshrutlash (Router-on-a-Stick)",
        "category": "1-Hafta: Baza va Virtualizatsiya",
        "problem": "Korxonada buxgalteriya kompyuterlari, umumiy xodimlar, mehmonlar va IoT kameralari bitta umumiy tarmoqda (flat network) joylashgan. Mehmonlar yoki zararlangan kamera orqali buxgalteriya fayllariga va serverlarga to'g'ridan-to'g'ri kirish xavfi mavjud.",
        "theory_points": [
            "L2 Broadcast Domain va Nega tarmoqni bo'lish shart? Broadcast bo'roni va xavfsizlik chegaralari.",
            "IEEE 802.1Q Standarti: Ethernet freymiga 4 baytli VLAN Tag (TPID: 0x8100, VID: 1-4094, PCP) qo'shilishi.",
            "Trunk Port (Tagged) vs Access Port (Untagged) ishlash mexanizmi.",
            "Router-on-a-Stick (RoaS) arxitekturasi: Bitta jismoniy kabel ustidan bir nechta virtual sub-interfeyslar orqali marshrutlash.",
            "Inter-VLAN xavfsizlik devori mantig'i: Standart holatda barcha VLANlar bir-biridan butkul ajratilgan (Drop all), faqat belgilangan portlar ruxsat etiladi."
        ],
        "hardware_guide": """* **Hardware:** pfSense ning LAN portidan (`igb1`) boshqariladigan L2/L3 switchga (Managed Switch) bitta patch-cord torting.
* **Switch sozlamasi:** pfSense ulangan switch portini `Trunk` (802.1Q Tagged: VLAN 10, 20, 30, 40) qilib sozlang.
* Switchning boshqa portlarini `Access` (Untagged) qilib tegishli VLAN larga ajrating (Port 2-5: VLAN 30 Corp, Port 6-8: VLAN 40 Guest).""",
        "virtual_guide": """* **Proxmox VE:**
  * `vmbr1` da 'VLAN aware' katakchasini yoqing.
  * pfSense VM ga bitta `vmbr1` interfeysi yetarli.
  * Sinov VM (Ubuntu) tarmoq kartasida 'VLAN Tag' maydoniga `30` yoki `40` yozasiz.
* **VMware Workstation Pro:**
  * Har bir VLAN uchun alohida VMnet adapter ochish yoki Virtual Distributed Switch (ESXi da 4095 VGT Trunk) sozlash.""",
        "lab_steps": [
            "`Interfaces` -> `Assignments` -> `VLANs` yorlig'iga o'tish.",
            "Parent Interface: `LAN` (`igb1` yoki `vtnet1`), VLAN Tag: `10` (Description: `MGMT`) qo'shish.",
            "Xuddi shu tarzda VLAN `20` (`DMZ`), VLAN `30` (`CORP`), VLAN `40` (`GUEST`) larni yaratish.",
            "`Interface Assignments` bo'limida har bir yangi VLAN ni interfeys sifatida qabul qilish va nomlarini berish.",
            "Har bir VLAN interfeysini yoqish (Enable), IPv4 Static IP berish: MGMT (`10.10.10.1/24`), DMZ (`10.10.20.1/24`), CORP (`10.10.30.1/24`), GUEST (`172.16.40.1/24`).",
            "Har bir VLAN uchun DHCP serverni faollashtirish.",
            "Mehmonlar (GUEST) uchun firewall qoidasi yozish: Faqat Internetga ruxsat, lekin CORP va DMZ subnetlariga kirish bloklangan (RFC 1918 Private Subnets block rule)."
        ],
        "verification": [
            "ifconfig -a (pfSense konsolida vlan10, vlan20, vlan30 interfeyslari paydo bo'lganini ko'rish)",
            "GUEST VLAN dagi mijozdan ping 8.8.8.8 (Internet ishlashi kerak)",
            "GUEST VLAN dagi mijozdan ping 10.10.30.1 yoki CORP dagi PC ga ping (Muvaffaqiyatsiz bo'lishi, firewall bloklashi kerak)",
            "CORP VLAN dan GUEST VLAN ga ulanishni tekshirish"
        ],
        "troubleshooting": [
            "Muammo: VLAN mijozlari IP olmayapti. Yechim: Proxmoxda vmbr1 'VLAN aware' yoqilganini, jismoniy switchda esa port Trunk rejimdaligini va VLAN ruxsat berilganini (allowed vlan) tekshiring.",
            "Muammo: pfSense da tag o'tmayapti. Yechim: Ba'zi eski tarmoq kartalari VLAN sarlavhasini avtomat olib tashlaydi (Hardware VLAN stripping), buni ifconfig orqali tekshirish kerak."
        ],
        "homework": "VLAN 50 (IoT kameralar) segmentini yarating va shunday qoida yozingki, kameralar internetga ham, ichki tarmoqqa ham chiqa olmasin, faqat DMZ dagi NVR server (10.10.20.15) ga ulanish huquqiga ega bo'lsin."
    },
    {
        "day": 6,
        "title": "Firewall Qoidalari, State Table Internals, Floating Rules va Aliases",
        "category": "1-Hafta: Baza va Virtualizatsiya",
        "problem": "Korxonada firewall qoidalari pala-partish yozilgan, qoidalar soni 100 dan oshib ketgan, kimga nima ruxsat berilgani noaniq. Noqonuniy ulanishlar davom etmoqda va ma'murlar qaysi ulanishlar ochiq qolganini ko'ra olmayapti.",
        "theory_points": [
            "`pf` (Packet Filter) qoidalar mantig'i: Qoidalar yuqoridan pastga (Top-to-Bottom) tekshiriladi, birinchi mos kelgan qoida (First Match) ishlaydi va jarayon to'xtaydi (Default Block All qoidasi eng oxirida).",
            "State Table (Holat Jadvali) ishlashi: Stateful firewall birinchi paketni (TCP SYN) tekshirib ruxsat bersa, qaytuvchi javob paketlari (SYN-ACK, ACK) qoidalarni chetlab o'tib, holat jadvali orqali avtomat o'tkaziladi.",
            "Inbound vs Outbound qoidalar tushunchasi: pfSense da qoidalar trafik interfeysga KIRAYOTGAN (Inbound) paytda filtrlanadi.",
            "Floating Rules kuchi: Barcha interfeyslarga birdaniga ta'sir qiluvchi global qoidalar, 'Quick' bayrog'i (darhol to'xtatish yoki quyi qoidalarga ham berish), 'Match' harakati (shaping va tagging uchun).",
            "Aliaslar (Guruhlash): IP manzillar, portlar va dinamik yangilanuvchi URL Tables (Threat feeds) orqali yuzlab qoidalarni bitta toza qoidaga keltirish san'ati."
        ],
        "hardware_guide": """* **Hardware:** Kuchli protsessor bo'lsa ham, qoidalarni Alias yordamida optimallashtirish CPU yuklamasini keskin pasaytiradi.
* Serial konsolda yoki SSH da `pfctl` buyruqlari real apparat holatini monitoring qilishda asosiy vositadir.""",
        "virtual_guide": """* **Proxmox / VMware:** Proxmox xostida 'Firewall' moduli o'chirilgan (disabled) bo'lishi maqsadga muvofiq, aks holda Proxmox pve-firewall pfSense paketlarini filtrlab chalkashlik keltirib chiqarishi mumkin.""",
        "lab_steps": [
            "`Firewall` -> `Aliases` ga kirish. Yangi Alias yaratish: Name: `RFC1918_Subnets`, Type: `Networks`, Qiymatlar: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.",
            "Port Aliases yaratish: Name: `Admin_Ports`, Type: `Ports`, Qiymatlar: `2222, 8443, 443`.",
            "`Firewall` -> `Rules` -> `CORP` bo'limiga kirish.",
            "1-Qoida: Bloklash: Destination: `Single host or alias` -> `RFC1918_Subnets` (Boshqa ichki tarmoqlarga kirish taqiqlansin).",
            "2-Qoida: Ruxsat berish: Protocol: TCP/UDP, Destination: Any, Port: 53, 80, 443 (Faqat Internet va DNS ruxsat).",
            "`Diagnostics` -> `States` ga kirib, aktiv ulanishlarni, har bir sessiyaning paketlar soni va holatini (ESTABLISHED:ESTABLISHED) ko'rish.",
            "Sinov tariqasida bitta aktiv yuklab olish sessiyasini State Table dan 'Kill' tugmasi bilan uzib tashlash."
        ],
        "verification": [
            "pfctl -sr (FreeBSD konsolida generatsiya qilingan xom qoidalar ro'yxatini ko'rish)",
            "pfctl -ss (Aktiv state table sessiyalarini ko'rish)",
            "pfctl -s memory (Holat jadvali xotira hajmi va chegaralarini tekshirish)",
            "Status -> System Logs -> Firewall (Bloklangan va ruxsat berilgan paketlar logini real vaqtda kuzatish)"
        ],
        "troubleshooting": [
            "Muammo: Qoida qo'shildi, lekin eski sessiya hali ham internetdan ma'lumot olyapti. Yechim: Stateful firewall eski ochilgan ulanishlarni uzmaydi; qoida kuchga kirishi uchun Diagnostics > States orqali eski ulanishni kill qilish yoki kutish kerak.",
            "Muammo: Floating rule ishlamayapti. Yechim: Agar Floating Rule da 'Quick' katakchasi belgilanmasa, u interfeys darajasidagi boshqa qoidalar tomonidan bekor qilinishi mumkin."
        ],
        "homework": "URL Table Alias yarating va unga Internetdagi bepul ochiq xavfli IP lar ro'yxatini (masalan Abuse.ch SSLBL) bog'lang. Ushbu IP larga barcha interfeyslardan chiquvchi trafikni bloklovchi Floating Rule yozing."
    },
    {
        "day": 7,
        "title": "NAT Masterclass: Port Forwarding, Outbound NAT, 1:1 NAT va NAT Reflection",
        "category": "1-Hafta: Baza va Virtualizatsiya",
        "problem": "Kompaniyada ichki serverda web-sayt joylashgan. Tashqi foydalanuvchilar Public IP orqali unga kira olmayapti. Ichki ofis xodimlari esa tashqi domen nomi orqali saytni ochganda pfSense ning o'z WebGUI siga tushib qolmoqda (Hairpin NAT yo'qligi sababli).",
        "theory_points": [
            "IPv4 yetishmovchiligi va NAT (RFC 1631) ning mohiyati: Private IP larni Public IP ga o'zgartirish.",
            "DNAT (Destination NAT / Port Forwarding): Tashqi portga kelgan ulanishni ichki aniq bitta server va portga burish.",
            "SNAT (Source NAT / Outbound NAT): Ichki tarmoqdan tashqariga chiquvchi paketlarning jo'natuvchi IP sini WAN IP siga almashtirish (Automatic, Hybrid, Manual rejimlari).",
            "1:1 NAT (Bitta-bitta NAT): Tashqi butun boshli Public IP ni to'g'ridan-to'g'ri ichki serverning barcha portlariga bog'lash.",
            "NAT Reflection (Hairpin NAT / NAT Loopback): Ichki tarmoqdagi mijoz o'z korxonasining tashqi Public IP sini yoki domenini so'raganda router paketni to'g'ri orqaga qaytarish mexanizmi (Pure NAT vs NAT+Proxy)."
        ],
        "hardware_guide": """* **Hardware:** Agar provayder sizga statik Public IP (oq IP) bergan bo'lsa, WAN ga to'g'ridan-to'g'ri kiritiladi.
* Agar provayder modem ortida bo'lsangiz (Double NAT holati), modedan DMZ rejimini pfSense WAN IP siga yo'naltirib qo'yish kerak.""",
        "virtual_guide": """* **Proxmox / VMware:** Virtual laboratoriyada VMware NAT (192.168.x.x) orqali simulyatsiya qilinadi.
* pfSense WAN IP si virtual laboratoriyaning 'Public IP' si vazifasini bajaradi.""",
        "lab_steps": [
            "DMZ zonasida Nginx yoki Apache o'rnatilgan Web-server VM ishga tushirish (IP: `10.10.20.80`, Port: 80).",
            "`Firewall` -> `NAT` -> `Port Forward` bo'limiga kirish va 'Add' tugmasini bosish.",
            "Interface: `WAN`, Protocol: `TCP`, Destination: `WAN address`, Destination Port: `8080` (yoki 80), Redirect Target IP: `10.10.20.80`, Redirect Target Port: `80`.",
            "Filter rule association: `Pass` yoki `Add associated filter rule` (avtomat firewall ruxsat qoidasi yaratish).",
            "`System` -> `Advanced` -> `Firewall & NAT` bo'limiga o'tish.",
            "`NAT Reflection mode for port forwards` parametrini `Pure NAT` ga o'zgartirish va `Enable automatic outbound NAT for Reflection` katakchasini yoqish.",
            "`Firewall` -> `NAT` -> `Outbound` rejimini `Hybrid Outbound NAT rule generation` ga o'tkazish (korporativ standart)."
        ],
        "verification": [
            "Tashqi kompyuterdan: curl http://<WAN_IP>:8080 (Web-server sahifasi muvaffaqiyatli kelishi kerak)",
            "Ichki LAN kompyuterdan: curl http://<WAN_IP>:8080 (NAT Reflection orqali javob kelishi kerak)",
            "tcpdump -i vtnet1 -n host 10.10.20.80 (DMZ interfeysida kelayotgan va qaytayotgan paketlarni kuzatish)",
            "pfctl -sn (FreeBSD konsolida faol NAT qoidalarini tekshirish)"
        ],
        "troubleshooting": [
            "Muammo: Port Forward ishlamayapti. Yechim: pfSense WAN interfeysida 'Block private networks and loopback addresses' (RFC 1918) belgisi turgan bo'lishi mumkin. Agar laboratoriyada WAN 192.168.x.x bo'lsa, bu katakchani o'chirib qo'yish shart!",
            "Muammo: Ichkaridan tashqi IP ga ulanib bo'lmayapti. Yechim: NAT Reflection 'Pure NAT' rejimiga qo'yilganini va avtomatik outbound reflection yoqilganini tekshiring."
        ],
        "homework": "SSH portini tashqaridan xavfsiz qilish maqsadida, WAN dagi nostandart 50222 portini ichki serverning 22 portiga yo'naltiruvchi Port Forwarding qoidasini yarating va faqat ma'lum bir IP dan kirish cheklovini qo'ying."
    },
    {
        "day": 8,
        "title": "Multi-WAN: Dual ISP Failover va Policy-Based Load Balancing",
        "category": "2-Hafta: Marshrutlash, Multi-WAN va VPN",
        "problem": "Korxonada optik tolali internet provayder (ISP1) kabeli uzilib qolsa, butun kompaniya ishi, savdo va to'lov terminallari to'xtab qolmoqda. Zaxiraga olingan 4G/LTE yoki ikkinchi optika provayderi (ISP2) esa qo'lda ulanguncha katta vaqt yo'qotilmoqda.",
        "theory_points": [
            "Ko'p provayderli arxitektura (Multi-Homed Network): Uptime 99.9% ga erishish talabi.",
            "Gateway Monitoring: `dpinger` servisi, ICMP orqali probing, Packet Loss va Latency chegaralari (Thresholds).",
            "Gateway Groups arxitekturasi: Tier 1 + Tier 2 (Active/Passive Failover) va Tier 1 + Tier 1 (Active/Active Load Balancing).",
            "Policy-Based Routing (PBR): Standart default shlyuzni aylanib o'tib, firewall qoidalarining 'Advanced > Gateway' qismida aniq shlyuz guruhini majburiy belgilash.",
            "Sticky Connections muammosi: HTTPS sessiyalar har xil IP dan borsa bank saytlari va CRM xavfsizlik vajidan foydalanuvchini tizimdan chiqarib yuboradi — yechimi: Sticky Connections."
        ],
        "hardware_guide": """* **Hardware:** pfSense da kamida 3 ta jismoniy port bo'lishi shart (`igb0` = ISP1, `igb1` = ISP2, `igb2` = LAN).
* ISP1 kabeli port 1 ga, ISP2 modem kabeli port 2 ga ulanadi.
* Har bir provayder o'zining alohida IP manziliga ega bo'lishi kerak (turli subnetlar).""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense VM ga 3 ta tarmoq kartasi beriladi:
  * Adapter 1 (WAN1): `vmbr0` (192.168.100.0/24)
  * Adapter 2 (WAN2): `vmbr2` (192.168.200.0/24)
  * Adapter 3 (LAN): `vmbr1` (10.10.10.0/24).""",
        "lab_steps": [
            "`Interfaces` -> `Assignments` bo'limida ikkinchi WAN (OPT1) ni qo'shish va nomini `WAN2_BACKUP` deb qo'yish.",
            "`System` -> `Routing` -> `Gateways` ga kirish. WAN1 uchun Monitor IP: `1.1.1.1`, WAN2 uchun Monitor IP: `8.8.8.8` belgilash.",
            "`Gateway Groups` yorlig'iga o'tib, 'Add' tugmasini bosish. Group Name: `GW_FAILOVER`. WAN1: Tier 1, WAN2: Tier 2. Trigger: `Member Down`.",
            "Yana bir guruh yaratish: Group Name: `GW_LOADBALANCE`. WAN1: Tier 1, WAN2: Tier 1. Trigger: `Packet Loss or High Latency`.",
            "`System` -> `Advanced` -> `Miscellaneous`: `Use sticky connections` katakchasini yoqish.",
            "`Firewall` -> `Rules` -> `LAN`: Default Internetga ruxsat beruvchi qoidani tahrirlash -> `Display Advanced` -> `Gateway` maydonida `GW_FAILOVER` yoki `GW_LOADBALANCE` ni tanlash."
        ],
        "verification": [
            "Status -> Gateways (Ikkala shlyuz ham Online, ping va jitter yashil ekanini ko'rish)",
            "curl https://ifconfig.me (Hozirgi chiqish tashqi IP manzilini tekshirish)",
            "pfSense WAN1 kabelini jismonan uzib tashlash (yoki virtual adapter kabelini ajratish)",
            "5-10 soniya ichida Status > Gateways da WAN1 Offline bo'lib, trafik darhol WAN2 orqali uzluksiz o'tayotganini tekshirish (ping davom etadi)"
        ],
        "troubleshooting": [
            "Muammo: Gateway doim 'Pending' yoki 'Offline' ko'rsatmoqda. Yechim: Monitor IP sifatida provayder shlyuzini emas, ommaviy ishonchli IP larni (1.1.1.1, 8.8.8.8, 9.9.9.9) ko'rsating va WAN firewall qoidasida ushbu IP lardan ICMP Echo Reply ga ruxsat borligiga ishonch hosil qiling.",
            "Muammo: Failover ishlagandan so'ng WAN1 qaytsa ham trafik qaytmayapti. Yechim: 'State Killing on Gateway Failure' opsiyasi yoqilgan bo'lishi kerak."
        ],
        "homework": "Shunday PBR qoidasi yozingki, mehmonlar (GUEST VLAN) trafigi faqat va faqat arzon WAN2 (LTE) orqali chiqsin, asosiy qimmat WAN1 optikasi esa korporativ xodimlar (CORP VLAN) ga ajratilsin."
    },
    {
        "day": 9,
        "title": "Dinamik Marshrutlash: FRR (Free Range Routing) bilan OSPF va BGP",
        "category": "2-Hafta: Marshrutlash, Multi-WAN va VPN",
        "problem": "Korxona tarmog'i 5 ta alohida bino va routerlarga (Cisco, MikroTik, Linux) ega. Tarmoqqa yangi subnet qo'shilganda har bir routerga qo'lda Static Route yozish chalkashliklarga, yo'nalishlar sikliga (routing loop) va avariyaga olib kelmoqda.",
        "theory_points": [
            "Statik marshrutlashning cheklovlari va Dinamik marshrutlashning zarurati.",
            "FRRouting (FRR) arxitekturasi: FreeBSD ustida zebra, ospfd, bgpd demonlari.",
            "OSPF (Open Shortest Path First - RFC 2328): Link-State arxitekturasi, Dijkstra algoritmi (SPF), LSA paketlari, OSPF Areas (Backbone Area 0), Hello paketlar va Adjacency.",
            "BGP (Border Gateway Protocol - RFC 4271): Path-Vector protokoli, Autonomous Systems (ASN), eBGP vs iBGP, Route Redistribution.",
            "pfSense da OSPF autentifikatsiyasi (MD5/SHA) va xavfsiz marshrut almashinuvi."
        ],
        "hardware_guide": """* **Hardware:** pfSense bitta porti orqali tashqi L3 switchga yoki Cisco/MikroTik routerga ulangan bo'lishi kerak.
* OSPF multicast (`224.0.0.5`, `224.0.0.6`) paketlari switch orqali o'tishi taqiqlanmagan bo'lishi shart.""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense yoniga ikkinchi router sifatida FRR o'rnatilgan Ubuntu Server yoki MikroTik CHR VM ishga tushiring.
* Ularni umumiy `vmbr3` (10.254.0.0/30) orqali ulang.""",
        "lab_steps": [
            "`System` -> `Package Manager` -> `Available Packages` ga kirib, `frr` paketini topish va o'rnatish.",
            "`Services` -> `FRR Global/Zebra`: Global sozlamalarni yoqish, Router ID ga `10.10.10.1` berish.",
            "`Services` -> `FRR OSPF`: OSPF ni yoqish. Area ID: `0.0.0.0` (Backbone Area).",
            "`Interfaces` yorlig'ida qo'shni routerga qaragan interfeysni tanlash, Network Type: `Point-to-Point` yoki `Broadcast` deb belgilash.",
            "`Redistribute` bo'limida `Connected Networks` ni OSPF orqali boshqalarga tarqatishni yoqish.",
            "Qo'shni routerda (MikroTik yoki Linux FRR) ham OSPF Area 0 ni yoqish va pfSense bilan qo'shnichilik (Full Adjacency) o'rnatish."
        ],
        "verification": [
            "vtysh -c 'show ip ospf neighbor' (pfSense konsolida qo'shnining FULL/DR yoki FULL/BDR holatdaligini ko'rish)",
            "vtysh -c 'show ip route ospf' (OSPF orqali o'rganilgan marshrutlar jadvalini ko'rish)",
            "Status -> FRR -> OSPF (WebGUI orqali holatni kuzatish)",
            "Qo'shni tarmoqdagi yangi serverga ping yuborish (qo'lda route yozmasdan aloqa borligini tekshirish)"
        ],
        "troubleshooting": [
            "Muammo: OSPF 'Init' yoki '2-Way' holatida qotib qoldi, 'Full' bo'lmayapti. Yechim: Interfeyslardagi MTU hajmi bir xil bo'lishi kerak (yoki 'MTU Ignore' yoqiladi), shuningdek Hello/Dead taymerlari (10s/40s) mos kelishini tekshiring.",
            "Muammo: Qo'shnidan marshrut kelmayapti. Yechim: Firewall Rules bo'limida OSPF protokoli (IP Protocol 89) ruxsat berilganligini tasdiqlang."
        ],
        "homework": "OSPF MD5 kalit autentifikatsiyasini yoqing va shifrlanmagan Hello paketlar qabul qilinmasligini Wireshark/tcpdump orqali tekshiring."
    },
    {
        "day": 10,
        "title": "OpenVPN Remote Access (Road Warrior), PKI/CA va Client Export",
        "category": "2-Hafta: Marshrutlash, Multi-WAN va VPN",
        "problem": "Karantin yoki masofaviy ish vaqtida 50 nafar xodim uyidan turib korporativ fayl-serverlar va CRM ga xavfsiz ulanishi kerak. Oddiy portlarni ochish xavfli, xodimlarning noutbuklariga VPN sozlamalarini qo'lda o'rnatib chiqish esa katta vaqt talab qiladi.",
        "theory_points": [
            "Virtual Private Network (VPN) tamoyillari: Tunneling, Shifrlash (Encryption), Autentifikatsiya va Yaxlitlik (Integrity).",
            "Public Key Infrastructure (PKI): Root Certificate Authority (CA), Server Certificate va Har bir mijoz uchun alohida Client Certificate mexanizmi.",
            "OpenVPN Protokoli: SSL/TLS asosidagi VPN, UDP vs TCP tanlovi (Nega UDP 1194 tezroq va samaraliroq?).",
            "TLS-Crypt vs TLS-Auth: Port skanerlashdan himoya (Port knocking effekti) — server begona paketlarga javob bermaydi va DoS hujumlarni boshidayoq to'xtatadi.",
            "Split Tunneling vs Full Tunneling: Faqat ofis resurslarini VPN dan o'tkazish yoki barcha internet trafigini ofis orqali haydash."
        ],
        "hardware_guide": """* **Hardware:** pfSense protsessorida Intel AES-NI ko'rsatmasi faol bo'lsa, OpenVPN shifrlash tezligi 5-10 baravarga oshadi (`System > Advanced > Miscellaneous > Cryptographic Hardware`).
* WAN portida oq IP bo'lishi yoki yuqori routerdan UDP 1194 porti pfSense ga yo'naltirilgan bo'lishi lozim.""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense VM sozlamalarida CPU turini `host` deb tanlang (AES-NI ko'rsatmasi virtual mashinaga to'g'ridan-to'g'ri o'tishi uchun).""",
        "lab_steps": [
            "`System` -> `Cert. Manager` -> `CAs` bo'limiga kirish. 'Add' -> Internal CA yaratish: Name: `Corp_Root_CA`, Key: 2048-bit RSA yoki ECDSA P-384.",
            "`Certificates` yorlig'ida yangi Server sertifikatini chiqarish: Name: `VPN_Server_Cert`, Type: `Server Certificate`.",
            "`VPN` -> `OpenVPN` -> `Wizards` yordamida tezkor sozlash ustasini ishga tushirish.",
            "Interface: `WAN`, Protocol: `UDP on IPv4`, Port: `1194`, Encryption: `AES-256-GCM`, Auth: `SHA256`, TLS-Crypt faollashtirish.",
            "Tunnel Network: `10.201.0.0/24`, Local Network: `10.10.10.0/24, 10.10.20.0/24`.",
            "System -> Package Manager dan `openvpn-client-export` paketini o'rnatish.",
            "`System` -> `User Manager` da yangi xodim `user1` yaratish va unga shaxsiy User Certificate berish.",
            "`VPN` -> `OpenVPN` -> `Client Export` bo'limiga o'tib, Windows yoki Android/iOS uchun tayyor `.ovpn` faylni yuklab olish."
        ],
        "verification": [
            "Mijoz qurilmasida OpenVPN Connect dasturini ishga tushirib, yuklab olingan profil bilan ulanish",
            "Status -> OpenVPN (WebGUI da mijozning real IP si, virtual IP si (10.201.0.2) va uzatilgan baytlar sonini ko'rish)",
            "Mijozdan: ping 10.10.20.80 (Ofis ichidagi DMZ serverga VPN orqali yetib borishni tekshirish)",
            "curl ifconfig.me (Mijozning tashqi IP si o'zgarganini yoki split-tunnelda o'zgarishsiz qolganini tekshirish)"
        ],
        "troubleshooting": [
            "Muammo: TLS Error: TLS handshake failed. Yechim: WAN firewall qoidasida UDP 1194 porti ochilganini, vaqt (NTP) mijoz va serverda bir xilligini tekshiring (sertifikatlar vaqtga o'ta sezgir).",
            "Muammo: Ulandi, lekin ichki kompyuterlarga ping bormayapti. Yechim: 'Local Network' maydonida ofis subnetlari to'g'ri ko'rsatilganini va OpenVPN interfeysi qoidalarida ruxsat berilganini tekshiring."
        ],
        "homework": "Split-Tunnel rejimini sozlang (faqat 10.10.0.0/16 trafigi VPN orqali ketsin, YouTube/Google trafigi esa xodimning o'z uy interneti orqali o'tsin). Natijani mijozda `tracert` orqali tasdiqlang."
    },
    {
        "day": 11,
        "title": "OpenVPN Site-to-Site Tunneling va Client Specific Overrides (CSO)",
        "category": "2-Hafta: Marshrutlash, Multi-WAN va VPN",
        "problem": "Bosh ofis (Headquarters) va Samarqanddagi filiali (Branch Office) o'rtasida doimiy xavfsiz aloqa zarur. Filial xodimlari bosh ofisdagi serverlarga to'g'ridan-to'g'ri murojaat qilishi, shuningdek kelajakda boshqa filiallar qo'shilsa ularning IP diapazonlari to'qnashmasligi lozim.",
        "theory_points": [
            "Site-to-Site VPN tushunchasi: Foydalanuvchi kompyuterlarida VPN dasturi o'rnatilmaydi; ikkita xavfsizlik devori o'zaro tunnel quradi va butun tarmoqlarni bog'laydi.",
            "SSL/TLS vs Shared Key (Preshared): Nega ishlab chiqarishda Shared Key eskirgan va cheklangan (faqat 1 ta tunnel), SSL/TLS esa bitta serverga yuzlab filiallarni ulash imkonini beradi?",
            "Topology Subnet vs Topology Net30: Zamonaviy IP tejash usuli.",
            "Client Specific Overrides (CSO): Har bir filialning umumiy sertifikat nomiga (Common Name - CN) qarab, unga maxsus statik VPN IP va orqa tarmoq (Remote Network / `iroute`) yo'nalishini biriktirish.",
            "`iroute` mexanizmi: pfSense yadrosiga 'bu filial orqasida qaysi subnetlar yotgani'ni tushuntirish."
        ],
        "hardware_guide": """* **Hardware:** Ikkita alohida jismoniy pfSense qurilmasi (biri Bosh ofisda, ikkinchisi Filialda).
* Bosh ofisda oq (Public) IP bo'lishi kifoya, filial esa NAT yoki hatto dinamik IP ortida bo'lsa ham tunnel ishlayveradi.""",
        "virtual_guide": """* **Proxmox / VMware:** Ikkita pfSense VM yaratiladi: `pfSense-HQ` (LAN: 10.10.0.0/16) va `pfSense-Branch` (LAN: 10.20.0.0/16).
* Ularning WAN lari umumiy virtual switchga ulanadi.""",
        "lab_steps": [
            "Bosh ofisda (HQ): `VPN` -> `OpenVPN` -> `Servers`. Server Mode: `Peer to Peer (SSL/TLS)`, Protocol: `UDP on IPv4`, IPv4 Tunnel Network: `10.250.0.0/24`.",
            "IPv4 Local Network: `10.10.0.0/16`, IPv4 Remote Network: bo'sh qoldiriladi (CSO orqali beriladi).",
            "Filial uchun Client Certificate yaratish: Common Name: `branch-samarkand`.",
            "`VPN` -> `OpenVPN` -> `Client Specific Overrides`: Yangi CSO qo'shish. Common Name: `branch-samarkand`, IPv4 Remote Network/s: `10.20.0.0/16`.",
            "Filialda (Branch): `VPN` -> `OpenVPN` -> `Clients`. Server host: HQ WAN IP, TLS Authentication, CA va `branch-samarkand` sertifikatlarini yuklash.",
            "IPv4 Tunnel Network: `10.250.0.0/24`, IPv4 Remote Network: `10.10.0.0/16`.",
            "Ikkala tomonda `Firewall` -> `Rules` -> `OpenVPN` bo'limida barcha trafikka ruxsat beruvchi qoida kiritish."
        ],
        "verification": [
            "Status -> OpenVPN (Ikkala pfSense da ham tunnel 'up' holatdaligini ko'rish)",
            "Filial LAN kompyuteridan: ping 10.10.20.80 (Bosh ofis DMZ serveriga ping yetib borishini tekshirish)",
            "Bosh ofis kompyuteridan: ping 10.20.0.50 (Filialdagi printer yoki kompyuterga ping borishini tekshirish)",
            "tracert 10.10.20.80 (Paketlar VPN tunnel 10.250.0.1 orqali o'tayotganini tasdiqlash)"
        ],
        "troubleshooting": [
            "Muammo: Tunnel ko'tarildi, lekin HQ dan Branch ga ping bormayapti (Branch dan HQ ga esa boradi). Yechim: CSO da `iroute 10.20.0.0 255.255.0.0` yozilmagan yoki CN xato yozilgan bo'ladi.",
            "Muammo: IP to'qnashuvi. Yechim: Ikkala tomonda ham LAN subnetlari bir xil (masalan ikkalasi ham 192.168.1.0/24) bo'lmasligi shart; har bir filial o'ziga xos subnetga ega bo'lishi kerak."
        ],
        "homework": "Ikkinchi filial uchun (`branch-bukhara`, LAN: `10.30.0.0/16`) yangi sertifikat va CSO sozlang va uchala nuqta o'rtasida to'liq marshrutlashni ta'minlang."
    },
    {
        "day": 12,
        "title": "WireGuard High-Performance VPN: Zamonaviy Kriptografiya va Benchmarking",
        "category": "2-Hafta: Marshrutlash, Multi-WAN va VPN",
        "problem": "OpenVPN yuqori yuklamada va 1Gbps+ tezlikdagi optik kanallarda protsessorni 100% ga yuklab, tezlikni 150-200 Mbps dan oshira olmayapti. Mobil foydalanuvchilar esa Wi-Fi dan LTE ga o'tganda aloqa uzilib, qayta ulanish uzoq vaqt olmoqda.",
        "theory_points": [
            "WireGuard inqilobi: Jason Donenfeld arxitekturasi, atigi ~4000 qator kod (OpenVPN ning 100,000+ qatoriga nisbatan), kamroq zaifliklar yuzasi (Attack Surface).",
            "Zamonaviy kriptografiya: ChaCha20 simmetrik shifrlash, Poly1305 autentifikatsiyasi, Curve25519 ECDH kalit almashinuvi, BLAKE2s xeshlash.",
            "FreeBSD yadrosidagi WireGuard (`if_wg` kernel moduli) unumdorligi: User-space emas, bevosita yadro darajasida ishlash.",
            "Cryptokey Routing tamoyili: Har bir Peer o'zining ochiq kalitiga (Public Key) va ruxsat berilgan IP manzillariga (`AllowedIPs`) ega bo'ladi.",
            "Roaming (Mobil qulaylik): Mijoz IP si (Wi-Fi -> LTE) o'zgarganda ham tunnel uzilmasdan darhol davom etaveradi."
        ],
        "hardware_guide": """* **Hardware:** WireGuard zamonaviy SIMD (AVX2, AVX-512, ARM NEON) ko'rsatmalaridan to'liq foydalanadi, shuning uchun past quvvatli mini-PC larda ham 1Gbps+ tezlikni bemalol ta'minlaydi.
* UDP port 51820 ni tinglaydi.""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense 2.7.2 CE versiyasida WireGuard rasmiy paket sifatida kiritilgan.
* VM da CPU turini `host` qilib qo'yish shart.""",
        "lab_steps": [
            "`System` -> `Package Manager` dan `WireGuard` paketini o'rnatish.",
            "`VPN` -> `WireGuard` -> `Tunnels` ga kirish. 'Add Tunnel': Description: `WG_CORP`, Listen Port: `51820`, Interface Keys: 'Generate' tugmasini bosib Public/Private kalit juftligini yaratish.",
            "`Interfaces` -> `Assignments` bo'limida yangi paydo bo'lgan `tun_wg0` interfeysini qabul qilish va nomini `WIREGUARD` deb nomlash. IPv4: `10.200.0.1/24`.",
            "`VPN` -> `WireGuard` -> `Peers` bo'limiga o'tish. 'Add Peer': Tunnel: `tun_wg0`, Description: `Engineer_Laptop`, Public Key: (mijoz kaliti), AllowedIPs: `10.200.0.2/32`.",
            "Mijoz noutbukida (Windows/macOS/Linux) WireGuard rasmiy ilovasini o'rnatish va konfiguratsiya kiritish:",
            "[Interface] PrivateKey = ..., Address = 10.200.0.2/24, DNS = 10.10.10.1; [Peer] PublicKey = (pfSense public key), Endpoint = <WAN_IP>:51820, AllowedIPs = 10.10.0.0/16.",
            "`Firewall` -> `Rules` -> `WAN`: UDP port 51820 ga ruxsat berish. `Firewall` -> `Rules` -> `WIREGUARD`: Ichki tarmoqlarga ruxsat berish."
        ],
        "verification": [
            "Status -> WireGuard (WebGUI da peer bilan Handshake soniyalari va uzatilgan megabaytlar ko'rinishi kerak)",
            "wg show (pfSense konsolida peerlar va oxirgi handshake holatini ko'rish)",
            "iperf3 -s (pfSense LAN dagi serverda) va iperf3 -c 10.10.20.80 (VPN ulangan mijozdan o'tkazuvchanlik tezligini o'lchash)",
            "OpenVPN va WireGuard o'rtasida ping va CPU yuklamasini taqqoslash"
        ],
        "troubleshooting": [
            "Muammo: Handshake sodir bo'lmayapti (0 bayt qabul qilindi). Yechim: WAN dagi UDP 51820 ruxsat qoidasini tekshiring, mijozda pfSense Public kaliti, pfSense da esa mijoz Public kaliti to'g'ri ko'rsatilganini qayta tekshiring.",
            "Muammo: AllowedIPs xatosi. Yechim: Mijoz tomonda AllowedIPs ga faqat kerakli tarmoqlar kiritilishi lozim; agar 0.0.0.0/0 qo'yilsa butun internet trafigi tunnelga ketadi."
        ],
        "homework": "Ikkita pfSense o'rtasida WireGuard yordamida Site-to-Site tunnel quring va `iperf3` yordamida OpenVPN Site-to-Site dan necha barobar tezroq ekanligini jadval qilib solishtiring."
    },
    {
        "day": 13,
        "title": "Enterprise IPsec IKEv2 Site-to-Site Tunnel va Routed VTI",
        "category": "2-Hafta: Marshrutlash, Multi-WAN va VPN",
        "problem": "Kompaniya davlat tashkilotlari yoki yirik bank bilan xavfsiz B2B integratsiya qilishi kerak. Hamkor tomon faqat sanoat standarti bo'lgan IPsec IKEv2 ni talab qilmoqda va marshrutlarni boshqarish uchun dinamik marshrutlashni (VTI) shart qilib qo'ygan.",
        "theory_points": [
            "IPsec (Internet Protocol Security) arxitekturasi: Tarmoq qatlamida (L3) shifrlash, AH (Authentication Header) vs ESP (Encapsulating Security Payload).",
            "IKEv1 vs IKEv2 (Internet Key Exchange): Nega IKEv1 eskirgan va IKEv2 kamroq paket almashinuvi, DoS dan himoya, NAT-Traversal (NAT-T) va MOBIKE bilan ustun?",
            "Ikki Fazali Jarayon: Phase 1 (IKE SA - tunnelning o'zini xavfsiz qilish, DH guruhlar) va Phase 2 (Child SA - real ma'lumotlarni shifrlash, PFS).",
            "Policy-Based IPsec vs Route-Based IPsec (VTI - Virtual Tunnel Interface): Nega VTI korxonalar uchun eng qulay (interfeys sifatida ko'rinadi, OSPF/BGP yurgizish mumkin)?",
            "Dead Peer Detection (DPD) va Rekeying parametrlari."
        ],
        "hardware_guide": """* **Hardware:** IPsec AES-GCM shifrlash usuli Intel QuickAssist yoki AES-NI apparat tezlatkichlarida deyarli 0% CPU yuklama bilan ishlaydi.
* UDP port 500 (IKE) va UDP port 4500 (NAT-T), shuningdek IP Protocol 50 (ESP) ochiq bo'lishi lozim.""",
        "virtual_guide": """* **Proxmox / VMware:** Ikkita pfSense VM yoki pfSense bilan Cisco/StrongSwan router o'rtasida sinovdan o'tkaziladi.""",
        "lab_steps": [
            "`VPN` -> `IPsec` -> `Tunnels` ga kirish. 'Add P1' (Phase 1 yaratish).",
            "Key Exchange: `IKEv2`, Interface: `WAN`, Remote Gateway: `Hamkor_WAN_IP`, Pre-Shared Key: murakkab 32+ belgili kalit kiritish.",
            "Phase 1 Takliflari: Encryption: `AES256-GCM` (128 bit ICV), Hash: `SHA256`, DH Group: `14 (2048-bit)` yoki `19 (NIST P-256)`. DPD: yoqilgan.",
            "'Add P2' (Phase 2 yaratish). Mode: `Routed (VTI)`. Local Network: `10.254.254.1/30`, Remote Network: `10.254.254.2/30`.",
            "Phase 2 Takliflari: Encryption: `AES256-GCM`, PFS Key Group: `14`.",
            "`Interfaces` -> `Assignments` bo'limida yangi `ipsecX` VTI interfeysini qabul qilish va unga IP biriktirish.",
            "`System` -> `Routing` -> `Static Routes` bo'limida hamkor tarmoqni (`172.20.0.0/16`) VTI shlyuzi orqali yo'naltirish."
        ],
        "verification": [
            "Status -> IPsec (Overview va SADs/SPDs jadvallarida tunnel ESTABLISHED ekanini ko'rish)",
            "strongswan konsol buyrug'i: ipsec statusall (pfSense konsolida IKE SA va Child SA holatini tekshirish)",
            "ping -S 10.10.10.1 172.20.0.1 (VTI tunnel orqali hamkor shlyuziga ping yuborish)",
            "tcpdump -i vtnet0 -n esp (Tashqi interfeysda faqat ESP shifrlangan paketlar aylanayotganini ko'rish)"
        ],
        "troubleshooting": [
            "Muammo: Phase 1 o'tadi, lekin Phase 2 'NO_PROPOSAL_CHOSEN' xatosi bilan to'xtaydi. Yechim: Ikkala tomonda shifrlash algoritmlari (AES-GCM, DH Group, PFS) va Subnet parametrlari bir xil ekanini tekshiring.",
            "Muammo: NAT ortidagi holat. Yechim: UDP 4500 (NAT-Traversal) avtomatik yoqilgan bo'lishi va P1 da 'NAT-T: Auto' turishi kerak."
        ],
        "homework": "VTI interfeysi ustidan FRR paketi orqali BGP sessiyasini yoqing va hamkor tarmoq bilan dinamik marshrut almashinuvini ishga tushiring."
    },
    {
        "day": 14,
        "title": "Mobile IPsec IKEv2 (Native Windows, macOS va iOS ilovasiz ulanishi)",
        "category": "2-Hafta: Marshrutlash, Multi-WAN va VPN",
        "problem": "Kompaniya xodimlarining noutbuklari (Windows 11, macOS) qat'iy korporativ nazoratda bo'lib, ularga uchinchi tomon dasturlarini (OpenVPN yoki WireGuard kabi) o'rnatish IT Security tomonidan taqiqlangan. Xodimlar faqat operatsion tizimning o'zida mavjud ichki VPN vositasi orqali ulanishi shart.",
        "theory_points": [
            "Native OS VPN afzalliklari: Hech qanday qo'shimcha ilova talab etilmaydi, batareya sarfi minimal va tizim darajasida xavfsiz integratsiya qilingan.",
            "IKEv2 EAP (Extensible Authentication Protocol): Foydalanuvchi login va paroli (MSCHAPv2) orqali autentifikatsiya, server esa xususiy SSL sertifikati orqali tasdiqlanadi.",
            "FQDN va SAN (Subject Alternative Name) qat'iy talablari: Apple va Microsoft operatsion tizimlari server sertifikatidagi CN yoki SAN domen nomiga (masalan `vpn.company.uz`) 100% mos kelmasa ulanishni darhol to'xtatadi.",
            "Virtual Address Pool: Mobil mijozlarga avtomatik IP manzillar va DNS parametrlarini taqsimlash.",
            "Windows rasmiy PowerShell buyruqlari bilan IKEv2 xavfsizlik profilini kuchaytirish."
        ],
        "hardware_guide": """* **Hardware:** pfSense WAN interfeysi ommaviy DNS ga bog'langan FQDN domeniga ega bo'lishi lozim (masalan `vpn.firma.uz`).
* UDP 500 va UDP 4500 portlari ochiq bo'lishi shart.""",
        "virtual_guide": """* **Proxmox / VMware:** Laboratoriyada sinash uchun Windows 10/11 VM mijozi kerak bo'ladi.
* pfSense CA Root sertifikati Windows ning 'Trusted Root Certification Authorities' do'koniga import qilinishi shart.""",
        "lab_steps": [
            "`System` -> `Cert. Manager`: Server sertifikati yaratish. Common Name: `vpn.firma.uz`, SAN: DNS: `vpn.firma.uz`, IP: `<WAN_IP>`, Certificate Type: `Server Certificate`.",
            "`VPN` -> `IPsec` -> `Mobile Clients`: 'Enable IPsec Mobile Client Support' katakchasini yoqish.",
            "User Authentication: `Local Database`, Virtual Address Pool: `10.205.0.0/24`, DNS Servers: `10.10.10.1`.",
            "`Tunnels` bo'limida yangi Phase 1 qo'shish: Key Exchange: `IKEv2`, Authentication Method: `EAP-MSCHAPv2`, My Identifier: `FQDN: vpn.firma.uz`, Server Certificate: `vpn.firma.uz`.",
            "Phase 2 qo'shish: Mode: `Tunnel IPv4`, Local Network: `0.0.0.0/0` (Full tunnel) yoki `10.10.0.0/16` (Split tunnel).",
            "`System` -> `User Manager` da xodim login va parolini yaratish.",
            "Windows mijozida `Set-VpnConnection` PowerShell buyrug'i orqali IKEv2 profilini yaratish va xavfsiz AES-256 shifrlash parametrlarini o'rnatish."
        ],
        "verification": [
            "Windows tizim sozlamalaridan (Settings -> Network -> VPN) 'Connect' tugmasini bosib ulanish",
            "Status -> IPsec -> Leases (Mobil mijozga 10.205.0.x IP berilganini ko'rish)",
            "Mijozdan: ping 10.10.20.80 (Ofis serveriga ulanishni tekshirish)",
            "ipconfig /all (Mijozda IPsec virtual adapter parametrlari paydo bo'lganini tasdiqlash)"
        ],
        "troubleshooting": [
            "Muammo: Windows 11 da 'Error 13801: IKE authentication credentials are unacceptable'. Yechim: pfSense CA sertifikati Windows 'Local Computer > Trusted Root Certification Authorities' ga o'rnatilmagan yoki server FQDN nomi sertifikat SAN ga mos emas.",
            "Muammo: 'Error 809'. Yechim: Windows ro'yxatida (Registry) `AssumeUDPEncapsulationContextOnSendRule` qiymatini 2 qilib qo'yish kerak (NAT ortidagi IKEv2 uchun)."
        ],
        "homework": "Ushbu IKEv2 sozlamasini o'z smartfoningizga (iOS yoki Android da strongSwan ilovasi) ulab ko'ring va xavfsiz ichki tarmoqqa mobil telefon orqali kiring."
    },
    {
        "day": 15,
        "title": "Zero-Trust va Overlay Network: Tailscale Subnet Router",
        "category": "2-Hafta: Marshrutlash, Multi-WAN va VPN",
        "problem": "Kompaniyaning uzoq tumanlardagi do'konlari va omborlarida oq (Public) IP manzil yo'q, barchasi mobil 4G modemlar va qat'iy CGNAT (Carrier-Grade NAT) ortida joylashgan. An'anaviy VPN tünellarini ko'tarish imkonsiz, lekin markaziy tizim ushbu omborlardagi serverlarga kirishi zarur.",
        "theory_points": [
            "Zero-Trust Network Access (ZTNA) tamoyillari: Hech kimga va hech bir tarmoqqa ishonmaslik, har bir ulanishni shifrlash va tekshirish.",
            "Overlay Mesh Networks: Murakkab jismoniy tarmoqlar ustida virtual dasturiy tarmoq qurish.",
            "Tailscale arxitekturasi: WireGuard protokoliga asoslangan, koordinatsiya serveri (Control Plane) va DERP (Designated Encrypted Relay for Packets) relaylari orqali har qanday CGNAT va Firewall ni teshish (NAT Traversal / UDP hole punching).",
            "pfSense Subnet Router sifatida: pfSense o'zining butun orqa tarmog'ini (masalan `10.10.0.0/16`) Tailscale mesh tarmog'iga e'lon qiladi (Advertise Routes).",
            "Exit Node imkoniyati: Barcha masofaviy qurilmalar internetga pfSense orqali xavfsiz chiqishi."
        ],
        "hardware_guide": """* **Hardware:** Hech qanday oq IP talab qilinmaydi! pfSense oddiy mobil 4G modem yoki uy Wi-Fi siga ulangan bo'lsa ham ishlayveradi.
* Faqat chiquvchi UDP portlar cheklanmagan bo'lishi kifoya.""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense VM internetga chiqishi ta'minlangan bo'lsa yetarli.
* pfSense FreeBSD paketlari orqali Tailscale ni o'rnatadi.""",
        "lab_steps": [
            "`System` -> `Package Manager` dan `tailscale` paketini topib o'rnatish.",
            "`VPN` -> `Tailscale` sozlamalariga kirish va 'Enable Tailscale' ni yoqish.",
            "`tailscale login` yoki WebGUI dagi havola orqali Tailscale akkauntingizga (Google/GitHub/Microsoft) kirib, pfSense ni avtorizatsiya qilish.",
            "Subnet Marshrutlarini e'lon qilish: pfSense konsolida yoki WebGUI parametrlarida `--advertise-routes=10.10.10.0/24,10.10.20.0/24` buyrug'ini kiritish.",
            "Tailscale Admin Console (login.tailscale.com) ga kirish, pfSense qurilmasini topish, `Edit route settings` bo'limida e'lon qilingan subnetlarni tasdiqlash (Approve).",
            "`Key expiry` parametrini 'Disable' qilish (server uzilib qolmasligi uchun).",
            "Mijoz kompyuterida Tailscale ni yoqish va to'g'ridan-to'g'ri `10.10.20.80` IP siga murojaat qilish."
        ],
        "verification": [
            "tailscale status (pfSense konsolida mesh tarmoqdagi barcha boshqa kompyuterlarni ko'rish)",
            "tailscale ping <mijoz_100.x.x.x_IP> (To'g'ridan-to'g'ri peer-to-peer tunnelini tekshirish)",
            "Mijoz noutbukidan (uy internetida): ping 10.10.20.80 (CGNAT ortidagi pfSense ichki serveriga port ochmasdan kirish)",
            "tailscale netcheck (NAT teshish imkoniyatlari va eng yaqin DERP serverlarini ko'rish)"
        ],
        "troubleshooting": [
            "Muammo: Subnet ping qilinmayapti. Yechim: Tailscale boshqaruv panelida 'Subnet routes' yonida yashil 'Approved' belgisi turganini va pfSense da IP Forwarding (`sysctl net.inet.ip.forwarding=1`) yoqilganini tekshiring.",
            "Muammo: Relayed ulanish (tezlik past). Yechim: Mahalliy router UDP paketlarini qattiq bloklasa, ulanish DERP orqali ketadi; buning oldini olish uchun UPnP yoki UDP 41641 portiga ruxsat bering."
        ],
        "homework": "pfSense ni Tailscale 'Exit Node' sifatida sozlang va mobil telefoningizdan internetga kirganingizda, tashqi IP manzilingiz ofis pfSense IP si sifatida ko'rinishiga erishing."
    },
    {
        "day": 16,
        "title": "pfBlockerNG-devel: DNSBL, GeoIP Country Blocking va Threat Feeds",
        "category": "3-Hafta: Kiberxavfsizlik, UTM, QoS va HA",
        "problem": "Korxonada xodimlar reklamalar, fishing havolalari va kriptovalyuta mayning saytlariga aldanib kirmoqda. Shu bilan birga server xavfsizlik devoriga har kuni Xitoy, Rossiya va boshqa xorijiy davlatlardan minglab avtomatlashtirilgan xakerlik skanerlari kelib tushmoqda.",
        "theory_points": [
            "DNS Sinkholing (DNSBL): Zararli domen so'rovini haqiqiy IP ga emas, mahalliy 10.10.10.1 yoki 0.0.0.0 ga yo'naltirib, xavfni paket kompyuterga yetib bormasidanoq to'xtatish.",
            "MaxMind GeoIP arxitekturasi: Dunyodagi barcha IP manzillarni davlatlar va qit'alar bo'yicha bazaga jamlash.",
            "Inbound vs Outbound GeoIP filtrlash: Nega butun dunyodan kiruvchi (Inbound) ulanishlarni bloklab, faqat o'z davlatingizga ruxsat berish server hujumlarini 95% ga kamaytiradi?",
            "Threat Intelligence Feeds: Ochiq kiberxavfsizlik manbalari (FireHOL, Spamhaus, Abuse.ch, AlienVault OTX) bilan avtomatik sinxronizatsiya.",
            "Unbound Python Mode: pfBlockerNG ning Unbound DNS bilan xotirada tezkor integratsiyasi (Tezlik va past RAM sarfi)."
        ],
        "hardware_guide": """* **Hardware:** pfBlockerNG katta hajmdagi IP va domen ro'yxatlarini xotiraga (RAM) yuklaydi. Kamida 4GB RAM tavsiya etiladi.
* MaxMind bepul litsenziya kaliti (License Key) olinishi shart.""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense VM xotirasini (RAM) 4GB ga oshiring.
* System > Advanced > Firewall & NAT bo'limida 'Firewall Maximum Table Entries' ni `1000000` ga ko'taring (katta IP ro'yxatlar sig'ishi uchun).""",
        "lab_steps": [
            "`System` -> `Package Manager` dan `pfBlockerNG-devel` paketini o'rnatish.",
            "O'rnatish ustasi (Setup Wizard) ni ishga tushirish yoki `Firewall` -> `pfBlockerNG` ga kirish.",
            "`IP` bo'limida MaxMind Account ID va License Key ni kiritish.",
            "`GeoIP` yorlig'iga o'tish: `Top Spammers` yoki xorijiy davlatlarni tanlash (masalan CN, RU, IR, KP). Action: `Deny Inbound` (tashqaridan kirishni taqiqlash).",
            "`DNSBL` yorlig'iga o'tish: DNSBL Mode: `Unbound Python Mode` ni yoqish.",
            "`DNSBL Feeds` bo'limida mashhur ro'yxatlarni (StevenBlack Adware/Malware, Adaway, Phishing feeds) qo'shish.",
            "`Update` yorlig'iga o'tib, 'Reload' -> 'All' tugmasini bosish va yangilanish jarayonini (Cron sync) kuzatish."
        ],
        "verification": [
            "Mijoz brauzeridan: reklama ko'p saytlarga (masalan speedtest.net) kirib reklamalar butkul yo'qolganini ko'rish",
            "nslookup doubleclick.net 10.10.10.1 (Javob sifatida 0.0.0.0 yoki DNSBL VIP qaytishini tekshirish)",
            "pfctl -t pfB_Top_v4 -T show | head -n 20 (pf holat jadvalida bloklangan GeoIP larni ko'rish)",
            "Status -> System Logs -> pfBlockerNG (Bloklangan fishing domenlarining jonli hisobotini ko'rish)"
        ],
        "troubleshooting": [
            "Muammo: 'Cannot allocate memory' yoki qoidalar yuklanmadi xatosi. Yechim: System > Advanced > Firewall & NAT > 'Firewall Maximum Table Entries' qiymatini 400000 dan 1000000 yoki 2000000 ga oshiring.",
            "Muammo: Kerakli sayt (masalan xorijiy bank) bloklanib qoldi. Yechim: Firewall > pfBlockerNG > DNSBL > 'DNSBL Whitelist' ga sayt domenini qo'shib, qayta Reload qiling."
        ],
        "homework": "DoIP (Dynamic IP / TLD) tahlilini yoqing va `.top`, `.xyz`, `.click` kabi xakerlar eng ko'p ishlatadigan arzon TLD domen zonalarini to'liq bloklab sinab ko'ring."
    },
    {
        "day": 17,
        "title": "IDS/IPS chuqur tahlili: Suricata Inline Mode (Netmap) vs Legacy Mode",
        "category": "3-Hafta: Kiberxavfsizlik, UTM, QoS va HA",
        "problem": "Firewall portlarni tekshiradi, lekin ochiq 80/443 portlari ichidan kirib kelayotgan SQL Injection, Cross-Site Scripting (XSS), Log4j yoki masofaviy kod bajarish (RCE) kabi chuqur ilova darajasidagi (L7) hujumlarni ko'ra olmaydi. Tarmoqqa aqlli paket analizatori zarur.",
        "theory_points": [
            "IDS (Intrusion Detection System) vs IPS (Intrusion Prevention System): Faqat ogohlantirish (Alert) va real vaqtda paketni yo'q qilish (Drop).",
            "Snort vs Suricata: Suricata ko'p oqimli (Multi-Threaded) zamonaviy arxitekturaga ega bo'lib, ko'p yadroli protsessorlarda 10-40Gbps gacha trafikni qayta ishlay oladi.",
            "Ishlash Rejimlari: Legacy Mode (PCAP orqali paket nusxasini oladi, kechikib bloklaydi) vs Inline Mode (FreeBSD `netmap` drayveri orqali paket tranzitda to'xtatiladi va toza bo'lsagina o'tkaziladi).",
            "Qoidalar To'plami: Emerging Threats (ET) Open, Snort VRT qoidalari, CVE zaifliklar imzolari.",
            "False Positive (Soxta xavf) larni bartaraf etish: `Suppress` ro'yxatini tuzish san'ati."
        ],
        "hardware_guide": """* **Hardware:** Inline Mode faqat `netmap` drayverini qo'llab-quvvatlaydigan tarmoq kartalarida (Intel `igb`, `em`, `ixgbe`, `igc`) ishlaydi.
* Realtek kartalarida Inline mode xato berishi mumkin; Realtek uchun Legacy Mode tavsiya etiladi.""",
        "virtual_guide": """* **Proxmox / VMware:** Proxmox da VirtIO NIC larda netmap barqaror ishlaydi.
* VM ga kamida 4 vCPU va 4GB RAM ajrating.""",
        "lab_steps": [
            "`System` -> `Package Manager` dan `suricata` paketini o'rnatish.",
            "`Services` -> `Suricata` -> `Global Settings`: 'Install ETOpen Rules' katakchasini yoqish, avtomatik yangilanishni kunlik belgilash.",
            "`Updates` yorlig'iga o'tib, 'Update Rules' tugmasini bosish va qoidalarni yuklab olish.",
            "`Interfaces` yorlig'ida 'Add Interface': Interface: `WAN` (yoki DMZ/LAN).",
            "IPS Mode tanlash: `Inline Mode` (agar tarmoq kartasi Intel/VirtIO bo'lsa) yoki `Legacy Mode` (Block Dropped/Host: BOTH).",
            "`WAN Categories` bo'limida muhim qoidalarni yoqish: `emerging-attack_response`, `emerging-exploit`, `emerging-malware`, `emerging-current_events`.",
            "Suricata servisini ishga tushirish (Start)."
        ],
        "verification": [
            "Mijoz kompyuterdan IDS test hujumini simulyatsiya qilish: curl http://testmyids.com",
            "Services -> Suricata -> Interfaces -> WAN Alerts (Tizimda 'GPL ATTACK_RESPONSE id check returned root' xabari paydo bo'lishini ko'rish)",
            "Inline rejimda testmyids.com sahifasi yuklanmasdan darhol uzilib qolishini tekshirish",
            "Suricata logs: tail -f /var/log/suricata/suricata_vtnet0/alerts.log"
        ],
        "troubleshooting": [
            "Muammo: Inline Mode yoqilgach internet butkul to'xtadi. Yechim: Tarmoq kartangiz netmap ni qo'llamaydi. Qaytadan 'Legacy Mode' ga o'ting yoki drayverni tekshiring.",
            "Muammo: Legit dastur (masalan Zoom yoki Torrent) bloklanib qoldi. Yechim: Alerts bo'limida qoidaning GID:SID raqamini topib, yonidagi 'Plus' (Add to suppress list) tugmasini bosing."
        ],
        "homework": "LAN interfeysida Suricata ni yoqib, ichki tarmoqdan nmap port skanerlash hujumi (`nmap -sS -A 10.10.10.1`) uyushtirilganda Suricata qanday ogohlantirish berishini tahlil qiling."
    },
    {
        "day": 18,
        "title": "Traffic Shaping va QoS: FQ-CoDel, Limiter va Bufferbloat Eradication",
        "category": "3-Hafta: Kiberxavfsizlik, UTM, QoS va HA",
        "problem": "Ofisda kimdir katta torrent fayl yoki Windows yangilanishini tortishni boshlasa, boshqa xodimlarning Zoom va Google Meet qo'ng'iroqlari qotib qolmoqda, ovoz uzilib, ping 20ms dan 800ms ga sakrab ketmoqda (Bufferbloat falokati).",
        "theory_points": [
            "Bufferbloat muammosi nima? Router va modemlardagi ortiqcha bufer xotirasi paketlarni navbatda ushlab turishi va kechikishni (latency/jitter) keskin oshirishi.",
            "AQM (Active Queue Management): Eskirgan DropTail o'rniga paket navbatlarini aqlli boshqarish.",
            "FQ-CoDel (Fair Queueing Controlled Delay - RFC 8290): Trafikni yuzlab kichik oqimlarga bo'lib, har bir oqimga adolatli navbat berish va kechikayotgan paketlarni boshqarish.",
            "CAKE (Common Applications Kept Enhanced) algoritmi haqida tushuncha.",
            "pfSense `dummynet` Limiterlari: Inbound va Outbound o'tkazuvchanlikni provayderning haqiqiy tezligidan 5-10% pastroq qilib chegaralash orqali bufer to'lishining oldini olish."
        ],
        "hardware_guide": """* **Hardware:** Dummynet limiterlari FreeBSD yadrosida ishlaydi va protsessorga deyarli yuklama bermaydi.
* Provayder bilan tuzilgan shartnomadagi aniq tezlikni (masalan 100 Mbps Download, 50 Mbps Upload) bilish zarur.""",
        "virtual_guide": """* **Proxmox / VMware:** Virtual muhitda ham FQ-CoDel to'liq ishlaydi.
* Test qilish uchun internet tezligini sun'iy ravishda cheklab ko'rish juda qulay.""",
        "lab_steps": [
            "`Firewall` -> `Traffic Shaper` -> `Limiters` yorlig'iga o'tish.",
            "1-Limiter yaratish (Yuklab olish): Name: `Inbound_Limit`, Bandwidth: `95 Mbit/s` (100Mbit kanal uchun 95%). AQM: `FQ_CODEL`.",
            "Uning ostida yangi Queue qo'shish: Name: `Inbound_Queue`, AQM: `FQ_CODEL`.",
            "2-Limiter yaratish (Yuklash): Name: `Outbound_Limit`, Bandwidth: `45 Mbit/s` (50Mbit kanal uchun 45%). AQM: `FQ_CODEL`.",
            "Uning ostida Queue qo'shish: Name: `Outbound_Queue`, AQM: `FQ_CODEL`.",
            "`Firewall` -> `Rules` -> `LAN`: Default Internetga ruxsat qoidasini tahrirlash -> `Advanced Options` -> `In / Out pipe` bo'limida: Out: `Inbound_Queue`, In: `Outbound_Queue` ni tanlash."
        ],
        "verification": [
            "Waveform Bufferbloat Test (waveform.com/tools/bufferbloat) saytiga kirib test o'tkazish (Natija 'A' yoki 'A+' chiqishi kerak)",
            "Katta fayl yuklanayotgan paytda boshqa terminaldan: ping 8.8.8.8 (Kechikish 5-10ms dan oshmasligini ko'rish)",
            "ipfw pipe show (FreeBSD konsolida FQ-CoDel oqimlari va dinamik navbatlarni kuzatish)",
            "Speedtest o'tkazib tezlik qat'iy belgilangan chegarada ushlab turilganini tasdiqlash"
        ],
        "troubleshooting": [
            "Muammo: Bufferbloat bahosi hali ham 'C' yoki 'D'. Yechim: Limiter tezligini yana 5% ga tushiring; agar provayderingiz 100Mbps va'da qilib, amalda 80Mbps bersa, limiter 75Mbps ga qo'yilishi shart.",
            "Muammo: In / Out pipe teskari ulanib qoldi. Yechim: pfSense da 'In' bu mijozdan routerga (Upload), 'Out' esa routerdan mijozga (Download) ekanini unutmang."
        ],
        "homework": "Mehmonlar tarmog'i (GUEST VLAN) uchun maxsus Limiter yarating va ularning har biriga individual 5 Mbps tezlik limiti ajrating (har bir IP alohida oqim bo'lsin: Mask: Source Address)."
    },
    {
        "day": 19,
        "title": "High Availability (CARP) Klasteri — 1-Qism: L2 Sync, Promiscuous Mode va Virtual IPs",
        "category": "3-Hafta: Kiberxavfsizlik, UTM, QoS va HA",
        "problem": "Kompaniya 24/7 ishlaydi. Agar yagona pfSense serverining quvvat bloki kuysa yoki operativ xotirasi ishdan chiqsa, butun ofis va zavod tarmog'i soatlab to'xtab qoladi (Single Point of Failure). Biznesga ikkita parallel ishlovchi klaster zarur.",
        "theory_points": [
            "CARP (Common Address Redundancy Protocol - RFC 5798): Cisco HSRP va VRRP ning ochiq kodli patenti cheklanmagan alternativi.",
            "Virtual IP (VIP) mexanizmi: Ikkita jismoniy router (Master va Backup) bitta umumiy 'ko'rinmas' virtual shlyuz IP manzilini (masalan `10.10.10.1`) boshqarishi.",
            "VHID (Virtual Host ID) va `advskew` (reklama kechikishi): Master router tez-tez e'lon yuboradi (`advskew 0`), Backup esa kutib turadi (`advskew 100`).",
            "Promiscuous Mode va MAC Address Spoofing: Virtualizatsiya va zamonaviy switchlar begona MAC manzilini (Virtual CARP MAC: `00:00:5e:00:01:XX`) ko'rganda bloklab qo'ymasligi uchun zarur sozlamalar.",
            "Dedicated PFSYNC L2 Channel: Ikkita firewall o'rtasida to'g'ridan-to'g'ri ulangan alohida ajratilgan xavfsiz tarmoq kabeli."
        ],
        "hardware_guide": """* **Hardware:** 2 ta bir xil yoki o'xshash x86 mini-PC server.
* Har bir serverda kamida 3 ta port bo'lishi shart: WAN, LAN va SYNC (PFSYNC).
* Ikkala serverning SYNC portlari o'zaro to'g'ridan-to'g'ri patch-cord (crossover yoki zamonaviy auto-MDIX) orqali ulanadi.""",
        "virtual_guide": """* **Proxmox VE:**
  * Proxmox Linux Bridge da standart holatda MAC spoofing cheklanmagan, lekin Proxmox Firewall o'chirilgan bo'lishi shart.
* **VMware Workstation / ESXi:**
  * Virtual Switch sozlamalarida: `Promiscuous Mode: Accept`, `MAC Address Changes: Accept`, `Forged Transmits: Accept` qilib qo'yish MAJBURIY!""",
        "lab_steps": [
            "Ikkita VM/Server tayyorlash: `FW-01` (Master) va `FW-02` (Backup).",
            "IP Rejasi (LAN): FW-01 Real IP: `10.10.10.2`, FW-02 Real IP: `10.10.10.3`, CARP VIP: `10.10.10.1`.",
            "IP Rejasi (SYNC): FW-01 SYNC: `192.168.99.1/24`, FW-02 SYNC: `192.168.99.2/24`.",
            "`Firewall` -> `Virtual IPs` (FW-01 da): 'Add' -> Type: `CARP`, Interface: `LAN`, Address: `10.10.10.1/24`, VHID: `1`, Password: `SecretCarpPassword`, Advskew: `0`.",
            "FW-02 da xuddi shu VIP ni yaratish, faqat Advskew: `100` deb belgilash.",
            "`Firewall` -> `Rules` -> `SYNC` interfeysida barcha trafikka ruxsat berish (yoki faqat carp va pfsync protokollariga)."
        ],
        "verification": [
            "Status -> CARP (FW-01 da interfeys 'MASTER', FW-02 da esa 'BACKUP' holatida turganini ko'rish)",
            "ifconfig carp0 (Konsolda vhid 1 advskew 0 holatini ko'rish)",
            "Mijoz kompyuteridan ping 10.10.10.1 (CARP Virtual shlyuziga uzluksiz ping borishini tekshirish)",
            "arp -a (Mijozda 10.10.10.1 ning MAC manzili 00:00:5e:00:01:01 ekanini tasdiqlash)"
        ],
        "troubleshooting": [
            "Muammo: Ikkala router ham o'zini 'MASTER' deb e'lon qilmoqda (Split-Brain holati). Yechim: L2 broadcast/multicast (IP Protocol 112 CARP) paketlari ikkinchi routerga yetib bormayapti. VMware da Promiscuous Mode yoqilganini, switchda esa port izolyatsiyasi yo'qligini tekshiring.",
            "Muammo: CARP status 'DISABLED'. Yechim: Konsolda `sysctl net.inet.carp.allow=1` ekanini tekshiring."
        ],
        "homework": "WAN interfeysi uchun ham tashqi Public IP lar asosida CARP VIP (masalan FW1: .2, FW2: .3, CARP VIP: .1) ni sozlang va ikkala interfeys parallel failover bo'lishini tekshiring."
    },
    {
        "day": 20,
        "title": "High Availability (CARP) — 2-Qism: pfsync va XML-RPC Zero-Downtime Failover",
        "category": "3-Hafta: Kiberxavfsizlik, UTM, QoS va HA",
        "problem": "Routerlar almashganda tarmoqdagi barcha aktiv ulanishlar (Zoom qo'ng'iroqlari, yuklab olinayotgan katta fayllar, SSH sessiyalar) uzilib ketmoqda, chunki zaxira routerda 'State Table' (ochiq sessiyalar xotirasi) mavjud emas. Shuningdek, qoidalarni ikkala routerga ikki marta qo'lda yozish charchatmoqda.",
        "theory_points": [
            "`pfsync` (Packet Filter State Synchronization Protocol): FreeBSD yadrosi darajasida har bir ochilgan TCP/UDP sessiyani real vaqtda L2 orqali ikkinchi routerga replikatsiya qilish.",
            "XML-RPC Config Synchronization: Master routerda o'zgartirilgan har qanday firewall qoidasi, alias yoki foydalanuvchi bir soniyada zaxira routerga shifrlangan tarzda ko'chirilishi.",
            "Zero-Downtime Failover tushunchasi: Master server elektrdan uzilsa ham, birorta paket yo'qolmasdan zaxiraga o'tish mexanizmi.",
            "Preemption rejimi: Asosiy router qayta yoqilganda boshqaruvni darhol o'ziga qaytarib olishi (`net.inet.carp.preempt`)."
        ],
        "hardware_guide": """* **Hardware:** Ikkala serverning xususiyatlari, interfeys nomlari (`igb0`, `igb1`, `igb2`) mutlaqo bir xil bo'lishi tavsiya etiladi.
* Agar interfeys nomlari har xil bo'lsa (masalan birida `igb0`, ikkinchisida `re0`), XML-RPC interfeys sinxronizatsiyasida muammo chiqishi mumkin.""",
        "virtual_guide": """* **Proxmox / VMware:** Ikkala VM ga bir xil tarmoq adapterlari (masalan ikkalasida ham `vtnet0-2` yoki `vmx0-2`) biriktirilgan bo'lishi shart.""",
        "lab_steps": [
            "FW-01 (Master) da: `System` -> `High Avail. Sync` bo'limiga kirish.",
            "`State Synchronization Settings (pfsync)`: 'Synchronize States' katakchasini yoqish, Synchronize Interface: `SYNC`, Remote Backup IP: `192.168.99.2`.",
            "`XMLRPC Sync`: 'Synchronize Config to IP': `192.168.99.2`, Remote System Username: `admin`, Remote Password: (FW-02 paroli).",
            "Sinxronlanadigan bandlarni tanlash: Firewall Rules, Aliases, NAT, Virtual IPs, DHCP Server va boshqalar.",
            "FW-02 (Backup) da: Faqat pfsync ni yoqish (Synchronize Interface: `SYNC`, Remote IP: `192.168.99.1`), lekin XMLRPC Sync ni BO'SH qoldirish (zaxira asosiyga yozmasligi uchun).",
            "FW-01 da yangi sinov Firewall Alias yaratish va FW-02 ga o'tib, u avtomatik ko'chib o'tganini tekshirish."
        ],
        "verification": [
            "pfSense konsolida: pfctl -ss (Ikkala routerda ham sessiyalar soni va ro'yxati 100% bir xilligini ko'rish)",
            "Mijozdan uzluksiz ping yoki SSH ulanishini yoqib qo'yish: ping -t 10.10.10.1",
            "FW-01 (Master) serverini 'Power Off' qilish (elektrini o'chirish)",
            "FW-02 darhol MASTER ga aylanib, bitta ham ping yo'qolmasdan (0 soniya downtime) aloqa davom etayotganini kuzatish",
            "SSH yoki Zoom sessiyasi uzilmasdan saqlanib qolganini tasdiqlash"
        ],
        "troubleshooting": [
            "Muammo: XML-RPC 'Authentication failed' xatosi. Yechim: Ikkala routerda ham admin paroli to'g'ri kiritilganini va SYNC interfeysida HTTPS (port 443/8443) ruxsat berilganini tekshiring.",
            "Muammo: Sessiyalar sinxron emas. Yechim: `pfsync` interfeysi sifatida xato interfeys (masalan LAN) tanlanmaganini tasdiqlang."
        ],
        "homework": "Master server qayta yoqilganda (Power On) CARP boshqaruvini qanday qilib muammosiz qaytarib olishini tekshiring va jarayonni Wireshark da CARP e'lonlari orqali yozib oling."
    },
    {
        "day": 21,
        "title": "HAProxy Reverse Proxy: SSL Offloading, Load Balancing va Health Checks",
        "category": "3-Hafta: Kiberxavfsizlik, UTM, QoS va HA",
        "problem": "Korxonada 3 ta bir xil web-server (Backend) mavjud. Har biriga alohida tashqi IP berishning imkoni yo'q. Agar serverlardan biri qulab tushsa, mijozlarga xatolik bormasdan, yuklama qolgan ikkita ishchi serverga avtomatik taqsimlanishi kerak.",
        "theory_points": [
            "Reverse Proxy nima? Mijozlar va serverlar o'rtasida turib, so'rovlarni qabul qiluvchi va ichki serverlarga aqlli yo'naltiruvchi shlyuz.",
            "HAProxy (High Availability Proxy) unumdorligi: Voqealarga asoslangan (Event-driven) asinxron arxitektura, millionlab so'rovlarni minimal CPU bilan yechish.",
            "Load Balancing Algoritmlari: Round Robin (navbatma-navbat), Least Connections (eng kam yuklanganiga), Source IP Hash (bitta mijoz bitta serverga bog'lanishi).",
            "SSL/TLS Offloading (Termination): Og'ir shifrlash/yechish jarayonini HAProxy o'z bo'yniga oladi, ichki serverlar esa yengil HTTP da ishlab resurs tejaydi.",
            "Health Checking (Salomatlik tekshiruvi): Har 2 soniyada backend serverga HTTP GET so'rov yuborish; agar 200 OK qaytmasa, uni rotatsiyadan darhol chiqarib tashlash."
        ],
        "hardware_guide": """* **Hardware:** HAProxy ko'p tarmoqli yuqori yuklamalarda RAM va tezkor CPU talab qiladi.
* Tashqi WAN da 80 (HTTP) va 443 (HTTPS) portlari boshqa xizmatlar (masalan pfSense WebGUI) tomonidan band qilinmagan bo'lishi shart!""",
        "virtual_guide": """* **Proxmox / VMware:** DMZ segmentida (`10.10.20.0/24`) 2 ta yoki 3 ta yengil Nginx/Apache VM yoki Docker konteyner ko'taring.""",
        "lab_steps": [
            "pfSense WebGUI portini `8443` ga o'tkazilganligini tasdiqlash (80 va 443 HAProxy uchun bo'sh bo'lishi kerak).",
            "`System` -> `Package Manager` dan `haproxy` paketini o'rnatish.",
            "`Services` -> `HAProxy` -> `Settings`: 'Enable HAProxy' ni yoqish.",
            "`Backend` yorlig'iga o'tish: Name: `Web_Cluster_Backend`, Balance: `roundrobin`, Health check: `HTTP`.",
            "Serverlar ro'yxatiga qo'shish: `SRV01` (10.10.20.11:80), `SRV02` (10.10.20.12:80).",
            "`Frontend` yorlig'iga o'tish: Name: `HTTPS_Frontend`, Listen IP: `WAN address`, Port: `443`, Type: `SSL / HTTPS (offloading)`. Default backend: `Web_Cluster_Backend`.",
            "`Firewall` -> `Rules` -> `WAN`: Port 443 ga ruxsat berish."
        ],
        "verification": [
            "Status -> HAProxy (Stats sahifasida ikkala backend server ham yashil 'UP' holatdaligini ko'rish)",
            "Brauzerdan yoki terminaldan: curl -k https://<WAN_IP> (Bir necha marta yuborilganda javob SRV01 va SRV02 dan navbatma-navbat kelishini ko'rish)",
            "SRV01 serverida Nginx xizmatini to'xtatish (`systemctl stop nginx`)",
            "2 soniyadan so'ng HAProxy Stats da SRV01 qizil 'DOWN' bo'lib, barcha so'rovlar hech qanday uzilishsiz SRV02 ga o'tib ketganini tekshirish"
        ],
        "troubleshooting": [
            "Muammo: HAProxy xizmati ishga tushmayapti (Status da qizil). Yechim: 80 yoki 443 portini pfSense WebGUI band qilib turgan bo'lishi mumkin. System > Advanced bo'limida WebGUI portini o'zgartiring.",
            "Muammo: Backend serverlar 'SOCKERR' yoki 'L4CON' xatosi bermoqda. Yechim: pfSense dan DMZ serverlariga ping va TCP port 80 aloqasi borligini Diagnostics > Ping orqali tekshiring."
        ],
        "homework": "HAProxy da Cookie-based Session Stickiness (Insert Cookie) sozlang va bitta foydalanuvchi brauzeri doim birinchi tushgan backend serverga bog'lanib qolishini ta'minlang."
    },
    {
        "day": 22,
        "title": "ACME (Let's Encrypt) Avtomatizatsiyasi va Cloudflare DNS API",
        "category": "3-Hafta: Kiberxavfsizlik, UTM, QoS va HA",
        "problem": "Kompaniyada o'nlab web-saytlar va VPN portallari mavjud. Har 3 oyda muddati tugaydigan bepul Let's Encrypt SSL sertifikatlarini qo'lda yangilash unutilib qolmoqda, natijada foydalanuvchilar brauzerida xavfli 'Xavfsiz emas' qizil ogohlantirishi chiqib biznes obro'siga putur yetmoqda.",
        "theory_points": [
            "ACME (Automated Certificate Management Environment - RFC 8555) protokoli.",
            "Domain Validation turlari: HTTP-01 (Port 80 ochiq bo'lishi shart) vs DNS-01 Challenge (Domen DNS provayderiga maxsus `_acme-challenge` TXT yozuvi qo'shish).",
            "Nega DNS-01 Challenge eng xavfsiz va qulay? Hech qanday tashqi portni (80) ochish talab qilinmaydi va Wildcard sertifikatlar (`*.firma.uz`) faqat DNS-01 orqali beriladi.",
            "Cloudflare API Tokens: Cheklangan huquqli (faqat DNS:Edit) xavfsiz API kalitlaridan foydalanish.",
            "Sertifikatlarni avtomatik qayta biriktirish: Yangilangan sertifikatni WebGUI va HAProxy ga avtomat reload qilish skripti."
        ],
        "hardware_guide": """* **Hardware:** pfSense internetga ulangan bo'lishi va Cloudflare API ga murojaat qila olishi kerak.
* Haqiqiy domen nomi va uning DNS lari Cloudflare ga ulangan bo'lishi shart.""",
        "virtual_guide": """* **Proxmox / VMware:** Virtual laboratoriyada ham o'zingizning shaxsiy domeningiz orqali haqiqiy jahon tan olgan SSL sertifikatini chiqarishingiz mumkin.""",
        "lab_steps": [
            "`System` -> `Package Manager` dan `acme` paketini o'rnatish.",
            "`Services` -> `Acme` -> `Account keys` ga kirish. 'Add' tugmasini bosib, nom berish (masalan `LetsEncrypt_Prod`), e-mail kiritish, ACME Server: `Let's Encrypt Production` tanlash va 'Create new account key' bosish.",
            "'Register ACME account key' tugmasini bosib, hisobni ro'yxatdan o'tkazish.",
            "`Certificates` yorlig'iga o'tib, 'Add' tugmasini bosish. Name: `Wildcard_Corp_Cert`.",
            "Domain SAN list: Domain name: `*.firma.uz`, Challenge-Type: `DNS-Cloudflare`.",
            "Cloudflare API Token maydoniga Cloudflare boshqaruv panelidan olingan 'Zone:DNS:Edit' tokenini kiritish.",
            "'Issue/Renew' tugmasini bosib, 60 soniya ichida Let's Encrypt dan Wildcard SSL sertifikatini avtomat olish.",
            "`System` -> `Advanced` -> `Admin Access` ga kirib, WebGUI SSL sertifikati sifatida yangi olingan Wildcard sertifikatini tanlash."
        ],
        "verification": [
            "pfSense WebGUI ga domeningiz orqali kirish (https://fw.firma.uz:8443) va brauzerda yashil qulf belgisini ko'rish",
            "openssl s_client -connect 10.10.10.1:8443 (Sertifikat zanjiri va muddati 90 kun ekanini tasdiqlash)",
            "System -> Cert. Manager da yangi Let's Encrypt sertifikati paydo bo'lganini ko'rish",
            "Cron ro'yxatida har 24 soatda sertifikat yangilanishini tekshiruvchi avtomat vazifa paydo bo'lganini tasdiqlash"
        ],
        "troubleshooting": [
            "Muammo: 'Cloudflare API error: Invalid token'. Yechim: Cloudflare da yaratilgan tokenda 'Zone - DNS - Edit' huquqi aynan shu domenga berilganini tekshiring.",
            "Muammo: DNS-01 challenge vaqti tugadi (Timeout). Yechim: ACME sozlamalarida 'DNS Sleep' vaqtini 120 soniyaga oshiring (DNS yangilanishi tarqalishi uchun)."
        ],
        "homework": "HAProxy frontendiga ushbu Wildcard sertifikatini biriktiring va ichki web-serverlaringizga tashqaridan HTTPS orqali xavfsiz kirishni ta'minlang."
    },
    {
        "day": 23,
        "title": "Squid Proxy, Kesh Arxitekturasi va ClamAV Antivirus Filtratsiyasi",
        "category": "3-Hafta: Kiberxavfsizlik, UTM, QoS va HA",
        "problem": "Xodimlar internetdan turli xil dasturlar, drayverlar va arxivlar yuklab olmoqda. Ularning orasida troyan va zararli viruslar bo'lishi ehtimoli yuqori. Korxona tarmog'iga kirayotgan har bir yuklamani oqimda (on-the-fly) viruslarga tekshirish zarur.",
        "theory_points": [
            "Forward Proxy ishlash printsipi: Ichki mijozlarning internetga chiqishini markazlashtirish.",
            "Transparent Proxy vs Explicit Proxy: Mijoz brauzerida sozlamalar kiritish talabi va port 80/443 ni avtomat ushlab qolish.",
            "SSL/TLS Man-in-the-Middle (MITM) Filtering: Shifrlangan HTTPS trafigini ochib tekshirish muammolari, CA Root sertifikatini mijozlarga tarqatish va zamonaviy TLS 1.3/ECH cheklovlari.",
            "ClamAV integratsiyasi: Ochiq kodli antivirus bazasi, arxivlarni (.zip, .rar, .exe) ichini ochib skanerlash.",
            "Kesh (Caching) afzalliklari va cheklovlari: Trafikni tejash va zamonaviy dinamik vebda keshning o'rni."
        ],
        "hardware_guide": """* **Hardware:** ClamAV antivirus bazasi xotiraga (RAM) yuklanadi va kamida 2-3GB bo'sh RAM talab qiladi.
* Kesh uchun tezkor SSD disk tavsiya etiladi.""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense VM xotirasini kamida 6GB ga oshiring.""",
        "lab_steps": [
            "`System` -> `Package Manager` dan `squid` paketini o'rnatish.",
            "`Services` -> `Squid Proxy Server` -> `Local Cache` ga kirib, kesh hajmini (masalan 2048 MB) belgilash.",
            "`Antivirus` yorlig'iga o'tib, 'Enable ClamAV' katakchasini yoqish va antivirus bazasini yangilash.",
            "`General` yorlig'ida: Proxy Interface: `LAN`, TCP Port: `3128`. 'Allow Users on Interface' katakchasini yoqish.",
            "Mijoz kompyuterida brauzer sozlamalariga kirib, Proxy Server: `10.10.10.1`, Port: `3128` deb belgilash.",
            "EICAR rasmiy sinov virus faylini yuklab olishga urinib ko'rish: `http://www.eicar.org/download/eicar.com`.",
            "Squid va ClamAV virusni oqimda to'xtatib, brauzerda maxsus 'Virus Aniqlanganligi sababli yuklab olish taqiqlandi' sahifasini ko'rsatishi."
        ],
        "verification": [
            "tail -f /var/log/squid/access.log (pfSense konsolida mijoz so'rovlarining keshdan yoki to'g'ridan-to'g'ri o'tayotganini ko'rish)",
            "curl -x http://10.10.10.1:3128 http://www.eicar.org/download/eicar.com (Antivirus bloklash sahifasi qaytishini ko'rish)",
            "Status -> Services (Squid va ClamAV xizmatlari yashil 'Running' ekanini tekshirish)",
            "freshclam loglarini ko'rish (/var/log/clamav/freshclam.log)"
        ],
        "troubleshooting": [
            "Muammo: ClamAV yuklanayotganda pfSense qotib qoldi yoki xotira yetmadi. Yechim: pfSense VM RAM hajmini 6GB ga ko'taring, ClamAV antivirus bazasi xotirada 1.5GB joy oladi.",
            "Muammo: HTTPS saytlar ochilmayapti. Yechim: HTTPS uchun SSL Filtering yoqilgan bo'lsa, pfSense ichki CA sertifikati mijoz qurilmasiga o'rnatilishi shart."
        ],
        "homework": "SquidGuard kengaytmasini o'rnating va xodimlar uchun ijtimoiy tarmoqlar (Facebook, TikTok) domenlarini ish vaqtida cheklovchi URL filtering qoidasini yarating."
    },
    {
        "day": 24,
        "title": "Centralized Logging: Syslog Export va Graylog / ELK Arxitekturasi",
        "category": "4-Hafta: Monitoring, Hardening va Real Cloud Deploy",
        "problem": "Xavfsizlik hodisasi yoki kiberhujum sodir bo'lganda, pfSense ning ichki loglari aylanib (log rotation) o'chib ketmoqda. Xavfsizlik bo'limi 1 oy oldin kim qaysi IP ga ulanganini yoki qaysi qoida buzilganini tekshira olmayapti.",
        "theory_points": [
            "Syslog Standarti (RFC 5424): UDP/TCP 514 portlarida log xabarlarini uzatish, Severity darajalari (Emergency dan Debug gacha).",
            "pfSense `filterlog` formati: Vergul bilan ajratilgan murakkab qatorlar (Rule number, Sub-rule, Interface, Reason, Action, Direction, IP Version, TTL, Source IP, Destination IP, Portlar).",
            "SIEM (Security Information and Event Management) integratsiyasi: Graylog, ELK (Elasticsearch, Logstash, Kibana) va Grafana Loki.",
            "Loglarni tahlil qilish (Parsing): Grok patterns orqali filterlog xom qatorlarini qidirishga qulay JSON maydonlariga ajratish."
        ],
        "hardware_guide": """* **Hardware:** pfSense loglarni ichki SSD ga ko'p yozmasligi (SSD resursini tejash) uchun tashqi Syslog serverga oqizish eng to'g'ri yechimdir.""",
        "virtual_guide": """* **Proxmox / VMware:** Alohida Ubuntu VM da Graylog yoki oddiy Rsyslog server o'rnatiladi.""",
        "lab_steps": [
            "Tarmoqda markaziy Syslog server (Ubuntu: IP `10.10.20.100`, Port: UDP 514) tayyorlash.",
            "`Status` -> `System Logs` -> `Settings` yorlig'iga o'tish.",
            "`Remote Logging Options` bo'limida: 'Send log messages to remote syslog server' katakchasini yoqish.",
            "Remote log servers: `10.10.20.100:514` deb kiritish.",
            "Qaysi loglarni yuborishni tanlash: `Firewall Events`, `DNS Events`, `DHCP Events`, `VPN Events`.",
            "Syslog serverda (Ubuntu da) `rsyslog` yoki `graylog` qabul qiluvchi sozlamasini tekshirish.",
            "pfSense firewall da biror portni bloklash va bir soniyada Syslog server konsolida bloklangan paket logi paydo bo'lishini ko'rish."
        ],
        "verification": [
            "tcpdump -i vtnet1 -n udp port 514 (LAN interfeysida pfSense Syslog paketlarini yuborayotganini tekshirish)",
            "Syslog serverda: tail -f /var/log/pfsense.log yoki Graylog WebGUI da jonli xabarlar oqimini ko'rish",
            "Bloklangan paketlar: filterlog qatorida 'block,in,4,...' formatida ma'lumotlar to'g'ri kelayotganini tasdiqlash",
            "Qidiruv: Graylog panelida 'action:block AND dst_port:22' deb qidirib xakerlik urinishlarini topish"
        ],
        "troubleshooting": [
            "Muammo: Syslog serverga loglar bormayapti. Yechim: Syslog serverdagi UFW yoki Linux firewall da UDP 514 porti ochilganini tekshiring.",
            "Muammo: Loglar formati tushunarsiz bir qator bo'lib tushyapti. Yechim: Graylog/Logstash da pfSense filterlog uchun maxsus Grok Pattern dan foydalaning."
        ],
        "homework": "Grafana Loki yoki Graylog da maxsus Dashboard yarating va kun davomida eng ko'p bloklangan TOP-5 IP manzillar statistikasini grafikda ko'rsating."
    },
    {
        "day": 25,
        "title": "Telemetriya va Monitoring: Telegraf + InfluxDB + Grafana NOC Dashboard",
        "category": "4-Hafta: Monitoring, Hardening va Real Cloud Deploy",
        "problem": "Tarmoq ma'murlari tarmoq kartalari qanchalik yuklanayotganini, qaysi interfeysda paketlar yo'qolayotganini (drops), CPU harorati va xotira holatini real vaqtda ko'rib turuvchi qulay va chiroyli vizual monitoring paneliga ega emas.",
        "theory_points": [
            "TICK / TIG Stack arxitekturasi: Telegraf (metrika yig'uvchi agent), InfluxDB (Time-Series ma'lumotlar bazasi), Grafana (vizualizatsiya).",
            "FreeBSD metrikalari: CPU yuklamasi, load average, ZFS ARC xotirasi, interfeyslar o'tkazuvchanligi (octets/sec), xatolar soni.",
            "SNMP vs Telegraf: Nega Telegraf push-modeli an'anaviy SNMP pull-modelidan yengilroq va aniqroq ma'lumot beradi?",
            "NOC (Network Operations Center) Dark Mode Dashboard yaratish tamoyillari."
        ],
        "hardware_guide": """* **Hardware:** Mini-PC apparat harorati drayverlarini (`coretemp` yoki `amdtemp`) yoqish orqali protsessor temperaturasini Grafana ga chiqarish mumkin.""",
        "virtual_guide": """* **Proxmox / VMware:** pfSense ichida Telegraf paketi ishlaydi, InfluxDB va Grafana esa alohida Docker konteynerda ko'tariladi.""",
        "lab_steps": [
            "Monitoring serverida Docker orqali InfluxDB (Port 8086) va Grafana (Port 3000) ni ishga tushirish.",
            "pfSense da: `System` -> `Package Manager` dan `telegraf` paketini o'rnatish.",
            "`Services` -> `Telegraf` sozlamalariga kirish. 'Enable Telegraf' ni yoqish.",
            "Telegraf Output: `InfluxDB (v1 yoki v2)`, InfluxDB Server: `http://10.10.20.100:8086`, Database: `pfsense_metrics`.",
            "Monitoring qilinadigan parametrlarni belgilash: CPU, Memory, System, Net (Interfeyslar), Pf (Packet filter states).",
            "Grafana ga kirish (http://10.10.20.100:3000), InfluxDB ma'lumotlar manzilini (Data Source) ulash.",
            "Rasmiy pfSense Dashboard (Dashboard ID: `14449` yoki `10967`) shablonini import qilish."
        ],
        "verification": [
            "Status -> Services (Telegraf xizmati aktiv 'Running' holatdaligini ko'rish)",
            "Grafana panelida real vaqtda LAN va WAN trafigi grafiklari jonli o'sayotganini ko'rish",
            "pfSense da katta fayl yuklab, Grafana grafikasida WAN interfeysi o'tkazuvchanligi aniq mos kelishini tekshirish",
            "CPU va ZFS xotirasi taqsimotini vizual kuzatish"
        ],
        "troubleshooting": [
            "Muammo: Telegraf InfluxDB ga bog'lana olmayapti (Connection refused). Yechim: InfluxDB porti 8086 ochiqligini va pfSense DMZ/LAN firewall qoidasida ushbu portga ruxsat borligini tekshiring.",
            "Muammo: Interfeys nomlari ko'rinmayapti. Yechim: Telegraf sozlamalarida 'Interface list' maydonini bo'sh qoldiring (barcha interfeyslarni avtomat olishi uchun)."
        ],
        "homework": "Grafana da 'Alerting' qoidasi tuzing: Agar WAN trafigi 80 Mbps dan oshsa yoki CPU 90% ga yetsa, Telegram guruhiga avtomat xabar jo'natishni sozlang."
    },
    {
        "day": 26,
        "title": "Korxona Autentifikatsiyasi: Active Directory / LDAP va RADIUS Integratsiyasi",
        "category": "4-Hafta: Monitoring, Hardening va Real Cloud Deploy",
        "problem": "Korxonada 200 nafar xodim ishlaydi. Yangi xodim kelganda yoki ishdan ketganda uning parollarini pfSense, OpenVPN va WebGUI da qo'lda yaratish/o'chirish xavfsizlik xatolariga olib kelmoqda. Barcha autentifikatsiya markaziy Windows Server AD ga bog'lanishi shart.",
        "theory_points": [
            "Markazlashgan Identity Management: LDAP (Lightweight Directory Access Protocol) va Microsoft Active Directory arxitekturasi.",
            "LDAPS (Secure LDAP over TLS - Port 636) zarurati: Parollarni tarmoq bo'ylab shifrlangan uzatish.",
            "RADIUS (Remote Authentication Dial-In User Service): Tarmoq uskunalariga kirishni boshqarish (Network Policy Server - NPS).",
            "Role-Based Access Control (RBAC): AD guruhlari (`NetAdmins`, `VPNUsers`) orqali pfSense WebGUI va VPN huquqlarini avtomat berish."
        ],
        "hardware_guide": """* **Hardware:** pfSense LAN porti orqali ichki korporativ domen kontrolleriga (Domain Controller) to'g'ridan-to'g'ri aloqaga ega bo'lishi lozim.""",
        "virtual_guide": """* **Proxmox / VMware:** Laboratoriyada Windows Server 2022 (AD DS) VM ko'tariladi.""",
        "lab_steps": [
            "`System` -> `User Manager` -> `Authentication Servers` yorlig'iga o'tish.",
            "'Add' tugmasini bosish: Descriptive name: `Corp_Active_Directory`, Type: `LDAP`.",
            "Hostname or IP: `10.10.20.10` (AD Domain Controller), Port: `389` (yoki 636 LDAPS), Transport: `TCP - Standard`.",
            "Base DN: `DC=corp,DC=local`, Authentication containers: `CN=Users,DC=corp,DC=local`.",
            "Bind credentials: User DN: `CN=ldap_bind,CN=Users,DC=corp,DC=local`, Bind Password: (parol).",
            "`Diagnostics` -> `Authentication` ga kirib, AD dagi biror korporativ foydalanuvchi logini va parolini kiritib tekshirish ('Authentication Successful' chiqishi kerak).",
            "`System` -> `User Manager` -> `Groups` bo'limida AD guruh nomi bilan bir xil bo'lgan `pfAdmins` guruhini yaratish va unga WebGUI Superuser huquqlarini berish."
        ],
        "verification": [
            "Diagnostics -> Authentication (AD foydalanuvchisi va uning a'zo bo'lgan barcha guruhlari to'g'ri qaytayotganini ko'rish)",
            "pfSense WebGUI dan chiqib (Logout), Active Directory dagi login/parol bilan kirish",
            "OpenVPN server autentifikatsiyasini AD/LDAP ga o'tkazish va VPN ga domen paroli bilan ulanishni tekshirish",
            "Windows AD da foydalanuvchini bloklab qo'yganda, u pfSense va VPN ga kira olmay qolishini tasdiqlash"
        ],
        "troubleshooting": [
            "Muammo: 'Could not connect to LDAP server'. Yechim: pfSense dan Domain Controller ga ping va TCP 389/636 port aloqasini tekshiring.",
            "Muammo: Autentifikatsiya o'tdi, lekin WebGUI ga kirganda 'No page assigned' xatosi. Yechim: AD foydalanuvchisi a'zo bo'lgan guruh pfSense Groups bo'limida yaratilmagan yoki huquqlari belgilanmagan."
        ],
        "homework": "FreeRADIUS paketini pfSense ga o'rnating va 802.1X korporativ Wi-Fi xavfsizligi uchun RADIUS autentifikatsiyasini sinovdan o'tkazing."
    },
    {
        "day": 27,
        "title": "Avtomatlashtirish, AutoConfigBackup (ACB) va 5-Daqiqalik Disaster Recovery Mashqi",
        "category": "4-Hafta: Monitoring, Hardening va Real Cloud Deploy",
        "problem": "Server xonasida yong'in yoki apparatning to'liq kuyishi sodir bo'ldi. Yangi olingan bo'sh kompyuterga pfSense ni o'rnatib, barcha qoidalar, sertifikatlar, VLAN va VPN sozlamalarini 5 daqiqa ichida noldan tiklab berish talab etiladi.",
        "theory_points": [
            "pfSense `config.xml` arxitekturasi: pfSense ning barcha sozlamalari yagona XML faylda saqlanadi — tizimni ko'chirish va tiklash nihoyatda oson.",
            "Netgate ACB (AutoConfigBackup): Har safar sozlama o'zgarganda konfiguratsiyani AES-256 bilan shifrlab, Netgate xavfsiz bulutiga avtomatik zaxiralash.",
            "Disaster Recovery (DR) rejasi va RTO / RPO ko'rsatkichlari: Qutidan chiqqan yangi routerga XML ni yuklash orqali darhol jonlantirish.",
            "ZFS Boot Environments orqali yangilanishlardan oldin xavfsiz nuqta yaratish."
        ],
        "hardware_guide": """* **Hardware:** Zaxira USB fleshkaga `config.xml` faylini nusxalab qo'yish kifoya; o'rnatish paytida pfSense USB dan konfiguratsiyani avtomat o'qib oladi (ECL - External Configuration Locator).""",
        "virtual_guide": """* **Proxmox / VMware:** Yangi bo'sh VM yaratib, unga zaxira fayli orqali tizimni to'liq jonlantirish sinovi o'tkaziladi.""",
        "lab_steps": [
            "`Services` -> `Auto Config Backup` -> `Settings` ga kirish.",
            "'Enable ACB' katakchasini yoqish, Encryption Password (shifrlash paroli) kiritish va 'Save' tugmasini bosish.",
            "`Restore` yorlig'iga o'tib, bulutda har bir o'zgarish bo'yicha saqlangan zaxira nuqtalarini ko'rish.",
            "Qo'lda to'liq zaxira olish: `Diagnostics` -> `Backup & Restore` ga kirib, `Download configuration as XML` tugmasini bosish va `config-latest.xml` faylini yuklab olish.",
            "Falokat Mashqi (Disaster Recovery Drill): Proxmox yoki VMware da yangi toza pfSense VM o'rnatish (yoki fizik uskunani tozalash).",
            "Konsolda interfeyslarni aniqlagach, toza WebGUI ga kirib `Diagnostics` -> `Backup & Restore` -> `Restore configuration` orqali saqlangan XML faylni yuklash.",
            "Tizim qayta yuklangach (Reboot), barcha VLAN, DHCP, Firewall va VPN lar 100% tiklanganini tekshirish."
        ],
        "verification": [
            "Zaxiradan tiklangan yangi serverda barcha qoidalar va sertifikatlar o'z joyida ekanini ko'rish",
            "Mijoz kompyuteridan ping va internet aloqasi darhol qayta tiklanganini tasdiqlash",
            "Tiklash jarayoni 5 daqiqadan kam vaqt olganini taymer bilan o'lchash",
            "zfs list snapshots (ZFS zaxira nuqtalarini ko'rish)"
        ],
        "troubleshooting": [
            "Muammo: Yangi serverda tarmoq kartalari boshqacha nomlangan (masalan vtnet o'rniga igb). Yechim: pfSense yuklanish paytida konsolda 'Interface Mismatch' deb so'raydi; qaysi port yangi kartaga to'g'ri kelishini konsol menyusidan belgilash kifoya.",
            "Muammo: Shifrlangan ACB paroli esdan chiqdi. Yechim: ACB parolini korxona parol menejerida (Bitwarden/KeePass) xavfsiz saqlash shart."
        ],
        "homework": "Bash yoki PowerShell skripti yozing, u har kecha pfSense dan `curl` orqali avtomat `config.xml` ni tortib olib, korxona xavfsiz NAS serveriga saqlasin."
    },
    {
        "day": 28,
        "title": "Cloud Muhitlar Arxitekturasi: AWS VPC, GCP va Linode Tarmoq Asoslari",
        "category": "4-Hafta: Monitoring, Hardening va Real Cloud Deploy",
        "problem": "Kompaniya o'z serverlarini jismoniy ofisdan AWS/GCP bulutiga ko'chirmoqda. Ammo bulut muhitida an'anaviy Layer 2 broadcast, multicast va CARP protokollari ishlamaydi. Cloud xavfsizligini ta'minlash uchun pfSense ni bulut arxitekturasiga moslashtirish lozim.",
        "theory_points": [
            "Cloud SDN (Software Defined Networking) o'ziga xosligi: Nega bulutda L2 yo'q va hamma narsa L3 da ishlaydi?",
            "AWS VPC (Virtual Private Cloud) va Subnetlar: Public Subnet va Private Subnet tushunchasi.",
            "Cloud Routing Tables: Private subnetdagi barcha serverlarning `0.0.0.0/0` standart shlyuzini AWS NAT Gateway o'rniga pfSense ENI (Elastic Network Interface) siga yo'naltirish — xarajatlarni 80% ga tejash va UTM nazoratini qo'lga olish.",
            "Source/Destination Check: Bulut interfeyslarida begona paketlarni o'tkazish uchun ushbu tekshiruvni o'chirib qo'yish sharti.",
            "Elastic IP va Public IP boshqaruvi."
        ],
        "hardware_guide": """* **Hardware:** Ushbu dars mahalliy serverlarni kelajakda bulutga bog'lash uchun poydevor hisoblanadi.""",
        "virtual_guide": """* **Cloud:** AWS Console, GCP Cloud Console yoki Linode Cloud Manager orqali VPC va tarmoq sxemasi loyihalanadi.""",
        "lab_steps": [
            "AWS boshqaruv konsoliga (yoki GCP / Linode) kirish.",
            "Yangi VPC yaratish: IPv4 CIDR: `172.31.0.0/16`.",
            "2 ta Subnet ochish: `Public-Subnet` (`172.31.1.0/24`) va `Private-Subnet` (`172.31.2.0/24`).",
            "Internet Gateway (IGW) yaratish va uni VPC ga biriktirish (Attach to VPC).",
            "Public Route Table yaratish: `0.0.0.0/0` marshrutini IGW ga yo'naltirish.",
            "Private Route Table yaratish: `0.0.0.0/0` marshrutini kelajakda pfSense bo'ladigan tarmoq interfeysi (ENI) ga yo'naltirish uchun tayyorlab qo'yish.",
            "Security Groups (SG) yaratish: pfSense-WAN-SG (faqat ma'lum portlar ochiq) va Private-SG (faqat pfSense dan kirish ruxsat)."
        ],
        "verification": [
            "AWS VPC Dashboard da barcha subnetlar va yo'nalishlar xaritasi (Resource Map) to'g'ri bog'langanini ko'rish",
            "Tarmoq xavfsizlik guruhlari (Security Groups) qoidalarini tekshirish",
            "IP planlash: AWS da har bir subnetdagi birinchi 4 ta va oxirgi 1 ta IP manzil zaxiralanganini (AWS reserved IPs) inobatga olishni tasdiqlash"
        ],
        "troubleshooting": [
            "Muammo: Internet Gateway VPC ga ulanmayapti. Yechim: VPC da avvaldan boshqa IGW yo'qligini tekshiring (bitta VPC ga faqat 1 ta IGW ulanadi).",
            "Muammo: Subnet to'qnashuvi. Yechim: Bulutdagi CIDR (172.31.0.0/16) mahalliy ofisingizdagi subnetlar (10.10.0.0/16) bilan mutlaqo bir xil bo'lmasligi shart (VPN ulanishi uchun)."
        ],
        "homework": "GCP (Google Cloud Platform) yoki Linode da ham xuddi shunday 2-zonali (Public va Private) tarmoq sxemasini tuzib, AWS bilan farqlarini jadval ko'rinishida yozing."
    },
    {
        "day": 29,
        "title": "pfSense Cloud Deployment: AWS / GCP / Linode da Real Instansiya Ko'tarish",
        "category": "4-Hafta: Monitoring, Hardening va Real Cloud Deploy",
        "problem": "Bulutda joylashgan o'nlab ma'lumotlar bazalari va dasturiy serverlar tashqi xakerlik hujumlariga ochiq qolgan. Ularni AWS Security Groups dan tashqari, korxona darajasidagi professional pfSense UTM xavfsizlik devori orqasida himoyalash talab qilinadi.",
        "theory_points": [
            "Cloud Deployment modellari: AWS Marketplace rasmiy pfSense Plus AMI yoki Linode/Hetzner da Custom FreeBSD ISO o'rnatish.",
            "Dual-NIC Cloud Architecture: Bitta instansiyaga ikkita ENI (biri Public Subnetda Elastic IP bilan, ikkinchisi Private Subnetda) biriktirish.",
            "Cloud Firewall Hardening: AWS Security Group orqali faqat ma'murning o'z IP siga port 8443 (WebGUI) va 2222 (SSH) ruxsat berish.",
            "Cloud Outbound NAT: Private serverlarning internetga pfSense orqali chiqishini ta'minlash."
        ],
        "hardware_guide": """* **Cloud Platform:** AWS bepul hisobi (Free Tier) yoki Linode/DigitalOcean/Hetzner serveri.""",
        "virtual_guide": """* **Cloud:** AWS EC2 t3.small yoki Linode 2GB instansiyasi.""",
        "lab_steps": [
            "AWS EC2 Console ga kirish -> 'Launch Instance'.",
            "AWS Marketplace dan `pfSense Plus Firewall/VPN/Router` tasvirini tanlash (yoki Linode da FreeBSD yuklash).",
            "Instance Type: `t3.small` (kamida 2 vCPU, 2GB RAM).",
            "Network Settings: Oldingi darsda yaratilgan VPC ni tanlash, Subnet: `Public-Subnet` (`172.31.1.0/24`).",
            "Ikkinchi tarmoq interfeysini (ENI) qo'shish: Subnet: `Private-Subnet` (`172.31.2.0/24`).",
            "AWS da KRITIK QADAM: Har ikkala ENI sozlamalariga kirib, `Change source/dest. check` parametrini 'Stop' (Disable) qilib qo'yish.",
            "Elastic IP yaratish va uni pfSense ning Public interfeysiga biriktirish (Associate Elastic IP).",
            "Brauzer orqali `https://<Elastic_IP>` ga kirish va bulutdagi pfSense ni dastlabki sozlash."
        ],
        "verification": [
            "Bulutdagi pfSense WebGUI ga xavfsiz ulanishni tasdiqlash",
            "Private Subnetda bitta yengil EC2 Linux server ko'tarish",
            "Private EC2 serveridan internetga ping yuborish: paketlar pfSense orqali NAT bo'lib chiqayotganini ko'rish",
            "pfSense Status -> Gateways da bulut shlyuzining Online ekanini tekshirish"
        ],
        "troubleshooting": [
            "Muammo: Private serverlar internetga chiqa olmayapti. Yechim: AWS ENI da 'Source/Dest Check' o'chirilmagan yoki AWS Route Table da 0.0.0.0/0 shlyuzi pfSense interfeysiga yo'naltirilmagan bo'ladi.",
            "Muammo: WebGUI ochilmayapti. Yechim: AWS Security Group da port 443 yoki 8443 o'zingizning tashqi IP manzilingiz uchun ruxsat berilganini tekshiring."
        ],
        "homework": "Bulutdagi pfSense da pfBlockerNG-devel paketini yoqing va bulutdagi xususiy serverlaringizni xalqaro xakerlik skanerlaridan himoyalang."
    },
    {
        "day": 30,
        "title": "Katta Final — Hybrid Cloud Production Project: On-Premise to Cloud IPsec/WireGuard",
        "category": "4-Hafta: Monitoring, Hardening va Real Cloud Deploy",
        "problem": "Kompaniyaning jismoniy ofisi/zavodi (On-Premise Proxmox / Hardware pfSense) bilan Cloud (AWS VPC pfSense) o'rtasida mustahkam, shifrlangan, uzluksiz Hybrid Cloud tuneli talab etiladi. Mahalliy xodimlar bulutdagi ma'lumotlar bazalariga xuddi qo'shni xonadagi serverdek xavfsiz ulanishi kerak.",
        "theory_points": [
            "Hybrid Cloud Enterprise Arxitekturasi: Mahalliy infratuzilma va Bulutni yagona xavfsiz tarmoqqa birlashtirish.",
            "IPsec VTI yoki WireGuard orqali Site-to-Cloud tunnel: Kechikish (Latency), MTU/MSS clamping (`mssfix`) va shifrlash tezligi.",
            "BGP dinamik marshrutlash: Bulutda yangi serverlar yoki subnetlar paydo bo'lganda, mahalliy pfSense ularni BGP orqali avtomat o'rganishi.",
            "Zero-Trust Cloud Access va Yakuniy 30 Kunlik Xulosa."
        ],
        "hardware_guide": """* **Hardware:** Mahalliy apparat pfSense (HQ) bevosita AWS/GCP bulutidagi ikkinchi pfSense instansiyasiga ulanadi.""",
        "virtual_guide": """* **Proxmox / VMware ⇄ Cloud:** Mahalliy virtual pfSense bulutdagi pfSense bilan IPsec orqali bog'lanadi.""",
        "lab_steps": [
            "Mahalliy pfSense (HQ: LAN `10.10.0.0/16`) va Bulut pfSense (Cloud: VPC `172.31.0.0/16`) parametrlarini tekshirish.",
            "Mahalliy pfSense da: `VPN` -> `IPsec` -> Phase 1 yaratish. Remote Gateway: `Bulut_Elastic_IP`, IKEv2, AES256-GCM, DH Group 14.",
            "Phase 2: Mode: `Routed (VTI)`, Local IP: `10.254.100.1/30`, Remote IP: `10.254.100.2/30`.",
            "Bulut pfSense da: Phase 1 yaratish. Remote Gateway: `Mahalliy_WAN_IP`, Phase 2 VTI: Local IP: `10.254.100.2/30`, Remote IP: `10.254.100.1/30`.",
            "Ikkala tomonda ham `Interfaces` -> `Assignments` orqali yangi VTI interfeyslarini qabul qilish va yoqish.",
            "Mahalliy pfSense da marshrut qo'shish: Destination: `172.31.0.0/16` -> Gateway: `VTI_Gateway`.",
            "Bulut pfSense da marshrut qo'shish: Destination: `10.10.0.0/16` -> Gateway: `VTI_Gateway`.",
            "Ikkala tomonda firewall qoidalarida IPsec va LAN trafigiga ruxsat berish."
        ],
        "verification": [
            "Mahalliy ofis kompyuteridan: ping 172.31.2.50 (Bulutdagi xususiy EC2 serverga to'g'ridan-to'g'ri ping borishini tekshirish)",
            "Bulutdagi serverdan: curl http://10.10.20.80 (Mahalliy DMZ dagi web-serverga ulanishni tekshirish)",
            "Status -> IPsec (Tunnel holati yashil 'ESTABLISHED' va baytlar uzatilayotganini ko'rish)",
            "iperf3 benchmark orqali mahalliy tarmoqdan bulutga tunnel o'tkazuvchanligi va ping kechikishini o'lchash"
        ],
        "troubleshooting": [
            "Muammo: Katta veb-sahifalar ochilmayapti yoki ulanish qotib qolmoqda. Yechim: MTU/MSS Clamping muammosi. Firewall > Rules > IPsec va System > Advanced bo'limida MSS Clamping qiymatini 1380 ga qo'ying.",
            "Muammo: Bulutdagi server javob qaytarmayapti. Yechim: AWS Security Group da mahalliy subnetdan (`10.10.0.0/16`) kiruvchi trafikka ruxsat berilganini tekshiring."
        ],
        "homework": "30 kunlik barcha laboratoriya tajribalaringiz, skrinshotlar va konfiguratsiyalaringizni jamlab, shaxsiy GitHub / LinkedIn profilingizda 'Zero to Hero: pfSense Production Engineering' maqolangizni e'lon qiling!"
    }
]

def generate_lecture_md(day_data):
    day_num = day_data["day"]
    title = day_data["title"]
    category = day_data["category"]
    theory_points = day_data.get("theory_points", [])
    
    tp_content = ""
    for idx, tp in enumerate(theory_points, 1):
        tp_content += f"### {idx}. {tp}\n\n"
        tp_content += f"Ushbu bo'limda {tp.split(':')[0]} mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.\n\n"

    content = f"""# 📚 [KUN-{day_num:02d}] LECTURE: {title}

**Kategoriya:** {category}  
**Dars Maqsadi:** Ushbu darsda talabalar {title} bo'yicha to'liq nazariy asoslarni, FreeBSD va pfSense arxitekturasini, tarmoq protokollari standartlarini hamda korxona darajasidagi (Enterprise) qo'llanish amaliyotini o'rganadilar.

---

## 🧭 Mundarija
1. [Mavzuning Mohiyati va Biznes Ahamiyati](#1-mavzuning-mohiyati-va-biznes-ahamiyati)
2. [Nazariy Asoslar va Protokol Spetsifikatsiyalari](#2-nazariy-asoslar-va-protokol-spetsifikatsiyalari)
3. [pfSense va FreeBSD Ichki Arxitekturasi](#3-pfsense-va-freebsd-ichki-arxitekturasi)
4. [Jismoniy Uskuna (Hardware) vs Virtualizatsiya Tahlili](#4-jismoniy-uskuna-hardware-vs-virtualizatsiya-tahlili)
5. [Production Xavfsizlik Qoidalari va Eng Yaxshi Amaliyotlar (Best Practices)](#5-production-xavfsizlik-qoidalari)
6. [Xulosa va O'z-o'zini Tekshirish Savollari](#6-xulosa-va-savollar)

---

## 1. Mavzuning Mohiyati va Biznes Ahamiyati

Zamonaviy korporativ IT infratuzilmasida **{title}** shunchaki sozlama emas, balki tarmoq xavfsizligi, barqarorligi va biznes jarayonlarining uzluksizligini (Business Continuity) ta'minlovchi strategik element hisoblanadi. 

Noto'g'ri loyihalashtirilgan arxitektura oqibatida:
* Tarmoqda xavfsizlik zaifliklari va ruxsatsiz kirish (Breach) xavfi ortadi;
* Katta hajmdagi paketlar oqimida kechikish (Latency) va paket yo'qotishlar (Packet drops) kuzatiladi;
* Muammo yuzaga kelganda nosozlikni aniqlash (Troubleshooting) soatlab vaqt talab qiladi.

Ushbu ma'ruzaning maqsadi — sizga har bir tugma va har bir buyruq ortida qanday jarayon yotganini chuqur tushuntirishdir.

---

## 2. Nazariy Asoslar va Protokol Spetsifikatsiyalari

{tp_content}

---

## 3. pfSense va FreeBSD Ichki Arxitekturasi

pfSense FreeBSD operatsion tizimiga asoslanganligi sababli, barcha tarmoq amallari FreeBSD yadrosining yuqori unumdor tarmoq steki orqali bajariladi:
* **Kernel & User Space:** Paketlarni qayta ishlash to'g'ridan-to'g'ri yadroda (`pf`, `dummynet`, `netmap`, `if_wg`) kechadi, foydalanuvchi interfeysi (PHP WebGUI) esa faqat konfiguratsiyani (`config.xml`) boshqarish va uni tizim buyruqlariga aylantirish uchun xizmat qiladi.
* **State Table (Holat jadvali):** Barcha aktiv sessiyalar xotirada tezkor hash-jadval sifatida saqlanadi. Har bir yangi ulanish xavfsizlik qoidalariga solishtiriladi, keyingi paketlar esa darhol holat jadvali orqali o'tkaziladi.
* **Resurs Boshqaruvi:** ZFS ARC kesh mexanizmi va mbuf (Memory Buffer) klasterlari tarmoq kartalaridan kelayotgan paketlarni uzluksiz qabul qilishni ta'minlaydi.

---

## 4. Jismoniy Uskuna (Hardware) vs Virtualizatsiya Tahlili

Talabalar ushbu texnologiyani ikki xil muhitda qo'llashlari mumkin:

| Parametr | Jismoniy Uskuna (Real Hardware pfSense) | Virtualizatsiya (Proxmox VE / VMware) |
|---|---|---|
| **Tarmoq Kartalari** | Intel I210/I225/I350 (`igb`, `igc`) yoki Realtek (`re`) | Virtual interfeyslar (`virtio-net`, `vmxnet3`, `e1000`) |
| **Paket Kechikishi** | Minimal (0.1ms), to'g'ridan-to'g'ri apparatga ulanish | Kichik virtualizatsiya kechikishi (+0.2-0.5ms) |
| **VLAN Boshqaruvi** | 802.1Q signali to'g'ridan-to'g'ri fizik switchga ketadi | Gipervizor virtual bridge'ida VLAN-aware bo'lishi shart |
| **Moslashuvchanlik** | Uskunaga bog'liq, ko'chirish qiyin | Snapshot, klonlash va tezkor zaxira olish imkoniyati |

---

## 5. Production Xavfsizlik Qoidalari va Eng Yaxshi Amaliyotlar (Best Practices)

1. **Prinsip: Least Privilege (Eng kam huquq):** Hech qachon ortiqcha port va protokollarga ruxsat bermang. Standart holatda barcha kirish taqiqlangan bo'lishi lozim.
2. **Hujjatlashtirish:** Har bir qoida, interfeys va aliasga aniq va tushunarli izoh (Description) yozing.
3. **Zaxiralash:** Har qanday jiddiy o'zgarishdan oldin ZFS snapshot yoki `config.xml` zaxira nusxasini oling.
4. **Monitoring:** Tizim loglarini doimiy ravishda tahlil qiling va anomaliyalarni erta aniqlang.

---

## 6. Xulosa va O'z-o'zini Tekshirish Savollari

* Ushbu mavzudagi asosiy protokol qaysi RFC standartiga asoslangan?
* Nega aynan ushbu yondashuv korxona darajasida an'anaviy usullardan afzalroq?
* Virtualizatsiya muhitida qaysi parametrlar noto'g'ri bo'lsa tizim ishlamay qoladi?
* Jismoniy tarmoq kartalarining qaysi xususiyati (Offloading) ba'zan tarmoqni uzib qo'yishi mumkin?

Endi nazariyani mustahkamlash uchun **[LAB YO'RIQNOMASI](lab.md)** ga o'ting va amaliy laboratoriya ishini bajaring!
"""
    return content

def generate_lab_md(day_data):
    day_num = day_data["day"]
    title = day_data["title"]
    category = day_data["category"]
    problem = day_data["problem"]
    hw_guide = day_data["hardware_guide"]
    virt_guide = day_data["virtual_guide"]
    steps = day_data.get("lab_steps", [
        "WebGUI ga kirish va kerakli modulni faollashtirish.",
        "Parametrlarni korporativ IP rejasiga mos ravishda sozlash.",
        "Qoidalarni qo'shish va sozlamalarni 'Apply Changes' orqali tatbiq qilish."
    ])
    verifs = day_data.get("verification", [
        "ping orqali aloqani tekshirish",
        "tcpdump yordamida paketlar oqimini tahlil qilish",
        "Status paneli orqali holatni tasdiqlash"
    ])
    troubles = day_data.get("troubleshooting", [
        "Muammo: Sozlamalar kuchga kirmadi. Yechim: 'Apply Changes' tugmasi bosilganligini va brauzer keshini tozalashni tekshiring.",
        "Muammo: Paketlar o'tmayapti. Yechim: Firewall qoidalarida Inbound/Outbound ruxsatlarni tekshiring."
    ])
    homework = day_data.get("homework", "O'tilgan sozlamalarni mustaqil ravishda boshqa subnet yoki mijoz kompyuterida takrorlang va xulosalarni qayd eting.")

    steps_text = ""
    for idx, s in enumerate(steps, 1):
        steps_text += f"{idx}. **Qadam:** {s}\n"

    verif_text = ""
    for v in verifs:
        if " (" in v and v.endswith(")"):
            cmd, desc = v.rsplit(" (", 1)
            desc = desc.rstrip(")")
            verif_text += f"**{desc}:**\n```bash\n{cmd}\n```\n\n"
        else:
            verif_text += f"```bash\n{v}\n```\n\n"

    trouble_text = ""
    for t in troubles:
        trouble_text += f"* ⚠️ **{t}**\n"

    content = f"""# 🛠️ [KUN-{day_num:02d}] LAB QO'LLANMASI: {title}

**Mavzu:** {title}  
**Bosqich:** {category}  
**Nazariy Ma'ruza:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi (Business Problem Statement)

> **Real Muammo:** {problem}

Ushbu laboratoriya mashg'ulotida siz ushbu real muammoni to'liq hal qilasiz, tizimni xalqaro standartlar asosida xavfsiz va barqaror qilib sozlaysiz.

---

## 🗺️ 2. Laboratoriya Topologiyasi va IP Sxemasi

```mermaid
flowchart LR
    subgraph WAN_ZONE["Tashqi Tarmoq (WAN)"]
        ISP["Internet Provayder (Uplink)"]
    end

    subgraph PFSENSE["pfSense Firewall (Lab Gateway)"]
        direction TB
        FW["pfSense 2.7.2 CE\\nIP: 10.10.10.1 / WAN: DHCP"]
    end

    subgraph INTERNAL["Ichki Tarmoq (Clients & Servers)"]
        SRV["Server (Ubuntu/Nginx)\\nIP: 10.10.20.x"]
        PC["Admin / Client PC\\nIP: 10.10.10.x"]
    end

    ISP === PFSENSE
    PFSENSE === SRV
    PFSENSE === PC
```

### 📋 Laboratoriya IP Jadvali

| Interfeys / Qurilma | Turi | IP Manzil / Subnet | Izoh |
|---|---|---|---|
| `WAN` | Tashqi | Provayder IP (DHCP / Static) | Internetga chiqish |
| `LAN` (MGMT) | Ichki | `10.10.10.1/24` | Boshqaruv va admin tarmog'i |
| `DMZ / SERVERS` | Segment | `10.10.20.1/24` | Korporativ serverlar |
| `Mijoz Mashinasi` | Test Client | `10.10.10.50` (DHCP) | Sinov o'tkazuvchi kompyuter |

---

## 🖥️ 3. Talabalar uchun Laboratoriya Muhiti (Ikkala Variant)

Talaba o'zida mavjud imkoniyatga qarab **Variant A** yoki **Variant B** dan birini tanlaydi:

### 🔹 VARIANT A: Real Jismoniy pfSense (Hardware Appliance / Mini-PC)
{hw_guide}

### 🔹 VARIANT B: Virtual Server pfSense (Proxmox VE / VMware Workstation)
{virt_guide}

---

## ⚙️ 4. Bosqichma-bosqich Amaliy Sozlash Qo'llanmasi (Step-by-Step)

{steps_text}

---

## 🧪 5. Verifikatsiya va Tekshirish (Testing & CLI)

Har bir amaliyot tugagach, quyidagi buyruqlar yordamida natijani qat'iy tekshiring:

{verif_text}

---

## 🚨 6. Eng Ko'p Uchraydigan Xatolar va Troubleshooting

{trouble_text}

---

## 🏆 7. Mustaqil Amaliy Topshiriq (Student Challenge / Homework)

> 📝 **Vazifa:** {homework}
"""
    return content

def update_progress_sheet():
    progress_file = os.path.join(BASE_DIR, "PROGRESS_SHEET.md")
    lines = [
        "# 📊 pfSense 30 Kunlik O'zlashtirish va Maqolalar Jadvali (Progress Tracker)\n",
        "Ushbu jadval orqali siz har kuni bajargan ishlaringizni, laboratoriya testlarini va GitHub maqolalaringiz holatini kuzatib borasiz. Ushbu jadvalni to'g'ridan-to'g'ri nusxalab Google Sheets yoki Excel ga ham joylashtirishingiz mumkin.\n",
        "| Kun | Mavzu | Lab Muhiti (Hardware/Virtual) | Test / Verifikatsiya | Maqola Holati | Sana | Dars & Lab Havolasi |",
        "|:---:|:---|:---:|:---:|:---:|:---:|:---|"
    ]
    
    for day in DAYS_DATA:
        d_num = day["day"]
        title_short = day["title"].split(":")[0] if ":" in day["title"] else day["title"]
        test_summary = day.get("verification", ["CLI test"])[0]
        if " (" in test_summary:
            test_summary = test_summary.split(" (")[0]
        row = f"| **{d_num:02d}** | {title_short} | [ ] Hardware [ ] Virtual | `{test_summary}` | [x] Tayyor | | 📖 [Lecture](day-{d_num:02d}/lecture.md) · 🛠️ [Lab Guide](day-{d_num:02d}/lab.md) |"
        lines.append(row)
        
    lines.append("\n")
    with open(progress_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Updated PROGRESS_SHEET.md successfully.")

def main():
    print(f"Creating 30-day curriculum folders in: {BASE_DIR}")
    for day_data in DAYS_DATA:
        day_num = day_data["day"]
        day_dir = os.path.join(BASE_DIR, f"day-{day_num:02d}")
        os.makedirs(day_dir, exist_ok=True)
        
        lecture_path = os.path.join(day_dir, "lecture.md")
        lab_path = os.path.join(day_dir, "lab.md")
        
        lecture_content = generate_lecture_md(day_data)
        lab_content = generate_lab_md(day_data)
        
        with open(lecture_path, "w", encoding="utf-8") as f:
            f.write(lecture_content)
            
        with open(lab_path, "w", encoding="utf-8") as f:
            f.write(lab_content)
            
        print(f"Created day-{day_num:02d}: lecture.md and lab.md")
        
    update_progress_sheet()

if __name__ == "__main__":
    main()

