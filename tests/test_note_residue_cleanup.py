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


def test_ch04_mid_and_late_note_residue_removed():
    text = CH04.read_text(encoding="utf-8")
    offenders = [
        "14. For period I inscriptions, see \\$527.1; for",
        "17. \\pinyinterm{dong-short} (1933), facing p. 344;",
        "21. The circled numbers indicate the ritual",
        "22. E.g., \\pinyinterm{jiatu} 87; \\pinyinterm{pinbian} 204.21;",
        "175. Pit E16 is a case in point. It contained",
        "176. The slope of the shell fragments in YH127",
        "177. To cite but one example, all but one of",
        "178. The situation in particular pits, as well as",
        "period IIb@@",
        "113 ]]}",
        "13.0.628131 ] U}",
        "will ever be written. More rigorous archaeological techniques will presumably be@@",
        "186. See n. 179",
        "damaged in 徐-chou-all",
        "came from YH127; according to 史",
        "engravers.*7",
        "pp. 4142",
        "Studies. 129 1",
        "useful.53",
        "Page design.''",
        "p. 339. Nor are",
        "A25\\%",
        "[1956]. p. 169",
        "\\pinyinterm{jiabian} 490928 came",
        "PTXFEKH",
        "vichih ti fa-hsien yü fa-chüeh: ting pien :",
        "311 119 後下X1 88 AKESNAE",
        "pp. 208209",
        "periodsrests",
        "101 U 11 C",
        "(1965, p. 96])",
        "Keightley [1973], p. 34",
        "Ta 甲 on chiach'en",
        "\\pinyinterm{jiabian} 3oo3",
        "Tui Ẻ:",
        "3.4.4.2. 98.",
        "to which periods.98 Spill-over",
        "1.4.2 1.4.3 1.4.4",
        "2.4.1\\%",
        "3.4.4;4.2",
        "515.12",
        "1767\\%",
        "2.15.1 RFG:",
        "Hsieh叶",
        "``Howen,''",
        "yüeh A, ``moon'' or ``month,''",
        "yüeh 曰 ``saying,''",
        "yue A, ``moon'' or ``month,''",
        "chin yüeh",
        "chin chi yüeh",
        "jin chi yue",
        "chi yüeh",
        "chi yue",
        "tsai chi yüeh",
        "zai chi yue",
        "yi-yüeh",
        "yi yue A, ``the first month,''",
        "cheng-yüeh",
        "zheng yue iE. A,",
        "1377 (\\$488.4)",
        "at \\$488.2491.4",
        "(all S489.1 \\pinyinterm{renwen} 3091",
        "\\pinyinterm{renwen} 2373 (\\$488.4)",
        "\\pinyinterm{qianbian} 5.25.5 (\\$489.1)",
        "Yipien 1834",
        "[D all S441.3]",
        "S442.4443.2",
        "Ninghu 1.331 [D]",
        "\\$417.2",
        "``Ming” 395 [D]",
        "Xplace",
        "\\pinyinterm{xu-jinxiong} 1963)",
        "胡, ibid., p. 481",
        "徐, ibid., p. 9a",
        "胡, ibid., p. 471",
        "originally meant here (at this point in the divination process)",
        "徐. ibid., p. gb",
        "Ogawa 6, shakubun, p. 263, n. 5. It is hard",
        "``verification notations, their presence",
        "pu yung T",
        "period II (n. 101 -\\listitem{4}",
        "wanted to have happen-``there will be no disaster,” “today",
        'it will not rain"-with the crack numbers',
        "甲三元三I 田宮管甲九二。KIX田宮::",
        "nega. tive pi-probably",
        "p. 128-were merely",
        "positivenegative pair",
        "pp. 37-38,46-48,57.",
        "it will perhaps rain''''",
        "spill-over-either",
        "Chang Ping-ch'ü (1952)",
        "Hsü also argues that",
        "Chang Ping-ch'üan (1952)",
        "there is I shang-chi and I hsiao-chi",
        "error.} pu\n% source: scan 138, printed 120\ntsai ming",
        "state or king was concerned or-which is not necessarily the same thing-as far as the",
        "the reduced size of the script-these",
        "Bovid scapulas\nfollowed\nwere the material used most commonly in 龙 and early",
        "period\\footnote[142]{Ibid., p. 123.} 1.142 Further research",
        "preparation technique-reflecting, presumably",
        "artisans involved-to be used as criteria",
        "\\pinyinterm{xu-jinxiong} (1974, pp. 209, 254-255, has proposed",
        "Other Neo-\n% source: scan 141, printed 123\nlithic and early",
        " 龙 scapulimancers mainly used bored",
        "p. 118. 刘 (p. 117, plate 12.1)",
        "led 徐 to",
        "as 徐 claims, the same as another",
        "diviner 成, whom",
        "what constitutes “sameness''?",
        "straight shoulders and tridentshaped ends",
        "cf [1973], pp. 6, 63",
        "\\pinyinposs{xu-jinxiong} con-\nclusions may need revision.",
        "the ``one-one'' pattern. in which",
        "the ``one-three pattern, in which",
        "period\\footnote[169]{\\pinyinterm{xu-jinxiong} (1973a), pp. 19, 101.} 1.169",
        "龙 site at Keshengzhuang E; see 豐西發掘報告, p. 68, plate 35) no cracks appear to have formed. 127 U ] B C",
        "It will be clear from\\ref{sec:chapters-ch04:4.3.2}",
        "physical criteria--hollow shapes, hollow placement, burn marks—are helping to develop",
        "see Itō (1971), p. 88. 科} %174",
        "judgment-barring the presence of criteria such as ancestral titles or diviners' names on\nevery single fragment—can never be more than probable",
        "Qu Wan, in his kǎoshì, dates these to period I.",
        "A26, E9 (\\pinyinterm{dong-short} [1929], p. 180);",
        "6 pieces bore the names of RFG diviners (Chu: \\pinyinterm{jiabian} 3003; Shao):",
        "1.2.01281.2.0139",
        "1.2.0123 and I.2.0145, for example, were found in A26",
    ]

    found = [needle for needle in offenders if needle in text]
    assert not found, "Found lingering ch04 mid/late note residue:\n" + "\n".join(found)

    assert "1206 (D); 1316 (D); \\pinyinterm{nanbei}, ``Ming'' 352 (D)" in text
    assert "lineage, in that order.\\footnote[21]{The circled numbers indicate the ritual order" in text
    assert "decreasing seniority.\\footnote[22]{E.g., \\pinyinterm{jiatu} 87; \\pinyinterm{pinbian} 204.21;" in text
    assert "% source: scan 114, printed 94\nHorizontal. Some divinations group ancestors of the same generation;" in text
    assert "by the careers of engravers.\\footnote[47]{See \\ref{ch:2} (see ch. 2), nn. 104, 108.}" in text
    assert "432 [D] [S52.3]), correspond to period IIb" in text
    assert "\\footnote[95]{E.g., table 7, no. 1.2, appears mostly in period V; no. 1.4 appears mostly in I; no. 2.3 was common in III + IV.} %95" in text
    assert "It is rarely possible to use other objects found in a pit, such as bronzes or pots, to date\n% source: scan 147, printed 130\nthe inscriptions; the inscriptions," in text
    assert "\\footnote[176]{The slope of the shell fragments in YH127 indicated that they had been poured into the pit from the north (\\pinyinterm{shi-zhangru} [1947], pp. 41-42).} %176" in text
    assert "pit provenance are probabilities rather than certainties.\\footnote[178]{The situation in particular pits, as well as the reasons why the \\pinyinterm{shang} buried their oracle bones, will be considered in Studies.} %178" in text
    assert "1937 will ever be written." in text
    assert "13.0.0628-13.0.17714 came from YH127; according to \\pinyinterm{shi-zhangru} (1959), p. 322, shells 13.0.17715-13.0.17756 should also be included." in text
    assert "resolve some of our dating problems.\\footnote[186]{See n. 179" in text
    assert "damaged in Xuzhou---all this" in text
    assert "Any discussion of the distribution of inscriptions by\nperiod (appendix \\ref{app:3} (appendix 3))" in text
    assert "criterion in these cases is frequently too subjective to be useful.\\footnote[53]{For an initial attempt to study the grooves objectively" in text
    assert "4. Page design. This refers to the care with which the graphs were placed on the" in text
    assert "found there (Itō [1959], p. 339). Nor are some of the early reports" in text
    assert "whether \\pinyinterm{jiabian} 110-178, 368-375, and 391 came from A26 or A25?;" in text
    assert "282-296 (cf. \\pinyinterm{chen-mengjia} [1956], p. 169)." in text
    assert "we can only suppose that \\pinyinterm{jiabian} 490-928 came from sector F within the village" in text
    assert "The title of this projected work was \\booktitle{Jiagu wenzi yu Yinxu yizhi};" in text
    assert "\\pinyinterm{shi-zhangru}'s forthcoming \\booktitle{Xiaotun diyi ben: yizhi de faxian yu fajue, yibian: jianzhu yicun}, to be published by the Academia Sinica" in text
    assert "according to \\pinyinterm{hu-houxuan} (1939a), p. 484, only in periods II and IV.} %130" in text
    assert "Kaizuka (1946), pp. 208-209 for a Chinese translation" in text
    assert "fundamental premise---that individual diviners may be associated with limited periods---rests upon the unverifiable assumption" in text
    assert "For another dispute, see n. 44.} %36" in text
    assert "perform [\\pinyinterm{dong-short} (1965), p. 96]) yung ritual to Ta Chia on chia-ch'en" in text
    assert "started auspiciously (cf. Keightley [1973a], p. 34)." in text
    assert "6 pieces bore the names of RFG diviners (Chu: \\pinyinterm{jiabian} 3003; Shao: \\pinyinterm{jiabian} 2941; 3012; 3045+3047;" in text
    assert "3045+3047; Tui É: \\pinyinterm{jiabian} 3045+3047; 3083;" in text
    assert "\\footnote[97]{E.g., table 7, nos. 1.4.-1.4.6; 2.4.-2.5.1; 3.4.4.2.} %97" in text
    assert "to which periods.\\footnote[98]{\\listitem{1} The phrase jin yue" in text
    assert "table 7, nos. 1.4.2; 1.4.3; 1.4.4; 1.4.5; 2.4; 2.4.1; 2.4.3; 3.4.1; 3.4.2; 3.4.3; 3.4.4; 4.2).} %92" in text
    assert "Yi yue: period I: \\pinyinterm{jiabian} 2111; \\pinyinterm{pinbian} 485.14; 515.1-2;" in text
    assert "period III-IV: \\pinyinterm{renwen} 1737; 1767; period V:" in text
    assert "period V: \\pinyinterm{houbian} 1.10.16; 2.15.1; RFG:" in text
    assert "Tuié and Hsieh.} %93" in text
    assert 'CKWP (1965), ``Ho-wen,\'\' pp. 27a-b;' in text
    assert "graphs for hsi , ``night,'' and yue 月, ``moon'' or ``month,'' changed places in different periods" in text
    assert "formulas which included the word yue 曰 ``saying,''" in text
    assert "The phrase jin yue, ``this month,'' or jin ji yue, ``this nth month,''" in text
    assert "Formula a. ji yue, ``the nth month,''" in text
    assert "Formula b, zai ji yue, ``in the nth month,''" in text
    assert "The term yi yue 一月, ``the first month,'' was used in all periods; the term zheng yue 正月" in text
    assert "For examples by period: Yi yue: period I:" in text
    assert "Zheng yue: period IIb:" in text
    assert "\\pinyinterm{renwen} 1373 (S488.3); 1377 (S488.4) (both period II);" in text
    assert "were mainly recorded in period I (see the inscriptions listed at S488.2-491.4)." in text
    assert "\\pinyinterm{renwen} 3085 (all S489.1); \\pinyinterm{renwen} 3091 (S489.2);" in text
    assert "\\pinyinterm{renwen} 2373 (S488.4), 2521 (S489.2), and \\pinyinterm{jiabian} 620 (S489.4)" in text
    assert "Only one period V case, \\pinyinterm{qianbian} 5.25.5 (S489.1) is listed." in text
    assert "RFG: \\pinyinterm{yibian} 1834; \\pinyinterm{qianbian} 8.6.3; \\pinyinterm{xucun} 2.586 [D] [all S441.3]" in text
    assert "appears mainly, if not exclusively, in period V (S442.4-443.2; possible exceptions are \\pinyinterm{renwen} 2141; \\pinyinterm{ninghu} 1.331 [D]; 葉三 43.2)." in text
    assert "recorded only in period V (S417.2; 431.2-432.1; 478.4-479.2)." in text
    assert "period II: \\pinyinterm{nanbei}, ``Ming'' 395 [D]; period V: \\pinyinterm{qianbian} 2.8.7)." in text
    assert 'occurrences of the phrase tsai mou, ``at X-place,\'\' may be found at S498;' in text
    assert "\\pinyinterm{xu-jinxiong} (1963), pp. 8a-11b." in text
    assert "equivalent phrases (e.g., Hu, ibid., p. 481; Ikeda [1964], 2.18.13);" in text
    assert "and campaigning (the inscriptions cited by Xu, ibid., p. 9a)." in text
    assert "originally meant ``here (at this point in the divination process) we offered sacrifice,''" in text
    assert "caught so many animals (Xu, ibid., p. 9b; cf. Ogawa 6, shakubun, p. 263, n. 5)." in text
    assert "which we may refer to as ``verification notations,'' their presence in an inscription provides a clue to its relative date." in text
    assert "The notations tzu puyung 茲不用, pu yung 不用, or tzu wu yung 茲毋用 appear rarely" in text
    assert "date should be considered a verification (see n. 99)\n---if so, such verifications also appeared, rarely, in\nperiod II (n. 101)---\\listitem{4} uncertainty about the" in text
    assert "wanted to have happen---``there will be no disaster,'' ``today\nit will not rain''---with the crack numbers running from 1 to 5" in text
    assert "and sets, in short, became standardized and simplified with the passage of time.\n\n\\subsubsection[Crack Notations]{Crack Notations}" in text
    assert "especially those containing the negative pi---probably a substitution, used principally in period III+IV, for wu ) (Serruys [1974], p. 6; cf. \\pinyinterm{chen-mengjia-spaced} [1956], p. 128)---were merely single, negative charges, and not one of a positive-negative pair." in text
    assert "Keightley (1973a), pp. 37-38, 46-48, 57.} %132" in text
    assert "e.g., ``Divining: ‘(The king) should not hunt on the jen day, (for if he does,) it will perhaps rain’'' (\\pinyinterm{jiabian} 1920 [S293.3])," in text
    assert "this is an instance of spill-over---either of period II diviners and engravers operating in period I" in text
    assert "\\pinyinterm{xu-jinxiong} also argues that \\pinyinterm{jiabian} 27+2 and \\pinyinterm{wenlu} 78" in text
    assert "The basic study is \\pinyinterm{zhang-bingquan} (1952); in English, see Wu Shih-ch'ang (1955)." in text
    assert "on RFG fragments there is 1 shang-chi and 1 hsiao-chi; in period II, there are no crack notations;" in text
    assert "hsiao-chi, “slightly auspicious,”\\footnote[133]{\\pinyinterm{yibian} 7767 (left hyoplastron) contains a unique hsia-chi F, probably an engraver's error.} pu tsai ming\\footnote[135]{" in text
    assert "state or king was concerned---which is not necessarily the same thing---as far as the \\pinyinterm{shang} diviners were concerned" in text
    assert "of calligraphic variants and divination formulas, the reduced size of the script---these\nphenomena were related" in text
    assert "Bovid scapulas\nwere the material used most commonly in \\pinyintext{longshan} and early \\pinyinterm{shang} pyromancy,\nfollowed in frequency by the scapulas of pig and sheep;" in text
    assert "sawn in the socket never appear after period I.\\footnote[142]{Ibid., p. 123.} Further research may permit relatively" in text
    assert "subtle distinctions in preparation technique---reflecting, presumably, the habits of the" in text
    assert "artisans involved---to be used as criteria for assigning different periods to the inscribed" in text
    assert "\\footnote[143]{E.g., \\pinyinterm{xu-jinxiong} (1974), pp. 209, 254-255, has proposed that variations in the shape of the ridge made on the outer edge" in text
    assert "Other Neolithic and early \\pinyinterm{shang} oracle bones, however, did have pyromantic hollows, which varied" in text
    assert "\\pinyintext{longshan} scapulimancers mainly used bored\nhollows that were round and shallow;" in text
    assert "periods II to V.\\footnote[151]{\\pinyinterm{liu-yuanlin} (1974), p. 118. \\pinyinterm{liu-yuanlin} (p. 117, plate 12.1) notes a rare period V bone fragment" in text
    assert "The topic---which has led \\pinyinterm{xu-jinxiong} to\nwrite several articles and two book-length monographs" in text
    assert "I frequently find myself uncertain as to whether one hollow was, as \\pinyinterm{xu-jinxiong} claims, the same as another." in text
    assert "the diviner Cheng, whom \\pinyinterm{xu-jinxiong-tight} (1974), pp. 86-87, suggests may be linked" in text
    assert "And what constitutes ``sameness''? These are not quibbles;" in text
    assert "straight shoulders and trident-shaped ends. He is also paying greater attention" in text
    assert "when needed (e.g., [1974], pp. 86, 170, 207-208; cf. [1973], pp. 6, 63).} and he is beginning to publish the" in text
    assert "This aspect of oracle-bone scholarship is still in its infancy, and some of \\pinyinposs{xu-jinxiong} conclusions may need revision." in text
    assert "the ``one-one'' pattern, in which the two columns of hollows start at the same level" in text
    assert "and the ``one-three'' pattern, in which the inner column of hollows starts two spaces below the outer column" in text
    assert "the bone surface was more frequently chipped in the later periods than it had been in\nperiod I.\\footnote[169]{\\pinyinterm{xu-jinxiong} (1973a), pp. 19, 101.} He has also discerned differences in the burn marks of periods III and IV." in text
    assert "the sheep scapulas from the Lung-shan site at Keshengzhuang E; see 豐西發掘報告, p. 68, plate 35) no cracks appear to have formed.} %168" in text
    assert "It will be clear from \\ref{sec:chapters-ch04:4.3.2} (see sec. 4.3.2) that \\pinyinterm{xu-jinxiong}'s pioneering analyses of related\nphysical criteria---hollow shapes, hollow placement, burn marks---are helping to develop" in text
    assert "regard to one another and other datable objects in the ground.\\footnote[174]{This is only possible in the case of oracle bones that were scientifically excavated; for these, see the archaeological reports listed in n. 173. For an interesting attempt to deduce the location where certain privately excavated inscriptions must have been found, see Itō (1971), p. 88.} %174" in text
    assert "judgment---barring the presence of criteria such as ancestral titles or diviners' names on\nevery single fragment---can never be more than probable" in text
    assert "\\pinyinterm{qu-wanli}, in his kǎoshì, dates these to period I." in text
    assert "More marked chronological confusion was found in other pits; e.g., A26, E9 (\\pinyinterm{dong-short} [1929a], p. 180); 5: H20;" in text
    assert "1.2.0123 (from A26; 20 October); 1.2.0128-1.2.0139 (from F24; 22 October); 1.2.0145 (from A26 again; 23 October);" in text
    assert "1.2.0123 and 1.2.0145, for example, were found in A26, but we cannot conclude" in text


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
