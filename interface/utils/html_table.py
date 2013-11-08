#coding:utf-8

class HTMLTable(object):
    """html表格"""

    def __init__(self, **style):

        if "border" not in style:
            style["border"] = "1px"
        if "cellspacing" not in style:
            style["cellspacing"] = "0"
        if "cellpadding" not in style:
            style["cellpadding"] = "5"
        self.style = " ".join(["%s='%s'" %(key, style[key]) for key in style])

        self.caption = ""
        self.title = ""
        self.rows = []

    def setCaption(self, name, **style):
        style = " ".join(["%s='%s'" %(key, style[key]) for key in style])
        self.caption = "<caption %s>%s</caption>" %(name, style)

    def setTitle(self, titleList, **style):
        html  = "<tr>"
        for item in titleList:
            html += "<th>%s</th>" % item 
        html += "</tr>"
        self.title = html

    def addRow(self, rowData, **style):
        html = "<tr>"
        for item in rowData:
            html += "<td>%s</td>" % item
        html += "</tr>"
        self.rows.append(html)

    def create(self):
        html  = "<table %s>" % self.style
        html += self.caption
        html += self.title
        html += " ".join(self.rows)
        html += "</table>"
        return html

if __name__ == "__main__":
    table = HTMLTable()
    table.setCaption("测试")
    table.setTitle(["姓名", "年龄"])
    table.addRow(["张文", "28"])
    table.addRow(["代文文", "26"])
    html  = "<html>"
    html += "<head>"
    html += "    <meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>"
    html += "</head>"
    html += table.create()
    html += "</html>"
    open("./template.html", "w+").write(html)
