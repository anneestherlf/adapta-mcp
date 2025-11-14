@echo off
echo Iniciando Gateway Inteligente - Backend
REM Gerar certificado autoassinado se necessário e iniciar com TLS
python tools\generate_self_signed_cert.py
if exist certs\cert.pem (
	echo Iniciando com TLS (HTTPS) na porta 8000
	python -m uvicorn backend.main:app --reload --port 8000 --ssl-certfile certs\cert.pem --ssl-keyfile certs\key.pem
) else (
	echo Certificados não encontrados; iniciando em HTTP (não recomendado em produção)
	python -m uvicorn backend.main:app --reload --port 8000
)

