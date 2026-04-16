# AuditShield: Professional Compliance & Governance Auditor

AuditShield is an enterprise-grade GitHub Action designed to automate the generation of compliance reports and audit logs for your software development lifecycle. It transforms technical metadata from your Pull Requests and repository structure into formal documentation suitable for regulatory audits (such as ISO 27001, SOC2, or PCI-DSS).

## Core Capabilities

- **Metadata Extraction**: Captures PR authorship, precise open times, and cycle metrics.
- **Review Governance**: Audits total reviews, active reviewers, and tracks "Changes Requested" events to prove rigorous vetting.
- **Standards Verification**: Automatically verifies the presence of mandatory legal and security documentation (License, Security Policies).
- **Formal Reporting**: Generates non-repudiable audit IDs and professional Markdown reports integrated directly into the GitHub Actions Summary.

## Installation and Usage

To integrate AuditShield into your repository, create a workflow file (e.g., `.github/workflows/audit.yml`) and paste the following configuration:

```yaml
name: Compliance Audit

on:
  pull_request:
    branches: [ main, master ]
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  compliance:
    name: Execute AuditShield
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Run AuditShield
        uses: actionsHubPro/audit-trace@main # Replace with your repo/version
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
        
      - name: Archive Audit Report
        uses: actions/upload-artifact@v4
        with:
          name: compliance-report
          path: compliance_report.md
```

### Multi-language Support

You can choose the language of the final report by using the `language` input. Currently supported: **English (`en`)** and **Spanish (`es`)**.

```yaml
      - name: Run AuditShield (Español)
        uses: actionsHubPro/audit-trace@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          language: 'es'
```

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `github-token` | The GITHUB_TOKEN used to query the GitHub API. | Yes | N/A |
| `language` | Report language (options: `en`, `es`). | No | `en` |

## Output

The action generates a professional compliance report in two locations:
1. **GitHub Job Summary**: Displayed directly on the Actions run page for immediate review.
2. **`compliance_report.md`**: A standalone file suitable for archiving as build artifacts.

## Example Report Structure

```text
REPORT-ID: REPO-NAME-202604152230
--------------------------------------------------
AUDITORIA DE CUMPLIMIENTO DE CODIGO FUENTE
--------------------------------------------------
### INFORMACION DEL REPOSITORIO
- Repositorio: actionsHubPro/audit-shield
- Fecha del Reporte: 2026-04-15 22:45:10
...
```

---
*Developed by actionsHubPro for high-compliance development teams.*
