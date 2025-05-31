# Ferum Customs (ferum_customs)

## Overview

`ferum_customs` is a Frappe application that extends ERPNext with custom DocTypes and business logic tailored for Ferum's service management and operational processes. It includes features for managing service requests, service objects, service reports, custom payroll entries, and more.

## Key Features

* **Service Management:** End-to-end workflow for service requests, from creation to closure.
* **Object and Project Tracking:** Management of service objects (equipment) and service projects.
* **Field Service Reporting:** Detailed service reports including work done, materials used, and time spent.
* **Custom Payroll:** Extensions to payroll functionalities to incorporate service-related payments.
* **Custom Attachments:** Enhanced attachment handling.

## Custom DocTypes

Below is a list of custom DocTypes introduced by this application:

* **Service Request (`service_request`):** Manages customer requests for service. Includes a workflow for tracking progress.
    * *Purpose:* Core document for initiating and tracking service jobs.
    * *Key Fields:* Customer, Service Object, Problem Description, Priority, Status, Assigned Engineers.
* **Service Object (`ServiceObject`):** Represents a piece of equipment or an asset that can be serviced.
    * *Purpose:* To track serviceable items and their assigned engineers.
    * *Key Fields:* Object ID, Customer, Location, Assigned Engineers (child table).
* **Service Report (`ServiceReport`):** Documented by engineers after performing a service.
    * *Purpose:* Records details of work performed, time, materials, and costs. Links to a Service Request.
    * *Key Fields:* Service Request, Engineer, Work Done, Start/End Time, Materials Used (child table), Documents Attached (child table), Costs.
* **Service Project (`ServiceProject`):** Used to group multiple service requests or objects under a larger project.
    * *Purpose:* Manages larger scale service engagements.
    * *Key Fields:* Project Name, Customer, Start/End Date, Linked Service Objects (child table).
* **Payroll Entry Custom (`PayrollEntryCustom`):** Customizations for payroll entries.
    * *Purpose:* To extend standard payroll with specific calculations, possibly including bonuses from service reports.
    * *Key Fields:* Employee, Pay Period, `total_payable` (calculated).
* **Custom Attachment (`CustomAttachment`):** A custom DocType for managing attachments with additional metadata or logic.
    * *Purpose:* To provide a more structured way to handle file attachments related to various documents.
    * *Key Fields:* `attach_to_doctype`, `attach_to_name`, `attachment_type`.
* **Assigned Engineer Item (`AssignedEngineerItem`):** Child DocType for `ServiceObject` linking engineers (Users).
* **Project Object Item (`ProjectObjectItem`):** Child DocType for `ServiceProject` linking service objects.
* **Service Report Work Item (`ServiceReportWorkItem`):** Child DocType for `ServiceReport` detailing work items.
* **Service Report Document Item (`ServiceReportDocumentItem`):** Child DocType for `ServiceReport` detailing attached documents.

## Business Logic and Workflows

### Service Request Lifecycle

1.  **Creation ("Новая"):** A new service request is logged. Default status is "Новая" (Draft).
2.  **Processing ("В обработку"):** Request is reviewed and assigned.
3.  **To Execution ("К выполнению"):** Engineer is ready to start work.
4.  **Fulfilled ("Выполнена"):** Work is completed by the engineer. This status is typically set automatically when a linked Service Report is marked as "Выполнен". `docstatus` can be 0 (Draft, allowing edits) or 1 (Submitted, if it's a final pre-closure state). *(See Workflow section for current status)*.
5.  **Closed ("Закрыта"):** Request is fully resolved and closed. `docstatus` is 1 (Submitted).
6.  **Rejected ("Отклонена"):** Request is rejected/cancelled. `docstatus` is 2 (Cancelled).

*(Refer to `ferum_customs/fixtures/workflow_service_request.json` for detailed states and transitions).*

### Key Hook Implementations

* **Service Report Submission (`service_report_hooks.py`):**
    * `update_service_request_status_from_report`: When a `ServiceReport` is submitted:
        * If report status is "Выполнен", the linked `service_request` status is updated to "Выполнена".
        * If report status is "Отменен", the linked `service_request` status is updated to "Отклонена".
* **Service Request Deletion (`service_request_hooks.py`):**
    * `prevent_deletion_with_links`: Prevents deletion of a `service_request` if it's linked in `ServiceReport`s.
* **Payroll Calculation (`payroll_entry_hooks.py`):**
    * `calculate_total_payable`: Calculates `total_payable` in `PayrollEntryCustom`, potentially including bonuses derived from `ServiceReport` data.
* **Attachment Handling (`attachment_hooks.py`):**
    * `after_upload_attachment`: Custom logic triggered after a file is uploaded via `CustomAttachment`.
    * `on_custom_attachment_trash`: Custom logic for when a `CustomAttachment` record is deleted.

## Installation and Setup

1.  **Get the App:**
    ```bash
    bench get-app https://your-git-repository-url/ferum_customs.git
    ```
2.  **Install the App:**
    ```bash
    bench --site [your.site.name] install-app ferum_customs
    ```
3.  **Migrations (if applicable after updates):**
    ```bash
    bench --site [your.site.name] migrate
    ```

## Configuration Details

### Roles & Permissions

The following custom Roles are defined (see `ferum_customs/fixtures/role.json`):

* **Service Engineer:** Typically performs service tasks and fills service reports.
* **Service Manager:** Oversees service requests and engineer assignments.
* *(Add other custom roles and their general responsibilities)*

Permissions for custom DocTypes are defined via fixtures (`custom_docperm.json`) and may rely on these roles. Ensure users are assigned appropriate roles.

### Notifications

*(Describe any custom Notification setups, e.g., "Service Request Assignment", "Service Request Status Change". Refer to `ferum_customs/notifications/` if implemented).*
Currently, `notifications.py` is empty.

### Constants

Key application-specific constants (like statuses, roles) are defined in `ferum_customs/constants.py`. It is recommended to use these constants in code instead of hardcoded strings.

## Custom Scripts

### Server Scripts (Hooks & Whitelisted)

* **`hooks.py`:** Defines document event hooks, scheduled tasks, and whitelisted methods.
* **`custom_logic/`:** Contains Python modules for business logic triggered by hooks.
    * `service_request_hooks.py`: Logic for `service_request`, including fetching assigned engineers.
    * `service_report_hooks.py`: Logic for `ServiceReport`, including updating `service_request`.
    * `payroll_entry_hooks.py`: Logic for `PayrollEntryCustom`.
    * `attachment_hooks.py`: Logic for `CustomAttachment`.
* **`utils.py` (if created):** General utility functions.

### Client Scripts

* **`ferum_customs/client_scripts/service_request.js`:** Custom client-side behavior for the `service_request` form (e.g., fetching engineers when a Service Object is selected). This is bundled into `js/ferum_customs.js` via `build.json`.
* **`ferum_customs/ferum_customs/doctype/service_request/service_request.js`:** DocType-specific JS for `service_request`. *Note: Efforts should be made to consolidate client-side logic for `service_request` into one primary file.*

## Deployment Recommendations

* Ensure all dependencies from `requirements.txt` are installed in the Frappe bench environment.
* Run `bench migrate` after deploying new versions of the app to apply schema changes and patches.
* Regularly back up your site data.
* Monitor logs for any errors originating from `ferum_customs`.

## Dependency Vulnerability Checks

It's recommended to periodically check dependencies for known vulnerabilities:
```bash
pip install pip-audit
pip-audit
# or
pip install safety
safety check -r requirements.txt