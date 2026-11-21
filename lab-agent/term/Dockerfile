# Brauzer-terminal: ttyd + docker CLI. Faqat lab-shell menyusini ishga tushiradi.
FROM alpine:3.20
RUN apk add --no-cache ttyd bash docker-cli ncurses
COPY lab-shell /usr/local/bin/lab-shell
RUN chmod 0755 /usr/local/bin/lab-shell
EXPOSE 7681
