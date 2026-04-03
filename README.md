# InteractiveSocket

This module forwards socket to stdin & stdout.

This is a simple cli module that constructs socket sessions with remote TCP / UDP port, made for debugging and educational purposes.

## Quick start

`python3 -m interactivesocket`. The module also exports the cli entrypoint `interactivesocket`.

Please refer to typer / source docstrings for further specifications. The module is built with cli simplicity in mind.

## Examples

Hi there!
```
root@host:~$ interactivesocket tcp --tls google.com 443
Interactive Socket v0.3.0, Scevenate (c) 2026
Connecting to google.com:443...
Connection established with google.com:443. Use Ctrl+D (EOF) to disconnect.
google.com:443 >>> HEAD / HTTP/1.1\r\n
google.com:443 >>> host: google.com\r\n
google.com:443 >>> connection: close\r\n
google.com:443 >>> \r\n
HTTP/1.1 301 Moved Permanently
Location: https://www.google.com/
Content-Type: text/html; charset=UTF-8
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-VDRuitCRV3iLQiNUCQ0HHA' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
Date: Fri, 03 Apr 2026 14:55:15 GMT
Expires: Sun, 03 May 2026 14:55:15 GMT
Cache-Control: public, max-age=2592000
Server: gws
Content-Length: 220
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000
Connection: close


Connection closed by server.
google.com:443 >>>
root@host:~$
```

What server is cloudflare on?
```
root@host:~$ interactivesocket tcp -ts cloudflare.com 443 | grep Server
Server: cloudflare
root@host:~$
```

How about asking root DNS server where's dot com:
```

0a1b0100000100000000000003636f6d0000020001
```