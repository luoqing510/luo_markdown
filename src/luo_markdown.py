from dominate import document
from dominate.tags import *
import re
index_css = '''
html, body { scrollbar-width: none;width: 100%; background-color: rgb(55, 68, 79); color: aliceblue; font-family: '楷体'; }
h1 { font-weight: bolder; }
h2, h3, h4, h5, h6 { font-weight: 200; }
.wire { width: 100%; background-color: rgb(143, 185, 175); height: 2px; border-radius: 5px; margin: 13px auto; }
#root { width: 90%; margin: 0 auto; }
img { width: 90%; border-radius: 5px; margin: 10px auto 0 5%; }
span {font-size: 1.2em;}
ol {font-size: 1.2em;margin-left: 10px;}
table { min-width: 40%;max-width: 90%;height: auto;border-collapse: collapse; border-spacing: 0px; margin-left: 10px; }
th, td {  min-width: 20%;height: 10%; border: 2px solid rgb(142, 156, 159);padding:5px 8px }
'''


def ul_li_create(lines: list[str]):
    length = len(lines)
    html = ul()

    def ul_li(line: str):
        html = li()

        def findLi():
            lis = html.getElementsByTagName("li")
            return lis[len(lis) - 1]

        value = line.replace("- ", "")
        sr_len = int((len(line) - len(value)) / 2)
        if sr_len == 1:
            return li(span(value))
        uli = ul(li())
        for j in range(sr_len):
            if j == 0 and sr_len != 1:
                html.add(uli)
            elif j == sr_len - 1:
                findLi().add_raw_string(span(value))
            else:
                findLi().add(ul(li()))
        return html

    for i in range(length):
        html.add(ul_li(lines[i]))
    return html


def ol_li_create(vals):
    html = ol()
    for i in vals:
        html.add(li(i))
    return html


def table_create(vals):
    text_align = {
        "left": r"^\:(\-)+$",
        "center": r"^\:(\-)+\:$",
        "right": r"^(\-)+\:$"
    }
    text_al = [None for i in range(len(vals[1]))]
    html = table()
    head = tr()
    body_list = []
    if len(vals) < 2:
        return span(vals)
    else:
        for i in range(len(vals)):
            if i > 1:
                body_list.append(tr())
            line = vals[i]
            table_len = len(line) - len(line.replace("|", "")) - 1
            table_re = re.match(r"\|(.*)" * table_len + "\\|", line)
            if (group := table_re.groups()) != None:
                for j in range(len(group)):
                    if i == 0:
                        head.add(th(group[j]))
                    elif i == 1:
                        for k in text_align.keys():
                            ty = re.match(
                                text_align[k], group[j].strip())
                            if ty != None:
                                text_al[j] = k
                            else:
                                if k == "right" and text_al[j] == None:
                                    text_al[j] = "left"
                    elif i != 1:
                        body_list[i - 2].add(td(group[j]))
    html.add(thead(head))
    for i in body_list:
        html.add(tbody(i))

    for i in html.getElementsByTagName("tr"):
        for j in range(len(i.children)):
            i.children[j].set_attribute("style", f"text-align:{text_al[j]}")
    return html


class Create_html:
    dir: str
    h1_h6 = [h1, h2, h3, h4, h5, h6]
    ul_li_list = []
    ol_li_list = []
    table_list = []

    def __init__(self, path: str, toPath: str):
        rot = document(title='LuoMarkdown')
        rot.header.add(style(index_css))
        rot.add(div(id="root"))
        root = rot.getElementById("root")
        if path.find("\\") != -1:
            path = path.replace("\\", "/")
        path_list = path.split("/")
        path_list.pop()
        self.dir = "/".join(path_list)
        with open(path, 'r', encoding="UTF_8") as f:
            lines = f.readlines()
            for i in range(0, len(lines)):
                line = lines[i].strip()
                html = self.get_html(line)
                if html != None:
                    if html == "ul_li":
                        self.ul_li_list.append(line)
                    elif html == "ol_li":
                        val = re.match(
                            r"(\d)\. (.*)", line).groups()[1]
                        self.ol_li_list.append(val)
                    elif html == "table":
                        self.table_list.append(line)
                    else:
                        if self.ul_li_list != []:
                            val = ul_li_create(self.ul_li_list)
                            if val:
                                self.ul_li_list = []
                            root.add(val)
                        if self.ol_li_list != []:
                            val = ol_li_create(self.ol_li_list)
                            if val:
                                self.ol_li_list = []
                            root.add(val)
                        if self.table_list != []:
                            val = table_create(self.table_list)
                            if val:
                                self.table_list = []
                            root.add(val)
                        root.add(html)
        with open(toPath, 'w', encoding="UTF_8") as f:
            f.write(str(rot))

    def GetPath(self, path: str):
        if path[0] == '/':
            return self.dir + path
        elif path[0] == '.':
            path_list = path.split('/')
            path_list.pop(0)
            return self.dir + "/" + "/".join(path_list)
        else:
            return self.dir + "/" + path

    def Regex(self, line: str):
        regex = {
            "img": r"\!\[(.*)\]\(((.*)\.(.*))\)",
            "ul_li": r"(- )+(.*)",
            "ol_li": r"(\d)\. (.*)"
        }
        table_len = len(line) - len(line.replace("|", "")) - 1
        table_re = re.match(r"\|(.*)" * table_len + "\\|", line)
        if table_re != None:
            return {"type": "table"}
        ret = {}
        for i in regex.keys():
            value = re.match(regex[i], line)
            if value != None:
                val = value.groups()
                ret["type"] = i
                match i:
                    case "img":
                        ret["alt"] = val[0]
                        ret["url"] = val[1]
        if ret != {}:
            return ret
        else:
            return None

    def get_html(self, line: str):
        if line == "":
            return None
        str_list = line.split(" ")
        match str_list[0]:
            case "style":
                src = str_list[1].split(":src>")[1].replace('"', "")
                with open(self.GetPath(src), 'r', encoding="UTF_8") as f:
                    return style(f.read().strip())
            case "---":
                return div(className="wire")
            case _:
                str_len = len(str_list[0])
                # 处理h1_h6
                if (str_list[0] == '#' * str_len):
                    return self.h1_h6[str_len - 1](str_list[1])
                # 处理特色大型字体
                if (str_list[0].replace("+" * (str_len - 1), "") == "#"):
                    return p(str_list[1], style=f"font-size:{str_len - 1}rem")
                # 处理图片
                if (reg := self.Regex(line)) != None:
                    match reg["type"]:
                        case "img":
                            return img(src=self.GetPath(reg["url"]), alt=reg["alt"], draggable="false")
                        case "ul_li": return "ul_li"
                        case "ol_li": return "ol_li"
                        case "table": return "table"
                else:
                    return span(line)
        return None
