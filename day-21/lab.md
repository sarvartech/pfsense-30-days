# 🛠️ [KUN-21] LAB: HAProxy Reverse Proxy, SSL Offloading va Serverlar Klasterini Sozlash

**Mavzu:** HAProxy orqali Web-klaster qurish, ACL yo'naltirish va jonli Health Check sinovi  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyaning ommaviy savdo saytiga kiruvchi trafik 5 baravarga oshdi. Bitta server ortiq yuklamani ko'tara olmay qulab tushmoqda. Dasturchilar 2 ta yangi server qo'shdi. IT bo'limiga vazifa: Ushbu serverlarni yagona klasterga birlashtirish, yuklamani teng taqsimlash, SSL sertifikatni o'rnatish va agar serverlardan biri ishdan chiqsa, sayt bir lahzaga ham to'xtamasligini ta'minlash.

---

## ⚙️ 2. Qadam-baqadam Sozlash

### 1-Qadam: pfSense WebGUI Portini Bo'shatish
Standart holatda pfSense WebGUI 443 portida o'tiradi. HAProxy ga joy bo'shatish kerak:
1. `System -> Advanced -> Admin Access` ga kiring.
2. TCP Port: `8443` qilib o'zgartiring. Saqlang. (Endi WebGUI: `https://10.10.10.1:8443`).

### 2-Qadam: HAProxy Paketini O'rnatish
1. `System -> Package Manager -> Available Packages` dan `haproxy` paketini o'rnating.
2. `Services -> HAProxy -> Settings` ga kirib, **Enable HAProxy** ni yoqing.

### 3-Qadam: Backend Serverlar Guruhini Yaratish
1. `Services -> HAProxy -> Backend` yorlig'iga o'ting, **Add** bosing:
   * Name: `WEB_CLUSTER_BACKEND`
   * Balance: `roundrobin`
2. **Server list** qismida backend serverlarni qo'shing:
   * Server 1: Name: `SRV01`, Address: `10.10.20.11`, Port: `80`
   * Server 2: Name: `SRV02`, Address: `10.10.20.12`, Port: `80`
3. **Health check method:**
   * Health check: `HTTP`
   * Http check method: `OPTIONS` yoki `GET`
   * Check frequency: `2000` ms (har 2 soniyada).
4. Saqlang.

### 4-Qadam: Frontend Ni Sozlash
1. `Services -> HAProxy -> Frontend` yorlig'iga o'ting, **Add** bosing:
   * Name: `HTTPS_FRONTEND`
   * External address: `WAN address` (yoki CARP VIP bo'lsa CARP VIP tanlanadi).
   * Port: `443`
   * Type: `SSL / HTTPS (offloading)`
   * Default backend: `WEB_CLUSTER_BACKEND`
2. **Certificate:**
   * SSL Offloading uchun sertifikatni tanlang (masalan ACME Let's Encrypt yoki Wildcard).
3. Saqlang va **Apply Changes** qiling.

### 5-Qadam: Firewall Qoidasini Ochish
1. `Firewall -> Rules -> WAN` ga kiring.
2. Action: `Pass`, Protocol: `TCP`, Destination: `WAN address` (yoki CARP VIP), Port: `443`. Saqlang.

---

## 🧪 3. Verifikatsiya va Jonli Sinovlar

1. **HAProxy Statistika Panelini Ko'rish:**
   * `Status -> HAProxy Stats` sahifasiga kiring.
   * `SRV01` va `SRV02` yashil **UP** holatdaligini tasdiqlang.
2. **Yuklama Taqsimoti Sinovi:**
   Terminaldan bir necha marta so'rov yuboring:
```bash
curl -k https://<WAN_IP>/
```
*Natija:* Javob navbatma-navbat birinchi `SRV01` dan, keyin `SRV02` dan keladi.
3. **Avariya (Health Check Failover) Sinovi:**
   * `SRV01` serverida Nginx/Apache xizmatini to'xtating:
   ```bash
   systemctl stop nginx
   ```
   * 2 soniyadan so'ng HAProxy Stats da `SRV01` qizil **DOWN** holatiga o'tadi.
   * Web-saytga kiring: birorta ham xatolik chiqmaydi, barcha foydalanuvchilar avtomat ravishda ishchi `SRV02` ga yo'naltiriladi!
