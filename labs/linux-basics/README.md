## Topologiya

```
[host1] eth1 ───────── eth1 [host2]
 10.0.12.1/24          10.0.12.2/24
```

## Topshiriqlar

1. Terminalda `1` ni tanlab **host1** ga kiring va interfeyslarni ko'ring:
   ```bash
   ip -br link
   ip -br addr
   ```
2. host1 ga manzil bering va interfeysni yoqing:
   ```bash
   ip addr add 10.0.12.1/24 dev eth1
   ip link set eth1 up
   ```
3. `exit` bilan menyuga qayting, **host2** ni tanlang va `10.0.12.2/24` ni bering.
4. host1 dan `ping -c 3 10.0.12.2` qiling.
5. ARP jadvalini ko'ring: `ip neigh`. MAC manzil qayerdan paydo bo'ldi?
6. Qo'shimcha: host2 da `tcpdump -ni eth1 arp or icmp` ishga tushirib, host1 dan ping yuboring va ARP request/reply ni kuzating.

Har bir qadamdan keyin chapdagi **Tekshirish** tugmasini bosing.
