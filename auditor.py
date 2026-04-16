import os
import json
from github import Github
from datetime import datetime

def run_audit():
    token = os.environ.get('GITHUB_TOKEN')
    repo_name = os.environ.get('GITHUB_REPOSITORY')
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    lang = os.environ.get('LANGUAGE', 'en').lower()
    auto_archive = os.environ.get('AUTO_ARCHIVE', 'false').lower() == 'true'
    archive_branch = os.environ.get('ARCHIVE_BRANCH', 'audit-history')
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    
    # Traducciones
    i18n = {
        "en": {
            "title": "SOURCE CODE COMPLIANCE AUDIT",
            "repo_info": "REPOSITORY INFORMATION",
            "repo_label": "Repository",
            "report_date": "Report Date",
            "pr_id": "PR Identifier",
            "metrics_title": "REVIEW METRICS (PULL REQUEST)",
            "param": "Parameter",
            "detail": "Detail",
            "author": "PR Author",
            "opened": "Opening Date",
            "rev_count": "Total Reviews",
            "active_rev": "Active Reviewers",
            "changes_req": "Changes Requested",
            "standards_title": "STANDARDS VERIFICATION",
            "control": "Audit Control",
            "status": "Status",
            "footer": "This is an automatically generated document by the AuditShield platform. No handwritten signature required.",
            "license": "Software License",
            "security": "Security Section",
            "pass": "PASS",
            "fail": "FAIL"
        },
        "es": {
            "title": "AUDITORIA DE CUMPLIMIENTO DE CODIGO FUENTE",
            "repo_info": "INFORMACION DEL REPOSITORIO",
            "repo_label": "Repositorio",
            "report_date": "Fecha del Reporte",
            "pr_id": "Identificador PR",
            "metrics_title": "METRICAS DE REVISION (PULL REQUEST)",
            "param": "Parametro",
            "detail": "Detalle",
            "author": "Autor del PR",
            "opened": "Fecha de Apertura",
            "rev_count": "Revisiones Totales",
            "active_rev": "Revisores Activos",
            "changes_req": "Solicitudes de Cambios",
            "standards_title": "VERIFICACION DE ESTANDARES",
            "control": "Control de Auditoria",
            "status": "Estatus",
            "footer": "Este es un documento generado automaticamente por la plataforma AuditShield. No requiere firma manuscrita.",
            "license": "Licencia de Software",
            "security": "Sección de Seguridad",
            "pass": "PASO",
            "fail": "FALLO"
        }
    }

    t = i18n.get(lang, i18n["en"])

    # Datos por defecto
    pr_data = {
        "author": "N/A",
        "opened_at": "N/A",
        "reviews_count": 0,
        "reviewers": "None",
        "changes_requested": 0,
        "pr_number": "N/A",
        "pr_id_only": "general"
    }

    if event_path:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
            if 'pull_request' in event_data:
                pr_num = event_data['pull_request']['number']
                pr = repo.get_pull(pr_num)
                pr_data["author"] = pr.user.login
                pr_data["opened_at"] = pr.created_at.strftime("%Y-%m-%d %H:%M:%S")
                pr_data["pr_number"] = f"#{pr.number}"
                pr_data["pr_id_only"] = f"PR-{pr.number}"
                
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
        t["license"]: t["pass"] if any(os.path.isfile(f) for f in ['LICENSE', 'LICENSE.md', 'LICENSE.txt']) else t["fail"],
        t["security"]: t["fail"],
    }
    
    if os.path.isfile('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            if 'security' in f.read().lower():
                checks[t["security"]] = t["pass"]

    # Generar Documento Formal
    now_obj = datetime.now()
    now_str = now_obj.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_id = now_obj.strftime("%Y%m%d_%H%M%S")
    
    report_id = f"{repo_name.replace('/', '-')}-{timestamp_id}"
    report = f"REPORT-ID: {report_id}\n"
    report += "--------------------------------------------------\n"
    report += f"{t['title']}\n"
    report += "--------------------------------------------------\n\n"
    
    report += f"### {t['repo_info']}\n"
    report += f"- {t['repo_label']}: {repo_name}\n"
    report += f"- {t['report_date']}: {now_str}\n"
    report += f"- {t['pr_id']}: {pr_data['pr_number']}\n\n"

    report += f"### {t['metrics_title']}\n"
    report += f"| {t['param']} | {t['detail']} |\n"
    report += "| --- | --- |\n"
    report += f"| {t['author']} | {pr_data['author']} |\n"
    report += f"| {t['opened']} | {pr_data['opened_at']} |\n"
    report += f"| {t['rev_count']} | {pr_data['reviews_count']} |\n"
    report += f"| {t['active_rev']} | {pr_data['reviewers']} |\n"
    report += f"| {t['changes_req']} | {pr_data['changes_requested']} |\n\n"

    report += f"### {t['standards_title']}\n"
    report += f"| {t['control']} | {t['status']} |\n"
    report += "| --- | --- |\n"
    for title, status in checks.items():
        report += f"| {title} | {status} |\n"

    report += f"\n\n---\n*{t['footer']}*"

    # Escribir en Resumen de GitHub
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(report)
    
    # Auto-archivado en rama
    if auto_archive:
        try:
            # Verificar si la rama existe, si no crearla
            try:
                branch = repo.get_branch(archive_branch)
            except:
                # Crear rama huérfana (orphan-like via API)
                print(f"La rama {archive_branch} no existe. Creándola...")
                # Para crear una rama nueva necesitamos un SHA origen. Usamos el actual.
                main_sha = repo.get_branch(repo.default_branch).commit.sha
                repo.create_git_ref(f"refs/heads/{archive_branch}", main_sha)
            
            # Crear la ruta del archivo: history/PR-123/audit_timestamp.md
            file_path = f"history/{pr_data['pr_id_only']}/audit_{timestamp_id}.md"
            commit_msg = f"Archive compliance report for {pr_data['pr_id_only']} at {now_str}"
            
            repo.create_file(file_path, commit_msg, report, branch=archive_branch)
            print(f"Reporte archivado exitosamente en la rama {archive_branch} -> {file_path}")
        except Exception as e:
            print(f"Error al archivar el reporte: {str(e)}")

    with open('compliance_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    run_audit()
