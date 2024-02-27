from tls import (
    generate_private_key,
    sign_certificate_key,
    write_certificate_file,
    write_private_key
)


if __name__ == "__main__":
  private_key = generate_private_key()
  certificate = sign_certificate_key(private_key)
  key_file = "rootCA.key"
  cert_file = "rootCA.crt"
  write_private_key(private_key, key_file)
  write_certificate_file(certificate, cert_file)
