# -*- coding: utf-8 -*-

from aqt.qt import *
from anki.utils import isMac, isWin
import anki.js

def getBaseUrlText(col):
    base = None
    mdir = col.media.dir()
    if isWin and not mdir.startswith("\\\\"):
        prefix = u"file:///"
    else:
        prefix = u"file://"
    mdir = mdir.replace("\\", "/")
    base = prefix + mdir.encode("utf-8") + "/"
    return base

def setHtmlWithBaseUrl(self, html, baseUrlText, loadCB=None):
    self.key = None
    self._loadFinishedCB = loadCB
    QWebView.setHtml(self, html, QUrl(baseUrlText))

def stdHtmlWithBaseUrl(self, body, baseUrlText, css="", bodyClass="", loadCB=None, js=None, head=""):
    if isMac:
        button = "font-weight: bold; height: 24px;"
    else:
        button = "font-weight: normal;"
    content = """
<!doctype html>
<html><head><style>
button {
%s
}
%s</style>
<script>%s</script>
%s

</head>
<body class="%s">%s</body></html>""" % (
        button, css, js or anki.js.jquery + anki.js.browserSel,
        head, bodyClass, body)
    setHtmlWithBaseUrl(self, content, baseUrlText, loadCB)