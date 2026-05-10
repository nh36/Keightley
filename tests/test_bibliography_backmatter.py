"""Regression checks for live bibliography backmatter wiring."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BIBLIO_A = REPO_ROOT / "tex" / "backmatter" / "biblio_a.tex"
BIBLIO_B = REPO_ROOT / "tex" / "backmatter" / "biblio_b.tex"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build.sh"
EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "08_extract_bibliography.py"
PREAMBLE = REPO_ROOT / "tex" / "preamble.tex"
MANUAL_BIB = REPO_ROOT / "tex" / "bibliography" / "keightley_manual.bib"
GENERATED_BIB = REPO_ROOT / "tex" / "bibliography" / "keightley.bib"


def test_backmatter_bibliography_files_are_live():
    biblio_a = BIBLIO_A.read_text(encoding="utf-8")
    biblio_b = BIBLIO_B.read_text(encoding="utf-8")

    assert "STUB" not in biblio_a
    assert "STUB" not in biblio_b

    assert r"\input{backmatter/abbreviations_live}" in biblio_a
    assert r"\printbibliography[heading=none]" in biblio_b
    assert r"\nocite{*}" in biblio_b


def test_build_script_runs_biber():
    build_script = BUILD_SCRIPT.read_text(encoding="utf-8")

    assert "command -v biber" in build_script
    assert '--input-directory="$BUILD_OUTPUT"' in build_script
    assert 'run_xelatex_pass 3' in build_script
    assert "render_abbreviations_tex.py" in build_script


def test_manual_bibliography_resource_is_loaded():
    preamble = PREAMBLE.read_text(encoding="utf-8")

    assert r"\addbibresource{bibliography/keightley.bib}" in preamble
    assert r"\addbibresource{bibliography/keightley_manual.bib}" in preamble
    assert r"\AtEveryBibitem{\clearfield{note}}" in preamble
    assert MANUAL_BIB.exists()


def test_generated_bibliography_qa_uses_annotation_not_note():
    extract_script = EXTRACT_SCRIPT.read_text(encoding="utf-8")

    assert "CHECK annotation" in extract_script
    assert "MANUAL_OVERRIDE_KEYS" in extract_script
    assert '"Chti1948Shih"' in extract_script
    assert '"Deydier1974BALD"' in extract_script
    assert '"Hsii1970aBIE"' in extract_script
    assert '"Hsiao1976Work"' in extract_script
    assert '"Studies1970The"' in extract_script
    assert '"Japan1972Work"' in extract_script
    assert '"Cheng1974Kao"' in extract_script
    assert '"Hsii1948Work"' in extract_script
    assert '"Hughes1964Inkyo"' in extract_script
    assert '"Jung1975Hsia"' in extract_script
    assert '"RRA1975Chigoku"' in extract_script
    assert '"Van1967Yin"' in extract_script
    assert '"Keightley1975Legitimation"' in extract_script
    assert '"LPR1959Some"' in extract_script
    assert '"Lao1969Yin"' in extract_script
    assert '"Linduff1972Tradition"' in extract_script
    assert '"Britton1968Divination"' in extract_script
    assert '"  annotation   = {CHECK: bibliography extraction artifacts retained "' in extract_script
    assert '"  note        = {CHECK: bibliography extraction artifacts retained "' not in extract_script


def test_first_manual_override_tranche_replaces_corrupted_top_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Bishop1932Chronology," in manual_bib
    assert "@article{Bishop1932Scapulimancy," not in manual_bib
    assert "@incollection{Andree1906Scapulimantia," in manual_bib
    assert "@article{Auffenberg1962Status," in manual_bib
    assert "@book{Barnard1974Mao," in manual_bib
    assert "@book{Britton1937aYin," in manual_bib

    assert "@book{LPR1959Some," not in generated_bib
    assert "@article{Bawden1958Practice," not in generated_bib
    assert "@book{Britton1968Divination," not in generated_bib


def test_ab_pinyin_audit_updates_chinese_language_entries_only():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "Rao Zongyi, Yindai zhengbu renwu tongkao" in manual_bib
    assert "Zhou Hongxiang, Shang Yin diwang benji" in manual_bib
    assert "author       = {An, Zhimin}" in manual_bib
    assert "title        = {1952 nian qiuji Zhengzhou Erligang fajue ji}" in manual_bib
    assert "title        = {Zhengzhou shi Renmin gongyuan fujin di Yindai yicun}" in manual_bib
    assert "journaltitle = {Wenwu cankao ziliao}" in manual_bib
    assert "Yinxu jiagu xiangpian" in manual_bib
    assert "Yinxu jiagu tapian" in manual_bib
    assert "Jiagu wushi pian" in manual_bib

    assert "Jao Tsung-yi, Yin-tai cheng-pu jen-wu t'ung-k'ao" not in manual_bib
    assert "Chou Hung-hsiang, Shang-Yin ti-wang pen-chi" not in manual_bib
    assert "author       = {An, Chih-min}" not in manual_bib
    assert "Yi-chiu-wu-erh-nien ch'iu-chi Cheng-chou Erh-li-kang fa-chueh chi" not in manual_bib
    assert "Cheng-chou-shih Jen-min kung-yuan fu-chin ti Yin-tai yi-ts'un" not in manual_bib
    assert "Wen-wu ts'an-k'ao tzu-liao" not in manual_bib
    assert "Yin-hsu chia-ku hsiang-p'ien" not in manual_bib
    assert "Yin-hsu chia-ku t'a-p'ien" not in manual_bib
    assert "Chia-ku wu-shih p'ien" not in manual_bib


def test_second_manual_override_tranche_replaces_corrupted_c_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Chang1972Rediscovery," in manual_bib
    assert "@article{Chang1963Shang," in manual_bib
    assert "@article{Zhang1954Yin," in manual_bib
    assert "@book{Chao1970Marriage," in manual_bib
    assert "@article{Cheng1974Kao," in manual_bib

    assert "@book{Japan1972Work," not in generated_bib
    assert "@book{Japan1972The," not in generated_bib
    assert "@book{Chang1954Yin," not in generated_bib
    assert "@book{Chao1970Marriage," not in generated_bib
    assert "@article{Cheng1971The," not in generated_bib


def test_third_manual_override_tranche_replaces_corrupted_chen_to_creel_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Chen1951Chiapien," in manual_bib
    assert "@article{Chin1962aKufang," in manual_bib
    assert "@incollection{Chou1968Early," in manual_bib
    assert "@article{Chu1965aShihchi," in manual_bib
    assert "@book{CooleyLohnes1971Multivariate," in manual_bib
    assert "@book{Creel1938Studies," in manual_bib

    assert "@book{Chen1936Yin," not in generated_bib
    assert "@book{Chin1962Shih," not in generated_bib
    assert "@book{Chou1968The," not in generated_bib
    assert "@book{Chti1948Shih," not in generated_bib
    assert "@book{Studies1970The," not in generated_bib


def test_fourth_manual_override_tranche_replaces_corrupted_d_to_h_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@book{Deydier1976Jiaguwen," in manual_bib
    assert "@article{Gelb1967Approaches," in manual_bib
    assert "@article{Gibson1934Picture," in manual_bib
    assert "@article{Hayashi1968Inshu," in manual_bib
    assert "@article{Hopkins1938Ancestral," in manual_bib
    assert "@article{Hsiao1976Anyang," in manual_bib

    assert "@book{Deydier1974BALD," not in generated_bib
    assert "@book{Eberhard1937Witchcraft," not in generated_bib
    assert "@article{Gardner1934The," not in generated_bib
    assert "@book{Hiroshima1973The," not in generated_bib
    assert "@book{Hsiao1976Work," not in generated_bib


def test_fifth_manual_override_tranche_replaces_tractable_hsu_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Hsu1963Shihyu," in manual_bib
    assert "@article{Hsu1965Tui," in manual_bib
    assert "@book{Hsu1968Yin," in manual_bib
    assert "@unpublished{Hsu1970New," in manual_bib
    assert "@article{Hsu1972aTan," in manual_bib

    assert "@book{Hsii1965Tui," not in generated_bib
    assert "@book{Hsii1968Yin," not in generated_bib
    assert "@book{Hsii1970New," not in generated_bib
    assert "@book{Hsii1970aBIE," not in generated_bib


def test_sixth_manual_override_tranche_replaces_huang_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Huang1958Negatives," in manual_bib
    assert "@book{Huang1967Yinli," in manual_bib
    assert "@article{Huang1969Putsaiming," in manual_bib
    assert "@article{Huang1964Measure," in manual_bib

    assert "@book{Van1958Chin," not in generated_bib
    assert "@book{Van1967Yin," not in generated_bib


def test_seventh_manual_override_tranche_replaces_mixed_hsu_hu_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{HsuChingtsan1935Chienshou," in manual_bib
    assert "@article{HsuChungshu1931Tsailun," in manual_bib
    assert "@article{Hsu1973Tsung," in manual_bib
    assert "@phdthesis{Hsu1974Scapulimantic," in manual_bib
    assert "@article{Hu1939Putzu," in manual_bib
    assert "@article{Hu1976Chiakuwen," in manual_bib
    assert "@incollection{Hu1782Pufa," in manual_bib

    assert "@book{Hsii1935Chung," not in generated_bib
    assert "@book{Hsii1944Ting," not in generated_bib
    assert "@book{Hsii1948Work," not in generated_bib


def test_eighth_manual_override_tranche_replaces_ito_jao_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Ikeda1951Keikeiji," in manual_bib
    assert "@article{Ishida1960Teitei," in manual_bib
    assert "@article{Ito1956Bokuji," in manual_bib
    assert "@book{Ito1975Chugoku," in manual_bib
    assert "@article{Jao1957Haiwai," in manual_bib
    assert "@article{Jao1961aLun," in manual_bib

    assert "@book{Hughes1964Inkyo," not in generated_bib
    assert "@book{Hughes1960Tei," not in generated_bib
    assert "@book{ItO1956Bokuji," not in generated_bib
    assert "@book{HAL1959Anyo," not in generated_bib
    assert "@book{RRA1975Chigoku," not in generated_bib
    assert "@article{Jao1957Hai," not in generated_bib
    assert "@book{Jao1961Sekai," not in generated_bib
    assert "@book{Jao1961aJung," not in generated_bib
    assert "@book{Jochelson1969The," not in generated_bib


def test_ninth_manual_override_tranche_replaces_jung_and_kk_spillover():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Jung1947Chiaku," in manual_bib
    assert "@book{Jung1959Chinwen," in manual_bib
    assert "@book{JungYuanJung1936Chinshishu," in manual_bib
    assert "@article{KK1959Shanhsi," in manual_bib
    assert "@article{KK1975aJufa," in manual_bib
    assert "@article{KKHP1975bKansu," in manual_bib
    assert "@incollection{KaizukaIto1953Kokotsubun," in manual_bib
    assert "@article{Kane1974Independent," in manual_bib
    assert "@article{Kao1949Yinhsu," in manual_bib

    assert "@book{Jung1947Chia," not in generated_bib
    assert "@book{Jung1936Chin," not in generated_bib
    assert "@book{Jung1959Work," not in generated_bib
    assert "@book{Jung1973Chiang," not in generated_bib
    assert "@book{Jung1973Kao," not in generated_bib
    assert "@book{Jung1975Hsia," not in generated_bib


def test_tenth_manual_override_tranche_replaces_k_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@book{Kato1970Kanji," in manual_bib
    assert "@article{Ke1939Shuo," in manual_bib
    assert "@phdthesis{Keightley1969Public," in manual_bib
    assert "@article{Keightley1973Religion," in manual_bib
    assert "@misc{Keightley1975bDate," in manual_bib
    assert "@article{Kryukov1968Differential," in manual_bib
    assert "@book{Kryukov1973Iazyk," in manual_bib
    assert "@book{Kuan1953Yufa," in manual_bib
    assert "@book{Kuo1957Liang," in manual_bib

    assert "@book{Kato1970Kanji," not in generated_bib
    assert "@book{Kato1939Shuo," not in generated_bib
    assert "@book{Keightley1969Public," not in generated_bib
    assert "@book{Keightley1975Legitimation," not in generated_bib
    assert "@book{Knoblock1968Work," not in generated_bib
    assert "@book{Kuan1957Liang," not in generated_bib


def test_eleventh_manual_override_tranche_replaces_l_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{KuoBaojun1951Yichiu," in manual_bib
    assert "@article{Lao1957Shih," in manual_bib
    assert "@book{Legge1865Chinese," in manual_bib
    assert "@article{LiHsiaoting1974Chungkuo," in manual_bib
    assert "@article{LiHsuehchin1958Ti," in manual_bib
    assert "@article{LiYen1969Tu," in manual_bib
    assert "@article{Lin1963Chi," in manual_bib
    assert "@phdthesis{Linduff1972Tradition," in manual_bib

    assert "@book{Lao1955Yin," not in generated_bib
    assert "@book{Lao1969Yin," not in generated_bib
    assert "@book{Lao1972Work," not in generated_bib
    assert "@book{Lin1963Work," not in generated_bib
    assert "@book{Lin1964Work," not in generated_bib
    assert "@book{Linduff1972Tradition," not in generated_bib


def test_twelfth_manual_override_tranche_replaces_late_l_and_m_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Ling1934Sunghua," in manual_bib
    assert "@article{Liu1974Puku," in manual_bib
    assert "@book{Lo1914Yinhsu," in manual_bib
    assert "@incollection{LotFalck1968Divination," in manual_bib
    assert "@book{Mao1971Turtles," in manual_bib
    assert "@article{Matsumaru1976Seishu," in manual_bib
    assert "@article{Matsumoto1915Fossil," in manual_bib
    assert "@article{Mattos1964Partition," in manual_bib
    assert "@book{Michels1973Dating," in manual_bib
    assert "@article{Mickel1976aIndex," in manual_bib
    assert "@article{Mickel1976bThree," in manual_bib
    assert "@book{Middleton1960Lugbara," in manual_bib
    assert "@article{Miyazaki1970Chiigoku," in manual_bib
    assert "@article{Montell1934Clemmys," in manual_bib

    assert "@book{Ling1974Work," not in generated_bib
    assert "@book{LotFalck1968Work," not in generated_bib
    assert "@book{Lukes1976Matsumoto," not in generated_bib
    assert "@book{Lukes1927Inkyo," not in generated_bib
    assert "@book{Mattos1964Partition," not in generated_bib
    assert "@book{Michels1973Dating," not in generated_bib
    assert "@article{Mickel1973Book," not in generated_bib
    assert "@book{Mickel1974aIndex," not in generated_bib
    assert "@book{Oracle1976aIndex," not in generated_bib
    assert "@book{Oracle1976bThree," not in generated_bib
    assert "@book{Oracle1977Index," not in generated_bib
    assert "@book{Middleton1960Lugbara," not in generated_bib
    assert "@book{Miyazaki1970Chiigoku," not in generated_bib
    assert "@book{Montell1934Clemmys," not in generated_bib


def test_thirteenth_manual_override_tranche_replaces_n_to_s_bridge():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@book{Needham1959Science," in manual_bib
    assert "@techreport{Newton1977Canon," in manual_bib
    assert "@unpublished{Nivison1973Existence," in manual_bib
    assert "@book{Ojima1968Kodai," in manual_bib
    assert "@book{Pao1931Tiehyun," in manual_bib
    assert "@incollection{Park1967Divination," in manual_bib
    assert "@article{Peng1965Annotated," in manual_bib
    assert "@article{Ping1931Honan," in manual_bib
    assert "@book{Pope1955ReptileWorld," in manual_bib
    assert "@book{Saito1958Nihon," in manual_bib
    assert "@article{Schmidt1927Reptiles," in manual_bib
    assert "@article{Nivison1977Three," not in manual_bib
    assert "@unpublished{Nivison1973Ritual," not in manual_bib

    assert "@book{Needham1939Science," not in generated_bib
    assert "@book{Needham1977Canon," not in generated_bib
    assert "@book{Needham1973Existence," not in generated_bib
    assert "@book{King1931Work," not in generated_bib
    assert "@book{Bit1955The," not in generated_bib
    assert "@book{Bit1968Book," not in generated_bib
    assert "@book{Bil1958Nihon," not in generated_bib
    assert "@article{Bil1972Book," not in generated_bib
    assert "@article{Bil1927The," not in generated_bib


def test_fourteenth_manual_override_tranche_replaces_s_page_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@unpublished{Serruys1969Negatives," in manual_bib
    assert "@article{Serruys1974The," in manual_bib
    assert "@article{Shih1933Tich," in manual_bib
    assert "@article{Shih1954Kupu," in manual_bib
    assert "@book{Shih1959Hsiao," in manual_bib
    assert "@book{Shihsanching1965Chushu," in manual_bib
    assert "@book{Shima1967Inkyo," in manual_bib
    assert "@article{Shirakawa1948Bokuji," in manual_bib
    assert "@book{Shirakawa1970Setsubun," in manual_bib
    assert "@article{Shirakawa1976Teishin," in manual_bib

    assert "@book{Serruys1969Negatives," not in generated_bib
    assert "@book{Serruys1974The," not in generated_bib
    assert "@book{Shih1933Tich," not in generated_bib
    assert "@book{Shih1943Hsiao," not in generated_bib
    assert "@book{Shih1953Hsiao," not in generated_bib
    assert "@book{Shih1934Work," not in generated_bib
    assert "@book{Shih1959Hsiao," not in generated_bib
    assert "@book{Shih1976Teishin," not in generated_bib
    assert "@book{Shirakawa1948Teishin," not in generated_bib
    assert "@book{Shirakawa1954EAR," not in generated_bib


def test_fifteenth_manual_override_tranche_replaces_early_t_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{TangChienyuan1969Yinhsu," in manual_bib
    assert "@article{TangChienyuan1974HsuYinhsu," in manual_bib
    assert "@book{TangLan1965Kuwentzu," in manual_bib
    assert "@article{TangLan1975Jiangxi," in manual_bib
    assert "@article{TangLan1976Hotsun," in manual_bib
    assert "@book{Tchang1905Synchronismes," in manual_bib
    assert "@book{Teng1971Annotated," in manual_bib
    assert "@article{Thai1963Curiosites," in manual_bib
    assert "@book{Thorp1936Geography," in manual_bib
    assert "@article{TingShan1973Shihshih," in manual_bib
    assert "@article{Su1966Chiwen," in manual_bib
    assert "@article{Su1968Fenghuang," in manual_bib
    assert "@article{Ting1931ProfGranet," in manual_bib
    assert "@book{Todo1969Kanji," in manual_bib
    assert "@book{Tsunoda1951Japan," in manual_bib

    assert "@book{Tang1965CFG," not in generated_bib
    assert "@book{Tang1973Kuan," not in generated_bib
    assert "@book{Tang1976Work," not in generated_bib
    assert "@book{Tang1905Synchronismes," not in generated_bib
    assert "@book{Teng1971Annotated," not in generated_bib
    assert "@article{Thai1963Curiosit," not in generated_bib
    assert "@book{Thai1969Chinese," not in generated_bib
    assert "@book{Thorp1936Geography," not in generated_bib
    assert "@book{Tien1931Prof," not in generated_bib
    assert "@book{Tien1956Chia," not in generated_bib
    assert "@book{Tien1966Work," not in generated_bib
    assert "@book{Tien1969Kanji," not in generated_bib
    assert "@book{Tien1969Shuo," not in generated_bib
    assert "@book{Tsunoda1951Japan," not in generated_bib


def test_sixteenth_manual_override_tranche_replaces_tung_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "{Tung1929Shang," in manual_bib
    assert "{Tung1929cMinkuo," in manual_bib
    assert "{Tung1931Takuei," in manual_bib
    assert "{Tung1933Chia," in manual_bib
    assert "{Tung1948Hsiaotun," in manual_bib
    assert "{Tung1951cChinese," in manual_bib
    assert "{Tung1954Work," in manual_bib
    assert "{Tung1964Fifty," in manual_bib
    assert "{Tung1967Hsueshu," in manual_bib
    assert "{Tung1967Hsii," in manual_bib
    assert "{Turner1975Revelation," in manual_bib

    assert "{Tung1929Shang," not in generated_bib
    assert "{Tung1929aHsin," not in generated_bib
    assert "{Tung1933Chia," not in generated_bib
    assert "{Tung1954Work," not in generated_bib
    assert "{Tung1965Chia," not in generated_bib
    assert "{Tung1967Hsii," not in generated_bib
    assert "{Tung1975Revelation," not in generated_bib
    assert "{Tung1974Work," not in generated_bib


def test_seventeenth_manual_override_tranche_replaces_post_tung_vw_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "author      = {Tung, Tso-pin and Huang, Jan-wei}" in manual_bib
    assert "{TungChin1961Penhsi," in manual_bib
    assert "{Umehara1964Inkyo," in manual_bib
    assert "{Van1961Sexual," in manual_bib
    assert "{WW1975Chianghsi," in manual_bib
    assert "{Walker1968Mammals," in manual_bib
    assert "{Wang1923Kuantang," in manual_bib
    assert "{Wang1933Chia," in manual_bib
    assert "{Wang1972The," in manual_bib
    assert "{Waterbury1942Early," in manual_bib
    assert "{Watson1963Handbook," in manual_bib
    assert "{Wermuth1961Schildkroten," in manual_bib
    assert "{White1945Bone," in manual_bib
    assert "{Wieger1923Textes," in manual_bib
    assert "{Wilkinson1973The," in manual_bib
    assert "{Wilson1970Rationality," in manual_bib

    assert "{Van1961Sexual," not in generated_bib
    assert "{Vernant1968Mammals," not in generated_bib
    assert "{Wang1933Chia," not in generated_bib
    assert "{Wang1972The," not in generated_bib
    assert "{Waterbury1942Early," not in generated_bib
    assert "{Watson1963Handbook," not in generated_bib
    assert "{White1945Bone," not in generated_bib
    assert "{White1923Textes," not in generated_bib
    assert "{Wilkinson1973The," not in generated_bib
    assert "{Wilkinson1970Rationality," not in generated_bib


def test_eighteenth_manual_override_tranche_replaces_y_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "{Yang1963Broken," in manual_bib
    assert "{Yang1949Anyang," in manual_bib
    assert "{Yang1977Tsung," in manual_bib
    assert "{Yeh1929Yinchi," in manual_bib
    assert "{Yeh1934Yinhsu," in manual_bib
    assert "{Yen1951Yinli," in manual_bib
    assert "{Yen1961Chiaku," in manual_bib
    assert "{Yen1974Chia," in manual_bib
    assert "{Yen1976Chiaku," in manual_bib
    assert "{YenYun1973Shangtai," in manual_bib
    assert "{Yetts1933Shang," in manual_bib
    assert "{Yetts1954Shang," in manual_bib
    assert "{Yin1962Chiangsu," in manual_bib
    assert "{Yu1940Shuang," in manual_bib
    assert "{Yu1972Tsung," in manual_bib
    assert "{Yu1929Hsin," in manual_bib

    assert "{Bent1974Chia," not in generated_bib
    assert "{Bent1957Man," not in generated_bib
    assert "{Bent1962KKHP," not in generated_bib
    assert "{Young1936New," not in generated_bib
    assert "{Young1940Shuang," not in generated_bib
    assert "{Young1929Hsin," not in generated_bib


def test_nineteenth_manual_override_tranche_replaces_postscript_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "{Chang1977Archaeology," in manual_bib
    assert "{Hsia1977Tan14," in manual_bib
    assert "{Hsinhua1977Zhouyuan," in manual_bib
    assert "{Hu1977Niao," in manual_bib
    assert "{KK1977Yinhsu," in manual_bib
    assert "{KK1977aAnyang," in manual_bib
    assert "{Lung1976Shih," in manual_bib
    assert "Collections Published 1935-1939" in manual_bib
    assert "{Nivison1977aPronominal," in manual_bib
    assert "{Shen1977Fuyu," in manual_bib
    assert "{Takashima1977aExistence," in manual_bib
    assert "{TungEncheng1977Computer," in manual_bib
    assert "{Yu1977Shuo," in manual_bib

    assert "{Chang1977The," not in generated_bib
    assert "{Haven1976Work," not in generated_bib
    assert "{Hsinhuashe1977Shen," not in generated_bib
    assert "{Hsinhuashe1977Chia," not in generated_bib
    assert "{Hsinhuashe1977Work," not in generated_bib
    assert "{REE1976Shih," not in generated_bib
