"""Regression checks for the first bibliography citation-conversion tranche."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
APP04 = REPO_ROOT / "tex" / "appendices" / "app04.tex"
APP02 = REPO_ROOT / "tex" / "appendices" / "app02.tex"
CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH02 = REPO_ROOT / "tex" / "chapters" / "ch02.tex"
CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
CH05 = REPO_ROOT / "tex" / "chapters" / "ch05.tex"
BIB = REPO_ROOT / "tex" / "bibliography" / "keightley.bib"
MANUAL_BIB = REPO_ROOT / "tex" / "bibliography" / "keightley_manual.bib"
CITATION_SCRIPT = REPO_ROOT / "scripts" / "09_intext_citations.py"


def test_first_tranche_citations_are_wired():
    app02 = APP02.read_text(encoding="utf-8")
    app04 = APP04.read_text(encoding="utf-8")
    ch01 = CH01.read_text(encoding="utf-8")
    ch02 = CH02.read_text(encoding="utf-8")
    ch03 = CH03.read_text(encoding="utf-8")
    ch05 = CH05.read_text(encoding="utf-8")

    assert "Lin Sheng (1963) records" not in ch01
    assert r"\textcite{Lin1963Chi} records" in ch01

    assert "Keightley (1973), p. 537, nn. 36, 37" not in ch02
    assert r"\textcite[p. 537, nn.~36, 37]{Keightley1973Religion}" in ch02

    assert "Lin Sheng (1963), pp. 162-163" not in ch05
    assert r"\textcite[pp.~162-163]{Lin1963Chi}" in ch05

    assert "Keightley (1975), pp. 132-1740; (1975b);" not in app04
    assert r"\textcite[pp.~132--174]{Keightley1975The};" in app04
    assert r"\textcite{Keightley1975bDate};" in app04

    assert "Keightley (1975), pp. 142144" not in ch02
    assert r"\textcite[pp.~142--144]{Keightley1975The}" in ch02
    assert r"\textcite[pp.~11--17]{Keightley1975Legitimation}" in ch02
    assert r"\textcite[pp.~13--15]{Keightley1975Legitimation}" in ch02

    assert r"\textcite[p. 98, n. 13]{Serruys1974The}" in ch01
    assert r"\textcite[p. 515, n.~1]{Young1936Fossil}" in ch01
    assert r"\textcite[p. 515]{Young1936Fossil}" in ch01
    assert r"\textcite[p. 86, n. 3]{Serruys1974The}" in ch02
    assert r"\textcite{Serruys1974The}" in ch03
    assert r"\textcite[esp. pp. 19-21]{Serruys1974The}" in ch03
    assert r"\textcite{Mickel1973Book}" in app02
    assert r"\textcite[pp.~79--94, 100--110, 240]{Mickel1976Semantic}" in ch02
    assert r"\textcite[pp.~174--178]{Mickel1976Semantic}" in ch02
    assert r"\textcite[pp.~72--75]{Mickel1976Semantic}" in ch03
    assert r"\textcite[p.~71]{Mickel1976Semantic}" in ch03
    assert r"\textcite[pp.~149--158]{Mickel1976Semantic}" in ch03
    assert r"\textcite{Mickel1976Semantic}" in ch05
    assert r"\textcite[pp.~28, 39, 56, 59--60, 119, 121]{Linduff1972Tradition}" in ch05


def test_citation_inventory_skips_backmatter():
    script = CITATION_SCRIPT.read_text(encoding="utf-8")

    assert 'if "backmatter" in tex.parts:' in script
    assert 'for bib_file in sorted(BIB_DIR.glob("*.bib")):' in script
    assert 'shortauthor' in script


def test_keightley_1975b_entry_exists():
    bib = BIB.read_text(encoding="utf-8")

    assert "@book{Keightley1975bDate," in bib
    assert "The Date of the Shang Historical Period: A Progress Report" in bib


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
    assert "@article{Bishop1932Scapulimancy," in bib
    assert "@book{Bogoras1907Chukchee," in bib
    assert "@book{Britton1935Yin," in bib
    assert "@book{CaquotLeibovici1968Divination," in bib
    assert "shortauthor = {Caquot and Leibovici}" in bib
    assert "@book{Carr1952Handbook," in bib
    assert "@book{Chang1968Archaeology," in bib
    assert "shortauthor = {Kwang-chih}" in bib
    assert "@book{Chienshou1917Yinxu," in bib
    assert "shortauthor = {Chien-shou}" in bib
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
    assert "shortauthor = {Fu-yin}" in bib
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
    assert "shortauthor  = {Hung}" in bib
    assert "@article{Huang1964Measure," in bib
    assert "shortauthor  = {Caijun}" in bib
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
    assert "shortauthor  = {Liu-lu}" in bib
    assert "@article{Lukes1967Problems," in bib
    assert "@book{MaenchenHelfen1973World," in bib
    assert "@article{Matsumaru1963Inkyo," in bib
    assert "@incollection{Matsumaru1970Inshu," in bib
    assert "@incollection{Matsumaru1973Oracle," in bib
    assert "@book{Matsumoto1966Shunju," in bib
    assert "@article{McDowell1964Partition," in bib
    assert "@article{Mickel1976bReview," in bib
    assert "@article{Mickel1977aIndex," in bib
    assert "@book{Matsumaru1959Kokotsu," in bib
    assert "@phdthesis{Mickel1976Semantic," in bib
    assert "@unpublished{Monroe1974Ritual," in bib
    assert "@incollection{Montell1945Ethnographer," in bib
    assert "@book{Noda1945Kanjo," in bib
    assert "shortauthor = {Noda and Yabuuchi}" in bib
    assert "@book{Needham1971Science," in bib
    assert "@book{ParkeWormell1956Delphic," in bib
    assert "shortauthor = {Parke and Wormell}" in bib
    assert "@book{Philippi1968Kojiki," in bib
    assert "@book{Pritchard1967Living," in bib
    assert "@article{Roux1968Divination," in bib
    assert "shortauthor  = {Roux and Boratav}" in bib
    assert "@article{Saussure1924Chronologie," in bib
    assert "shortauthor  = {Saussure}" in bib
    assert "@article{Shima1960TiYi," in bib
    assert "@article{Shima1966Bokuji," in bib
    assert "@book{Shirakawa1971Kimbun," in bib
    assert "@article{Sivin1969Cosmos," in bib
    assert "@book{Smith1931Fauna," in bib
    assert "@article{Soper1966Early," in bib
    assert "@book{Speck1935Naskapi," in bib
    assert "@article{Satow1879Ancient," in bib
    assert "@book{Shirakawa1972Kokotsubun," in bib
    assert "@phdthesis{Takashima1973Negatives," in bib
    assert "@unpublished{Takashima1976Subordinate," in bib
    assert "@book{Tung1945Yin," in bib
    assert "@article{Tung1953Chia," in bib
    assert "@article{Nivison1977Three," in bib
    assert "@incollection{Vandermeersch1974Tortue," in bib
    assert "@phdthesis{Vandermeersch1975Wangdao," in bib
    assert "@incollection{Vernant1974Parole," in bib
    assert "@article{MacGregor1941Domestic," in bib
    assert "@article{Maekawa1974Koken," in bib
    assert "@article{Su1969Shuo," in bib
    assert "shortauthor  = {Su}" in bib
    assert "@book{Wheatley1971Pivot," in bib
    assert "@book{Woodhead1967Study," in bib
    assert "@inproceedings{Wu1955Broken," in bib
    assert "shortauthor = {Shih-ch'ang}" in bib
    assert "@article{Young1936Fossil," in bib
    assert "@article{Yu1977Computer," in bib
    assert "shortauthor  = {Hao-liang}" in bib
    assert "@article{Yagimoto1966Kiboku," in bib
    assert "@article{Yetts1954Shang," in bib
    assert "@book{Zhang1970Der," in bib
    assert "shortauthor = {Zongdong}" in bib
