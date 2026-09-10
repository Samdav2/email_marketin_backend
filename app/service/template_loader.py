import os
from typing import List, Dict, Optional

class TemplateLoaderService:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Resolve absolute path to project root/templates
            from pathlib import Path
            self.base_dir = str(Path(__file__).resolve().parent.parent.parent / "templates")
        else:
            self.base_dir = base_dir

    def list_templates(self) -> Dict[str, List[str]]:
        """List all available HTML and Text templates."""
        templates = {"html": [], "text": []}

        for t_type in ["html", "text"]:
            path = os.path.join(self.base_dir, t_type)
            if os.path.exists(path):
                templates[t_type] = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        return templates

    def get_template_content(self, template_type: str, template_name: str) -> Optional[str]:
        """Read the content of a specific template."""
        if template_type not in ["html", "text"]:
            return None

        path = os.path.join(self.base_dir, template_type, template_name)
        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def render_template(self, template_type: str, template_name: str, placeholders: Dict[str, str]) -> Optional[str]:
        """Load and render a template with placeholders."""
        content = self.get_template_content(template_type, template_name)
        if not content:
            return None

        for key, value in placeholders.items():
            content = content.replace(f"{{{key}}}", str(value))

        return content

# Singleton instance
template_loader = TemplateLoaderService()
