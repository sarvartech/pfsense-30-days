## Topologiya

```
site-a  203.0.113.1 ── "internet" ── 203.0.113.2  site-b
   wg0: 10.99.99.1/30  ═══ tunnel ═══  wg0: 10.99.99.2/30
```

## Topshiriqlar

1. Ikkala tomonda kalit juftligini yarating:
   ```bash
   umask 077; wg genkey | tee /root/priv | wg pubkey > /root/pub; cat /root/pub
   ```
2. **site-a**:
   ```bash
   ip link add wg0 type wireguard
   wg set wg0 private-key /root/priv listen-port 51820 \
      peer <SITE-B-PUBKEY> endpoint 203.0.113.2:51820 allowed-ips 10.99.99.2/32 persistent-keepalive 25
   ip addr add 10.99.99.1/30 dev wg0
   ip link set wg0 up
   ```
3. **site-b** da ko'zgu sozlama (`10.99.99.2/30`, endpoint `203.0.113.1`, allowed-ips `10.99.99.1/32`).
4. `wg show` — *latest handshake* va *transfer* qatorlarini tahlil qiling.
5. `ping 10.99.99.2`, so'ng `tcpdump -ni eth1 udp port 51820` bilan shifrlangan trafikni ko'ring.

> 💡 Bu aynan platformamizning VPS ↔ home server ulanishi qanday ishlashining kichik nusxasi!
