from pathlib import Path


APP03 = Path("tex/appendices/app03.tex")
APP04 = Path("tex/appendices/app04.tex")


def test_appendix_3_page_marker_debris_removed():
    text = APP03.read_text(encoding="utf-8")

    assert "165 U U D" not in text
    assert "C C C" not in text
    assert "@@HEADING@@228@@" not in text
    assert "228 plastrons (or, more accurately, plastron fragments)" in text
    assert "109,617" in text


def test_appendix_4_heading_debris_and_note_splice_removed():
    text = APP04.read_text(encoding="utf-8")

    assert "171 U U U" not in text
    assert "E D O" not in text
    assert "TEL\nAPPENDIX 4" not in text
    assert "@@HEADING@@21@@" not in text
    assert "@@HEADING@@1180@@" not in text
    assert "21 years; Later Han, at 16 years; T'ang, at 12" in text
    assert "Knoblock (1964).} %27" in text
    assert "period II burial (see n. 13)." in text
    assert "The possibility that the charcoal was older than the burial has already been mentioned." in text


def test_appendix_2_ratios_and_footnote_stubs_restored():
    text = Path("tex/appendices/app02.tex").read_text(encoding="utf-8")

    assert "shell-bone ratio of 2 to 1." in text
    assert '``the ratio of plastrons to extant scapulae is 3 to 1.\'\' '[:-1] in text
    assert "ratio of 4 to 3." in text
    assert "[\\textasciicircum{}5]" not in text
    assert "[\\textasciicircum{}6]" not in text
    assert "\\footnote[5]{In what follows, I make no attempt to distinguish plastrons from carapaces" in text
    assert "\\footnote[6]{I exclude 易編 from these discussions." in text
    assert "approximately 16 bone fragments (310 ÷ 19)" in text
    assert "8 bone fragments;\\footnote[16]" in text
    assert "\\footnote[8]{For similar tabulations" in text
    assert "\\footnote[18]{On this find, see ch. 4, n. 188, above." in text
    assert "\\footnote[22]{Ca. 72 inscribed shell fragments = ca. 2 plastrons; ca. 145 inscribed bone fragments = ca. 17 scapulas.}" in text
    assert "But see n. 11." in text
    assert "But see n. II." not in text
    assert "8 bone fragments;\\footnote[16]{" in text
    assert "} the shell fragments" in text
    assert "18. On this find, see ch. 4, n. 188, above." not in text
    assert "22. Ca. 72 inscribed shell fragments = ca. 2" not in text


def test_appendix_5_vertical_ocr_garbage_removed():
    text = Path("tex/appendices/app05.tex").read_text(encoding="utf-8")

    assert "戬五面中a:文中干館ㄜ十九:(繪五)" not in text
    assert "(1)\n(2)\n\\inscriptionsection{INSCRIPTION}" in text
    assert "(I)\n(2)\n\\inscriptionsection{INSCRIPTION}" not in text
    assert "[Hsing] divined:" in text
    assert "[Xing] divined:" not in text
    assert "\\inscriptionref{\\pinyinterm{jisi} divination}\n\n(1)\n(PREFACE:)" in text
    assert "(POSTFACE:) In the [seventh month].\n\n(2)\n(PREFACE:) Crack-making on ping-shen" in text
    assert "(POSTFACE:) In the eighth month.\n\n(3)\n(PREFACE:) Crack-making on hsin-ch'ou" in text
    assert "(POSTFACE:) In the eighth month.\n\n(4)\n(PREFACE:) Crack-making on hsin-ch'ou" in text
    assert "(CHARGE:) The king entertains; performs the chui ritual.\n\n(5)\n(PREFACE:) Crack-making on jen-yin" in text
    assert "ritual; no fault.\n\n(6)\n(PREFACE:) Crack-making on jen-yin" in text
    assert "(POSTFACE:) In the eighth month.\n\n(7)\n(PREFACE:) Crack-making on jen-tzu" in text
    assert "wish that no fault or misfortune would occur.''\\footnote[7]{" in text
    assert "Royal Family group inscriptions.\\footnote[7]" not in text
    assert "\\footnote[13]{See the inscriptions listed at S43.1-3; Shih-to 2.82, to III + IV; the rest are either RFG or, in my opinion, undatable.}" in text
    assert "\\footnote[26]{See the inscriptions listed at S230.2-3; phrases wang hsing 往省, ``go to inspect,'' 489.3-4, and wang t'ien 往田, ``go to hunt'' (S76.4-77.4); the fact that wang hsing was not used after period I suggests that this topic came to be incorporated in the hsing-t'ien, ``inspect and hunt,'' or t'ien-hsing, ``hunt and inspect,'' divinations of III + IV.}" in text
    assert "Other divinations contain the wang t'ien E" not in text
