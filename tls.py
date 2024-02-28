import datetime
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.x509.base import Certificate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.x509.oid import NameOID

KEY_SIZE = 3072
PUBLIC_EXPONENT = 65537
COMMON_NAME = "Self TLS"
ORGANIZATION_NAME = "Self TLS Inc."
COUNTRY_NAME = "VN"
CERTIFICATE_DURATION_DAYS = 365


def generate_private_key(key_size=KEY_SIZE, public_exponent=PUBLIC_EXPONENT) -> RSAPrivateKey:
  """Generate a private key

  Args:
      key_size (int, optional): Size of rsa key [2048, 3072, 4096]. Defaults to `3072`.
      public_exponent (int, optional): RSA number. Defaults to `65537`.

  Returns:
      RSAPrivateKey: A RSA private key
  """
  private_key = rsa.generate_private_key(
      public_exponent=public_exponent,
      key_size=key_size,
      backend=default_backend()
  )
  return private_key


def sign_certificate_key(
    private_key: RSAPrivateKey,
    common_name=COMMON_NAME,
    organization_name=ORGANIZATION_NAME,
    country_name=COUNTRY_NAME,
    certificate_duration_days=CERTIFICATE_DURATION_DAYS
) -> Certificate:
  """Sign a new certificate key

  Args:
      private_key (RSAPrivateKey): RSA private key
      common_name (str, optional): _description_. Defaults to `Self TLS`.
      organization_name (str, optional): _description_. Defaults to `Self TLS Inc.`.
      country_name (str, optional): _description_. Defaults to `VN`.
      certificate_duration_days (int, optional): _description_. Defaults to `365`.

  Returns:
      Certificate: A Certificate
  """
  subject = issuer = x509.Name([
      x509.NameAttribute(NameOID.COMMON_NAME, common_name),
      x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
      x509.NameAttribute(NameOID.COUNTRY_NAME, country_name)
  ])
  certificate = x509 \
      .CertificateBuilder() \
      .subject_name(subject) \
      .issuer_name(issuer) \
      .public_key(private_key.public_key()) \
      .serial_number(x509.random_serial_number()) \
      .not_valid_before(datetime.datetime.utcnow()) \
      .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=certificate_duration_days)) \
      .sign(private_key, SHA256(), default_backend())
  return certificate


def generate_key_cert_for_host(
    root_private_key: RSAPrivateKey,
    root_certificate: Certificate,
    host: str,
    certificate_duration_days=CERTIFICATE_DURATION_DAYS
) -> tuple[RSAPrivateKey, Certificate]:
  private_key = generate_private_key()
  csr = x509.CertificateSigningRequestBuilder() \
      .subject_name(x509.Name([
          x509.NameAttribute(NameOID.COMMON_NAME, u"rancher.localhost.com")
      ])) \
      .sign(private_key, SHA256(), default_backend())
  certificate = x509.CertificateBuilder() \
      .subject_name(csr.subject) \
      .issuer_name(root_certificate.issuer) \
      .public_key(csr.public_key()).serial_number(x509.random_serial_number()) \
      .not_valid_before(datetime.datetime.utcnow()) \
      .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=certificate_duration_days)) \
      .add_extension(x509.SubjectAlternativeName([x509.DNSName(u"rancher.localhost.com")]), critical=False) \
      .sign(root_private_key, SHA256(), default_backend())
  return private_key, certificate


def write_private_key(private_key: RSAPrivateKey, file_name: str) -> None:
  """Write private key to file

  Args:
      private_key (RSAPrivateKey): RSAPrivateKey
      file_name (str): Name of file to write
  """
  with open(file_name, "wb") as file:
    file.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))


def read_private_key_from_file(file_name: str) -> RSAPrivateKey:
  with open(file_name, "rb") as file:
    private_key = serialization.load_pem_private_key(
        file.read(),
        password=None,
        backend=default_backend()
    )
  return private_key


def read_certificate_key_from_file(file_name: str) -> Certificate:
  """Read certificate key from file

  Args:
      file_name (str): Certificate file name

  Returns:
      Certificate: Certificate
  """
  with open(file_name, "rb") as file:
    certificate = x509.load_pem_x509_certificate(
        file.read(),
        backend=default_backend()
    )
  return certificate


def write_certificate_file(certificate: Certificate, file_name: str) -> None:
  """Write certificate key to file

  Args:
      certificate (Certificate): Certificate
      file_name (str): Name of file to write
  """
  with open(file_name, "wb") as file:
    file.write(certificate.public_bytes(serialization.Encoding.PEM))
