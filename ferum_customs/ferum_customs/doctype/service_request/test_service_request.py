# ferum_customs/ferum_customs/doctype/service_request/test_service_request.py
import pytest; pytest.importorskip("frappe") # noqa: E402,F401
import frappe # noqa: F401
import unittest
from unittest.mock import patch # Для мокирования frappe.sendmail
import re
from frappe.utils import now_datetime, add_days, today, get_first_day, get_last_day

# Импортируйте ваши константы
from ferum_customs.constants import (
    STATUS_VYPOLNENA,
    STATUS_OTKRYTA,
    STATUS_ZAKRYTA,
    ROLE_PROEKTNYJ_MENEDZHER,
    ROLE_INZHENER
)

class TestServiceRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создание ролей, если их нет
        for role_name in [ROLE_PROEKTNYJ_MENEDZHER, ROLE_INZHENER]:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_if_duplicate=True)
        
        cls.test_customer_name = "_Test Customer for SR Tests"
        if not frappe.db.exists("Customer", cls.test_customer_name):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": cls.test_customer_name,
                "customer_type": "Individual"
            }).insert(ignore_if_duplicate=True)

        cls.test_engineer_user_email = "test_sr_engineer_ferum@example.com"
        if not frappe.db.exists("User", cls.test_engineer_user_email):
            user = frappe.get_doc({
                "doctype": "User", "email": cls.test_engineer_user_email,
                "first_name": "TestSR", "last_name": "Engineer", "send_welcome_email": 0
            })
            user.add_roles(ROLE_INZHENER) # Используем метод add_roles
            user.insert(ignore_if_duplicate=True)
        
        cls.test_pm_user_email = "test_sr_pm_ferum@example.com"
        if not frappe.db.exists("User", cls.test_pm_user_email):
            user = frappe.get_doc({
                "doctype": "User", "email": cls.test_pm_user_email,
                "first_name": "TestSR", "last_name": "PM", "send_welcome_email": 0
            })
            user.add_roles(ROLE_PROEKTNYJ_MENEDZHER) # Используем метод add_roles
            user.insert(ignore_if_duplicate=True)

        # Создание ServiceProject
        cls.test_sp_name_field = "_Test SP for SR Tests" # Уникальное имя для project_name
        sp_doc = frappe.db.exists("ServiceProject", {"project_name": cls.test_sp_name_field})
        if not sp_doc:
            sp = frappe.get_doc({
                "doctype": "ServiceProject",
                "project_name": cls.test_sp_name_field,
                "customer": cls.test_customer_name, # Предполагаем, что ServiceProject имеет поле customer
                "start_date": get_first_day(today()),
                "end_date": get_last_day(today())
            })
            sp.insert(ignore_permissions=True, ignore_if_duplicate=True)
            cls.actual_test_sp_name = sp.name # Это имя документа (ID)
        else:
            cls.actual_test_sp_name = sp_doc

        # Создание ServiceObject
        # Для ServiceObject может быть автоименование, поэтому лучше получать имя после создания
        so = frappe.new_doc("ServiceObject")
        so.customer = cls.test_customer_name
        so.linked_service_project = cls.actual_test_sp_name # Связываем с ServiceProject
        so.append("assigned_engineers", {
            "engineer": cls.test_engineer_user_email,
            "assignment_date": now_datetime()
        })
        # so.object_name = "_Test SO for SR Tests" # Если есть такое поле и оно уникально
        so.insert(ignore_permissions=True)
        cls.actual_test_so_name = so.name # Это имя документа (ID)


    def setUp(self):
        frappe.db.savepoint()
        self.current_user_for_test = frappe.session.user
        frappe.set_user(self.test_pm_user_email) # Действия от имени ПМ

    def tearDown(self):
        frappe.set_user(self.current_user_for_test)
        frappe.db.rollback()

    def create_service_request_doc(self, status=STATUS_OTKRYTA, submit_doc=False):
        sr = frappe.new_doc("ServiceRequest")
        sr.subject = "Test SR - " + frappe.generate_hash(length=5)
        # Используем custom_ префиксы
        sr.custom_customer = self.test_customer_name
        sr.custom_service_object_link = self.actual_test_so_name
        # custom_project должен подтянуться из custom_service_object_link
        sr.request_datetime = now_datetime()
        sr.status = status 
        sr.insert(ignore_permissions=True) # insert вызовет before_save и validate
        if submit_doc and sr.docstatus == 0:
            try:
                sr.submit()
            except frappe.exceptions.DoesNotExistError as e:
                # Иногда workflow может быть не до конца синхронизирован в тестах
                if "WorkflowState" in str(e) and "Открыта" in str(e): # Имя статуса из workflow_service_request.json
                     frappe.get_doc("Workflow State", {"workflow_state_name": "Открыта"}).save(ignore_permissions=True)
                     sr.reload()
                     sr.submit()
                else:
                    raise
        return sr

    def test_sr_creation_and_custom_fields(self):
        sr = self.create_service_request_doc()
        self.assertEqual(sr.custom_customer, self.test_customer_name)
        self.assertEqual(sr.custom_service_object_link, self.actual_test_so_name)
        
        # Проверяем, что custom_project подтянулся (логика в ServiceRequest.before_save)
        fetched_sr = frappe.get_doc("ServiceRequest", sr.name)
        self.assertEqual(fetched_sr.custom_project, self.actual_test_sp_name)

    def test_validate_vyapolnena_requires_linked_report(self):
        sr = self.create_service_request_doc(status=STATUS_OTKRYTA, submit_doc=True)
        sr.status = STATUS_VYPOLNENA # Имитируем изменение статуса
        # sr.custom_linked_report = None # Убедимся, что поле пустое (оно и так будет None для нового SR)
        
        with self.assertRaisesRegex(frappe.ValidationError, "Нельзя отметить заявку выполненной без связанного отчёта"):
            sr.save() # save вызовет validate

    def test_hook_get_engineers_for_object(self):
        from ferum_customs.custom_logic.service_request_hooks import get_engineers_for_object
        engineers = get_engineers_for_object(self.actual_test_so_name)
        self.assertIn(self.test_engineer_user_email, engineers)

    def test_sr_controller_internal_methods_with_custom_fields(self):
        sr_doc = frappe.new_doc("ServiceRequest")
        sr_doc.subject = " Test Subject for Cleaning "
        # Даты
        sr_doc.planned_start_datetime = now_datetime()
        sr_doc.planned_end_datetime = add_days(now_datetime(), -1) # Некорректная дата
        
        with self.assertRaisesRegex(frappe.ValidationError, "Планируемая дата начала не может быть позже"):
            sr_doc.validate() 
        
        sr_doc.planned_end_datetime = add_days(now_datetime(), 1) 
        sr_doc.actual_start_datetime = now_datetime()
        sr_doc.actual_end_datetime = add_days(sr_doc.actual_start_datetime, 0.5) # 12 часов
        
        # Установка кастомных полей для проверки _clean_fields (если бы они очищались)
        # sr_doc.custom_customer = f" {self.test_customer_name} " # Пример для очистки, если бы она была для Link

        sr_doc.validate() 
        sr_doc.run_method("before_save") 
        
        self.assertEqual(sr_doc.subject, "Test Subject for Cleaning")
        # if sr_doc.custom_customer: # Если бы custom_customer очищался
        #     self.assertEqual(sr_doc.custom_customer, self.test_customer_name)
        self.assertAlmostEqual(sr_doc.duration_hours, 12.0, places=2)

    @patch('frappe.sendmail') # Мокируем функцию frappe.sendmail
    def test_notify_project_manager_on_close(self, mock_sendmail_func):
        sr = self.create_service_request_doc(status=STATUS_OTKRYTA, submit_doc=True)
        
        # Имитируем изменение статуса на Закрыта
        # В реальной системе это произойдет через Workflow Action
        # Для теста хука on_update_after_submit, нужно чтобы документ был submitted (docstatus=1)
        # и чтобы изменилось отслеживаемое поле (например, status).
        sr.reload() # Убедимся, что работаем с последней версией
        sr.status = STATUS_ZAKRYTA
        sr.save(ignore_permissions=True) # Это вызовет on_update, который для submitted вызовет on_update_after_submit

        mock_sendmail_func.assert_called_once()
        args, kwargs = mock_sendmail_func.call_args
        
        self.assertIn(self.test_pm_user_email, kwargs.get("recipients"))
        self.assertIn(sr.name, kwargs.get("subject"))
        self.assertEqual(kwargs.get("reference_doctype"), "ServiceRequest")
        self.assertEqual(kwargs.get("reference_name"), sr.name)
        # Проверка, что custom_customer используется в сообщении, если он есть
        if sr.custom_customer:
            self.assertIn(self.test_customer_name, kwargs.get("message"))


    @classmethod
    def tearDownClass(cls):
        # Опционально: удалить тестовые данные, созданные в setUpClass
        # Это полезно, чтобы не загрязнять БД, но может замедлить тесты.
        # Frappe rollback в tearDown каждого теста обычно достаточен для тестовых данных, создаваемых в самом тесте.
        # frappe.delete_doc("Customer", cls.test_customer_name, force=True, ignore_missing=True)
        # frappe.delete_doc("User", cls.test_engineer_user_email, force=True, ignore_missing=True)
        # frappe.delete_doc("User", cls.test_pm_user_email, force=True, ignore_missing=True)
        # if hasattr(cls, 'actual_test_so_name'):
        #     frappe.delete_doc("ServiceObject", cls.actual_test_so_name, force=True, ignore_missing=True)
        # if hasattr(cls, 'actual_test_sp_name'):
        #     frappe.delete_doc("ServiceProject", cls.actual_test_sp_name, force=True, ignore_missing=True)
        pass