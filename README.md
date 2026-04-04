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
Interactive Socket v0.3.1, Scevenate (c) 2026
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
root@host:~$ interactivesocket udp -x d.root-servers.net 53
Interactive Socket v0.3.1, Scevenate (c) 2026
Creating endpoint for d.root-servers.net:53...
Endpoint created for d.root-servers.net:53. Use Ctrl+D (EOF) to destroy.
d.root-servers.net:53 >>> 0a1b0100000100000000000003636f6d0000020001
0a1b810000010000000d000f03636f6d0000020001c00c000200010002a300001401610c67746c642d73657276657273036e657400c00c000200010002a30000040162c023c00c000200010002a30000040163c023c00c000200010002a30000040164c023c00c000200010002a30000040165c023c00c000200010002a30000040166c023c00c000200010002a30000040167c023c00c000200010002a30000040168c023c00c000200010002a30000040169c023c00c000200010002a3000004016ac023c00c000200010002a3000004016bc023c00c000200010002a3000004016cc023c00c000200010002a3000004016dc023c021000100010002a3000004c005061ec041000100010002a3000004c0210e1ec051000100010002a3000004c01a5c1ec061000100010002a3000004c01f501ec071000100010002a3000004c00c5e1ec081000100010002a3000004c023331ec091000100010002a3000004c02a5d1ec0a1000100010002a3000004c036701ec0b1000100010002a3000004c02bac1ec0c1000100010002a3000004c0304f1ec0d1000100010002a3000004c034b21ec0e1000100010002a3000004c029a21ec0f1000100010002a3000004c037531ec021001c00010002a300001020010503a83e00000000000000020030c041001c00010002a300001020010503231d00000000000000020030
d.root-servers.net:53 >>>
Destroyed.
root@host:~$
```