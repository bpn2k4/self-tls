mkdir -p /tmp/tls
cd /tmp/tls

wget https://github.com/cloudflare/cfssl/releases/download/v1.6.5/cfssl_1.6.5_linux_amd64 -O cfssl
wget https://github.com/cloudflare/cfssl/releases/download/v1.6.5/cfssljson_1.6.5_linux_amd64 -O cfssljson
chmod +x cfssl cfssljson

cat <<EOF > ca-config.json
{
  "signing": {
    "default": {
      "usages": ["signing", "key encipherment", "server auth", "client auth"],
      "expiry": "876000h"
    }
  }
}
EOF

cat <<EOF > ca-csr.json
{
  "CN": "Self TLS",
  "key": { "algo": "rsa", "size": 2048 },
  "names": [{ "O": "Self TLS", "OU": "Self TLS" }],
  "ca": { "expiry": "876000h" }
}
EOF

cat <<EOF > req-csr.json
{
  "CN": "Self TLS",
  "key": { "algo": "rsa",  "size": 2048 },
  "names": [{ "O": "Self TLS", "OU": "Self TLS" }],
  "hosts": [
    "localhost",
    "127.0.0.1"
  ]
}
EOF

./cfssl gencert -initca ca-csr.json | ./cfssljson -bare root
./cfssl gencert -ca root.pem -ca-key root-key.pem -config ca-config.json req-csr.json | ./cfssljson -bare server
mv root.pem root.crt
mv root-key.pem root.key
mv server.pem server.crt
mv server-key.pem server.key
rm -rf root.csr server.csr
rm -rf ca-config.json ca-csr.json req-csr.json
rm -rf cfssl cfssljson
