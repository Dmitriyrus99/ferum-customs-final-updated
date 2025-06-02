# Ferum Customs

[!Run Frappe Tests](https://github.com/Dmitriyrus99/ferum-customs-final-updated/actions/workflows/tests.yml/badge.svg
)

Custom application for ERPNext.

- Custom DocTypes: Service Request, Service Object, Service Report
- Custom Payroll Entries and Attachments
- Custom Workflows for approval processes

## Setup

Install as a Frappe app:

```
bench get-app https://github.com/Dmitriyrus99/ferum-customs-final-updated.git
bench ini--site site.local --mariadb-root-password root --admin-password admin
bench --site site.local install-app ferum_customs
```

## Run Tests

To run the automated tests:

```bash
bench --site site.local run-tests --app ferum_customs
```

## CI Badge

This repository uses GitHub Actions to run automated tests for every push/pull request.

![Run Frappe Tests_badge](https://github.com/Dmitriyrus99/ferum-customs-final-updated/actions/workflows/tests.yml/badge.svg)

Let me know if you want to add more badges (e.g. Version, Code, Status).