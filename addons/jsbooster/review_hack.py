# -*- coding: utf-8 -*-

from __future__ import division
import difflib
import re
import cgi
import unicodedata as ucd
import HTMLParser

from anki.lang import _, ngettext
from aqt.qt import *
from anki.utils import  stripHTML, isMac, json
from anki.hooks import addHook, runHook
from anki.sound import playFromText, clearAudioQueue, play
from aqt.utils import mungeQA, getBase, openLink, tooltip, askUserDialog
from aqt.sound import getAudio
import aqt

from location_hack import getBaseUrlText, stdHtmlWithBaseUrl

def customInitWeb(self):
    self._reps = 0
    self._bottomReady = False
    # show answer / ease buttons
    self.bottom.web.show()
    self.bottom.web.stdHtml(
        self._bottomHTML(),
        self.bottom._css + self._bottomCSS,
    loadCB=lambda x: self._showAnswerButton())
    self._showQuestion()

def customShowQuestion(self):
    self._reps += 1
    self.state = "question"
    self.typedAnswer = None
    c = self.card
    # grab the question and play audio
    if c.isEmpty():
        q = _("""\
The front of this card is empty. Please run Tools>Empty Cards.""")
    else:
        q = c.q()
    if self.autoplay(c):
        playFromText(q)
    # render & update bottom
    q = self._mungeQA(q)
    baseUrlText = getBaseUrlText(self.mw.col) + "__reviewer__.html"
    stdHtmlWithBaseUrl(self.web,
        (review_html_content % q) + review_html_scripts,
        baseUrlText,
        self._styles(),
        loadCB=lambda x: customShowQuestionLoadCallback(self, c))

def customShowQuestionLoadCallback(self, card):
    klass = "card card%d" % (card.ord+1)
    self.web.eval("_updateQA(false, '%s');" % klass)
    self._toggleStar()
    if self._bottomReady:
        self._showAnswerButton()
    # if we have a type answer field, focus main web
    if self.typeCorrect:
        self.mw.web.setFocus()
    # user hook
    runHook('showQuestion')

def customShowAnswer(self):
    if self.mw.state != "review":
        # showing resetRequired screen; ignore space
        return
    self.state = "answer"
    c = self.card
    a = c.a()

    # play audio?
    if self.autoplay(c):
        playFromText(a)
    # render and update bottom
    a = self._mungeQA(a)
    baseUrlText = getBaseUrlText(self.mw.col) + "__reviewer__.html"
    stdHtmlWithBaseUrl(self.web,
        (review_html_content % a) + review_html_scripts,
        baseUrlText,
        self._styles(),
        loadCB=lambda x: customShowAnswerLoadCallback(self, c))

def customShowAnswerLoadCallback(self, card):
    klass = "card card%d" % (card.ord+1)
    self.web.eval("_updateQA(true, '%s');" % klass)
    self._showEaseButtons()
    # user hook
    runHook('showAnswer')

review_html_content = """
<img src="qrc:/icons/rating.png" id=star class=marked>
<div id=qa>%s</div>"""

review_html_scripts = """<script>
var ankiPlatform = "desktop";
var typeans;
function _updateQA (answerMode, klass) {
    typeans = document.getElementById("typeans");
    if (typeans) {
        typeans.focus();
    }
    if (answerMode) {
        var e = $("#answer");
        if (e[0]) { e[0].scrollIntoView(); }
    } else {
        window.scrollTo(0, 0);
    }
    if (klass) {
        document.body.className = klass;
    }
    // don't allow drags of images, which cause them to be deleted
    $("img").attr("draggable", false);
};

function _toggleStar (show) {
    if (show) {
        $(".marked").show();
    } else {
        $(".marked").hide();
    }
}

function _getTypedText () {
    if (typeans) {
        py.link("typeans:"+typeans.value);
    }
};
function _typeAnsPress() {
    if (window.event.keyCode === 13) {
        py.link("ansHack");
    }
}
</script>"""

aqt.reviewer.Reviewer._initWeb = customInitWeb
aqt.reviewer.Reviewer._showQuestion = customShowQuestion
aqt.reviewer.Reviewer._showAnswer = customShowAnswer
