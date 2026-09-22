"""
engineering_report_html_renderer.py
 
Professional HTML renderer and exporter for the
Thermal Design Agent engineering report.
 
The renderer:
 
- consumes only EngineeringReport;
- performs no engineering calculations;
- does not modify engineering status;
- performs no LLM operations;
- keeps presentation separate from report content.
 
Visual direction:
- professional engineering-document appearance;
- compact typography;
- restrained Havells-red accent;
- no decorative emojis or AI-demo styling;
- optional Havells logo support.
"""
 
from __future__ import annotations
 
import base64
import html
from pathlib import Path
 
from models.engineering_report import (
    EngineeringReport,
    EngineeringReportSection,
)
 
 
class EngineeringReportHTMLRenderer:
    """
    Render EngineeringReport into professional,
    self-contained HTML.
    """
 
    HAVells_RED = "#D71920"
 
    @classmethod
    def render(
        cls,
        report: EngineeringReport,
        *,
        logo_path: str | Path | None = None,
    ) -> str:
        """
        Render one EngineeringReport as standalone HTML.
        """
 
        if not isinstance(
            report,
            EngineeringReport,
        ):
            raise ValueError(
                "'report' must be an EngineeringReport object."
            )
 
        logo_html = cls._render_logo(
            logo_path
        )
 
        status_text = cls._display_value(
            report.status.value
        )
 
        section_html = "\n".join(
            cls._render_section(
                section
            )
            for section in report.sections
        )
 
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>
<title>{html.escape(report.title)}</title>
 
<style>
    :root {{
        --havells-red: {cls.HAVells_RED};
        --text-primary: #202124;
        --text-secondary: #5f6368;
        --border: #d9dce1;
        --surface: #ffffff;
        --surface-muted: #f7f8fa;
        --status-background: #f3f4f6;
    }}
 
    * {{
        box-sizing: border-box;
    }}
 
    body {{
        margin: 0;
        background: #eef0f3;
        color: var(--text-primary);
        font-family:
            "Segoe UI",
            Arial,
            Helvetica,
            sans-serif;
        font-size: 12px;
        line-height: 1.5;
    }}
 
    .report-page {{
        width: min(100%, 980px);
        margin: 24px auto;
        background: var(--surface);
        min-height: 100vh;
        padding: 34px 42px 42px 42px;
        box-shadow:
            0 1px 4px rgba(0, 0, 0, 0.10);
    }}
 
    .header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        padding-bottom: 18px;
        border-bottom:
            3px solid var(--havells-red);
    }}
 
    .brand {{
        display: flex;
        align-items: center;
        min-height: 38px;
    }}
 
    .brand img {{
        max-height: 38px;
        max-width: 145px;
        object-fit: contain;
    }}
 
    .brand-text {{
        color: var(--havells-red);
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }}
 
    .product {{
        text-align: right;
    }}
 
    .product-name {{
        margin: 0;
        font-size: 17px;
        font-weight: 700;
        color: var(--text-primary);
    }}
 
    .product-subtitle {{
        margin-top: 3px;
        color: var(--text-secondary);
        font-size: 11px;
    }}
 
    .document-header {{
        margin-top: 24px;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 24px;
        align-items: start;
    }}
 
    .document-title {{
        margin: 0;
        font-size: 19px;
        line-height: 1.25;
        font-weight: 700;
    }}
 
    .status-block {{
        text-align: right;
    }}
 
    .status-label {{
        color: var(--text-secondary);
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
 
    .status-value {{
        display: inline-block;
        margin-top: 5px;
        padding: 5px 9px;
        border: 1px solid var(--border);
        border-left:
            3px solid var(--havells-red);
        background: var(--status-background);
        font-size: 11px;
        font-weight: 700;
    }}
 
    .executive-summary {{
        margin-top: 22px;
        padding: 15px 17px;
        background: var(--surface-muted);
        border-left:
            3px solid var(--havells-red);
    }}
 
    .executive-summary h2 {{
        margin: 0 0 7px 0;
        font-size: 13px;
        font-weight: 700;
    }}
 
    .executive-summary p {{
        margin: 0;
        color: #303236;
    }}
 
    .section {{
        margin-top: 26px;
        break-inside: avoid;
    }}
 
    .section-title {{
        margin: 0 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border);
        font-size: 14px;
        font-weight: 700;
        color: var(--text-primary);
    }}
 
    .data-table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }}
 
    .data-table td {{
        padding: 6px 9px;
        border-bottom: 1px solid #eceef1;
        vertical-align: top;
    }}
 
    .data-table td:first-child {{
        width: 38%;
        color: var(--text-secondary);
        font-weight: 600;
    }}
 
    .text-content {{
        white-space: pre-line;
        color: #303236;
    }}
 
    .assessment-block {{
        margin-bottom: 14px;
    }}
 
    .assessment-heading {{
        font-weight: 700;
    }}
 
    .footer {{
        margin-top: 36px;
        padding-top: 12px;
        border-top: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        color: #777b82;
        font-size: 9px;
    }}
 
    @media print {{
        body {{
            background: white;
        }}
 
        .report-page {{
            width: 100%;
            margin: 0;
            box-shadow: none;
            padding: 18mm 16mm;
        }}
 
        .section {{
            break-inside: avoid;
        }}
    }}
</style>
</head>
 
<body>
<div class="report-page">
 
    <header class="header">
 
        <div class="brand">
            {logo_html}
        </div>
 
        <div class="product">
            <div class="product-name">
                Thermal Design Agent
            </div>
            <div class="product-subtitle">
                Engineering Design &amp; Analysis
            </div>
        </div>
 
    </header>
 
    <div class="document-header">
 
        <h1 class="document-title">
            {html.escape(report.title)}
        </h1>
 
        <div class="status-block">
            <div class="status-label">
                Engineering Status
            </div>
 
            <div class="status-value">
                {html.escape(status_text.upper())}
            </div>
        </div>
 
    </div>
 
    <section class="executive-summary">
        <h2>Executive Summary</h2>
        <p>
            {html.escape(report.executive_summary)}
        </p>
    </section>
 
    {section_html}
 
    <footer class="footer">
        <span>
            Thermal Design Agent
        </span>
        <span>
            Engineering analysis output
        </span>
    </footer>
 
</div>
</body>
</html>
"""
 
    @classmethod
    def export(
        cls,
        report: EngineeringReport,
        output_path: str | Path,
        *,
        logo_path: str | Path | None = None,
    ) -> Path:
        """
        Render and write the report to an HTML file.
        """
 
        path = Path(
            output_path
        )
 
        if path.suffix.lower() != ".html":
            raise ValueError(
                "Engineering report output path must "
                "use the '.html' extension."
            )
 
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
 
        rendered_html = cls.render(
            report,
            logo_path=logo_path,
        )
 
        path.write_text(
            rendered_html,
            encoding="utf-8",
        )
 
        return path
 
    @classmethod
    def _render_section(
        cls,
        section: EngineeringReportSection,
    ) -> str:
        """
        Render one structured report section.
        """
 
        title = html.escape(
            section.title
        )
 
        if section.section_id in {
            "requirements",
            "selected_design",
            "thermal_performance",
        }:
            body = cls._render_key_value_content(
                section.content
            )
 
        else:
            body = (
                '<div class="text-content">'
                f"{html.escape(section.content)}"
                "</div>"
            )
 
        return f"""
<section class="section">
    <h2 class="section-title">
        {title}
    </h2>
    {body}
</section>
"""
 
    @staticmethod
    def _render_key_value_content(
        content: str,
    ) -> str:
        """
        Render simple 'Label: value' report content as a
        compact engineering-data table.
        """
 
        rows = []
 
        for line in content.splitlines():
 
            stripped = line.strip()
 
            if not stripped:
                continue
 
            if ":" not in stripped:
                rows.append(
                    (
                        html.escape(stripped),
                        "",
                    )
                )
                continue
 
            key, value = stripped.split(
                ":",
                1,
            )
 
            rows.append(
                (
                    html.escape(
                        key.strip()
                    ),
                    html.escape(
                        value.strip()
                    ),
                )
            )
 
        row_html = "\n".join(
            (
                "<tr>"
                f"<td>{key}</td>"
                f"<td>{value}</td>"
                "</tr>"
            )
            for key, value in rows
        )
 
        return f"""
<table class="data-table">
    <tbody>
        {row_html}
    </tbody>
</table>
"""
 
    @staticmethod
    def _render_logo(
        logo_path: str | Path | None,
    ) -> str:
        """
        Return embedded logo HTML.
 
        When no logo is configured, a restrained text
        fallback is used.
        """
 
        if logo_path is None:
            return (
                '<div class="brand-text">'
                "HAVELLS"
                "</div>"
            )
 
        path = Path(
            logo_path
        )
 
        if not path.is_file():
            raise ValueError(
                "Configured report logo file does not exist: "
                f"'{path}'."
            )
 
        suffix = path.suffix.lower()
 
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
        }
 
        if suffix not in mime_types:
            raise ValueError(
                "Report logo must be PNG, JPG, JPEG, or SVG."
            )
 
        encoded = base64.b64encode(
            path.read_bytes()
        ).decode(
            "ascii"
        )
 
        return (
            '<img '
            'alt="Havells" '
            f'src="data:{mime_types[suffix]};base64,{encoded}">'
        )
 
    @staticmethod
    def _display_value(
        value: str,
    ) -> str:
        """
        Convert machine-facing enum-style values into
        professional display text.
        """
 
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "'value' must be a string."
            )
 
        normalized = (
            value
            .strip()
            .replace("_", " ")
        )
 
        return normalized.title()