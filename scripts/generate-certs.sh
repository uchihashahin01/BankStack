#!/bin/bash
# ============================================================
# BankStack — SSL Certificate Generator
# Generates self-signed certs for Wazuh Indexer cluster
# ============================================================

set -euo pipefail

CERT_DIR="$(cd "$(dirname "$0")/.." && pwd)/config/wazuh_indexer_ssl_certs"
DAYS=3650
KEY_SIZE=2048

echo "[*] BankStack Certificate Generator"
echo "[*] Output directory: ${CERT_DIR}"

mkdir -p "${CERT_DIR}"

# Check if certs already exist
if [ -f "${CERT_DIR}/root-ca.pem" ]; then
    echo "[!] Certificates already exist. Remove them first to regenerate."
    echo "[!] Run: rm -rf ${CERT_DIR}/*.pem"
    exit 0
fi

echo "[*] Generating Root CA..."
openssl genrsa -out "${CERT_DIR}/root-ca-key.pem" ${KEY_SIZE} 2>/dev/null
openssl req -new -x509 -sha256 -key "${CERT_DIR}/root-ca-key.pem" \
    -out "${CERT_DIR}/root-ca.pem" -days ${DAYS} \
    -subj "/C=BD/ST=Dhaka/L=Dhaka/O=BankStack/OU=SOC/CN=BankStack Root CA" 2>/dev/null

generate_cert() {
    local name=$1
    local cn=$2

    echo "[*] Generating certificate for: ${name} (CN=${cn})"

    # Generate key
    openssl genrsa -out "${CERT_DIR}/${name}-key.pem" ${KEY_SIZE} 2>/dev/null

    # Create CSR
    openssl req -new -key "${CERT_DIR}/${name}-key.pem" \
        -out "${CERT_DIR}/${name}.csr" \
        -subj "/C=BD/ST=Dhaka/L=Dhaka/O=BankStack/OU=SOC/CN=${cn}" 2>/dev/null

    # Create extensions file for SAN
    cat > "${CERT_DIR}/${name}-ext.cnf" <<EOF
[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${cn}
DNS.2 = localhost
IP.1 = 127.0.0.1
EOF

    # Sign certificate
    openssl x509 -req -in "${CERT_DIR}/${name}.csr" \
        -CA "${CERT_DIR}/root-ca.pem" -CAkey "${CERT_DIR}/root-ca-key.pem" \
        -CAcreateserial -out "${CERT_DIR}/${name}.pem" \
        -days ${DAYS} -sha256 \
        -extfile "${CERT_DIR}/${name}-ext.cnf" -extensions v3_req 2>/dev/null

    # Cleanup CSR and extension files
    rm -f "${CERT_DIR}/${name}.csr" "${CERT_DIR}/${name}-ext.cnf"
}

# Generate certificates for each component
generate_cert "wazuh-indexer" "wazuh-indexer"
generate_cert "wazuh-manager" "wazuh-manager"
generate_cert "wazuh-dashboard" "wazuh-dashboard"
generate_cert "admin" "admin"

# Set permissions
chmod 400 "${CERT_DIR}"/*-key.pem
chmod 444 "${CERT_DIR}"/*.pem

# Cleanup serial file
rm -f "${CERT_DIR}/root-ca.srl"

echo ""
echo "[+] All certificates generated successfully!"
echo "[+] Location: ${CERT_DIR}"
ls -la "${CERT_DIR}"
