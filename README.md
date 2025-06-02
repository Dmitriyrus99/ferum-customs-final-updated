# Ferum Customs

[!Run Frappe Tests](https://github.com/Dmitriyrus99/ferum-customs-final-updated/actions/workflows/tests.yml/badge.svg

Specialized application for ERPNext.

- Custom DocTypes: Service Request, Service Object, Service Report
- Payroll Entries, Attachments, workflows for approval processes

## Setup

Install as a Frappe app:

```
bench get-app https://github.com/Dmitriyrus99/ferum-customs-final-updated.git
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
bench new-site site.local --mariadb-root-password root --admin-password admin
bench --site site.local install-app ferum_customs
```

## Run Tests

Run the automated tests:

```bash
bench --site site.local run-tests --app ferum_customs
```

## CI Badge

This repo uses GitHub Actions to run automated tests on every push/pull request.

[!Run Frappe Tests](https://github.com/Dmitriyrus99/ferum-customs-final-updated/actions/workflows/tests.yml/badge.svg

Say if you want me to add more badges (e.g. Version, Code Quality, Status).