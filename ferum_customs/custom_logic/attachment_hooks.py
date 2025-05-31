"""Whitelisted-методы для работы с файлами вложений.

Исправлена уязвимость Path-Traversal в `delete_attachment_file`.
"""

from __future__ import annotations

import os
from pathlib import Path

import frappe
from frappe import _


@frappe.whitelist()
def delete_attachment_file(attachment_name: str) -> None:
    """Безопасно удалить файл из `public/files`.

    Args:
        attachment_name: Имя файла, полученное от клиента.

    Raises:
        frappe.DoesNotExistError: Если файл не найден.
        frappe.PermissionError:   Если путь выходит за пределы `public/files`.
    """
    # Получить только базовое имя, удалив возможные «../» и пути
    safe_name = os.path.basename(attachment_name)

    # Полный абсолютный путь к ожидаемой папке
    base_dir = Path(frappe.get_site_path("public", "files")).resolve()
    file_path = (base_dir / safe_name).resolve()

    # Убедиться, что файл действительно внутри `public/files`
    if not str(file_path).startswith(str(base_dir)):
        raise frappe.PermissionError(_("Неверный путь вложения."))

    if not file_path.exists():
        raise frappe.DoesNotExistError(_("Файл {0} не найден.").format(safe_name))

    file_path.unlink()  # удаляем файл
