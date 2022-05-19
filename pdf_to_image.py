import os
from pathlib import Path
from pdf2image import convert_from_path

# poppler/binを環境変数PATHに追加する
# poppler_dir = Path(__file__).parent.absolute() / "poppler/bin"
# os.environ["PATH"] += os.pathsep + str(poppler_dir)

# PDFファイルのパス
pdf_path = Path("./pdf_file/05B31405A1 MTL-FRONT.pdf")

# PDF -> Image に変換（150dpi）
pages = convert_from_path(str(pdf_path), 200)

# 画像ファイルを１ページずつ保存
image_dir = Path("./image_file")
for i, page in enumerate(pages):
    file_name = pdf_path.stem + "_{:02d}".format(i + 1) + ".jpeg"
    image_path = image_dir / file_name
    # JPEGで保存
    page.save(str(image_path), "JPEG")