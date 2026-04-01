import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


prepare_icon = load_module("prepare_icon", "aso-appstore-icon/prepare_icon.py")
preview_icons = load_module("preview_icons", "aso-appstore-icon/preview_icons.py")


class PrepareIconTests(unittest.TestCase):
    def test_prepare_icon_center_crops_and_resizes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "source.png"
            output_path = Path(tmpdir) / "prepared.png"

            image = Image.new("RGB", (300, 180), "#224488")
            image.paste(Image.new("RGB", (100, 180), "#CC3344"), (200, 0))
            image.save(input_path)

            prepare_icon.prepare_icon(input_path, output_path, 128, "auto")

            with Image.open(output_path) as prepared:
                self.assertEqual(prepared.size, (128, 128))

    def test_prepare_icon_flattens_alpha_with_requested_matte(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "alpha.png"
            output_path = Path(tmpdir) / "prepared.png"

            image = Image.new("RGBA", (120, 80), (0, 0, 0, 0))
            image.paste(Image.new("RGBA", (40, 40), (255, 0, 0, 255)), (40, 20))
            image.save(input_path)

            prepare_icon.prepare_icon(input_path, output_path, 64, "#112233")

            with Image.open(output_path) as prepared:
                self.assertEqual(prepared.size, (64, 64))
                self.assertEqual(prepared.getpixel((0, 0)), (17, 34, 51))


class PreviewIconsTests(unittest.TestCase):
    def test_create_board_outputs_expected_dimensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            icon_paths = []
            for index, color in enumerate(("#2E6CF6", "#F97316", "#10B981"), start=1):
                icon_path = tmp / f"icon-{index}.png"
                Image.new("RGB", (1024, 1024), color).save(icon_path)
                icon_paths.append(icon_path)

            output_path = tmp / "board.png"
            preview_icons.create_board(
                icon_paths=icon_paths,
                output_path=output_path,
                labels=["Version 1", "Version 2", "Version 3"],
                app_name="PunchAI",
                title="PunchAI Icon Review",
            )

            expected_width = (
                preview_icons.PADDING * 2
                + len(icon_paths) * preview_icons.COLUMN_W
                + (len(icon_paths) - 1) * preview_icons.COLUMN_GAP
            )
            expected_height = (
                preview_icons.PADDING * 2
                + preview_icons.TITLE_H
                + preview_icons.HERO_CARD_H
                + preview_icons.CONTEXT_CARD_H
                + preview_icons.BOTTOM_STRIP_H
                + preview_icons.LABEL_GAP * 4
            )

            with Image.open(output_path) as board:
                self.assertEqual(board.size, (expected_width, expected_height))


if __name__ == "__main__":
    unittest.main()
