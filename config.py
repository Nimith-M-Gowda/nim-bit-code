import os
import shutil

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
   """Load settings and place relative generated-data paths in the workspace."""
   _ensure_runtime_ssl_certs()
   app_root = Path(__file__).resolve().parent
   workspace_root = Path.cwd().resolve()
   settings = yaml.safe_load((app_root / "config.yaml").read_text())

   for section, key in (("chromadb", "persist_dir"), ("memory", "db_path")):
       path = Path(settings[section][key]).expanduser()
       if not path.is_absolute():
           path = workspace_root / path
       settings[section][key] = str(path.resolve())

   _migrate_legacy_generated_data(workspace_root, settings)
   Path(workspace_root / ".nim-bit-code").mkdir(parents=True, exist_ok=True)
   return settings


def _migrate_legacy_generated_data(workspace_root: Path, settings: dict) -> None:
   """Move legacy workspace data into the configured .nim-bit-code locations."""
   migrations = (
       (workspace_root / ".chromadb", Path(settings["chromadb"]["persist_dir"])),
       (workspace_root / ".memory", Path(settings["memory"]["db_path"]).parent),
   )

   for source, destination in migrations:
       if not source.exists() or source.resolve() == destination.resolve():
           continue

       destination.parent.mkdir(parents=True, exist_ok=True)
       if not destination.exists():
           shutil.move(str(source), str(destination))
           continue

       conflicts = []
       for item in source.rglob("*"):
           target = destination / item.relative_to(source)
           if target.exists() and (
               item.is_symlink() or not item.is_dir() or not target.is_dir()
           ):
               conflicts.append(target)
       if conflicts:
           paths = ", ".join(str(path) for path in conflicts)
           raise FileExistsError(
               f"Cannot migrate {source} into {destination}; "
               f"these destination paths already exist: {paths}"
           )

       for item in sorted(source.rglob("*")):
           target = destination / item.relative_to(source)
           if item.is_dir() and not item.is_symlink():
               target.mkdir(parents=True, exist_ok=True)
           else:
               target.parent.mkdir(parents=True, exist_ok=True)
               shutil.move(str(item), str(target))

       for directory in sorted(
           (path for path in source.rglob("*") if path.is_dir() and not path.is_symlink()),
           reverse=True,
       ):
           directory.rmdir()
       source.rmdir()


config = load_config()
