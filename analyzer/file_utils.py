from pathlib import Path
import logging

def iter_log_files(path: str):
    p = Path(path)

    if not p.exists():
        logging.error(f"Path not found: {path}")
        raise FileNotFoundError(f"Path not found: {path}")

    if p.is_file():
        if p.suffix == ".log":
            yield p
        return

    elif p.is_dir():
        try:
            for f in p.rglob("*.log"):
                try:
                    # بررسی دسترسی خواندن به فایل
                    if not f.is_file():
                        continue
                    f.open("r").close()  # تست باز شدن فایل
                    yield f
                except PermissionError:
                    logging.warning(f"Permission denied for file: {f}")
                    raise 
                
        except PermissionError:
            logging.error(f"Permission denied for directory: {p}")
            raise



