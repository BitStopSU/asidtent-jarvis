"""
JARVIS - File Manager
Работа с любыми файлами
"""
import os
import json
import zipfile
import shutil
from datetime import datetime
from pathlib import Path


class FileManager:
    """Управление файлами"""

    def __init__(self, base_dir="data/files"):
        self.base_dir = base_dir
        self.uploads = os.path.join(base_dir, "uploads")
        self.outputs = os.path.join(base_dir, "outputs")
        self.temp = os.path.join(base_dir, "temp")

        for d in [self.uploads, self.outputs, self.temp]:
            os.makedirs(d, exist_ok=True)

    # ============ ЧТЕНИЕ ============

    def read(self, filepath):
        """Читает файл и возвращает содержимое"""
        if not os.path.exists(filepath):
            return f"Файл не найден: {filepath}"

        ext = os.path.splitext(filepath)[1].lower()

        try:
            # Текстовые
            if ext in ['.txt', '.md', '.log', '.py', '.js', '.html',
                       '.css', '.json', '.xml', '.yaml', '.yml', '.csv']:
                return self._read_text(filepath)

            # Изображения (OCR)
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                return self._read_image(filepath)

            # Excel
            elif ext in ['.xlsx', '.xls']:
                return self._read_excel(filepath)

            # PDF
            elif ext == '.pdf':
                return self._read_pdf(filepath)

            # Архивы
            elif ext in ['.zip']:
                return self._read_zip(filepath)

            else:
                return f"Формат {ext} не поддерживается"

        except Exception as e:
            return f"Ошибка чтения: {e}"

    def _read_text(self, filepath):
        """Чтение текстового файла"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _read_image(self, filepath):
        """OCR — текст с изображения"""
        try:
            from PIL import Image
            import pytesseract
            image = Image.open(filepath)
            text = pytesseract.image_to_string(image, lang='rus+eng')
            return text if text.strip() else "Текст не найден"
        except ImportError:
            return "Установите: pip install pillow pytesseract"
        except Exception as e:
            return f"Ошибка OCR: {e}"

    def _read_excel(self, filepath):
        """Чтение Excel"""
        try:
            import pandas as pd
            df = pd.read_excel(filepath)
            return df.to_string()
        except ImportError:
            return "Установите: pip install pandas openpyxl"

    def _read_pdf(self, filepath):
        """Чтение PDF"""
        try:
            import PyPDF2
            text = ""
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except ImportError:
            return "Установите: pip install PyPDF2"

    def _read_zip(self, filepath):
        """Список файлов в архиве"""
        with zipfile.ZipFile(filepath, 'r') as z:
            files = z.namelist()
            return f"В архиве {len(files)} файлов:\n" + "\n".join(files[:50])

    # ============ ЗАПИСЬ ============

    def write(self, filename, content, folder="outputs"):
        """Записывает файл"""
        path = os.path.join(self.base_dir, folder, filename)

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return path
        except Exception as e:
            return f"Ошибка записи: {e}"

    def create_excel(self, data, filename="table.xlsx"):
        """Создаёт Excel"""
        try:
            import pandas as pd
            df = pd.DataFrame(data)
            path = os.path.join(self.outputs, filename)
            df.to_excel(path, index=False)
            return path
        except ImportError:
            return "Установите: pip install pandas openpyxl"

    def create_csv(self, data, filename="table.csv"):
        """Создаёт CSV"""
        try:
            import pandas as pd
            df = pd.DataFrame(data)
            path = os.path.join(self.outputs, filename)
            df.to_csv(path, index=False)
            return path
        except ImportError:
            return "Установите: pip install pandas"

    # ============ РЕДАКТИРОВАНИЕ ============

    def edit_text(self, filepath, old, new):
        """Замена текста в файле"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            content = content.replace(old, new)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Заменено '{old}' → '{new}'"
        except Exception as e:
            return f"Ошибка: {e}"

    def edit_image(self, filepath, text=None, operation=None):
        """Редактирование изображения"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            image = Image.open(filepath)

            if operation == 'grayscale':
                image = image.convert('L')
            elif operation == 'rotate':
                image = image.rotate(90)
            elif operation == 'flip':
                image = image.transpose(Image.FLIP_LEFT_RIGHT)

            if text:
                draw = ImageDraw.Draw(image)
                try:
                    font = ImageFont.truetype("arial.ttf", 30)
                except Exception:
                    font = ImageFont.load_default()
                draw.text((10, 10), text, fill="white", font=font)

            output = os.path.join(
                self.outputs,
                "edited_" + os.path.basename(filepath)
            )
            image.save(output)
            return output
        except ImportError:
            return "Установите: pip install pillow"

    # ============ УПРАВЛЕНИЕ ============

    def list_files(self, folder="uploads"):
        """Список файлов в папке"""
        path = os.path.join(self.base_dir, folder)
        if not os.path.exists(path):
            return []
        return os.listdir(path)

    def delete(self, filepath):
        """Удалить файл"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return f"Удалён: {filepath}"
            return "Файл не найден"
        except Exception as e:
            return f"Ошибка: {e}"

    def copy(self, src, dst):
        """Копировать файл"""
        try:
            shutil.copy2(src, dst)
            return f"Скопировано: {dst}"
        except Exception as e:
            return f"Ошибка: {e}"

    def get_info(self, filepath):
        """Информация о файле"""
        if not os.path.exists(filepath):
            return None

        stat = os.stat(filepath)
        return {
            "name": os.path.basename(filepath),
            "size": stat.st_size,
            "size_human": self._human_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": os.path.splitext(filepath)[1].lower()
        }

    def _human_size(self, size):
        """Человекочитаемый размер"""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} ПБ"

    # ============ БЭКАП ============

    def backup_folder(self, folder_path, backup_name=None):
        """Создать zip-архив папки"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        backup_path = os.path.join(self.outputs, backup_name)

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as z:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        z.write(file_path, arcname)
            return backup_path
        except Exception as e:
            return f"Ошибка бэкапа: {e}"