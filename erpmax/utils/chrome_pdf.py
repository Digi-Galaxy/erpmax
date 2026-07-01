import frappe
import io
import os
import re
import shutil
import subprocess
import tempfile
from frappe.utils import get_url
from frappe.utils.pdf import prepare_options
from pypdf import PdfReader, PdfWriter

_URLS_NOT_HTTP_TAG = re.compile(
    r"(href|src){1}([\s]*=[\s]*[\x27\"]?)((?!http)[^\x27\">]+)([\x27\"]?)"
)
_URL_NOT_HTTP_NOTATION = re.compile(
    r"(:[\s]?url)(\([\x27\"]?)((?!http)[^\x27\">]+)([\x27\"]?\))"
)


def scrub_urls(html):
    return expand_relative_urls(html)


def expand_relative_urls(html):
    url = get_url()
    if url.endswith("/"):
        url = url[:-1]

    _URLS_HTTP_TAG = re.compile(
        r"(href|src)([\s]*=[\s]*[\x27\"]?)((?:{0})[^\x27\">]+)([\x27\"]?)".format(
            re.escape(url.replace("https://", "http://"))
        )
    )
    _URL_HTTP_NOTATION = re.compile(
        r"(:[\s]?url)(\([\x27\"]?)((?:{0})[^\x27\">]+)([\x27\"]?\))"
        .format(re.escape(url.replace("https://", "http://")))
    )

    def _expand(match):
        parts = list(match.groups())
        val = parts[2]
        if val.startswith(("data:", "mailto:", "tel:")):
            return "".join(parts)
        if not val.startswith(url):
            if not val.startswith("/"):
                val = "/" + val
            val = url + val
        parts[2] = val
        if frappe.session and frappe.session.sid and hasattr(frappe.local, "request"):
            sep = "&" if "?" in parts[-2] else "?"
            parts[-2] += f"{sep}sid={frappe.session.sid}"
        return "".join(parts)

    html = _URLS_HTTP_TAG.sub(_expand, html)
    html = _URLS_NOT_HTTP_TAG.sub(_expand, html)
    html = _URL_NOT_HTTP_NOTATION.sub(_expand, html)
    html = _URL_HTTP_NOTATION.sub(_expand, html)
    return html


_paper_sizes = {
    "A0": {"width": 33.1, "height": 46.8},
    "A1": {"width": 23.4, "height": 33.1},
    "A2": {"width": 16.5, "height": 23.4},
    "A3": {"width": 11.7, "height": 16.5},
    "A4": {"width": 8.3, "height": 11.7},
    "A5": {"width": 5.8, "height": 8.3},
    "A6": {"width": 4.1, "height": 5.8},
    "A7": {"width": 2.9, "height": 4.1},
    "A8": {"width": 2.0, "height": 2.9},
    "A9": {"width": 1.5, "height": 2.0},
    "A10": {"width": 1.0, "height": 1.5},
    "Letter": {"width": 8.5, "height": 11.0},
    "Legal": {"width": 8.5, "height": 14.0},
    "Ledger": {"width": 17.0, "height": 11.0},
    "Tabloid": {"width": 11.0, "height": 17.0},
}


def get_pdf(html, options=None, output=None):
    if options is None:
        options = {}
    pdf_path = f"/tmp/{frappe.generate_hash()}.pdf"
    html = scrub_urls(html)
    html, options = prepare_options(html, options)

    style = ""
    if options:
        if options.get("page-height") and options.get("page-width"):
            style += f"""<style>
            @page {{ size: {options["page-width"]}mm {options["page-height"]}mm; }}
            </style>"""
        elif options.get("page-size"):
            size = _paper_sizes.get(options["page-size"])
            if size:
                style += f"""<style>
                @page {{ size: {size["width"]}in {size["height"]}in; }}
                </style>"""
        margins = " ".join([
            f"{k}: {options[k]};"
            for k in ("margin-top", "margin-bottom", "margin-left", "margin-right")
            if options.get(k)
        ])
        if margins:
            style += f"<style>@page {{ {margins} }}</style>"

    html = style + html

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".html", delete=True) as f:
        f.write(html)
        f.seek(0)
        chrome = "google-chrome" if shutil.which("google-chrome") else "google-chrome-stable"
        cmd = [
            chrome, "--headless", "--disable-gpu", "--no-sandbox",
            "--disable-web-security", "--disable-dev-shm-usage",
            "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
            f"--user-data-dir=/home/dg/.chrome-pdf-profile",
            f"--print-to-pdf={pdf_path}",
            f.name,
        ]
        env = os.environ.copy()
        env["HOME"] = "/home/dg"
        r = subprocess.run(cmd, shell=False, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            raise Exception(f"Chrome PDF failed ({r.returncode}): {r.stderr[:500]}")
        with open(pdf_path, "rb") as pf:
            content = pf.read()
        os.remove(pdf_path)

    reader = PdfReader(io.BytesIO(content))
    if output:
        output.append_pages_from_reader(reader)
        return output
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    if "password" in options:
        writer.encrypt(options["password"])
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    return stream.read()

