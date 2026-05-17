"""Regression checks for recent inline note-residue cleanup."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH02 = REPO_ROOT / "tex" / "chapters" / "ch02.tex"
CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
CH04 = REPO_ROOT / "tex" / "chapters" / "ch04.tex"
CH05 = REPO_ROOT / "tex" / "chapters" / "ch05.tex"
APP04 = REPO_ROOT / "tex" / "appendices" / "app04.tex"
APP05 = REPO_ROOT / "tex" / "appendices" / "app05.tex"


def test_ch03_no_long_note_spills():
    text = CH03.read_text(encoding="utf-8")
    offenders = [
        "dictionary. 14 Following",
        "} 15 it also quotes",
        "(fig.\\footnote[57]",
        "(fig.\\footnote[65]",
        "104105106107108109",
        "inscriptionless cracks identified in sec.\\footnote[119]",
        "87 U U ]",
        'it will be inauspicious."92',
        "be inauspicious.93",
        "In Tuan (?).94",
        "(cf. sec.\\footnote[92]",
        "carved. more",
        "CCC C D U 0 81",
    ]

    found = [needle for needle in offenders if needle in text]
    assert not found, "Found lingering ch03 note residue:\n" + "\n".join(found)

    assert "dictionary.\\footnote[14]{" in text
    assert "vessels,\\footnote[15]{" in text
    assert "Guo\\footnote[104]{" in text
    assert "routine abbreviation.\\footnote[106]{" in text
    assert "inscriptionless cracks identified in \\ref{sec:chapters-ch03:3.7.2} (sec. 3.7.2)\\footnote[119]{" in text
    assert "it will be inauspicious.\\footnote[92]{" in text
    assert "be inauspicious.\\footnote[93]{" in text
    assert "In Tuan (?).\\footnote[94]{" in text
    assert "\\ref{sec:chapters-ch01:1.6.4} (sec. 1.6.4)).\\footnote[95]{" in text
    assert "cracks were left numberless.\\footnote[96]{" in text
    assert "\\pinyinterm{hu-houxuan} (\\citeyear{Hu1955Yinhsu}), pp. 38-41" in text
    assert "胡 (1955), pp. 38-41" not in text


def test_ch04_no_calligraphy_note_block_spill():
    text = CH04.read_text(encoding="utf-8")
    offenders = [
        "董 found the style",
        "董 described the style",
        "陳 cites",
        "乙 Kung",
        "(fig. 7)@@",
        "upon}",
        "107 U 11 |",
        "(sec. 4.3.1.2).49",
        "*135",
    ]

    found = [needle for needle in offenders if needle in text]
    assert not found, "Found lingering ch04 note residue:\n" + "\n".join(found)

    assert "\\footnote[49]{On touchstone inscriptions, see n. 1.}" in text
    assert "\\pinyinterm{dong-short} found the style of period II" in text
    assert "\\pinyinterm{dong-short} found the style of period III" in text
    assert "\\pinyinterm{dong-short} found the style of period IV" in text
    assert "\\pinyinterm{dong-short} described the style of period V" in text
    assert "Yi Kung (1957)" not in text
    assert r"Yi Kung (\citeyear{Yi1957Mantan})" in text
    assert "periods III and V.\\footnote[63]{" in text
    assert "corners than curves.\\footnote[65]{" in text
    assert "any period.\\footnote[66]{" in text
    assert "fig. 10).\\footnote[67]{" in text
    assert "epigraphic traditions).\\footnote[68]{" in text
    assert "tsai ming\\footnote[135]{" in text
    assert "charge (?),''\\footnote[134]{" in text
    assert "period II.\\footnote[136]{" in text
    assert "recorded.\\footnote[137]{" in text
    assert "shape changes;\\footnote[159]{" in text
    assert "other scholars.\\footnote[160]{" in text
    assert "need revision.\\footnote[161]{" in text
    assert "marks behind them.\\footnote[162]{" in text
    assert "disordered;\\footnote[163]{" in text
    assert "sites.\\footnote[164]{" in text


def test_ch01_and_ch02_long_note_sentinel_runs_removed():
    ch01 = CH01.read_text(encoding="utf-8")
    ch02 = CH02.read_text(encoding="utf-8")

    assert "535455565758" not in ch01
    assert "848586878889" not in ch01
    assert "146147148149150151152153" not in ch02
    assert "6970717273" not in ch02

    assert "smoothed.\\footnote[53]{" in ch01
    assert "shell is speculative.} %52" in ch01
    assert "thickness (fig. 3).\\footnote[54]{" in ch01
    assert "written on.\\footnote[55]{" in ch01
    assert "tie them together.\\footnote[56]{" in ch01
    assert "period V.\\footnote[57]{" in ch01
    assert "had been formed\\footnote[58]{" in ch01
    assert "\\pinyinterm{hu-houxuan} (\\citeyear{Hu1944Wuting}), p. 55b" in ch01
    assert "see 胡 (1944), p. 55b" not in ch01
    assert "\\pinyinterm{xu-jinxiong} stresses" in ch01
    assert "scapulas, 徐 stresses" not in ch01
    assert "\\pinyinterm{hu-houxuan} (\\citeyear{Hu1944aYintai}), pp. 6b-8a." in ch01
    assert "see \\pinyinterm{hu-houxuan} (\\citeyear{Hu1944Wuting}), p. 55b" in ch01
    assert "\\pinyinterm{xu-jinxiong} (\\citeyear{Hsu1974Scapulimantic}), p. 12;" in ch01
    assert "cf. \\pinyinterm{xu-jinxiong} (\\citeyear{Hsu1973aPuku}), pp. 6, 40-41, 64-65." in ch01
    assert "cf. 徐 (1973a), pp. 6, 40-41, 64-65." not in ch01
    assert "cf. \\pinyinterm{xu-jinxiong} (\\citeyear{Hsu1973aPuku}), pp. 15, 40-41, 88-89;" in ch01
    assert "cf. 徐 (1973a), pp. 15, 40-41, 88-89;" not in ch01
    assert "vice versa.\\footnote[84]{" in ch01
    assert "vice versa.\\footnote[85]{" in ch01
    assert "pp. 125–127.} %83" in ch01
    assert "n 0 ] 0 0" not in ch01
    assert "\\footnote[95]{\\pinyinterm{xu-jinxiong} (\\citeyear{Hsu1973aPuku}), pp. 15, 88-89;" in ch01
    assert "\\footnote[95]{徐 (1973a), pp. 15, 88-89;" not in ch01
    assert "bureaucratic works of art.\\footnote[86]{" in ch01
    assert "left scapula.\\footnote[87]{" in ch01
    assert "marginal notations.\\footnote[88]{" in ch01
    assert "consistently followed.\\footnote[89]{" in ch01
    assert "continuing a tradition first recorded in Kojiki" in ch01
    assert "Unlike this unprepared, Neolithic scapulimancy," in ch01
    assert "23 \\{] | J}" not in ch01
    assert "shell is 13 [ ] ]] ] 11 1}" not in ch01
    assert "appeared behind the semicircular side hollow,\\footnote[102]{" in ch01

    assert "black.\\footnote[146]{" in ch02
    assert "with brown.\\footnote[147]{" in ch02
    assert "clear.\\footnote[148]{" in ch02
    assert "beautiful.''\\footnote[149]{" in ch02
    assert "matter.''\\footnote[150]{" in ch02
    assert "divining rod.\\footnote[151]{" in ch02
    assert "notations were.\\footnote[152]{" in ch02
    assert "determined.\\footnote[153]{" in ch02
    assert 'exercise sheets."100' not in ch02
    assert "shell. 102 We are" not in ch02
    assert "exercise sheets.''\\footnote[100]{" in ch02
    assert "shell.\\footnote[102]{" in ch02
    assert "Ti 乙" not in ch02
    assert "Royal Family group.\\footnote[69]{" in ch02
    assert "ten-day week.\\footnote[70]{" in ch02
    assert "day of divination.\\footnote[71]{" in ch02
    assert "advance.\\footnote[72]{" in ch02
    assert "to stress.\\footnote[73]{" in ch02


def test_appendix_note_reference_residue_removed():
    app04 = APP04.read_text(encoding="utf-8")
    app05 = APP05.read_text(encoding="utf-8")

    assert "table\\footnote[28]" not in app04
    assert "table 2.\\footnote[28]{" in app04
    assert "described in sec.\\footnote[1]" not in app05
    assert "described in \\ref{sec:chapters-ch04:4.3.1.12} (sec. 4.3.1.12). Changes" in app05
    assert "period I.\\footnote[1]{" in app05
    assert "(day\\footnote[5]" not in app05
    assert "[In the tenth month].\\footnote[5]{" in app05
    assert "no fault.\\footnote[6]{Zhuixin 304." in app05
    assert "ritual, may also be established.8" not in app05
    assert "I inscriptions. 10 The names" not in app05
    assert "statelets. 15 Divinations" not in app05
    assert "periods II to V.30 Divinations" not in app05
    assert "period V.31 Divinations" not in app05
    assert "criteria. 32" not in app05
    assert "period I inscriptions.33" not in app05
    assert "7. E.g., Hou-pien" not in app05
    assert "30. See the inscriptions listed at S169.3" not in app05
    assert "established.\\footnote[8]{" in app05
    assert "group.\\footnote[9]{" in app05
    assert "statelets.\\footnote[15]{" in app05
    assert "periods II to V.\\footnote[30]{" in app05
    assert "group, but never in period V.\\footnote[31]{" in app05


def test_cross_chapter_footnote_and_name_residue_removed():
    ch03 = CH03.read_text(encoding="utf-8")
    ch04 = CH04.read_text(encoding="utf-8")

    assert "first published by 董" not in ch03
    assert "Wang 乙-jung" not in ch03
    assert "刘 E" not in ch03
    assert "Wang Yi-jung and Liu E" in ch03

    assert "vice versa.¹ 179" not in ch04
    assert "110111112113114115" not in ch04
    assert "116117118119120121122123" not in ch04
    assert "(V).8 These dating" not in ch04
    assert "significant.\\footnote[179]" not in ch04
    assert "董 concluded that the pit" not in ch04
    assert "董 and his" not in ch04
    assert "Ti 乙" not in ch04
    assert "vice versa.\\footnote[179]{" in ch04
    assert "significant.\\footnote[180]{" in ch04
    assert "appeared.\\footnote[181]{" in ch04
    assert "Jiabian.\\footnote[182]{" in ch04
    assert "Late (V).\\footnote[8]{" in ch04
    assert "comparative certainty.\\footnote[10]{" in ch04
    assert "historical terms.\\footnote[11]{" in ch04
    assert "inauspicious.\\footnote[110]{" in ch04
    assert "changed radically.\\footnote[111]{" in ch04
    assert "lacked them altogether.\\footnote[112]{" in ch04
    assert "commoner by period V.\\footnote[113]{" in ch04
    assert "period I,\\footnote[114]{" in ch04
    assert "only the chi.\\footnote[115]{" in ch04
    assert "as the charge.\\footnote[116]{" in ch04
    assert "the cracks.''\\footnote[117]{" in ch04
    assert "Royal Family group).\\footnote[118]{" in ch04
    assert "shared a similar evolution.\\footnote[119]{" in ch04
    assert "period I.\\footnote[120]{" in ch04
    assert "detailed verifications,\\footnote[121]{" in ch04
    assert "thirteen foxes''\\footnote[122]{" in ch04
    assert "other periods.\\footnote[123]{" in ch04


def test_ch05_reconstruction_note_runs_removed():
    ch05 = CH05.read_text(encoding="utf-8")

    assert "7071727374757677" not in ch05
    assert "mirror together\\footnote[69]" not in ch05
    assert "'' 69 should remind us" not in ch05
    assert "151 0 ]" not in ch05

    assert "mirror together''\\footnote[69]{" in ch05
    assert "question.\\footnote[70]{" in ch05
    assert "\\ref{sec:chapters-ch02:2.9.4} (secs. 1.5.1; 2.4; 2.6; 2.9.4)).\\footnote[71]{" in ch05
    assert "fig. 30),\\footnote[72]{" in ch05
    assert "to be wrong.\\footnote[73]{" in ch05
    assert "serious consequences.\\footnote[74]{" in ch05
    assert "completed.\\footnote[75]{" in ch05
    assert "features matched.\\footnote[76]{" in ch05
    assert "fig. 30).\\footnote[77]{" in ch05
    assert "role of the historian.\\footnote[90]{" in ch05
    assert "silenced.''\\footnote[91]{" in ch05
    assert "unreason''\\footnote[92]{" in ch05
    assert "history.''\\footnote[93]{" in ch05
    assert "extend our own.\\footnote[94]{" in ch05
