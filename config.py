import os

import yaml
from pathlib import Path


def _ensure_runtime_ssl_certs() -> None:
   """Ensure outbound HTTPS clients use a valid CA bundle for model downloads."""
   if os.environ.get("SSL_CERT_FILE") or os.environ.get("SSL_CERT_DIR"):
       return

   try:
       import certifi
   except ModuleNotFoundError:
       return

   cert_path = certifi.where()
   if not cert_path or not Path(cert_path).exists():
       return

   for key in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"):
       os.environ.setdefault(key, cert_path)

   os.environ.setdefault("SSL_CERT_DIR", str(Path(cert_path).parent))


def load_config() -> dict:
   """Load settings from config.yaml at the project root."""
   _ensure_runtime_ssl_certs()
   return yaml.safe_load((Path(__file__).parent / "config.yaml").read_text())


config = load_config()
