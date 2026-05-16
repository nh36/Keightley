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


def test_appendix_3_note_block_restored():
    text = APP03.read_text(encoding="utf-8")

    assert "150 years\\footnote[9]{" in text
    assert "every 16 days.”\\footnote[8]{" in text
    assert "original corpus.''\\footnote[10]{" in text
    assert "from pit YH127.\\footnote[11]{" in text
    assert "same notation,\\footnote[12]{" in text
    assert "1,000 (shells)''\\footnote[13]{" in text
    assert "been discovered.\\footnote[14]{" in text
    assert "likely to have\\footnote[15]{" in text
    assert "average size was 88.\\footnote[16]{" in text
    assert "to the Shang.\\footnote[17]{" in text
    assert "20 years,\\footnote[18]{" in text
    assert "ritual divinations.\\footnote[19]{" in text
    assert "the original.\\footnote[20]{" in text
    assert "50 years,\\footnote[21]{" in text
    assert "each cycle,\\footnote[22]{" in text
    assert "2 percent.\\footnote[23]{" in text
    assert "7 percent.\\footnote[24]{" in text
    assert "Shima's Sörui.\\footnote[25]{" in text
    assert "8. Presumably, the rate of use varied from" not in text
    assert "15. The records of ritual preparation" not in text
    assert "20. This approach was pioneered by Tung" not in text


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


def test_appendix_4_opening_note_block_restored():
    text = APP04.read_text(encoding="utf-8")

    assert "appendixes 2 and 3 depend upon" in text
    assert "appendixes\\footnote[2]" not in text
    assert "we possess.\\footnote[2]{" in text
    assert "1028 B.C.\\footnote[3]{" in text
    assert "Triple Concordance System,''\\footnote[5]{" in text
    assert "the conquest.\\footnote[6]{" in text
    assert "Han times.\\footnote[7]{" in text
    assert "its preface.\\footnote[8]{" in text
    assert "257 years.”\\footnote[9]{" in text
    assert "Western Chou records.\\footnote[10]{" in text
    assert "flawed accordingly.\\footnote[11]{" in text
    assert "5. This is the translation given by Sivin" not in text
    assert "6. The passage in question reads" not in text
    assert "7. Eberhard, Müller, and Henseling (1970)," not in text
    assert "10. The chronological problems are discussed" not in text
    assert "68 percent (or one-sigma) confidence intervals" in text
    assert "corresponding confidence intervals.'' or" not in text
    assert "5,568 ± 30 years" in text
    assert "pp. 252, 258-259.} %18" in text
    assert "we possess.2" not in text
    assert "1028 B.C.³" not in text


def test_appendix_4_mid_note_block_restored():
    text = APP04.read_text(encoding="utf-8")

    assert "1180 B.C.\\footnote[19]{" in text
    assert "of \\pinyinterm{di-yi} and \\pinyinterm{di-xin}" in text
    assert "thirty-three years.\\footnote[20]{" in text
    assert "state rulers of Chou.\\footnote[21]{" in text
    assert "(if not shorter).\\footnote[22]{" in text
    assert "were nine).\\footnote[23]{" in text
    assert "1041 B.C.\\footnote[24]{" in text
    assert "\\pinyinterm{lin-xin}),\\footnote[25]{" in text
    assert "assigned to \\pinyinterm{wu-ding}\\footnote[26]{" in text
    assert "new interpretation of the ritual cycle derived from inscriptions not used by Shima" in text
    assert "(1200 - [7 x 25]) = ca. 1025 B.C." in text
    assert "T₁ Yi" not in text
    assert "19. This canon, which has now been published" not in text
    assert "20. Ch'en Meng-chia (1955), p. 59." not in text
    assert "21. Bishop (1932), pp. 234-235." not in text
    assert "26. See table 37, note d." not in text


def test_missing_character_glyph_residue_cleaned():
    ch02 = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")
    ch03 = Path("tex/chapters/ch03.tex").read_text(encoding="utf-8")
    ch04 = Path("tex/chapters/ch04.tex").read_text(encoding="utf-8")
    app04 = APP04.read_text(encoding="utf-8")

    assert "nature of the ailment---\ntoothache" in ch02
    assert "estimates are---and they are probably conservative---\nthey indicate" in ch03
    assert "Specific changes in topics and idioms---changes" in ch04
    assert "general evolution\n---are presented in appendix \\ref{app:5} (appendix 5)." in ch04
    assert "The topic---which has led 徐 to" in ch04
    assert "\n---is technical and the conclusions still tentative." in ch04
    assert "to Ta Chia (K3 9)." in ch04
    assert "yüeh yu chih (*fiak)." in app04
    assert "―" not in ch02 + ch03 + ch04
    assert "⑨" not in ch04
    assert "Ƒ" not in app04
    assert "×âÌ" not in app04


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
    assert "\\inscriptionref{\\pinyinterm{jisi} divination}\n\n(1)\n\\inscriptionlabel{Preface} [Crack-making] on \\pinyinterm{jisi}" in text
    assert "\\inscriptionlabel{Postface} In the [seventh month].\n\n(2)\n\\inscriptionlabel{Preface} Crack-making on ping-shen" in text
    assert "\\inscriptionlabel{Postface} In the eighth month.\n\n(3)\n\\inscriptionlabel{Preface} Crack-making on hsin-ch'ou" in text
    assert "\\inscriptionlabel{Postface} In the eighth month.\n\n(4)\n\\inscriptionlabel{Preface} Crack-making on hsin-ch'ou" in text
    assert "\\inscriptionlabel{Charge} The king entertains; performs the chui ritual.\n\n(5)\n\\inscriptionlabel{Preface} Crack-making on jen-yin" in text
    assert "ritual; no fault.\n\n(6)\n\\inscriptionlabel{Preface} Crack-making on jen-yin" in text
    assert "\\inscriptionlabel{Postface} In the eighth month.\n\n(7)\n\\inscriptionlabel{Preface} Crack-making on jen-tzu" in text
    assert "wish that no fault or misfortune would occur.''\\footnote[7]{" in text
    assert "Royal Family group inscriptions.\\footnote[7]" not in text
    assert "\\footnote[13]{See the inscriptions listed at S43.1-3; Shih-to 2.82, to III + IV; the rest are either RFG or, in my opinion, undatable.}" in text
    assert "\\footnote[26]{See the inscriptions listed at S230.2-3; phrases wang hsing 往省, ``go to inspect,'' 489.3-4, and wang t'ien 往田, ``go to hunt'' (S76.4-77.4); the fact that wang hsing was not used after period I suggests that this topic came to be incorporated in the hsing-t'ien, ``inspect and hunt,'' or t'ien-hsing, ``hunt and inspect,'' divinations of III + IV.}" in text
    assert "Other divinations contain the wang t'ien E" not in text
    assert "``encountering great rain'' (kou ta yü) or ``encountering great wind'' (kou ta feng), which" in text
    assert "``encountering great rain'' (kou ta yü or “encountering great wind'' (kou ta feng), which" not in text
    assert "One of the disaster words---thought to refer to drought or dearth---appears only in period I inscriptions." in text
    assert "One of the disaster words-thought to refer to drought or dearth-appears only in period I inscriptions." not in text


def test_appendix_1_opening_restored():
    text = Path("tex/appendices/app01.tex").read_text(encoding="utf-8")

    assert "There have been a number of limited attempts at identifying the turtle remains from the\narchaeological site at \\pinyinterm{anyang}." in text
    assert "\\appendixsectionlabel{sec:appendices-app01:1}{1}" in text
    assert "Ting Su (1969) has made the only attempt to date to identify the \\pinyinterm{anyang} turtle shells quantitatively." in text
    assert "\n2.\n\\appendixsectionlabel{sec:appendices-app01:2}{2}\nMaterial and Methods\n" in text
    assert "[\\textasciicircum{}2]" not in text
    assert ":L" not in text
    assert "Only relationships between scute seams (fig. 3) will be considered here" in text
    assert "which were scraped clean (\\ref{sec:chapters-ch01:1.3.2} (sec. 1.3.2)) so that only the bone seams are visible" in text
    assert "Blackith and Reyment [1971]).\\footnote[1]{" in text
    assert "(R - \\lambda I)v = 0" in text
    assert "yielding a set of eigenvalues ($\\lambda$)" in text
    assert "1. With the technique of principal component" not in text


def test_chapter_4_opening_note_block_restored():
    text = Path("tex/chapters/ch04.tex").read_text(encoding="utf-8")

    assert "but not in 史赤.\\footnote[13]{" in text
    assert "\\pinyinterm{zu-xin}, ``Grand-\n% source: scan 113, printed 93\nfather Hsin'';" in text
    assert "brothers.\\footnote[28]{" in text
    assert "\\booktitle{Jimbun shakubun}, English preface, p. 15;" in text
    assert "\\pinyinterm{pinbian} 12--21 (\\ref{sec:chapters-ch03:3.7} (sec. 3.7))." in text
    assert "groups of kings.\\footnote[3]{" in text
    assert "to \\pinyinterm{di-xin}.\\footnote[4]{" in text
    assert "period IVa.\\footnote[5]{" in text
    assert "periods III and IV.\\footnote[6]{" in text
    assert "the New (V).\\footnote[7]{" in text
    assert "[\\textasciicircum{}13]" not in text
    assert "father 新''" not in text
    assert "99 99 U C C C U 11" not in text
    assert "[\\textasciicircum{}5]" not in text
    assert "U U J" not in text
    assert "3. In some cases, two or more inscriptions may" not in text
    assert "Shima apology ([1960], p. 49" not in text
def test_chapter_4_calligraphy_note_band_restored():
    text = Path("tex/chapters/ch04.tex").read_text(encoding="utf-8")

    assert "of a new king.\\footnote[47]{See \\ref{ch:2} (see ch. 2), nn. 104, 108.}" in text
    assert "same shell,\\footnote[48]{" in text
    assert "most\nprefaces.\\footnote[50]{" in text
    assert "below 6 mm. in length.\\footnote[51]{" in text
    assert "may be compared.\\footnote[52]{" in text
    assert "[\\textasciicircum{}47 \\textasciicircum{}47]" not in text
    assert "\n48. Table 19 indicates the variety of styles on\n" not in text
    assert "\n49. On touchstone inscriptions, see n. 1.\n" not in text
    assert "\n50. See \\ref{ch:2} (see ch. 2), n. 7." not in text
    assert "\n52. For display inscriptions, see \\ref{ch:2} (see ch. 2), n. 9o.\n" not in text


def test_chapter_4_note_24_page_turn_residue_cleaned():
    text = Path("tex/chapters/ch04.tex").read_text(encoding="utf-8")

    assert "But this has not been confirmed by the ancestral titles.} %24" in text
    assert "\\pinyinterm{di-xin} (K28) may be excluded in" in text
    assert "57 97 C C C C D C D C" not in text
    assert "KHHD+" not in text


def test_chapter_4_note_144_tail_cleaned():
    text = Path("tex/chapters/ch04.tex").read_text(encoding="utf-8")

    assert "pp. 99-112.} %144" in text
    assert "123 == C D D ]" not in text


def test_chapter_4_note_83_tail_cleaned():
    text = Path("tex/chapters/ch04.tex").read_text(encoding="utf-8")

    assert "single diviner.} %83" in text
    assert "III U C D" not in text


def test_chapter_3_mid_note_block_restored():
    text = Path("tex/chapters/ch03.tex").read_text(encoding="utf-8")

    assert "have indeed identified our two fragments-\\pinyinterm{yibian} 603 + 605.\\footnote[72]{" in text
    assert "used for hunting and farming.\\footnote[73]{" in text
    assert "Graphs 4 and 5, therefore, may be taken to mean ``in Chi.''\\footnote[74]{" in text
    assert "used for kuan, ``to observe.''\\footnote[75]{" in text
    assert "transcribe the inscription in this preliminary way.\\footnote[76]{" in text
    assert "``receive harvest.''\\footnote[77]{" in text
    assert "have indeed identified our two fragments-\\pinyinterm{yibian} 603 + 605.72" not in text
    assert "``receive harvest.''77" not in text


def test_chapter_3_note_52_restored():
    text = Path("tex/chapters/ch03.tex").read_text(encoding="utf-8")

    assert "than serving as word signs,\\footnote[52]{" in text
    assert "full or transitional form of the graph is found in similar context." in text
    assert "[\\textasciicircum{}52]" not in text
    assert "This approach cannot always yield certain results." in text


def test_chapter_3_opening_source_block_restored():
    text = Path("tex/chapters/ch03.tex").read_text(encoding="utf-8")

    assert "form of rubbings.\\footnote[4]{" in text
    assert "(\\ref{sec:chapters-ch05:5.5} (see sec. 5.5)), these rubbings are the primary sources" in text
    assert "historians.''\\footnote[5]{" in text
    assert "published collections.\\footnote[6]{" in text
    assert "study of the inscriptions.\\footnote[7]{" in text
    assert "57 ] U L U" not in text
    assert "sec.\\footnote[5]{" not in text
    assert "[\\textasciicircum{}6 \\textasciicircum{}6]" not in text
    assert "Over\\footnote[7]{" not in text
    assert "长 春术 [1972]" not in text


def test_chapter_3_note_32_tail_cleaned():
    text = Path("tex/chapters/ch03.tex").read_text(encoding="utf-8")

    assert "n. 87.} %32" in text
    assert "63 U U CEE U 0" not in text


def test_chapter_5_authenticity_note_block_restored():
    text = Path("tex/chapters/ch05.tex").read_text(encoding="utf-8")

    assert "See too n. 34.} %47" in text
    assert "buy these bones he may encounter a hundred forgeries for every genuine piece" in text
    assert "\\footnote[34]{For an introduction to authenticating criteria, see White (1945), pp. 75, 77; \\pinyinterm{yan-yiping} (1967), 1, pp. 2-6." in text
    assert "As Yetts (1954), p. xix, concludes, ``Their words in jest were only too true." in text
    assert "recognized.\\footnote[36]{" in text
    assert "inscription.\\footnote[37]{" in text
    assert "forgery;\\footnote[38]{" in text
    assert "confidence.\\footnote[39]{" in text
    assert "mind.\\footnote[40]{" in text
    assert "same time,\\footnote[41]{" in text
    assert "our guard.\\footnote[42]{" in text
    assert "identified.\\footnote[43]{" in text
    assert "1973 finds,\\footnote[44]{" in text
    assert "satisfy).\\footnote[45]{" in text
    assert "36. For the extensive career of one master" not in text
    assert "145 L C U" not in text
    assert "40. The Musée Guimet, for example, possesses" not in text


def test_chapter_5_transcription_tail_cleanup():
    text = Path("tex/chapters/ch05.tex").read_text(encoding="utf-8")

    assert "\\footnote[63]{E.g., \\pinyinterm{jiabian} kǎoshì, ``凡例,'' p. 9.}" in text
    assert "to the left or downward and to the right, respectively.\n% source: scan 167, printed 149" in text
    assert "conclusions@@" not in text
    assert "149 0 U" not in text


def test_chapter_2_mid_note_block_restored():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "Tribute payments.\\footnote[25]{" in text
    assert "not yet been made.\\footnote[26]{" in text
    assert "other topic.\\footnote[27]{" in text
    assert "sacrifice itself.\\footnote[28]{" in text
    assert "ten-day week.\\footnote[29]{" in text
    assert "days in advance,\\footnote[30]{" in text
    assert "prognostications.\\footnote[31]{" in text
    assert "sec. 2.5)).\\footnote[32]{" in text
    assert "\\textit{xushu})\\footnote[33]{" in text
    assert "1 to 10.\\footnote[34]{" in text
    assert "itself was carved.\\footnote[35]{" in text
    assert "study of sets (\\ref{sec:chapters-ch02:2.5} (sec. 2.5)).\\footnote[37]{" in text
    assert "fan-chao\\footnote[38]{" in text
    assert "}), the crack numbers were commonly erased" in text
    assert "25. But cf." not in text
    assert "29. Period I divinations enquiring whether it" not in text
    assert "35. I see no way to tell whether" not in text
    assert "(sec.\\footnote[37]{" not in text
    assert "}), 38 the crack numbers" not in text


def test_chapter_2_late_note_block_restored():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "period I.\\footnote[135]{" in text
    assert "fan-chao situation.\\footnote[136]{" in text
    assert "inscription was engraved.\\footnote[137]{" in text
    assert "more visible.\\footnote[138]{" in text
    assert "fig. 7).\\footnote[139]{" in text
    assert "were carved\\footnote[140]{" in text
    assert "135. E.g., \\pinyinterm{pinbian} 57;" not in text
    assert "140. The unique example of \\pinyinterm{pinbian} 390.5," not in text
    assert "\nline had been carved prior to the inscription\n" not in text


def test_chapter_2_note_101_tail_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "p. 13.} %101" in text
    assert "47 C D J 1 U" not in text


def test_chapter_2_note_88_tail_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "see sec. 3.7.2).} %88" in text
    assert "45 Q D E L U [" not in text


def test_chapter_2_note_111_restored():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "intentional abbreviation; cf. \\ref{sec:chapters-ch03:3.7.1.1} (see sec. 3.7.1.1));" in text
    assert "\\pinyinterm{yan-yiping} [1959], pp. 230, 233;" in text
    assert "\\pinyinterm{qiu-short} (1972), p. 43.} %111" in text
    assert "see  cf. sec. 3.7.1.1" not in text
    assert "49 1 U U" not in text


def test_chapter_2_note_115_tail_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "\\ref{ch:1} (see ch. 1), n. 46." in text
    assert "right in order for the writing to be read.} %115" in text
    assert "(see ch. 1). n. 46." not in text
    assert "394.} %115" not in text


def test_chapter_2_notes_116_to_124_restored():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "(1951a), p. 304.} %116" in text
    assert "For the symbols \\_ or \\_, \\ref{sec:chapters-ch05:5.6} (see sec. 5.6).} %121" in text
    assert "has made an exhaustive study of inscription patterns on various parts of the shell, both front and back." in text
    assert "center.\\footnote[123]{It was frequently the case that columns on a left scapula ran to the right and vice versa;" in text
    assert "vice versa.\\footnote[124]{\\pinyinterm{zhou-hongxiang} (1969), pp. 37-52," in text
    assert "The remains of the wished-for, negative charge, ``Tzu [\\pinyinterm{shang}] will not have sickness,''" in text
    assert "123. It was frequently the case that columns" not in text
    assert "124. \\pinyinterm{zhou-hongxiang} (1969), pp. 37-52," not in text
    assert "4130@@" not in text
    assert "库 fang 1595" not in text


def test_chapter_2_note_130_hybrid_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "Li Daliang [1972], p. 29" in text
    assert "李 Taliang [1972], p. 29" not in text


def test_chapter_2_note_99_local_cleanup():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "\\listitem{1} practice inscriptions carved on unprepared or unburned bone (e.g., KK [1975.1], p. 45, citing H99:3);" in text
    assert "Taida 2, 7; see \\pinyinterm{liu-yuanlin} [1974], p. 121" in text
    assert "see \\pinyinterm{xu-zhongshu} [1931], p. 528, for a drawing" in text
    assert "\\pinyinterm{jiatu} 125/126); \\listitem{5}" in text
    assert "\\listitem{6} kan-chih tables (n. 100).} %99" in text
    assert "(I) practice inscriptions" not in text
    assert "台-ta 2, 7" not in text
    assert "徐 Chungshu [1931], p. 528" not in text


def test_chapter_2_note_84_spill_removed():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "\\footnote[84]{\\listitem{1} \\pinyinterm{jinghua} 1 (S307.3);" in text
    assert "% source: scan 063, printed 46\ntell.89 And it is not certain whether all the units of an inscription" in text
    assert "\n84. \\listitem{1} \\pinyinterm{jinghua} 1 (\\$307.3);" not in text
    assert "that 焦@@" not in text
    assert "translated in\\ref{sec:chapters-ch02:2.8} (see sec. 2.8)); \\listitem{5} 乙-chu 620 (S91.1);" not in text


def test_chapter_2_note_143_hybrid_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "with Zhixu 64 and \\pinyinterm{cuibian} 79" in text
    assert "with 知-hsü 64 and \\pinyinterm{cuibian} 79" not in text
    assert "with Chih-hsü 64 and \\pinyinterm{cuibian} 79" not in text


def test_chapter_2_note_145_hybrids_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "the inscription of diviner Wei on \\pinyinterm{jiabian} 3339 was colored red" in text
    assert "6274; \\pinyinterm{jinghua} 2 (fig. 14)." in text
    assert "diviner 韦 on \\pinyinterm{jiabian} 3339" not in text
    assert "6274; 京-hua 2 (fig. 14)." not in text


def test_chapter_2_note_142_hybrid_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "see the \\pinyintext{kaoshi} to Yizhu 27 and 73" in text
    assert "see the \\pinyintext{kaoshi} to 乙-chu 27 and 73" not in text
    assert "see the \\pinyintext{kaoshi} to Yi-chu 27 and 73" not in text


def test_chapter_2_note_54_hybrid_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "For similar examples, see \\pinyinterm{xucun} 1.2580; 1.2684; Yizhu 246.} %54" in text
    assert "For similar examples, see \\pinyinterm{xucun} 1.2580; 1.2684; 乙-chu 246.} %54" not in text
    assert "For similar examples, see \\pinyinterm{xucun} 1.2580; 1.2684; Yi-chu 246.} %54" not in text


def test_chapter_2_note_100_hybrid_cleaned():
    text = Path("tex/chapters/ch02.tex").read_text(encoding="utf-8")

    assert "\\footnote[100]{Guo detects in one fragment a row of graphs written by the teacher;" in text
    assert "\\footnote[100]{郭 detects in one fragment a row of graphs written by the teacher;" not in text
    assert "\\footnote[100]{Kuo detects in one fragment a row of graphs written by the teacher;" not in text
