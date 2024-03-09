import os
import sys
import tls
import argparse

DEFAULT_PRIVATE_KEY_FILENAME = "root-ca.key"
DEFAULT_CERTIFICATE_FILENAME = "root-ca.crt"


class Parser:
  key_size: int
  duration: int
  key_filename: str
  cert_filename: str
  domains: []


def print_all_help():
  print(
      """
Usage of tls tool:
  
  tls --help

""")


def generate_private_key(filename: str = DEFAULT_PRIVATE_KEY_FILENAME):
  private_key = tls.generate_private_key()
  tls.write_private_key(private_key=private_key, file_name=filename)
  return private_key, filename


def init(parser: Parser):
  private_key = tls.generate_private_key(key_size=parser.key_size)
  certificate = tls.sign_certificate_key(
      private_key=private_key,
      certificate_duration_days=parser.duration
  )
  tls.write_private_key(private_key, parser.key_filename)
  tls.write_certificate_file(certificate, parser.cert_filename)
  print(f"Save private key to {parser.key_filename}")
  print(f"Save certificate to {parser.cert_filename}")


def sign(parser: Parser):
  if len(parser.domains) == 0:
    print("Error: Required a domain!")
    return
  invalid_domains = [i for i in parser.domains if not tls.is_valid_domain(i)]
  if len(invalid_domains) > 0:
    print("ERROR: Invalid domain:", ",".join(invalid_domains))
    return
  if not os.path.exists(parser.key_filename):
    print("ERROR: Can not find private key file. Check private key filename or try to run: tls init")
    return
  if not os.path.exists(parser.cert_filename):
    print("ERROR: Can not find certificate file. Check certificate filename or try to run: tls init")
    return
  try:
    root_private_key = tls.read_private_key_from_file('root-ca.key')
  except:
    print("Invalid private key. Check private key filename or try to run: tls init")
    return
  try:
    root_certificate = tls.read_certificate_key_from_file('root-ca.crt')
  except:
    print("Invalid certificate. Check certificate filename or try to run: tls init")
    return
  for host in parser.domains:
    private_key, certificate = tls.generate_key_cert_for_host(
        root_private_key=root_private_key,
        root_certificate=root_certificate,
        host=host
    )
    output_key_file = f"{host}.key"
    output_cert_file = f"{host}.crt"
    tls.write_private_key(private_key, output_key_file)
    tls.write_certificate_file(certificate, output_cert_file)
    print(f"Save private key to {output_key_file}")
    print(f"Save certificate to {output_cert_file}")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("COMMAND", choices=["init", "sign", "show"])
  parser.add_argument('-k', '--key-file', metavar='\b',
                      required=False,
                      default=DEFAULT_PRIVATE_KEY_FILENAME,
                      dest="key_filename",
                      help="Private key filename. Default: root-ca.key"
                      )
  parser.add_argument('-c', '--cert-file', metavar='\b',
                      required=False,
                      default=DEFAULT_CERTIFICATE_FILENAME,
                      dest="cert_filename",
                      help="Certificate filename. Default: root-ca.crt"
                      )
  parser.add_argument('-d', "--duration",
                      metavar='\b',
                      default=tls.CERTIFICATE_DURATION_DAYS,
                      required=False, help="Certificate duration time. Default: 3560 days.")
  parser.add_argument('-s',
                      '--key-size',
                      metavar='\b',
                      default=tls.KEY_SIZE,
                      help=f"Private key size. Options: [2048, 3072, 4096]. Default: {tls.KEY_SIZE}."
                      )
  parser.add_argument('--common-name-by',
                      metavar='\b',
                      default=tls.COMMON_NAME,
                      required=False,
                      dest="common_name_by",
                      help="Common name by. Default: Self TLS"
                      )
  parser.add_argument('--organization-name-by',
                      metavar='\b',
                      default=tls.ORGANIZATION_NAME,
                      required=False,
                      dest="organization_name_by",
                      help="Organization name by. Default: Self TLS Inc."
                      )
  parser.add_argument('--country-name-by',
                      metavar='\b',
                      default=tls.COUNTRY_NAME,
                      required=False,
                      dest="country_name_by",
                      help="Country name by. Default: VN"
                      )
  parser.add_argument('--common-name-to',
                      metavar='\b',
                      default=None,
                      required=False,
                      dest="common_name_to",
                      help="Common name to. Default: Self TLS"
                      )
  parser.add_argument('--organization-name-to',
                      metavar='\b',
                      default=None,
                      required=False,
                      dest="organization_name_to",
                      help="Organization name to. Default: Self TLS Inc."
                      )
  parser.add_argument('--country-name-to',
                      metavar='\b',
                      default=None,
                      required=False,
                      dest="country_name_to",
                      help="Country name to. Default: VN"
                      )
  parser.add_argument('domains', nargs='*')
  try:
    args = parser.parse_args()
    if args.COMMAND == "init":
      init(args)
      return
    if args.COMMAND == "sign":
      sign(args)
      return
  except Exception as e:
    print(e)


if __name__ == "__main__":
  main()
