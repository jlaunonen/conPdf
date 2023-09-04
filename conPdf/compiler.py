# -*- coding: utf-8 -*-
# Copyright (c) 2023 Jyrki Launonen

import csv
import datetime
import os
import re
from collections import OrderedDict

import weasyprint
from jinja2 import Environment
from jinja2 import pass_eval_context
from jinja2.loaders import FileSystemLoader
from jinja2.runtime import Undefined, make_logging_undefined
from markupsafe import Markup

LoggingUndefined = make_logging_undefined(None, Undefined)


@pass_eval_context
def nl2br(eval_ctx, value):
    br = "<br>\n"

    if eval_ctx.autoescape:
        br = Markup(br)

    result = "\n\n".join(
        f"<p>{br.join(p.splitlines())}</p>"
        for p in re.split(r"(?:\r\n|\r(?!\n)|\n){2,}", value)
    )
    return Markup(result) if eval_ctx.autoescape else result


def datetime_format(value, format="%H:%M %d-%m-%y"):
    if isinstance(value, str):
        value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    return value.strftime(format)


def render(template: str, tabular: str, encoding: str, args):
    project_path = os.path.dirname(template)
    env = Environment(
        autoescape=True,
        loader=FileSystemLoader(project_path),
        undefined=LoggingUndefined,
    )

    env.filters["nl2br"] = nl2br
    env.filters["datetime"] = datetime_format
    tpl = env.get_template(os.path.basename(template))

    data = []
    with open(tabular, "rt", encoding=encoding) as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        if args.dblquote:
            dialect.doublequote = True
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        header = next(reader)
        header = parse_header(header)
        for row_index, row in enumerate(reader):
            row_data = OrderedDict(zip(header, row))
            row_data["META"] = dict(
                index=row_index,
            )
            data.append(row_data)

    html = ""
    for row in data:
        html += tpl.render(row)

    if args.html:
        head = """<!DOCTYPE html>
        <html lang="fi">
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="main.css">
        </head>"""
        return head + html + "</html>"

    pdf_html = weasyprint.HTML(string=html, base_url=project_path)
    pdf_css = weasyprint.CSS(filename=os.path.splitext(template)[0] + ".css")
    pdf = pdf_html.write_pdf(
        stylesheets=[pdf_css],
    )
    return pdf


def parse_header(cols: list[str]) -> list[str]:
    non_word_char = re.compile(r"\W+")
    return [
        non_word_char.sub("_", col).strip("_").lower()
        for col in cols
    ]
