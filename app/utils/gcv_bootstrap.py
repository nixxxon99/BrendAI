# app/utils/gcv_bootstrap.py
import os, json, pathlib

def ensure_gcv_credentials():
    """If env GCV_JSON is present and GOOGLE_APPLICATION_CREDENTIALS file is missing,
    write JSON to that path so google-cloud-vision can work on Render.
    """
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    gcv_json  = os.getenv("GCV_JSON", "").strip()
    if not cred_path:
        return False
    p = pathlib.Path(cred_path)
    if p.exists():
        return True
    if not gcv_json:
        return False
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        # sanity check valid json
        data = json.loads(gcv_json)
        p.write_text(json.dumps(data), encoding="utf-8")
        os.chmod(p, 0o600)
        return True
    except Exception:
        return False
