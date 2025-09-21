import os


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def static_dir() -> str:
    return os.path.join(project_root(), "static")


