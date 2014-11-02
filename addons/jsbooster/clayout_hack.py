import re

from aqt.qt import *
from anki.consts import *
import aqt
from anki.sound import playFromText, clearAudioQueue
from aqt.utils import saveGeom, restoreGeom, getBase, mungeQA,\
    showInfo, askUser, getOnlyText, \
     showWarning, openHelp
from anki.utils import isMac, isWin, joinFields
from aqt.webview import AnkiWebView
import anki.js
import aqt.clayout

from location_hack import getBaseUrlText, stdHtmlWithBaseUrl

def customRenderPreview(self):
    c = self.card
    ti = self.maybeTextInput
    baseUrlText = getBaseUrlText(self.mw.col) + "__previewer__.html"
    stdHtmlWithBaseUrl(self.tab['pform'].frontWeb,
        ti(mungeQA(self.mw.col, c.q(reload=True))),
        baseUrlText, self.mw.reviewer._styles(),
        bodyClass="card card%d" % (c.ord+1),
        js=anki.js.browserSel)
    stdHtmlWithBaseUrl(self.tab['pform'].backWeb,
        ti(mungeQA(self.mw.col, c.a()), type='a'),
        baseUrlText, self.mw.reviewer._styles(),
        bodyClass="card card%d" % (c.ord+1),
        js=anki.js.browserSel)
    clearAudioQueue()
    if c.id not in self.playedAudio:
        playFromText(c.q())
        playFromText(c.a())
        self.playedAudio[c.id] = True

aqt.clayout.CardLayout.renderPreview = customRenderPreview