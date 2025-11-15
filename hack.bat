mkdir C:\tmp\tls 2>nul
cd /d C:\tmp\tls

curl -L -o cfssl.exe https://github.com/cloudflare/cfssl/releases/download/v1.6.5/cfssl_1.6.5_windows_amd64.exe
curl -L -o cfssljson.exe https://github.com/cloudflare/cfssl/releases/download/v1.6.5/cfssljson_1.6.5_windows_amd64.exe

(
echo {
echo   "signing": {
echo     "default": {
echo       "usages": ["signing", "key encipherment", "server auth", "client auth"],
echo       "expiry": "876000h"
echo     }
echo   }
echo }
) > ca-config.json

(
echo {
echo   "CN": "Self TLS",
echo   "key": { "algo": "rsa", "size": 2048 },
echo   "names": [ { "O": "Self TLS", "OU": "Self TLS" } ],
echo   "ca": { "expiry": "876000h" }
echo }
) > ca-csr.json

(
echo {
echo   "CN": "Self TLS",
echo   "key": { "algo": "rsa", "size": 2048 },
echo   "names": [ { "O": "Self TLS", "OU": "Self TLS" } ],
echo   "hosts": [
echo     "localhost",
echo     "127.0.0.1"
echo   ]
echo }
) > req-csr.json

cfssl.exe gencert -initca ca-csr.json | cfssljson.exe -bare root
cfssl.exe gencert -ca root.pem -ca-key root-key.pem -config ca-config.json req-csr.json | cfssljson.exe -bare server

ren root.pem root.crt
ren root-key.pem root.key
ren server.pem server.crt
ren server-key.pem server.key

del root.csr 2>nul
del server.csr 2>nul
del ca-config.json ca-csr.json req-csr.json 2>nul
del cfssl.exe cfssljson.exe 2>nul
