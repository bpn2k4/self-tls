package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha1"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/asn1"
	"encoding/pem"
	"math/big"
	"os"
	"time"
)

func main() {
	root_private_key, _ := rsa.GenerateKey(rand.Reader, 4096)
	root_public_key := root_private_key.Public().(*rsa.PublicKey)
	root_public_key_info, _ := x509.MarshalPKIXPublicKey(root_public_key)
	var PublicKeyInfo struct {
		Algorithm        pkix.AlgorithmIdentifier
		SubjectPublicKey asn1.BitString
	}
	asn1.Unmarshal(root_public_key_info, &PublicKeyInfo)
	skid := sha1.Sum(PublicKeyInfo.SubjectPublicKey.Bytes)
	serial_number_limit := new(big.Int).Lsh(big.NewInt(1), 128)
	serial_number, _ := rand.Int(rand.Reader, serial_number_limit)
	root_template := &x509.Certificate{
		SerialNumber: serial_number,
		Subject: pkix.Name{
			Organization:       []string{"Self TLS"},
			OrganizationalUnit: []string{"Self TLS"},
			CommonName:         "Self TLS",
		},
		SubjectKeyId:          skid[:],
		NotAfter:              time.Now().AddDate(20, 0, 0),
		NotBefore:             time.Now(),
		KeyUsage:              x509.KeyUsageCertSign,
		BasicConstraintsValid: true,
		IsCA:                  true,
		MaxPathLenZero:        true,
	}
	root_private_key_byte, _ := x509.MarshalPKCS8PrivateKey(root_private_key)

	root_certificate_byte, _ := x509.CreateCertificate(rand.Reader, root_template, root_template, root_public_key, root_private_key)

	_ = os.WriteFile("./cert/ca.key", pem.EncodeToMemory(
		&pem.Block{Type: "PRIVATE KEY", Bytes: root_private_key_byte}), 0644)
	_ = os.WriteFile("./cert/ca.crt", pem.EncodeToMemory(
		&pem.Block{Type: "CERTIFICATE", Bytes: root_certificate_byte}), 0644)

	private_key, _ := rsa.GenerateKey(rand.Reader, 4096)
	public_key := private_key.Public().(*rsa.PublicKey)
	serial_number, _ = rand.Int(rand.Reader, serial_number_limit)
	template := &x509.Certificate{
		SerialNumber: serial_number,
		Subject: pkix.Name{
			Organization:       []string{"Self TLS"},
			OrganizationalUnit: []string{"Self TLS"},
		},
		NotBefore: time.Now(),
		NotAfter:  time.Now().AddDate(10, 0, 0),
		DNSNames:  []string{"localhost", "localhost.com", "*.localhost.com"},
		KeyUsage:  x509.KeyUsageKeyEncipherment | x509.KeyUsageDigitalSignature,
	}

	private_key_byte, _ := x509.MarshalPKCS8PrivateKey(private_key)
	certificate_byte, _ := x509.CreateCertificate(rand.Reader, template, root_template, public_key, root_private_key)

	_ = os.WriteFile("./cert/ssl.key", pem.EncodeToMemory(
		&pem.Block{Type: "PRIVATE KEY", Bytes: private_key_byte}), 0644)
	_ = os.WriteFile("./cert/ssl.crt", pem.EncodeToMemory(
		&pem.Block{Type: "CERTIFICATE", Bytes: certificate_byte}), 0644)
}
