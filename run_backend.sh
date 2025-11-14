#!/bin/bash
echo "Iniciando Gateway Inteligente - Backend"
python3 tools/generate_self_signed_cert.py
if [ -f "certs/cert.pem" ] && [ -f "certs/key.pem" ]; then
	echo "Iniciando com TLS (HTTPS) na porta 8000"
	uvicorn backend.main:app --reload --port 8000 --ssl-certfile certs/cert.pem --ssl-keyfile certs/key.pem
else
	echo "Certificados não encontrados; iniciando em HTTP (não recomendado em produção)"
	uvicorn backend.main:app --reload --port 8000
fi

