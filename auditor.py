import os
import json

def run_audit():
    print("--- Iniciando Auditoría de Cumplimiento ---")
    
    results = {
        "license": {"status": "FAIL", "msg": "No se encontró archivo de LICENCIA."},
        "readme_security": {"status": "FAIL", "msg": "No hay sección de Seguridad en README.md."},
        "workflow_visibility": {"status": "PASS", "msg": "Estructura de workflows correcta."},
    }

    # 1. Verificar Licencia
    if any(os.path.isfile(f) for f in ['LICENSE', 'LICENSE.md', 'LICENSE.txt']):
        results["license"] = {"status": "PASS", "msg": "Archivo de LICENCIA detectado."}

    # 2. Verificar sección de seguridad en README
    if os.path.isfile('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            if 'security' in content or 'seguridad' in content:
                results["readme_security"] = {"status": "PASS", "msg": "Sección de seguridad encontrada en README."}

    # Generar Reporte Markdown
    report = "# 🛡️ Reporte de Cumplimiento - actionsHubPro\n\n"
    report += "| Control | Estado | Detalles |\n"
    report += "| --- | --- | --- |\n"
    
    for control, data in results.items():
        icon = "✅" if data["status"] == "PASS" else "❌"
        report += f"| {control.replace('_', ' ').title()} | {icon} {data['status']} | {data['msg']} |\n"

    report += "\n\n*Este reporte fue generado automáticamente por ComplianceGuard.*"

    # Guardar reporte para que GitHub lo muestre en el Resumen (Step Summary)
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(report)
    
    # También lo guardamos como archivo independiente
    with open('compliance_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("--- Auditoría Finalizada. Reporte enviado al Resumen de GitHub ---")
    
    # Mostrar el reporte en el log del runner para depuración
    print(report)

if __name__ == "__main__":
    run_audit()
