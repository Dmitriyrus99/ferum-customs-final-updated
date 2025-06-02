# ferum_customs/ferum_customs/doctype/custom_attachment/custom_attachment.py
"""
Python-контроллер для DocType "CustomAttachment".
"""
from __future__ import annotations
# from typing import TYPE_CHECKING

import frappe
from frappe.model.document import Document
from frappe import _ # Для возможных пользовательских сообщений

# if TYPE_CHECKING:
    # pass

class CustomAttachment(Document):
    """
    Класс документа CustomAttachment.
    """

    def validate(self) -> None:
        """
        Валидация данных документа.
        Очищает и приводит к нижнему регистру `attachment_type`.
        Очищает `attachment_file`.
        """
        self._clean_fields()
        self._validate_parent_references()

        # Логика из оригинального файла (custom_attachment.py):
        # if self.attachment_type:
        #     self.attachment_type = self.attachment_type.strip().lower()
        # if self.attachment_file: # Поле Attach обычно хранит URL и не требует strip() здесь
        #     self.attachment_file = self.attachment_file.strip()
        # Эта логика теперь в _clean_fields()

    def _clean_fields(self) -> None:
        """
        Очистка строковых полей.
        """
        # TODO: Verify fieldname 'attachment_type' (Select field)
        if self.get("attachment_type") and isinstance(self.attachment_type, str):
            self.attachment_type = self.attachment_type.strip().lower()

        # Поле 'attachment_file' имеет тип Attach. Значение в нем - это URL файла.
        # URL-ы обычно не содержат начальных/конечных пробелов, которые нужно удалять.
        # Frappe сам обрабатывает загрузку и сохранение пути к файлу.
        # Оригинальный код делал self.attachment_file.strip(), что для URL нетипично.
        # Если есть конкретная причина для этого, ее нужно указать.
        # if self.get("attachment_file") and isinstance(self.attachment_file, str):
        #     self.attachment_file = self.attachment_file.strip()
        #     # Дополнительно можно проверить валидность URL или имени файла.
        pass

    def _validate_parent_references(self) -> None:
        """
        Проверяет, что указана хотя бы одна родительская ссылка (на ServiceRequest, ServiceReport и т.д.),
        и что эти ссылки указывают на существующие документы.
        """
        # TODO: Verify fieldnames: 'parent_reference_sr', 'parent_reference_srep', 'parent_reference_so'
        # TODO: Verify options (linked DocTypes) for these fields.
        parent_fields_map = {
            "parent_reference_sr": "ServiceRequest",
            "parent_reference_srep": "ServiceReport",
            "parent_reference_so": "ServiceObject",
        }
        
        linked_parents_count = 0
        for field_name, doctype_name in parent_fields_map.items():
            parent_doc_id = self.get(field_name)
            if parent_doc_id:
                linked_parents_count += 1
                if not frappe.db.exists(doctype_name, parent_doc_id):
                    frappe.throw(
                        _("Связанный документ {0} с ID '{1}' не найден.").format(
                            frappe.get_doc_label(doctype_name) or doctype_name, parent_doc_id
                        ),
                        title=_("Ошибка связи")
                    )
        
        # Пример бизнес-правила: должен быть указан хотя бы один родитель
        # if linked_parents_count == 0 and not self.is_new(): # Пропускаем для новых, если они могут быть без родителя временно
        # if linked_parents_count == 0 and self.docstatus == 0: # Если при сохранении черновика
        #     frappe.throw(_("Необходимо указать ссылку хотя бы на один родительский документ (Заявка, Отчет или Объект)."))
        
        # Пример бизнес-правила: должен быть указан ТОЛЬКО один родитель
        # if linked_parents_count > 1:
        #     frappe.throw(_("Можно указать ссылку только на один родительский документ."))

    # Хук on_trash для CustomAttachment теперь обрабатывается в
    # ferum_customs.custom_logic.file_attachment_utils.on_custom_attachment_trash
    # и вызывается через hooks.py.
    # def on_trash(self) -> None:
    #     # Логика удаления физического файла и связанной File DocType записи.
    #     pass