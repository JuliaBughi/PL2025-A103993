import sys
import re

def markdown_to_html(md):
    file = open(md, 'r', encoding='utf-8')
    html = file.read()

    #header em md são representados por '#', '##', '###'
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    #bold em md é representado por **bold**
    html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
    
    #itálico em md é representado por *itálico*
    html = re.sub(r'\*([^*]+?)\*', r'<i>\1</i>', html)

    #links em md são representados por [texto](endereço url)
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    
    #imagens em md são representadas por ![texto alternativo](path para a imagem)
    html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1">', html)

    def replace_list(match):
        list_text = match.group(1)
        items = re.findall(r'^\d+\. (.+)$', list_text, re.MULTILINE)
        html_list = '<ol>\n'
        for item in items:
            html_list += f'  <li>{item}</li>\n'
        html_list += '</ol>'
        return html_list

    #listas numeradas em md são 1., 2., 3., etc...
    html = re.sub(r'((?:^\d+\. .+\n?)+)', replace_list, html, flags=re.MULTILINE)

    f = open("converted.html", 'w', encoding='utf-8')
    f.write(html)
    
md = "README.md"

markdown_to_html(md)