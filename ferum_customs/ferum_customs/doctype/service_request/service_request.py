# -*- coding: utf-8 -*-
# Copyright (c) 2025, Ferum LLC and contributors
# For license information, please see license.txt

"""
Контроллер DocType Service Request (service_request).

Этот модуль содержит серверную логику для DocType Service Request,
включая валидацию данных, обработчики событий жизненного цикла документа (hooks),
и другую бизнес-логику, специфичную для заявок на обслуживание.
"""

from __future__ import annotations # Для поддержки отложенных аннотаций типов
from typing import TYPE_CHECKING # Для type-checking циклических зависимостей

import frappe
from frappe.model.document import Document
from frappe.utils import now, get_link_to_form # Пример импорта для установки дат и ссылок

# Импорт констант из вашего приложения
from ferum_customs.constants import (
    ROLE_PROEKTNYJ_MENEDZHER,
    # STATUS_VYPOLNENA, # Пример, если используется в логике контроллера
    # STATUS_ZAKRYTA    # Пример
)

if TYPE_CHECKING:
    # Это для статических анализаторов типов, чтобы избежать реального импорта во время выполнения
    # если есть циклические зависимости или для улучшения автодополнения.
    # from frappe.types import DF # Пример для типов полей Frappe
    pass


class ServiceRequest(Document):
    """
    DocType "Service Request" представляет собой основную сущность для отслеживания
    запросов на сервисное обслуживание от клиентов или для внутренних нужд.
    Управляется через Workflow "Service Request Workflow".
    Имя документа (ID) генерируется согласно Naming Series: "SR-.YYYY.-.#####".
    """

    # --- События жизненного цикла (Lifecycle Hooks) ---

    def autoname(self) -> None:
        """
        Вызывается для установки имени документа (ID) при создании.
        Поскольку в service_request.json определен naming_series,
        стандартная логика Frappe автоматически сгенерирует имя.
        Этот метод можно оставить пустым или удалить, если не требуется кастомная логика autoname.
        """
        # frappe.model.naming.make_autoname(self.naming_series, doc=self) # Это вызывается автоматически
        pass

    def before_validate(self) -> None:
        """
        Вызывается перед основной валидацией (validate).
        Используется для предварительной обработки данных или установки значений по умолчанию
        до того, как сработают стандартные проверки Frappe и кастомные валидации.
        """
        # Пример: Автоматическое заполнение адреса из клиента, если он не указан
        if self.customer and not self.address_display:
            customer_address = frappe.db.get_value(
                "Address", {"link_doctype": "Customer", "link_name": self.customer, "is_primary_address": 1}, "address_line1"
            ) # Предполагается, что у клиента есть основной адрес
            if customer_address:
                self.address_display = customer_address

        # Обновление отображаемого статуса на основе workflow_state
        # Это более надежно делать здесь или в on_update, чем полагаться на fetch_from для workflow_state.
        if self.workflow_state:
            self.workflow_state_display = self.workflow_state

    def validate(self) -> None:
        """
        Основной метод валидации. Вызывается перед сохранением документа (insert/save).
        Здесь должны быть проверки на корректность и полноту данных.
        Обратите внимание: если этот DocType имеет хук 'validate' в hooks.py,
        то логика из custom_logic/service_request_hooks.py будет иметь приоритет
        или будет вызвана вместо этого метода, в зависимости от настроек Frappe.

        Текущая конфигурация в ferum_customs/hooks.py указывает:
        "ServiceRequest": {
            "validate": "ferum_customs.custom_logic.service_request_hooks.validate",
            ...
        }
        Это означает, что функция validate из custom_logic/service_request_hooks.py будет вызвана.
        Если вы хотите, чтобы и эта функция validate (из контроллера) тоже выполнялась,
        вам нужно либо вызвать ее явно из хука, либо убрать хук из hooks.py для validate.

        Для примера, здесь оставим некоторые базовые валидации, которые могут быть специфичны
        для контроллера или если хук будет удален/изменен.
        """
        self._ensure_request_code_is_generated() #

        if not self.subject:
            frappe.throw("Поле 'Тема заявки' является обязательным.")

        if not self.customer:
            frappe.throw("Поле 'Клиент' является обязательным.")

        if self.planned_start_datetime and self.planned_end_datetime and            self.planned_start_datetime > self.planned_end_datetime:
            frappe.throw("Планируемая дата начала не может быть позже планируемой даты окончания.")

        # Пример валидации из custom_logic/service_request_hooks.py, которую можна перенести сюда,
        # если хук validate из hooks.py будет указывать на этот контроллер или будет удален.
        # current_hook_validate_logic = frappe.get_doc("ServiceRequest", self.name) # Это неверно, нужно передавать self
        # from ferum_customs.custom_logic.service_request_hooks import validate as hook_validate
        # hook_validate(self) # Пример явного вызова, если нужно

    def before_insert(self) -> None:
        """
        Вызывается только один раз перед первой вставкой документа в базу данных.
        Не вызывается при последующих сохранениях (save).
        """
        self.request_datetime = now() # Установка даты и времени создания заявки

        # Генерация request_code (дополнительного кода заявки), как в вашем оригинальном файле
        # Эта логика теперь в _ensure_request_code_is_generated и вызывается из validate.
        # Если request_code должен генерироваться *только* один раз при создании и никогда не меняться,
        # то вызов _ensure_request_code_is_generated можно сделать здесь.
        # self._ensure_request_code_is_generated()

    def before_save(self) -> None:
        """
        Вызывается каждый раз перед сохранением документа (при insert и обычном save).
        """
        # Пример: Обновление имени инженера, если выбран пользователь-инженер
        if self.assigned_engineer_user and not self.engineer_name: # или если изменился assigned_engineer_user
            user_full_name = frappe.db.get_value("User", self.assigned_engineer_user, "full_name")
            if user_full_name:
                self.engineer_name = user_full_name

        # Обновляем workflow_state_display перед сохранением, если оно изменилось
        if self.workflow_state and self.workflow_state_display != self.workflow_state:
            self.workflow_state_display = self.workflow_state


    def on_update(self) -> None:
        """
        Вызывается после успешного сохранения документа (insert и save).
        В hooks.py этот хук для ServiceRequest (on_update_after_submit)
        направлен на ferum_customs.custom_logic.service_request_hooks.on_update_after_submit.
        Поэтому логика, определенная там, будет выполнена.
        Если нужна дополнительная логика именно здесь, ее можна добавить.
        """
        # Пример: Логика, которая должна выполняться после каждого сохранения,
        # независимо от хука on_update_after_submit (который может быть специфичен для "после submit").
        # frappe.msgprint(f"Заявка {self.name} обновлена.")
        pass

    def on_submit(self) -> None:
        """
        Вызывается после успешной "отправки" документа (docstatus = 1).
        Это происходит, когда Workflow переводит документ в состояние с doc_status = 1.
        """
        # Пример: Отправка уведомления клиенту или менеджеру о том, что заявка принята в работу.
        # if self.workflow_state == "Открыта": # Используйте константы из constants.py
        #    _notify_customer_on_submission(self)
        pass

    def on_cancel(self) -> None:
        """
        Вызывается после "отмены" документа (docstatus = 2).
        Это происходит, когда Workflow переводит документ в состояние с doc_status = 2.
        """
        # Пример: Уведомление заинтересованных сторон об отмене заявки.
        # frappe.log_error(message=f"Service Request {self.name} was cancelled.", title="Service Request Cancelled")
        pass

    def on_trash(self) -> None:
        """
        Вызывается перед удалением документа (когда он перемещается в корзину).
        Хук on_trash в hooks.py указывает на
        ferum_customs.custom_logic.service_request_hooks.prevent_deletion_with_links.
        Эта функция и будет выполнена.
        """
        # frappe.get_doc("ferum_customs.custom_logic.service_request_hooks").prevent_deletion_with_links(self, "on_trash") # Это вызовется автоматически хуком
        pass

    # --- Пользовательские (вспомогательные) методы ---

    def _ensure_request_code_is_generated(self) -> None:
        """
        Гарантирует, что у заявки есть дополнительный request_code.
        Это поле было в вашем изначальном service_request.py.
        Генерируется, если поле пустое.
        """
        if hasattr(self, "request_code") and not self.get("request_code"):
            # Naming Series уже генерирует основной ID (self.name).
            # request_code - это дополнительное поле, если оно все еще нужно.
            # Его формат должен быть четко определен. Простой хеш может быть не лучшим вариантом.
            # Для примера, оставляем генерацию хеша.
            self.request_code = f"CODE-{frappe.generate_hash(length=7).upper()}"
            # frappe.msgprint(f"Сгенерирован дополнительный Код Заявки: {self.request_code}") # Для отладки

# --- Приватные вспомогательные функции для уведомлений (примеры) ---
# Эти функции лучше вынести в отдельный модуль (например, notifications.py или utils.py),
# если они становятся сложными или используются в нескольких местах.

# def _notify_customer_on_submission(doc: ServiceRequest) -> None:
#     if doc.customer_email: # Предполагается, что есть поле customer_email или оно получается из doc.customer
#         subject = f"Ваша заявка на обслуживание {doc.name} принята"
#         message = (f"Уважаемый клиент,<br><br>"
#                    f"Ваша заявка <b>{doc.subject}</b> (номер {doc.name}) была успешно зарегистрирована и принята в работу.<br>"
#                    f"Вы можете отслеживать ее статус по ссылке: {get_link_to_form('service_request', doc.name)}<br><br>"
#                    f"Спасибо за обращение!")
#         frappe.sendmail(
#             recipients=doc.customer_email,
#             subject=subject,
#             message=message,
#             reference_doctype=doc.doctype,
#             reference_name=doc.name
#         )

# def _notify_project_manager_on_closure(doc: ServiceRequest) -> None:
#     """
#     Эта логика уже есть в custom_logic.service_request_hooks.on_update_after_submit
#     и вызывается через hooks.py.
#     Если этот хук будет удален или изменен, логику можно разместить здесь.
#     """
#     if doc.workflow_state == STATUS_ZAKRYТА: # Используйте константы
#         recipients = frappe.get_all(
#             "User",
#             filters={"enabled": 1, "user_type": "System User", "roles.role": ROLE_PROEKTNYJ_MENEDZHER},
#             pluck="name",
#             distinct=True,
#         )
#         if recipients:
#             subject = f"Заявка на обслуживание {doc.name} ({doc.subject}) закрыта"
#             message = (f"Заявка на обслуживание <b>{doc.subject}</b> (номер {doc.name}) была закрыта.<br>"
#                        f"Клиент: {doc.customer}<br>"
#                        f"Объект обслуживания: {doc.service_object or 'Не указан'}<br>"
#                        f"Ссылка: {get_link_to_form('service_request', doc.name)}")
#             frappe.sendmail(
#                 recipients=recipients,
#                 subject=subject,
#                 message=message,
#                 reference_doctype=doc.doctype,
#                 reference_name=doc.name
#             )