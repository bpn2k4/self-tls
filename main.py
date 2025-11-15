import os
import datetime
import typing
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from cryptography.hazmat import backends

ROOT_KEY_FILE = 'root.key'
ROOT_CERT_FILE = 'root.crt'
SERVER_KEY_FILE = 'server.key'
SERVER_CERT_FILE = 'server.crt'
DOMAIN = ['localhost']
IP = ['127.0.0.1']


def _convert_ip(ip: str) -> typing.Union[IPv4Address, IPv6Address, IPv4Network, IPv6Network]:
  try:
    return IPv4Address(ip)
  except ValueError:
    pass
  try:
    return IPv6Address(ip)
  except ValueError:
    pass
  try:
    return IPv4Network(ip)
  except ValueError:
    pass
  return IPv6Network(ip)


if os.path.exists(ROOT_KEY_FILE):
  with open(ROOT_KEY_FILE, 'rb') as f:
    ca_private_key = serialization.load_pem_private_key(f.read(), password=None, backend=backends.default_backend())
else:
  ca_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=backends.default_backend())
  with open(ROOT_KEY_FILE, 'wb') as f:
    f.write(ca_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

if os.path.exists(ROOT_CERT_FILE):
  with open(ROOT_CERT_FILE, 'rb') as f:
    ca_cert = x509.load_pem_x509_certificate(f.read(), backend=backends.default_backend())
else:
  subject = issuer = x509.Name([
      x509.NameAttribute(NameOID.COMMON_NAME, 'Self TLS'),
      x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Self TLS'),
      x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, 'Self TLS'),
  ])
  ca_cert = (
      x509.CertificateBuilder()
      .subject_name(subject)
      .issuer_name(issuer)
      .public_key(ca_private_key.public_key())
      .serial_number(x509.random_serial_number())
      .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1))
      .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365*10))
      .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
      .sign(ca_private_key, hashes.SHA256(), backends.default_backend())
  )
  with open(ROOT_CERT_FILE, 'wb') as f:
    f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

if os.path.exists(SERVER_KEY_FILE):
  with open(SERVER_KEY_FILE, 'rb') as f:
    server_key = serialization.load_pem_private_key(f.read(), password=None, backend=backends.default_backend())
else:
  server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=backends.default_backend())
  with open(SERVER_KEY_FILE, 'wb') as f:
    f.write(server_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

if os.path.exists(SERVER_CERT_FILE):
  with open(SERVER_CERT_FILE, 'rb') as f:
    server_cert = x509.load_pem_x509_certificate(f.read(), backend=backends.default_backend())
else:
  subject = x509.Name([
      x509.NameAttribute(NameOID.COMMON_NAME, 'Self TLS'),
      x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Self TLS'),
      x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, 'Self TLS'),
  ])

  san = x509.SubjectAlternativeName(
      [x509.DNSName(d) for d in DOMAIN] + [x509.IPAddress(_convert_ip(ip)) for ip in IP]
  )

  server_cert = (
      x509.CertificateBuilder()
      .subject_name(subject)
      .issuer_name(ca_cert.subject)
      .public_key(server_key.public_key())
      .serial_number(x509.random_serial_number())
      .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1))
      .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365*10))
      .add_extension(san, critical=False)
      .add_extension(
          x509.BasicConstraints(ca=False, path_length=None),
          critical=True
      )
      .add_extension(
          x509.KeyUsage(
              digital_signature=True,
              key_encipherment=True,
              content_commitment=False,
              data_encipherment=False,
              key_agreement=False,
              key_cert_sign=False,
              crl_sign=False,
              encipher_only=False,
              decipher_only=False
          ),
          critical=True
      )
      .add_extension(
          x509.ExtendedKeyUsage([
              ExtendedKeyUsageOID.SERVER_AUTH,
              ExtendedKeyUsageOID.CLIENT_AUTH,
          ]),
          critical=True
      )
      .add_extension(
          x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_private_key.public_key()),
          critical=False
      )
      .add_extension(
          x509.SubjectKeyIdentifier.from_public_key(server_key.public_key()),
          critical=False
      )
      .sign(ca_private_key, hashes.SHA256(), backends.default_backend())
  )

  with open(SERVER_CERT_FILE, 'wb') as f:
    f.write(server_cert.public_bytes(serialization.Encoding.PEM))
