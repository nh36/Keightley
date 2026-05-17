"""Regression checks for the first bibliography citation-conversion tranche."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
APP04 = REPO_ROOT / "tex" / "appendices" / "app04.tex"
APP01 = REPO_ROOT / "tex" / "appendices" / "app01.tex"
APP02 = REPO_ROOT / "tex" / "appendices" / "app02.tex"
CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH02 = REPO_ROOT / "tex" / "chapters" / "ch02.tex"
CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
CH04 = REPO_ROOT / "tex" / "chapters" / "ch04.tex"
CH05 = REPO_ROOT / "tex" / "chapters" / "ch05.tex"
PREFACE = REPO_ROOT / "tex" / "frontmatter" / "preface.tex"
FIGURES = REPO_ROOT / "tex" / "plates" / "figures.tex"
BIB = REPO_ROOT / "tex" / "bibliography" / "keightley.bib"
MANUAL_BIB = REPO_ROOT / "tex" / "bibliography" / "keightley_manual.bib"
CITATION_SCRIPT = REPO_ROOT / "scripts" / "09_intext_citations.py"


def test_first_tranche_citations_are_wired():
    app01 = APP01.read_text(encoding="utf-8")
    app02 = APP02.read_text(encoding="utf-8")
    app04 = APP04.read_text(encoding="utf-8")
    ch01 = CH01.read_text(encoding="utf-8")
    ch02 = CH02.read_text(encoding="utf-8")
    ch03 = CH03.read_text(encoding="utf-8")
    ch04 = CH04.read_text(encoding="utf-8")
    ch05 = CH05.read_text(encoding="utf-8")
    preface = PREFACE.read_text(encoding="utf-8")
    figures = FIGURES.read_text(encoding="utf-8")

    assert "Lin Sheng (1963) records" not in ch01
    assert r"\textcite{Lin1963Chi} records" in ch01

    assert "Keightley (1973), p. 537, nn. 36, 37" not in ch02
    assert r"\textcite[p. 537, nn.~36, 37]{Keightley1973Religion}" in ch02

    assert "Lin Sheng (1963), pp. 162-163" not in ch05
    assert r"\textcite[pp.~162-163]{Lin1963Chi}" in ch05

    assert "Keightley (1975), pp. 132-1740; (1975b);" not in app04
    assert r"\textcite[pp.~132--174]{Keightley1975The};" in app04
    assert r"\textcite{Keightley1975bDate};" in app04
    assert "Keightley (1975) and (1975b)." not in app04
    assert (
        r"Keightley (\citeyear{Keightley1975The}) and "
        r"(\citeyear{Keightley1975bDate})."
    ) in app04
    assert "Barnard (1975), pp. 16-17" not in app04
    assert r"Barnard (\citeyear{Barnard1975First}), pp. 16-17" in app04
    assert "cf. Barnard (1972), pp. xxxix-xlii" not in app04
    assert r"cf. Barnard (\citeyear{Barnard1972Early}), pp. xxxix-xlii" in app04
    assert "Tung (1945), pt. 1, ch. 2, pp. 6b-8a; ch. 4, pp. 11b-28b; (1951b), p. 199; Shima (1966); Shirakawa (1971), pp. 280–281." not in app04
    assert r"Tung (\citeyear{Tung1945Yin}), pt. 1, ch. 2, pp. 6b-8a; ch. 4, pp. 11b-28b; (\citeyear{Tung1951bWuWang}), p. 199; Shima (\citeyear{Shima1966Bokuji}); Shirakawa (\citeyear{Shirakawa1971Kimbun}), pp. 280–281." in app04
    assert "Chang Kwang-chih has remarked ([1965], pp. 505-506)" not in app04
    assert r"Chang Kwang-chih has remarked ([\citeyear{Chang1965Relative}], pp. 505-506)" in app04
    assert "Chavannes (1895), pp. cxc-cxcvi; Gardner (1961), p. 26, n. 8." not in app04
    assert r"Chavannes (\citeyear{Chavannes1895Memoires}), pp. cxc-cxcvi; Gardner (\citeyear{Gardner1961Chinese}), p. 26, n. 8." in app04
    assert "de Saussure (1924), pp. 322-339; Noda and Yabuuchi (1945), pp. 137-179 and passim;" not in app04
    assert r"de Saussure (\citeyear{Saussure1924Chronologie}), pp. 322-339; Noda and Yabuuchi (\citeyear{Noda1945Kanjo}), pp. 137-179 and passim;" in app04
    assert "This is the translation given by Sivin (1969), p. 12." not in app04
    assert r"This is the translation given by Sivin (\citeyear{Sivin1969Cosmos}), p. 12." in app04
    assert "For comment on this passage, see de Saussure (1924), pp. 330-331; Noda and Yabuuchi (1945), p. 289." not in app04
    assert r"de Saussure (\citeyear{Saussure1924Chronologie}), pp. 330-331; Noda and Yabuuchi (\citeyear{Noda1945Kanjo}), p. 289." in app04
    assert "Eberhard, Müller, and Henseling (1970), pp. 949-979; Noda and Yabuuchi (1945), pp. 161-164." not in app04
    assert r"Eberhard, Müller, and Henseling (\citeyear{Eberhard1970Astronomie}), pp. 949-979; Noda and Yabuuchi (\citeyear{Noda1945Kanjo}), pp. 161-164." in app04
    assert "The text has been glossed by de Saussure (1924), pp. 330-331; Noda and Yabuuchi (1945), p. 289." not in app04
    assert r"The text has been glossed by de Saussure (\citeyear{Saussure1924Chronologie}), pp. 330-331; Noda and Yabuuchi (\citeyear{Noda1945Kanjo}), p. 289." in app04
    assert "Fan (1962), p. 35." not in app04
    assert r"Fan (\citeyear{Fan1962Kuben}), p. 35." in app04
    assert "Barnard (1960b)." not in app04
    assert r"Barnard (\citeyear{Barnard1960bReview})." in app04
    assert "see Keightley [1975a]" not in app04
    assert r"see Keightley [\citeyear{Keightley1975aThe}]" in app04
    assert "Barnard (1975), pp. 30-31." not in app04
    assert r"Barnard (\citeyear{Barnard1975First}), pp. 30-31." in app04
    assert "Michels (1973), pp. 158-159." not in app04
    assert r"Michels (\citeyear{Michels1973Dating}), pp. 158-159." in app04
    assert 'Barnard (1975), p. 31, refers to it as ``a comparatively late burial,'' but Kane (1975), p. 109,' not in app04
    assert r"Barnard (\citeyear{Barnard1975First}), p. 31," in app04
    assert r"Kane (\citeyear{Kane1975Reexamination}), p. 109," in app04
    assert "Ch'iu (1972) argues, unconvincingly in my view," not in app04
    assert r"Ch'iu (\citeyear{Chiu1972DuAnyang}) argues, unconvincingly in my view," in app04
    assert "Clark (1975), pp. 265-266." not in app04
    assert r"Clark (\citeyear{Clark1975Calibration}), pp. 265-266." in app04
    assert "Goodyear (1971), p. 181:" not in app04
    assert r"Goodyear (\citeyear{Goodyear1971Archaeological}), p. 181:" in app04
    assert "Clark (1975) uses the 5568 half-life. Barnard (1975) usually records both the 5568 and the 5730 half-life figures." not in app04
    assert r"Clark (\citeyear{Clark1975Calibration}) uses the 5568 half-life. Barnard (\citeyear{Barnard1975First}) usually records both the 5568 and the 5730 half-life figures." in app04
    assert "Cf. Barnard (1975), p. 38." not in app04
    assert r"Cf. Barnard (\citeyear{Barnard1975First}), p. 38." in app04
    assert "Kigoshi and Hasegawa (1966)" not in app04
    assert r"Kigoshi and Hasegawa (\citeyear{Kigoshi1966Secular})" in app04
    assert "Clark (1975), p. 260," not in app04
    assert r"Clark (\citeyear{Clark1975Calibration}), p. 260," in app04
    assert "Cf. Barnard (1975), pp. vi, vii, 21-22; Clark (1975), pp. 252, 258-259." not in app04
    assert r"Cf. Barnard (\citeyear{Barnard1975First}), pp. vi, vii, 21-22; Clark (\citeyear{Clark1975Calibration}), pp. 252, 258-259." in app04
    assert "Newton [1977]" not in app04
    assert r"Newton [\citeyear{Newton1977Canon}]" in app04
    assert "Dubs (1947)" not in app04
    assert r"Dubs (\citeyear{Dubs1947Canon})" in app04
    assert "Chang P'ei-yü (1975)." not in app04
    assert r"Chang P'ei-yü (\citeyear{Chang1975Ancient})." not in app04
    assert "Zhang Peiyu (1975)." not in app04
    assert r"Zhang Peiyu (\citeyear{Chang1975Jiaguwen})." in app04
    assert "Shima [1958], p. 270; Serruys [1974], p. 104" not in app04
    assert r"Shima [\citeyear{Shima1958Inkyo}], p. 270; Serruys [\citeyear{Serruys1974The}], p. 104" in app04

    assert "Keightley (1975), pp. 142144" not in ch02
    assert r"\textcite[pp.~142--144]{Keightley1975The}" in ch02
    assert r"\textcite[pp.~11--17]{Keightley1975Legitimation}" in ch02
    assert r"\textcite[pp.~13--15]{Keightley1975Legitimation}" in ch02

    assert "Ping (1930) described an extinct terrestrial tortoise" not in app01
    assert r"Ping (\citeyear{Ping1930Notes}) described an extinct terrestrial tortoise" in app01
    assert "Lindholm (1931) concluded that the" not in app01
    assert r"Lindholm (\citeyear{Lindholm1931Uber}) concluded that the" in app01
    assert "Pope (1935), in his monograph on the" not in app01
    assert r"Pope (\citeyear{Pope1935Reptiles}), in his monograph on the" in app01
    assert "Carr, 1952" not in app01
    assert r"Carr (\citeyear{Carr1952Handbook})" in app01
    assert "Auffenberg (1962) commented" not in app01
    assert r"Auffenberg (\citeyear{Auffenberg1962Status}) commented" in app01
    assert "McDowell (1964), in a taxonomic revision" not in app01
    assert r"McDowell (\citeyear{McDowell1964Partition}), in a taxonomic revision" in app01
    assert "Nakamura (1934) and more recently by Mao (1971)" not in app01
    assert r"Nakamura (\citeyear{Nakamura1934Clemmys}) and more recently by Mao (\citeyear{Mao1971Turtles})" in app01
    assert "Bien (1937) referred to the shell as Ocadia sinensis" not in app01
    assert r"Bien (\citeyear{Bien1937Turtle}) referred" in app01
    assert "to the shell as Ocadia sinensis" in app01
    assert "Ping's figure reproduced in Pope [1935]" not in app01
    assert r"Ping's figure reproduced in Pope [\citeyear{Pope1935Reptiles}]" in app01
    assert "H. W. Wu (1943) identified the largest plastron" not in app01
    assert r"H. W. Wu (\citeyear{Wu1943Notes}) identified the largest plastron" in app01
    assert "Ting Su (1969) has made the only attempt" not in app01
    assert r"Ting Su (\citeyear{Su1969Shuo}) has made the only attempt" in app01
    assert "adopted by Ting Su (1969)" not in app01
    assert r"adopted by Ting Su (\citeyear{Su1969Shuo})" in app01
    assert "As noted by Wu (1943), the" not in app01
    assert r"As noted by Wu (\citeyear{Wu1943Notes}), the" in app01
    assert "Notes on the habits of these turtles can be found in Smith (1931), Pritchard (1967), and Mao" not in app01
    assert r"Notes on the habits of these turtles can be found in Smith (\citeyear{Smith1931Fauna}), Pritchard (\citeyear{Pritchard1967Living}), and Mao" in app01
    assert r"(\citeyear{Mao1971Turtles}). Individuals of Ocadia" in app01
    assert "Boulenger [1889]; Bourret [1941]; Smith [1931]; and Wermuth and Mertens [1961]" not in app01
    assert r"Boulenger [\citeyear{Boulenger1889Catalogue}]; Bourret [\citeyear{Bourret1941Tortues}]; Smith [\citeyear{Smith1931Fauna}]; and Wermuth and Mertens [\citeyear{Wermuth1961Schildkroten}]" in app01
    assert "Schmidt [1927]; Pope [1935]; McDowell [1964]" not in app01
    assert r"Schmidt [\citeyear{Schmidt1927Reptiles}]; Pope [\citeyear{Pope1935Reptiles}]; McDowell [\citeyear{McDowell1964Partition}]" in app01
    assert "Stejneger [1907]; Pope [1935]; McDowell [1964]; Mao [1971]" not in app01
    assert r"Stejneger [1907]; Pope [\citeyear{Pope1935Reptiles}]; McDowell [\citeyear{McDowell1964Partition}]; Mao [\citeyear{Mao1971Turtles}]" in app01
    assert "Stejneger [1907]; Pope [1935]; McDowell [1964]; and Mao [1971]" not in app01
    assert r"Stejneger [1907]; Pope [\citeyear{Pope1935Reptiles}]; McDowell [\citeyear{McDowell1964Partition}]; and Mao [\citeyear{Mao1971Turtles}]" in app01
    assert "Smith [1931]; Pope [1935]" not in app01
    assert r"Smith [\citeyear{Smith1931Fauna}]; Pope [\citeyear{Pope1935Reptiles}]" in app01

    assert r"\textcite[p. 98, n. 13]{Serruys1974The}" in ch01
    assert r"\textcite[p. 515, n.~1]{Young1936Fossil}" in ch01
    assert r"\textcite[p. 515]{Young1936Fossil}" in ch01
    assert r"\textcite[p. 86, n. 3]{Serruys1974The}" in ch02
    assert r"\textcite{Serruys1974The}" in ch03
    assert r"\textcite[esp. pp. 19-21]{Serruys1974The}" in ch03
    assert r"\textcite{Mickel1973Review}" in app02
    assert r"\textcite[pp.~79--94, 100--110, 240]{Mickel1976Semantic}" in ch02
    assert r"\textcite[pp.~174--178]{Mickel1976Semantic}" in ch02
    assert r"\textcite[pp.~72--75]{Mickel1976Semantic}" in ch03
    assert r"\textcite[p.~71]{Mickel1976Semantic}" in ch03
    assert r"\textcite[pp.~149--158]{Mickel1976Semantic}" in ch03
    assert r"\textcite{Mickel1976Semantic}" in ch05
    assert r"\textcite[pp.~28, 39, 56, 59--60, 119, 121]{Linduff1972Tradition}" in ch05
    assert "Park and Wormell (1956), p. 33" not in ch05
    assert r"Park and Wormell (\citeyear{ParkeWormell1956Delphic}), p. 33." in ch05
    assert "Zhou Lin (1970); (1972);" not in ch05
    assert r"Zhou Lin (\citeyear{Chao1970Marriage}); (\citeyear{Chao1972ShangGovernment});" in ch05
    assert "David Nivison (1977)" not in ch03
    assert r"David Nivison (\citeyear{Nivison1977aPronominal})" in ch03
    assert "Nivison (1977)." not in ch05
    assert r"Nivison (\citeyear{Nivison1977Interpretation})." in ch05
    assert "Wu Tse (1953)" not in ch03
    assert r"Wu Tse (\citeyear{Wu1953Kutai})" in ch03
    assert "Ting Shan (1956), p. 125" not in ch01
    assert r"Ting Shan (\citeyear{TingShan1956Chia}), p. 125" in ch01
    assert "Chan Pingleung (1972), pp. 39-41" not in ch01
    assert r"Chan Ping-leung (\citeyear{Chan1972Chutzu}), pp. 39-41" in ch01
    assert "并 知 (1931)" not in ch01
    assert "Ping Chih (1931)" not in ch01
    assert "see Bing Zhi (1931)," not in ch01
    assert r"see Bing Zhi (\citeyear{Ping1931Honan})," in ch01
    assert "Malcolm A. Smith (1931), facing p. 50" not in ch01
    assert r"Malcolm A. Smith (\citeyear{Smith1931Fauna}), facing p. 50" in ch01
    assert "Carr (1952), pp. 37-39" not in ch01
    assert r"Carr (\citeyear{Carr1952Handbook}), pp. 37-39" in ch01
    assert "Romer (1956), p. 32" not in ch01
    assert r"Romer (\citeyear{Romer1956Osteology}), p. 32" in ch01
    assert "Malcolm A. Smith (1931), p. 50" not in ch01
    assert r"Malcolm A. Smith (\citeyear{Smith1931Fauna}), p. 50" in ch01
    assert "史 Changju (1959), p. 321." not in ch05
    assert r"\pinyinterm{shi-zhangru} (\citeyear{Shih1959Hsiao}), p. 321." in ch05
    assert "Wang Ziyu (1933)" not in ch05
    assert r"Wang Ziyu (\citeyear{Wang1933Chia})" in ch05
    assert "陳 春县 (1933)" not in ch04
    assert r"Ch'en Ch'ün-hsien (\citeyear{Chen1933Chenren})" not in ch04
    assert r"Chen Qunxian (\citeyear{Chen1933Chenren}) or Hopkins (1934), pp. 80-81" in ch04
    assert "并 (1930)" not in ch05
    assert "Ping (1930) described an extinct terrestrial tortoise" not in ch05
    assert r"Ping (\citeyear{Ping1930Notes}) described an extinct terrestrial tortoise" in ch05
    assert "Lindholm (1931) concluded" not in ch05
    assert r"Lindholm (\citeyear{Lindholm1931Uber}) concluded" in ch05
    assert "Pope (1935), in his monograph" not in ch05
    assert r"Pope (\citeyear{Pope1935Reptiles}), in his monograph" in ch05
    assert "turtle examined by Ping was, in fact," in ch05
    assert r"cf. \pinyinterm{zhou-hongxiang} [1976]," in ch05
    assert r"\pinyinterm{zhou-dynasty} [1976]" not in ch05
    assert r"\pinyinterm{jin-xiangheng} (\citeyear{Chin1973Fujen});" in ch05
    assert r"金 相横 (1973);" not in ch05
    assert r"\pinyinterm{rao-short} (1961a), p. 95;" in ch02
    assert r"\pinyinterm{rao-short} [1961], p. 953" in ch02
    assert r"\pinyinterm{rao-short} [1961], p. 957" not in ch01
    assert r"\pinyinterm{rao-short} [\citeyear{Jao1961Yupuchao}], p. 957" in ch01
    assert r"see 焦 (1961), p. 957" not in ch01
    assert r"(\pinyinterm{rao-short}, loc. cit.;" in ch01
    assert r"\pinyinterm{jiao-short}" not in ch01
    assert r"\pinyinterm{jiao-short}" not in ch02
    assert r"\pinyinterm{huang-peirong} [1969], pp. 3a-b" in ch02
    assert r"\pinyinterm{huang-peirong} [1975]" not in ch02
    assert r"\pinyinterm{hu-houxuan} (\citeyear{Hu1945Chiakuhsueh}), p. 5b," in ch03
    assert r"\pinyinterm{hu-houxuan} (\citeyear{Hu1955Yinhsu}), pp. 38-41" in ch03
    assert "Lefeuvre (1971)" not in ch03
    assert r"Lefeuvre (\citeyear{Lefeuvre1971SerieH})" in ch03
    assert "Kuo Mo-jo (1972), p. 5" not in app04
    assert r"Kuo Mo-jo (\citeyear{Kuo1972Anyang}), p. 5" in app04
    assert r"\pinyinterm{chen-mengjia} (\citeyear{Chen1955ShangYin}), pp. 67-72." in app04
    assert r"\pinyinterm{chen-mengjia} (\citeyear{Chen1955ShangYin}), p. 59." in app04
    assert r"\pinyinterm{chen-mengjia} ([\citeyear{Chen1955ShangYin}], pp. 55-56) has shown" in app04
    assert r"\pinyinterm{chen-mengjia} (\citeyear{Chen1956Yin}), p. 251;" in preface
    assert r"\pinyinterm{chen-mengjia} [\citeyear{Chen1956Yin}], p. 252;" in preface
    assert r"\pinyinterm{tang-lan} [\citeyear{TangLan1976Hotsun}], p. 60" in preface
    assert r"\pinyinterm{qu-wanli} (\citeyear{Chu1965aShihchi}), pp. 88-89," in preface
    assert r"\pinyinterm{yan-yiping} (\citeyear{Yen1961Chiaku}), pp. 207-215" in preface
    assert "\\pinyinterm{yan-yiping} (\\citeyear{Yen1961Chiaku}),\n207-217." in preface
    assert r"\pinyinterm{hu-houxuan} (\citeyear{Hu1977Niao})," in preface
    assert r"from \pinyinterm{yan-yiping} (\citeyear{Yen1961Chiaku}), 1." in figures


def test_citation_inventory_skips_backmatter():
    script = CITATION_SCRIPT.read_text(encoding="utf-8")

    assert 'if "backmatter" in tex.parts:' in script
    assert 'for bib_file in sorted(BIB_DIR.glob("*.bib")):' in script
    assert 'shortauthor' in script
    assert 'PINYIN_TERMS_TSV = DATA_DIR / "pinyin_terms.tsv"' in script
    assert '"source_kind"' in script


def test_keightley_1975b_entry_exists():
    bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "@misc{Keightley1975bDate," in bib
    assert "The Date of the Shang Historical Period: A Progress Report" in bib


def test_zero_candidate_citation_entries_exist():
    bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "@article{McDowell1964Partition," in bib
    assert "@article{Nakamura1934Clemmys," in bib
    assert "@article{Chiu1972DuAnyang," in bib
    assert "@book{LiHsiaoting1965Chiaku," in bib
    assert "shortauthor = {CKWT}" in bib
    assert "@article{Mickel1977aIndex," in bib


def test_manual_bibliography_entries_exist():
    bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "@book{Shima1958Inkyo," in bib
    assert "@book{Barnard1975First," in bib
    assert "@article{Barnard1960aReview," in bib
    assert "@article{Barnard1960bReview," in bib
    assert "@article{Barnard1963Reviews," in bib
    assert "@article{Barnard1968Incidence," in bib
    assert "@article{Barnard1959Remarks," in bib
    assert "@book{Barnard1972Early," in bib
    assert "shortauthor  = {Barnard}" in bib
    assert "@book{Barnard1973Chu," in bib
    assert "@incollection{Beattie1967Divination," in bib
    assert "@article{BenedettiPichler1937Microchemical," in bib
    assert "@book{Bogoras1907Chukchee," in bib
    assert "@book{Britton1935Yin," in bib
    assert "@book{CaquotLeibovici1968Divination," in bib
    assert "shortauthor = {Caquot and Leibovici}" in bib
    assert "@book{Carr1952Handbook," in bib
    assert "@book{Chang1968Archaeology," in bib
    assert "shortauthor = {Kwang-chih}" in bib
    assert "@phdthesis{Chao1972ShangGovernment," in bib
    assert "shortauthor = {Zhou Lin}" in bib
    assert "@book{Chienshou1917Yinxu," in bib
    assert "shortauthor = {Jianshou}" in bib
    assert "@book{CKWP1965Chia," in bib
    assert "shortauthor = {CKWP}" in bib
    assert "@book{CKWP1934Anyang," in bib
    assert "@article{Chamberlain1883Kojiki," in bib
    assert "@article{ChardinYoung1936Mammalian," in bib
    assert "shortauthor  = {Chardin and Young}" in bib
    assert "@book{Chavannes1895Memoires," in bib
    assert "@article{Chavannes1911Divination," in bib
    assert "@article{Clark1975Calibration," in bib
    assert "@article{Clavier1968Resurgences," in bib
    assert "@book{Chen1956Yin," in bib
    assert "shortauthor  = {Mengjia}" in bib
    assert "@book{Creel1937Birth," in bib
    assert "@book{Creel1970Origins," in bib
    assert "@book{Crump1963Dragon," in bib
    assert "@book{Chu1935Shangshi," in bib
    assert "shortauthor = {Chu}" in bib
    assert "@article{Eberhard1970Astronomie," in bib
    assert "shortauthor  = {Henseling}" in bib
    assert "@book{Fan1962Kuben," in bib
    assert "@book{Fischer1970Historians," in bib
    assert "@book{Fuyin1925Zhengwen," in bib
    assert "shortauthor = {Fuyin}" in bib
    assert "@book{Gadd1948Ideas," in bib
    assert "@book{Gardner1961Chinese," in bib
    assert "@article{Gelb1967Approaches," in bib
    assert "@article{Gibson1934Picture," in bib
    assert "@article{Gibson1938Domestic," in bib
    assert "@book{Goodyear1971Archaeological," in bib
    assert "@book{Kaizuka1946Chiigoku," in bib
    assert "@article{Kaizuka1947Kiboku," in bib
    assert "@book{Kaizuka1967Kodai," in bib
    assert "@article{Eisenberger1938Das," in bib
    assert "@book{EvansPritchard1937Witchcraft," in bib
    assert "@article{Fujino1960Kiboku," in bib
    assert "@article{Hultkrantz1968La," in bib
    assert "@book{Ho1975Cradle," in bib
    assert "@article{Hopkins1934Archaic," in bib
    assert "@book{Ikeda1964Inkyo," in bib
    assert "@article{Hung1976Panlongcheng," in bib
    assert "shortauthor  = {Hong}" in bib
    assert "@article{Huang1964Measure," in bib
    assert "shortauthor  = {Caijun}" in bib
    assert "@book{Chou1976OracleBone," in bib
    assert "@article{Ito1959Anyo," in bib
    assert "shortauthor  = {Ito}" in bib
    assert "@article{Ju1969Metaphysical," in bib
    assert "shortauthor  = {Ju}" in bib
    assert "@article{Kane1973Chronological," in bib
    assert "@article{Kane1975Reexamination," in bib
    assert "@book{Jochelson1905Religion," in bib
    assert "@article{Lei1931Yinzhou," in bib
    assert "shortauthor  = {Lei}" in bib
    assert "@article{Lefeuvre1975Les," in bib
    assert "@article{Lindholm1931Uber," in bib
    assert "@book{Levine1919Farm," in bib
    assert "@book{Li1972Kuei," in bib
    assert "shortauthor = {Daliang}" in bib
    assert "@article{LiuLu1945Jiaku," in bib
    assert "shortauthor  = {Liulu}" in bib
    assert "@article{Lukes1967Problems," in bib
    assert "@book{MaenchenHelfen1973World," in bib
    assert "@article{Matsumaru1963Inkyo," in bib
    assert "@incollection{Matsumaru1970Inshu," in bib
    assert "@incollection{Matsumaru1973Oracle," in bib
    assert "@book{Matsumoto1966Shunju," in bib
    assert "@article{Mattos1976Reference," in bib
    assert "@book{Matsumaru1959Kokotsu," in bib
    assert "@phdthesis{Mickel1976Semantic," in bib
    assert "@unpublished{Monroe1974Ritual," in bib
    assert "@incollection{Montell1945Ethnographer," in bib
    assert "@book{Noda1945Kanjo," in bib
    assert "shortauthor = {Noda and Yabuuchi}" in bib
    assert "@book{Needham1971Science," in bib
    assert "@article{Nivison1977aPronominal," in bib
    assert "@book{Oppenheim1964Ancient," in bib
    assert "@book{ParkeWormell1956Delphic," in bib
    assert "shortauthor = {Parke and Wormell}" in bib
    assert "@book{Philippi1968Kojiki," in bib
    assert "@article{Ping1930Notes," in bib
    assert "@book{Pope1935Reptiles," in bib
    assert "@book{Pritchard1967Living," in bib
    assert "@article{Roux1968Divination," in bib
    assert "shortauthor  = {Roux and Boratav}" in bib
    assert "@book{Rockhill1900Journey," in bib
    assert "@book{Romer1956Osteology," in bib
    assert "@article{Rorty1972World," in bib
    assert "@article{Saussure1924Chronologie," in bib
    assert "shortauthor  = {Saussure}" in bib
    assert "@article{Lu1961Yinchi," in bib
    assert "shortauthor  = {Shih-hsien}" in bib
    assert "@book{LeviStrauss1969Raw," in bib
    assert "shortauthor = {Strauss}" in bib
    assert "@article{Shen1977Fuyu," in bib
    assert "shortauthor  = {Wenzhuo}" in bib
    assert "@article{Shima1960TiYi," in bib
    assert "@article{Shima1966Bokuji," in bib
    assert "@book{Shirakawa1971Kimbun," in bib
    assert "@article{Sivin1969Cosmos," in bib
    assert "@book{Sisson1953Anatomy," in bib
    assert "@book{Smith1931Fauna," in bib
    assert "@article{Smith1972Parrot," in bib
    assert "@article{Soper1966Early," in bib
    assert "@book{Speck1935Naskapi," in bib
    assert "@article{Satow1879Ancient," in bib
    assert "@book{Shirakawa1972Kokotsubun," in bib
    assert "@article{Hayashi1909Shinkoku," in bib
    assert "shortauthor  = {Taisuke}" in bib
    assert "@article{Ke1939Shuo," in bib
    assert "shortauthor  = {Yiqing}" in bib
    assert "@article{Pulleyblank1968Review," in bib
    assert "@unpublished{Pulleyblank1975Chinese," in bib
    assert "@article{Schafer1972Review," in bib
    assert "@unpublished{Nivison1977Interpretation," in bib
    assert "@unpublished{Lefeuvre1971SerieH," in bib
    assert "@phdthesis{Takashima1973Negatives," in bib
    assert "@unpublished{Takashima1977aExistence," in bib
    assert "@book{Thompson1969ChineseReligion," in bib
    assert "@unpublished{Takashima1976Subordinate," in bib
    assert "@book{Tung1945Yin," in bib
    assert "@article{Tung1929bHsin," in bib
    assert "@article{Tung1949aYin," in bib
    assert "@article{Tung1953Chia," in bib
    assert "@book{TingShan1956Chia," in bib
    assert "@phdthesis{Chan1972Chutzu," in bib
    assert "@article{Kuo1972Anyang," in bib
    assert "@article{Kuo1972aFachan," in bib
    assert "@incollection{Vandermeersch1974Tortue," in bib
    assert "@phdthesis{Vandermeersch1975Wangdao," in bib
    assert "@incollection{Vernant1974Parole," in bib
    assert "@article{MacGregor1941Domestic," in bib
    assert "@article{Maekawa1974Koken," in bib
    assert "@article{Su1969Shuo," in bib
    assert "shortauthor  = {Su}" in bib
    assert "@book{Wheatley1971Pivot," in bib
    assert "@book{Wieger1923Textes," in bib
    assert "@collection{Wilson1970Rationality," in bib
    assert "@article{Winch1964Understanding," in bib
    assert "@book{Wu1953Kutai," in bib
    assert "@book{Woodhead1967Study," in bib
    assert "@article{Wu1943Notes," in bib
    assert "@article{Wu1955Broken," in bib
    assert "@article{Yi1957Mantan," in bib
    assert "shortauthor = {Shih-ch'ang}" in bib
    assert "@article{Young1936Fossil," in bib
    assert "@article{Yu1977Shuo," in bib
    assert "shortauthor  = {Haoliang}" in bib
    assert "@article{Yagimoto1966Kiboku," in bib
    assert "@incollection{Yetts1954Shang," in bib
    assert "@book{Zhang1970Der," in bib
    assert "shortauthor = {Zongdong}" in bib
