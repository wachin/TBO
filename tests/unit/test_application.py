from pathlib import Path

import tbo.application


def test_application_finds_repository_asset_directory() -> None:
    repository_root = Path(tbo.application.__file__).resolve().parents[2]

    assert (repository_root / "data" / "doodle" / "tbo" / "logo" / "tbo.svg").is_file()
