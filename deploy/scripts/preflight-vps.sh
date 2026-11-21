#!/usr/bin/env bash
# FAQAT O'QIYDI — hech narsani o'zgartirmaydi. VPS da mavjud loyihalar bilan to'qnashuvlarni aniqlaydi.
# Foydalanish:  sudo ./deploy/scripts/preflight-vps.sh
set -u
ok()   { printf '  \033[32m✔\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m⚠\033[0m %s\n' "$*"; }

port_busy() { ss -Hltnu "( sport = :$1 )" 2>/dev/null | grep -q .; }

echo "== Tizim"
. /etc/os-release 2>/dev/null && ok "OS: $PRETTY_NAME"
ok "RAM: $(free -h | awk '/Mem:/{print $2" jami, "$7" bo`sh"}')"
ok "Disk /: $(df -h / | awk 'NR==2{print $4" bo`sh"}')"

echo "== Docker"
if command -v docker >/dev/null; then
  ok "Docker: $(docker --version)"
  docker compose version >/dev/null 2>&1 && ok "Compose: $(docker compose version --short)" || warn "docker compose plugin yo'q"
  echo "  Ishlayotgan konteynerlar:"
  docker ps --format '    {{.Names}}\t{{.Image}}\t{{.Ports}}'
  docker ps -a --format '{{.Names}}' | grep -q '^men-tarmoq' && warn "men-tarmoq konteynerlari allaqachon bor"
else
  warn "Docker o'rnatilmagan"
fi

echo "== Portlar"
for p in 80 443 51820 8010; do
  if port_busy "$p"; then
    warn "$p band: $(ss -Hltnup "( sport = :$p )" 2>/dev/null | awk '{print $NF}' | head -1)"
  else
    ok "$p bo'sh"
  fi
done

echo "== Firewall"
if command -v ufw >/dev/null; then ufw status | sed 's/^/    /'; else ok "ufw yo'q"; fi
iptables -S INPUT 2>/dev/null | head -5 | sed 's/^/    /'

echo "== WireGuard"
ip -br link show type wireguard 2>/dev/null | sed 's/^/    /'
ip -4 route | grep -q '10\.99\.0\.' && warn "10.99.0.0/24 allaqachon ishlatilmoqda — WG_SUBNET ni o'zgartiring" || ok "10.99.0.0/24 bo'sh"

echo
echo "== Tavsiya"
if port_busy 80 || port_busy 443; then
  echo "  80/443 band → mavjud reverse proxy orqali ulang (MODE=proxy): docs/PLATFORM_DEPLOY.md, 3.5-bo'lim"
else
  echo "  80/443 bo'sh → o'rnatilgan Caddy bilan (MODE=caddy)"
fi
