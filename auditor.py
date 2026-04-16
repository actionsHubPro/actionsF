import os
import json
from github import Github
from datetime import datetime

def run_audit():
    token = os.environ.get('GITHUB_TOKEN')
    repo_name = os.environ.get('GITHUB_REPOSITORY')
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    
    # Datos por defecto
    pr_data = {
        "author": "N/A",
        "opened_at": "N/A",
        "reviews_count": 0,
        "reviewers": "None",
        "changes_requested": 0,
        "pr_number": "N/A"
    }

    # Intentar obtener datos del Pull Request si existen
    if event_path:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
            if 'pull_request' in event_data:
                pr = repo.get_pull(event_data['pull_request']['number'])
                pr_data["author"] = pr.user.login
                pr_data["opened_at"] = pr.created_at.strftime("%Y-%m-%d %H:%M:%S")
                pr_data["pr_number"] = f"#{pr.number}"
                
                reviews = pr.get_reviews()
                reviewers_set = set()
                changes_req = 0
                for r in reviews:
                    reviewers_set.add(r.user.login)
                    if r.state == "CHANGES_REQUESTED":
                        changes_req += 1
                
                pr_data["reviews_count"] = reviews.totalCount
                pr_data["reviewers"] = ", ".join(reviewers_set) if reviewers_set else "None"
                pr_data["changes_requested"] = changes_req

    # Controles de archivo
    checks = {
        "Licencia de Software": "PASS" if any(os.path.isfile(f) for f in ['LICENSE', 'LICENSE.md', 'LICENSE.txt']) else "FAIL",
        "Seccion de Seguridad": "FAIL",
    }
    
    if os.path.isfile('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            if 'security' in f.read().lower():
                checks["Seccion de Seguridad"] = "PASS"

    # Generar Documento Formal
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"REPORT-ID: {repo_name.replace('/', '-')}-{datetime.now().strftime('%Y%m%d%H%M')}\n"
    report += "--------------------------------------------------\n"
    report += "AUDITORIA DE CUMPLIMIENTO DE CODIGO FUENTE\n"
    report += "--------------------------------------------------\n\n"
    
    report += "### INFORMACION DEL REPOSITORIO\n"
    report += f"- Repositorio: {repo_name}\n"
    report += f"- Fecha del Reporte: {now}\n"
    report += f"- Identificador PR: {pr_data['pr_number']}\n\n"

    report += "### METRICAS DE REVISION (PULL REQUEST)\n"
    report += "| Parametro | Detalle |\n"
    report += "| --- | --- |\n"
    report += f"| Autor del PR | {pr_data['author']} |\n"
    report += f"| Fecha de Apertura | {pr_data['opened_at']} |\n"
    report += f"| Revisiones Totales | {pr_data['reviews_count']} |\n"
    report += f"| Revisores Activos | {pr_data['reviewers']} |\n"
    report += f"| Solicitudes de Cambios | {pr_data['changes_requested']} |\n\n"

    report += "### VERIFICACION DE ESTANDARES\n"
    report += "| Control de Auditoria | Estatus |\n"
    report += "| --- | --- |\n"
    for title, status in checks.items():
        report += f"| {title} | {status} |\n"

    report += "\n\n---\n*Este es un documento generado automaticamente por la plataforma de auditoria de actionsHubPro. No requiere firma manuscrita.*"

    # Escribir en Resumen de GitHub
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(report)
    
    with open('compliance_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    run_audit()
