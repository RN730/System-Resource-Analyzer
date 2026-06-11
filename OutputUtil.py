import webbrowser
import texttable
import csv
import os
import random
import matplotlib.pyplot as plt
from datetime import datetime
from numpy import mean, median, std

TAG_DOCTYPE = '!DOCTYPE html'
TAG_HTML = 'html'
TAG_HEAD = 'head'
TAG_BODY = 'body'
TAG_TABLE = 'table'
TAG_TH = 'th'
TAG_TD = 'td'
TAG_TR = 'tr'
TAG_PAR = 'p'
TAG_DIV = 'div'
TAG_H1 = 'h1'
TAG_H2 = 'h2'
TAG_H3 = 'h3'
TAG_H4 = 'h4'
TAG_H5 = 'h5'
TAG_H6 = 'h6'
TAG_BR = 'br'
TAG_OL = "ol"
TAG_UL = "ul"
TAG_LI = "li"
TAG_CENTER = 'center'
TAG_LINK = 'link'
TAG_A = 'a'
TAG_SPAN = 'span'
TAG_STYLE = 'style'
TAG_SCRIPT = 'script'
TAG_META = 'meta'

sort_script = """
function sortTable(tableId, colNum, colType) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchCount = 0;
  table = document.getElementById(tableId);
  switching = true;
  dir = "asc";
  while (switching) {
    switching = false;
    rows = table.rows;
    for (i = 1; i < (rows.length - 1); i++) {
      shouldSwitch = false;
      x = rows[i].getElementsByTagName("td")[colNum];
      y = rows[i + 1].getElementsByTagName("td")[colNum];
      if (colType == 'N') { 
        if (((dir == "asc") && (Number(x.innerHTML) > Number(y.innerHTML))) ||
            ((dir == "desc") && (Number(x.innerHTML) < Number(y.innerHTML)))) {
          shouldSwitch = true;
          break;
        }
      } else {
        if (((dir == "asc") && (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase())) ||
            ((dir == "desc") && (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()))) {
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchCount ++;
    } else {
     if (switchCount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
"""

dict_align = {"l": "left", "c": "center", "r": "right", "L": "left", "C": "center", "R": "right"}


def read_style(file_name="mystyle.css"):
    with open(file_name, 'r', encoding="UTF-8") as file:
        return file.read()


def create_elements(tag, list_contents, attribute=""):
    elements = ""
    for content in list_contents:
        elements += create_element(tag, content, attribute)
    return elements


def create_element(tag, content, attributes=None, end_tag=True):
    element = "<" + tag
    if attributes:
        element += " " + attributes
    element += ">"
    if end_tag:
        element += str(content) + "</" + tag + ">"
    return element + "\n"


def create_table(headers, types, alignments, rows, google_links=False, hrefs=None, table_id="table1"):
    # table_id = "table1"
    ths = ""
    types = [t.upper() for t in types]
    for j in range(len(headers)):
        href = 'javascript:sortTable(\'' + table_id + '\', ' + str(j) + ', \'' + types[j] + '\')"'
        attributes = 'href="' + href + '"'
        a = create_element(TAG_A, headers[j], attributes)
        ths += create_element(TAG_TH, a)
    trs = ths
    for i in range(len(rows)):
        tds = ""
        row = rows[i]
        for j in range(len(row)):
            header = headers[j]
            if "Google" in header or "Wiki" in header or (j == 0 and (google_links or hrefs)):
                name = row[j]
                href = None
                if j == 0 and hrefs and hrefs[i]:
                    href = hrefs[i]
                elif "Google" in header or (j == 0 and google_links):
                    href = "https://www.google.com/search?q=" + name.replace(' ', '+')
                elif "Wiki" in header:
                    href = "https://www.google.com/search?q=" + "Wiki+" + name.replace(' ', '+')
                a_attributes = 'href="' + href + '" target="_blank"'
                td_cont = create_element(TAG_A, name, a_attributes)
            else:
                td_cont = row[j]
            td_attributes = 'style="text-align:' + dict_align[alignments[j]] + ';"' if alignments else None
            tds += create_element(TAG_TD, td_cont, td_attributes)
        tr = create_element(TAG_TR, tds)
        trs += tr
    attributes = 'id="' + table_id + '" ' + 'style="width:100%"'
    # attributes = 'id="' + table_id + '" '
    table = create_element(TAG_TABLE, trs, attributes)
    return table


def write_file(file_name, message):
    with open(file_name, 'w', encoding="UTF-8") as file:
        file.write(message)


def open_file_in_browser(file_name):
    url = 'file:///' + os.getcwd() + '/' + file_name
    webbrowser.open_new_tab(url)


def write_html_exam_file(file_name, title, instructions, headers, types, alignments, data, open_file=False, style_file=None, do_trailer=True):
    tables = [(None, headers, types, alignments, data)]
    write_html_file_new(file_name, title, instructions, tables, open_file, style_file, False, do_trailer)


def write_html_file(file_name, title, headers, types, alignments, data, open_file=False):
    tables = [(None, headers, types, alignments, data)]
    write_html_file_new(file_name, title, None, tables, open_file)


def create_table_of_contents(items):
    list_items = create_elements(TAG_LI, [create_element(TAG_A, item[0], f'href="#{item[1]}"') for item in items])
    return create_element(TAG_H3, "Table of Contents") + create_element(TAG_OL, list_items)


def write_html_file_new(file_name, my_title, my_instructions, my_tables, open_file=False, style_file=None, do_toc=False, do_trailer=True):
    if style_file:
        # link_attributes = f'rel="stylesheet" href="{style_sheet}"'
        # style = create_element(TAG_LINK, "", link_attributes, False)
        style_sheet = read_style(style_file)
    else:
        style_sheet = read_style()
    style = create_element(TAG_STYLE, style_sheet)
    heading = create_element(TAG_H1, my_title)
    if my_instructions:
        instructions = create_element(TAG_DIV, my_instructions)
        heading += "<br>" + instructions
    script = create_element(TAG_SCRIPT, sort_script)
    meta_desc_attributes = f'name="description" content="OutputUtil developed by LT. Executed by {os.getcwd()}"'
    meta = create_element(TAG_META, "",  meta_desc_attributes, False)
    head = create_element(TAG_HEAD, meta + style + script)
    tables = ""
    toc_items = []
    for table in my_tables:
        title, headers, types, alignments, data = table
        if len(data) == 0:
            data = [[""] * len(headers)]
        if len(headers) != len(types) or len(types) != len(alignments) or len(types) != len(data[0]):
            print("ERROR: Mismatch in headers, types, alignments, and data for file", file_name, "headers", headers)
            return
        table_id = f"table-{random.randint(1, 1000)}"
        if title:
            tables += create_element(TAG_H3, title)
            table_id = f"table-{title.replace(' ', '-')}"
        tables += create_table(headers, types, alignments, data, False, None, table_id)
        toc_items.append([title, table_id])
    trailer = ""
    if do_trailer:
        dt = datetime.now().strftime("%b. %d, %Y %H:%M %p")
        trailer = create_element(TAG_CENTER, create_element(TAG_H6, f'&copy;2025 • All Rights Reserved • Generated on {dt}'))
    toc = create_table_of_contents(toc_items) if do_toc else ""
    body = create_element(TAG_BODY, heading + toc + tables + trailer)
    message = create_element(TAG_HTML, head + body)
    write_file(file_name, message)
    print("Wrote output file", file_name)
    if open_file:
        open_file_in_browser(file_name)


def write_csv_file(file_name, headers, data):
    with open(file_name, 'w', newline='', encoding='UTF-8') as file:
        write = csv.writer(file)
        write.writerow(headers)
        write.writerows(data)
    print("Wrote output file", file_name)


def write_tt_file(file_name, heading, headers, data, alignment=None):
    if not alignment:
        alignment = ["l"] * len(headers)
    rows = [headers] + data
    tt = texttable.Texttable(0)
    tt.set_cols_align(alignment)
    tt.add_rows(rows, header=True)
    table = heading + "\n" + tt.draw()
    with open(file_name, 'w', encoding='UTF-8') as file:
        file.write(table)
    print("Wrote output file", file_name)


def xml_clean(item):
    return str(item).replace("&", "&amp;")


def write_xml_file(file_name, title, headers, data, do_open=False):
    nl = "\n"
    headers = [header.replace(" ", "") for header in headers]
    x_header = '<?xml version="1.0" encoding="UTF-8"' + '?>'
    x_title = nl + create_element("title", xml_clean(title))
    content = ""
    for row in data:
        x_items = nl + "".join([create_element(headers[i], xml_clean(row[i])) for i in range(len(row))])
        x_row = create_element("row", x_items)
        content += x_row
    x_body = nl + create_element("root", x_title + content)
    xml = x_header + x_body
    write_file(file_name, xml)
    if do_open:
        open_file_in_browser(file_name)


def get_random_colors(size):
    return ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(size)]


def write_bar_graph(file_name, title, x_label, x_data, x_ticks, y_label, y_data, y_ticks):
    size = len(x_data)
    colors = get_random_colors(size)
    plt.xticks([j for j in range(size)], [str(item) for item in x_data])
    plt.bar(x_data, y_data, color=colors, width=0.1)
    plt.title(title)
    if x_ticks:
        plt.xticks(x_data, x_ticks)
    if y_ticks:
        plt.yticks(y_data, y_ticks)
    ax = plt.gca()
    ax.tick_params(axis='x', labelrotation=-90, labelsize=5)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(file_name)
    plt.show()


def add_stats(data, stat_cols, stat_idx=0, dec=1, bold=False):
    dict_stats = {"COUNT": len, "TOTAL": sum, "MINIMUM": min, "MAXIMUM": max,
                  "MEDIAN": median, "MEAN": mean, "STD DEV": std}
    rows = len(data)
    cols = len(data[0])
    for stat in dict_stats:
        func = dict_stats[stat]
        stat_row = [""] * cols
        stat_row[stat_idx] = create_element("b", stat) if bold else stat
        for col in stat_cols:
            val = round(func([data[row][col] for row in range(rows)]), dec)
            stat_row[col] = create_element("b", val) if bold else val
        data.append(stat_row)
