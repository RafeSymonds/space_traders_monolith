import importlib
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

package_path = Path(__file__).parent


def __walk_and_import_routers(path: Path, module_prefix: str):
    init_file = path / "__init__.py"
    if init_file.exists():
        module_name = module_prefix
        module = importlib.import_module(module_name)
        if hasattr(module, "router"):
            router.include_router(module.router)

    for child in path.iterdir():
        if child.is_dir():
            __walk_and_import_routers(child, f"{module_prefix}.{child.name}")


__walk_and_import_routers(package_path, __name__)
