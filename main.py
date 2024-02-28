from tls import (
    generate_private_key,
    sign_certificate_key,
    write_certificate_file,
    write_private_key,
    generate_key_cert_for_host,
    read_private_key_from_file,
    read_certificate_key_from_file
)


def generate_pair_key():
  private_key = generate_private_key()
  certificate = sign_certificate_key(private_key)
  key_file = "rootCA.key"
  cert_file = "rootCA.crt"
  write_private_key(private_key, key_file)
  write_certificate_file(certificate, cert_file)


if __name__ == "__main__":
  key_file = "rootCA.key"
  cert_file = "rootCA.crt"
  root_private_key = read_private_key_from_file(key_file)
  root_certificate = read_certificate_key_from_file(cert_file)
  private_key, certificate = generate_key_cert_for_host(
      root_private_key=root_private_key,
      root_certificate=root_certificate,
      host="localhost.com"
  )
  output_key_file = "localhost.com.key"
  output_cert_file = "localhost.com.crt"
  write_private_key(private_key, output_key_file)
  write_certificate_file(certificate, output_cert_file)
