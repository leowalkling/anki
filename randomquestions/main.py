# -*- coding: utf-8 -*-

import os

from anki.utils import json
from aqt import editor, mw
from anki.hooks import wrap
from aqt.qt import *
from aqt.webview import AnkiWebView
from aqt.reviewer import Reviewer
from anki.sound import playFromText
from aqt.utils import getBase
from anki.hooks import runHook
import re

# Helper functions
##################################################

def counter(start=0, step=1):
    "Generator to create infinite numbers."
    n = start
    while True:
        yield n
        n += step

def set_icon(button, name):
    icon_path = os.path.join(addons_folder(),
        "extra_buttons/icons/{}.png".format(name))
    button.setIcon(QIcon(icon_path))

# Preferences
##################################################

def addons_folder():
    return mw.pm.addonFolder()

def setup_randomquestions_buttons(self):
    self._addButton("format_choice", self.format_choice, text = "CH")

last_choice_set = None
last_choice_id = None

def format_choice(self):
    dialog = QDialog(self.parentWindow)
    dialog.setWindowTitle("Define the choice")

    form = QFormLayout()
    form.addRow(QLabel("Define the choice"))
    
    choiceSetSpinBox = QSpinBox(dialog)
    choiceSetSpinBox.setMinimum(1)
    choiceSetSpinBox.setMaximum(5)
    if last_choice_set:
        choiceSetSpinBox.setValue(last_choice_set)
    choiceSetLabel = QLabel("Choice set:")
    form.addRow(choiceSetLabel, choiceSetSpinBox)

    choiceIdLineEdit = QLineEdit(dialog)
    if last_choice_id is None:
        choiceIdLineEdit.setText(str(0))
    elif re.match(r"^\d{,2}$", last_choice_id):
        choiceIdLineEdit.setText(str(int(last_choice_id) + 1))
    else:
        choiceIdLineEdit.setText(last_choice_id)
    choiceIdLabel = QLabel("Choice id:")
    form.addRow(choiceIdLabel, choiceIdLineEdit)

    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok |
        QDialogButtonBox.Cancel, Qt.Horizontal, dialog)

    buttonBox.accepted.connect(dialog.accept)
    buttonBox.rejected.connect(dialog.reject)

    form.addRow(buttonBox)

    dialog.setLayout(form)

    if dialog.exec_() == QDialog.Accepted:
        self.currentChoiceSet = choiceSetSpinBox.value()
        self.currentChoiceId = choiceIdLineEdit.text()
        _myscript = """
var selection = document.getSelection();
if (selection && selection.rangeCount === 1) {{
var range = selection.getRangeAt(0);
if (selection.isCollapsed) {{
    var container = selection.anchorNode;
    if (container.nodeType !== 1) {{
        container = container.parentElement;
    }}
    if (container) {{
        var currentClassName = container.className;
        container.setAttribute('data-choice', '{0}:{1}');
    }}
}} else {{
    if (range.startContainer === range.commonAncestorContainer || range.startContainer.parentNode === range.commonAncestorContainer &&
        range.endContainer === range.commonAncestorContainer || range.endContainer.parentNode === range.commonAncestorContainer) {{
        var wrapping = document.createElement('span');
        wrapping.setAttribute('data-choice', '{0}:{1}');
        range.surroundContents(wrapping);
    }}
}}
}}
        """.format(last_choice_set, last_choice_id)
        self.web.eval(_myscript)

editor.Editor.format_choice = format_choice
editor.Editor.setupButtons = wrap(editor.Editor.setupButtons, setup_randomquestions_buttons)

BASE_URL_REGEX = re.compile('''<base href="(.*?)">''')

def get_base_url(html):
    match_result = BASE_URL_REGEX.search(html)
    if match_result is None or match_result:
        return None
    try:
        url = urllib.unquote(matchResult.group(1)) + "__viewer__.html"
        return QUrl(url)
    except AttributeError:
        None

def setHtml(self, html, loadCB=None):
	self.key = None
	self._loadFinishedCB = loadCB
	base_url = get_base_url(html)
	if (base_url is None):
		QWebView.setHtml(self, html)
	else:
		QWebView.setHtml(self, html, base_url)

AnkiWebView.setHtml = setHtml

def nextCardPreHook(self):
    self._reps = None

def myShowAnswer(self):
    base = getBase(self.mw.col)
    klass = "card card%d" % (self.card.ord+1)
    self.web.stdHtml(self._revHtml, self._styles(), head=base)
    self.web.eval("_updateQA({}, false, '%s');" % klass)

Reviewer.nextCard = wrap(Reviewer.nextCard, nextCardPreHook, 'before')
Reviewer._showAnswer = wrap(Reviewer._showAnswer, myShowAnswer, 'before')