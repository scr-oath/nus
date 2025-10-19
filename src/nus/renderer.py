"""Static HTML generation for news digests."""

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import Category, Digest


class HTMLRenderer:
    """Generate static HTML digest with embedded CSS/JS."""

    def __init__(self, template_dir: Path = Path("templates")):
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        # Register custom filters
        self.env.filters["format_datetime"] = self._format_datetime

    def render_digest(self, digest: Digest, output_path: Path) -> None:
        """Render digest to HTML file."""
        template = self.env.get_template("digest.html")

        html = template.render(
            digest=digest,
            categories=Category,
            generated_at=digest.generated_at,
            success_rate=f"{digest.success_rate:.1%}",
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

    @staticmethod
    def _format_datetime(dt: datetime) -> str:
        """Format datetime for display."""
        return dt.strftime("%B %d, %Y at %I:%M %p")
