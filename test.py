from cryptography import x509
from cryptography.hazmat.backends import default_backend

from tls import read_certificate_key_from_file


def print_certificate_data(cert_file):
  certificate = read_certificate_key_from_file(cert_file)

  # Print basic information
  print("Subject:", certificate.subject)
  print("Issuer:", certificate.issuer)
  print("Not Valid Before:", certificate.not_valid_before_utc)
  print("Not Valid After:", certificate.not_valid_after_utc)
  print("Serial Number:", certificate.serial_number)

  # Print extensions
  print("\nExtensions:")
  for extension in certificate.extensions:
    print(extension)


# Example usage
cert_file = "rootCA.crt"
print_certificate_data(cert_file)
