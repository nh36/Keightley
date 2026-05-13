"""Regression checks for live bibliography backmatter wiring."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BIBLIO_A = REPO_ROOT / "tex" / "backmatter" / "biblio_a.tex"
BIBLIO_B = REPO_ROOT / "tex" / "backmatter" / "biblio_b.tex"
ABBREVIATIONS_YML = REPO_ROOT / "data" / "abbreviations.yml"
ABBREVIATIONS_LIVE = REPO_ROOT / "tex" / "backmatter" / "abbreviations_live.tex"
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


def test_bibliography_a_uses_curated_abbreviation_entries():
    abbreviations_yml = ABBREVIATIONS_YML.read_text(encoding="utf-8")
    abbreviations_live = ABBREVIATIONS_LIVE.read_text(encoding="utf-8")

    assert 'abbr: "Chi-ch\'eng I"' in abbreviations_yml
    assert 'cjk: "誠齋殷墟文字"' in abbreviations_yml
    assert 'cjk: "甲骨卜辭七集"' in abbreviations_yml
    assert 'cjk: "甲骨集成"' in abbreviations_yml
    assert 'cjk: "柏根氏舊藏甲骨文字"' in abbreviations_yml
    assert 'cjk: "小屯第二本：殷墟文字：甲編"' in abbreviations_yml
    assert 'cjk: "海外甲骨錄遺"' in abbreviations_yml
    assert 'cjk: "小屯第二本：殷墟文字：乙編"' in abbreviations_yml
    assert 'cjk: "小屯第二本：殷墟文字：丙編"' in abbreviations_yml
    assert 'cjk: "甲骨綴合新編"' in abbreviations_yml
    assert 'cjk: "甲骨續補"' in abbreviations_yml
    assert 'cjk: "廈門大學所藏甲骨文字"' in abbreviations_yml
    assert 'cjk: "金璋所藏甲骨卜辭"' in abbreviations_yml
    assert 'cjk: "甲骨文零拾"' in abbreviations_yml
    assert 'cjk: "美國納爾森美術舘藏甲骨卜辭考釋"' in abbreviations_yml
    assert 'cjk: "傅氏所藏甲骨文字"' in abbreviations_yml
    assert 'cjk: "傅氏殷契徵文"' in abbreviations_yml
    assert 'cjk: "殷契摭佚"' in abbreviations_yml
    assert 'cjk: "殷契摭佚續編"' in abbreviations_yml
    assert 'cjk: "鐵雲藏龜新編"' in abbreviations_yml
    assert 'cjk: "鐵雲藏龜零拾"' in abbreviations_yml
    assert 'cjk: "鐵雲藏龜拾遺"' in abbreviations_yml
    assert 'cjk: "鐵雲藏龜之餘"' in abbreviations_yml
    assert 'cjk: "殷墟書契續編"' in abbreviations_yml
    assert 'cjk: "殷墟卜辭後編"' in abbreviations_yml
    assert 'cjk: "殷墟文字外編"' in abbreviations_yml
    assert 'cjk: "殷契遺珠"' in abbreviations_yml
    assert 'cjk: "殷契粹編"' in abbreviations_yml
    assert 'cjk: "本系所藏甲骨文字"' in abbreviations_yml
    assert 'cjk: "殷契拾掇"' in abbreviations_yml
    assert 'cjk: "天壤閣甲骨文存并考釋"' in abbreviations_yml
    assert 'cjk: "鄴中片羽初集"' in abbreviations_yml
    assert 'cjk: "鄴中片羽三集"' in abbreviations_yml
    assert 'cjk: "臺灣大學所藏甲骨文字附考釋"' in abbreviations_yml
    assert 'cjk: "卜辭通纂"' in abbreviations_yml
    assert 'cjk: "殷墟卜辭"' in abbreviations_yml
    assert 'abbr: "Hsü-pu"' in abbreviations_yml
    assert 'abbr: "US"' in abbreviations_yml
    assert 'abbr: "Yi-pien"' in abbreviations_yml

    assert r"\item[Chi-ch'eng I] Yen Yi-p'ing. Chia-ku chi-ch'eng. Vol. I. [Taipei], 1975. \textit{[甲骨集成]}" in abbreviations_live
    assert r"\item[Chia-pien] Tung Tso-pin. Hsiao-t'un ti-erh-pen: Yin-hsü wen-tzu: chia-pien. Nanking, 1948. Reprint, Taipei, 1977. \textit{[小屯第二本：殷墟文字：甲編]}" in abbreviations_live
    assert r"\item[Ch'eng-chai] Sun Hai-po. Ch'eng-chai Yin-hsü wen-tzu. Peking, 1940. \textit{[誠齋殷墟文字]}" in abbreviations_live
    assert r"\item[Ch'i-chi] Fang Fa-han [Frank H. Chalfant] and Po Jui-hua [Roswell S. Britton]. Chia-ku pu-tz'u ch'i-chi (Seven Collections of Inscribed Oracle Bone). New York, 1938. Reprint, Taipei, 1966. \textit{[甲骨卜辭七集]}" in abbreviations_live
    assert r"\item[Chih-hsü] Li Ya-nung. Yin-ch'i chih-yi hsü-pien. Peking, 1950. \textit{[殷契摭佚續編]}" in abbreviations_live
    assert r"\item[Chih-yi] Li Tan-ch'iu. Yin-ch'i chih-yi. Peking, 1941. \textit{[殷契摭佚]}" in abbreviations_live
    assert r"\item[Chin-chang] Fang Fa-han [Frank H. Chalfant] and Po Jui-hua [Roswell S. Britton]. Chin-chang so-ts'ang chia-ku pu-tz'u (The Hopkins Collection of Inscribed Oracle Bone). New York, 1939. Reprint, Taipei, 1966. \textit{[金璋所藏甲骨卜辭]}" in abbreviations_live
    assert r"\item[Ching-chin] Hu Hou-hsüan. Chan-hou Ching-chin hsin-huo chia-ku-chi. Shanghai, 1954. \textit{[戰後京津薪穫甲骨集]}" in abbreviations_live
    assert r"\item[Cho-ts'un] Tseng Yi-kung. Chia-ku cho-ts'un. N.p., 1939. \textit{[甲骨綴存]}" in abbreviations_live
    assert r"\item[Chui-hsin] Yen Yi-p'ing. Chia-ku chui-ho hsin-pien. Taipei, 1975. \textit{[甲骨綴合新編]}" in abbreviations_live
    assert r"\item[Fu-chia] Shang Ch'eng-tso. Fu-shih so-ts'ang chia-ku wen-tzu. Nanking, 1933. \textit{[傅氏所藏甲骨文字]}" in abbreviations_live
    assert r"\item[Fu-yin] Wang Hsiang. Fu-shih Yin-ch'i cheng-wen. Tientsin, 1925. \textit{[傅氏殷契徵文]}" in abbreviations_live
    assert r"\item[Hai-wai] Jao Tsung-yi. Hai-wai chia-ku lu-i. Journal of Oriental Studies 4.1-2 (1957/58), pp. 1-22. \textit{[海外甲骨錄遺]}" in abbreviations_live
    assert r"\item[Hsia-men] Hu Hou-hsüan. Hsia-men ta-hsüeh so-ts'ang chia-ku wen-tzu. In Chia-ku-hsüeh Shang-shih lun-ts'ung ch'u-chi. Ch'eng-tu, 1944. \textit{[廈門大學所藏甲骨文字]}" in abbreviations_live
    assert r"\item[Hsü-pien] Lo Chen-yü. Yin-hsü shu-ch'i hsü-pien. N.p., 1933. Reprint, [Taipei], n.d. \textit{[殷墟書契續編]}" in abbreviations_live
    assert r"\item[Hsü-pu] Hu Hou-hsüan. Chia-ku hsü-pu [unpublished collection, title uncertain]. \textit{[甲骨續補]}" in abbreviations_live
    assert r"\item[Ping-pien] Chang Ping-ch'üan. Hsiao-t'un ti-erh-pen: Yin-hsü wen-tzu: ping-pien. Taipei. Vol. 1, pt. 1 (1957); pt. 2 (1959). Vol. 2, pt. 1 (1962); pt. 2 (1965). Vol. 3, pt. 1 (1967); pt. 2 (1972). \textit{[小屯第二本：殷墟文字：丙編]}" in abbreviations_live
    assert r"\item[Jimbun] Kaizuka Shigeki. Kyōto daigaku jimbun kagaku kenkyūjo zō kōkotsu monji. 2 vols. Kyoto, 1959. Shakubun. Kyoto, 1960. Sakuin. Kyoto, 1968. \textit{[京都大學人文科學研究所藏甲骨文字]}" in abbreviations_live
    assert r"\item[Kikkō] Hayashi Taisuke. Kikkō jūkotsu monji. N.p., 1921. Reprint, Taipei, 1970. \textit{[龜甲獸骨文字]}" in abbreviations_live
    assert r"\item[K'u-fang] Fang Fa-lien [Frank H. Chalfant] and Po Jui-hua [Roswell S. Britton]. K'u-Fang erh-shih-ts'ang chia-ku pu-tz'u (The Couling-Chalfant Collection of Inscribed Oracle Bone). Shanghai, 1935. Reprint, Taipei, 1966. \textit{[庫方二氏藏甲骨卜辭]}" in abbreviations_live
    assert r"\item[Ling-shih] Ch'en Pang-huai. Chia-ku-wen ling-shih. Tientsin, 1959. Reprint, Tokyo, 1970. \textit{[甲骨文零拾]}" in abbreviations_live
    assert r"\item[Liu-lu] Hu Hou-hsüan. Chia-ku liu-lu. In Chia-ku-hsüeh Shang-shih lun-ts'ung san-chi. Ch'eng-tu, 1945. \textit{[甲骨六錄]}" in abbreviations_live
    assert r"\item[Ming-hou] Ming Yi-shih [James M. Menzies]. Yin-hsü pu-tz'u hou-pien. Edited by Hsü Chin-hsiung. 2 vols. Taipei, 1972. \textit{[殷墟卜辭後編]}" in abbreviations_live
    assert r"\item[Nan-pei] Hu Hou-hsüan. Chan-hou nan-pei so-chien chia-ku-lu. Peking and Shanghai, 1951. \textit{[戰後南北所見甲骨錄]}" in abbreviations_live
    assert r"\item[Na-erh] Yen Yi-p'ing. Mei-kuo Na-erh-sen mei-shu-kuan ts'ang chia-ku pu-tz'u k'ao-shih. Taipei, 1973. (Originally published in Chung-kuo wen-tzu 22-25, 29 [1966-1968].) \textit{[美國納爾森美術舘藏甲骨卜辭考釋]}" in abbreviations_live
    assert r"\item[Ning-hu] Hu Hou-hsüan. Chan-hou Ning-hu hsin-huo chia-ku-chi. Peking, 1951. \textit{[戰後寧滬新獲甲骨集]}" in abbreviations_live
    assert r"\item[Ogawa] Itō Michiharu. Ko Ogawa Chikanosuke shi zō kōkotsu monji. Tōhō gakuhō 37 (1966), pp. 249-263. \textit{[故小川睦之輔氏藏甲骨文字]}" in abbreviations_live
    assert r"\item[Pa-li] Jao Tsung-yi. Pa-li so-chien chia-ku-lu. Hongkong, 1956. \textit{[巴黎所見甲骨錄]}" in abbreviations_live
    assert r"\item[Pai-ken] Ming Yi-shih [James M. Menzies]. Pai-ken-shih chiu-ts'ang chia-ku wen-tzu (The Paul D. Bergen Collection: Chinese Oracle Bone Characters). Ch'i-ta chi-k'an 6 and 7 (1935). \textit{[柏根氏舊藏甲骨文字]}" in abbreviations_live
    assert r"\item[Pu-tz'u] Jung Keng and Ch'ü Jun-min. Yin-ch'i pu-tz'u. Peiping, 1933. Reprint, Taipei, 1970. \textit{[殷契卜辭]}" in abbreviations_live
    assert r"\item[Shih-to] Kuo Jo-yü. Yin-ch'i shih-to. Vol. 1. Shanghai, 1951. Vol. 2. Peking, 1953. \textit{[殷契拾掇]}" in abbreviations_live
    assert r"\item[T'ai-ta I] Tung Tso-pin. Tai-wan ta-hsüeh so-ts'ang chia-ku wen-tzu fu-k'ao-shih. Kuo-li T'ai-wan ta-hsüeh k'ao-ku jen-lei hsüeh-k'an 1 (1953), pp. 22-46. \textit{[臺灣大學所藏甲骨文字附考釋]}" in abbreviations_live
    assert r"\item[T'ai-ta 2] Tung Tso-pin and Chin Hsiang-heng. Pen-hsi so-ts'ang chia-ku wen-tzu. Kuo-li T'ai-wan ta-hsüeh k'ao-ku jen-lei hsüeh-k'an 17-18 (1961), pp. 71-84. \textit{[本系所藏甲骨文字]}" in abbreviations_live
    assert r"\item[T'ien-jang] T'ang Lan. T'ien-jang-ke chia-ku wen-ts'un. Peiping, 1939. \textit{[天壤閣甲骨文存并考釋]}" in abbreviations_live
    assert r"\item[T'ieh-hsin] Yen Yi-p'ing. Tieh-yün ts'ang-kuei hsin-pien. Taipei, 1975. \textit{[鐵雲藏龜新編]}" in abbreviations_live
    assert r"\item[T'ieh-shih] Li Tan-ch'iu. Tieh-yün ts'ang-kuei ling-shih. Shanghai, 1939. \textit{[鐵雲藏龜零拾]}" in abbreviations_live
    assert r"\item[T'ieh-yi] Yeh Yü-sen. Tieh-yün ts'ang-kuei shih-yi. N.p., 1925. \textit{[鐵雲藏龜拾遺]}" in abbreviations_live
    assert r"\item[T'ieh-yü] Lo Chen-yü. Tieh-yün ts'ang-kuei chih-yü. N.p., 1915. Reprint, Hongkong, 1972. \textit{[鐵雲藏龜之餘]}" in abbreviations_live
    assert r"\item[T'ieh-yün] Liu E. Tieh-yün ts'ang-kuei. N.p., 1903. Reprint, [Taipei], 1959. \textit{[鐵雲藏龜]}" in abbreviations_live
    assert r"\item[Ts'ui-pien] Kuo Mo-jo. Yin-ch'i ts'ui-pien. Tokyo, 1937. Rev. ed., Peking, 1959. Reprint, Taipei, 1971. \textit{[殷契粹編]}" in abbreviations_live
    assert r"\item[US] Chou Hung-hsiang. Oracle Bone Collections in the United States." in abbreviations_live
    assert r"\item[T'ung-tsuan] Kuo Mo-jo. Pu-tz'u t'ung-tsuan. Tokyo, 1933. \textit{[卜辭通纂]}" in abbreviations_live
    assert r"\item[Wai-pien] Tung Tso-pin. Yin-hsü wen-tzu wai-pien. Taipei, 1956. \textit{[殷墟文字外編]}" in abbreviations_live
    assert r"\item[Wen-lu] Sun Hai-po. Chia-ku wen-lu. Honan, 1938. Reprint, Taipei, 1971. \textit{[甲骨文錄]}" in abbreviations_live
    assert r"\item[Yeh-ch'u] Huang Chün. Yeh-chung p'ien-yü ch'u-chi. Peiping, 1935. [The oracle-bone rubbings are reprinted in Yeh-chung p'ien-yü. Taipei, 1972.] \textit{[鄴中片羽初集]}" in abbreviations_live
    assert r"\item[Yeh-san] Huang Chün. Yeh-chung p'ien-yü san-chi. Peiping, 1939. [The oracle-bone rubbings are reprinted in Yeh-chung p'ien-yü. Taipei, 1972.] \textit{[鄴中片羽三集]}" in abbreviations_live
    assert r"\item[Yin-hsü] Ming Yi-shih [James Mellon Menzies]. Yin-hsü pu-tz'u (Oracle Records from the Waste of Yin)." in abbreviations_live
    assert r"\item[Yin-hsü] Ming Yi-shih [James Mellon Menzies]. Yin-hsü pu-tz'u (Oracle Records from the Waste of Yin). Shanghai, 1917. Reprint, Taipei, 1972. \textit{[殷墟卜辭]}" in abbreviations_live
    assert r"\item[Yi-chu] Chin Tsu-t'ung. Yin-ch'i yi-chu. Shanghai, 1939. Reprint, Taipei, 1975. \textit{[殷契遺珠]}" in abbreviations_live
    assert r"\item[Yi-pien] Tung Tso-pin. Hsiao-t'un ti-erh-pen: Yin-hsü wen-tzu: yi-pien. Pt. 1 [Nanking], 1948. Pt. 2 [Nanking], 1949. Pt. 3, Taipei, 1953. \textit{[小屯第二本：殷墟文字：乙編]}" in abbreviations_live
    assert r"\item[Yi-ts'un] Shang Ch'eng-tso. Yin-ch'i yi-ts'un. Nanking, 1933. Reprint, Tokyo, 1966. \textit{[殷契遺存]}" in abbreviations_live

    assert "[CJK:" not in abbreviations_live
    assert "Ghi-ch" not in abbreviations_live
    assert "ACE AE AINE SEAR" not in abbreviations_live


def test_manual_bibliography_resource_is_loaded():
    preamble = PREAMBLE.read_text(encoding="utf-8")

    assert r"\addbibresource{bibliography/keightley.bib}" in preamble
    assert r"\addbibresource{bibliography/keightley_manual.bib}" in preamble
    assert r"\DeclareFieldFormat{usera}{#1}" in preamble
    assert r"\DeclareFieldFormat{userb}{#1}" in preamble
    assert r"\DeclareFieldFormat{userc}{#1}" in preamble
    assert r"\DeclareFieldFormat{series}{#1\iffieldundef{userc}{}{\addspace\printfield{userc}}}" in preamble
    assert r"\renewbibmacro*{author}{" in preamble
    assert r"\renewbibmacro*{editor}{" in preamble
    assert r"\renewbibmacro*{title}{" in preamble
    assert r"\renewbibmacro*{booktitle}{" in preamble
    assert r"\renewbibmacro*{journal}{" in preamble
    assert r"\clearfield{note}%" in preamble
    assert r"\clearfield{nameaddon}%" in preamble
    assert r"\clearfield{titleaddon}%" in preamble
    assert r"\clearfield{booktitleaddon}%" in preamble
    assert r"\clearfield{maintitleaddon}%" in preamble
    assert r"\clearfield{journaltitleaddon}%" in preamble
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
    assert '"Lao1974Chou"' in extract_script
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


def test_c_pinyin_audit_updates_high_confidence_chinese_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author      = {Zhongguo kexueyuan kaogu yanjiusuo}" in manual_bib
    assert "title       = {Jiagu wenbian}" in manual_bib
    assert "author      = {Guoli zhongyang yanjiuyuan lishi yuyan yanjiusuo}" in manual_bib
    assert "title       = {Anyang fajue baogao}" in manual_bib
    assert "author      = {Ji, Fotuo}" in manual_bib
    assert "title       = {Jianshoutang suocang Yinxu wenzi}" in manual_bib
    assert "author       = {Chen, Mengjia}" in manual_bib
    assert "shortauthor  = {Mengjia}" in manual_bib
    assert "title        = {Jiagu duantaixue jiabian}" in manual_bib
    assert "title        = {Jiefanghou jiagu de xin ziliao he zhengli yanjiu}" in manual_bib
    assert "title        = {Shang Yin yu Xia Zhou de niandai wenti}" in manual_bib
    assert "title       = {Yinxu buci zongshu}" in manual_bib
    assert "author      = {Jin, Xiangheng}" in manual_bib
    assert "title       = {Xu jiagu wenbian}" in manual_bib
    assert "title        = {Jiaguwen tongjietzi juyu}" in manual_bib
    assert "title        = {Jiaguwen youzi yinyi kao}" in manual_bib
    assert "author      = {Qu, Wanli}" in manual_bib
    assert "title       = {Xiaotun dier ben: Yinxu wenzi: Jiabian kaoshi}" in manual_bib

    assert "author      = {Chung-kuo k'e-hsueh-yuan k'ao-ku yen-chiu-so}" not in manual_bib
    assert "title       = {An-yang fa-chieh pao-kao}" not in manual_bib
    assert "author      = {Chi, Fo-t'o}" not in manual_bib
    assert "author       = {Ch'en Meng-chia}" not in manual_bib
    assert "author      = {Ch'en Meng-chia}" not in manual_bib
    assert "title       = {Hsu chia-ku wen-pien}" not in manual_bib
    assert "title        = {Shih yu-cheng yu-cheng}" not in manual_bib
    assert "title        = {Chia-ku-wen t'ung-chieh-tzu chü-yü}" not in manual_bib
    assert "title        = {Chia-ku-wen yu-tzu yin-yi k'ao}" not in manual_bib
    assert "title        = {Fu-jen ta-hsueh so-ts'ang chia-ku wen-tzu hou-yen}" not in manual_bib
    assert "title        = {Shih-fa lan-shang yu Yin-tai lun}" not in manual_bib
    assert "title        = {Yueh-yi chi-ku}" not in manual_bib
    assert "title       = {Yin-hsu pu-tz'u tsung-shu}" not in manual_bib
    assert "Hsiao-t'un ti-erh-pen: Yin-hsu wen-tzu: chia-pien k'ao-shih" not in manual_bib


def test_c_pinyin_audit_updates_zhang_henan_zheng_subcluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Zhang, Guangzhi}" in manual_bib
    assert "shortauthor  = {Guangzhi}" in manual_bib
    assert 'title        = {Shang wang miaohao xinkao}' in manual_bib
    assert "userb        = {商王廟號新考}" in manual_bib
    assert 'title        = {Guanyu "Shang wang miaohao xinkao" yiwen de buchong yijian}' in manual_bib
    assert "userb        = {關於《商王廟號新考》一文的補充意見}" in manual_bib
    assert "title        = {Shang Zhou qingtongqi qixing zhuangshi huawen yu mingwen zonghe}" in manual_bib
    assert "title        = {Tan Wang Hai yu Yi Yin de jiri bing zai lun Yin Shang wangzhi}" in manual_bib
    assert "title       = {Shang Zhou qingtongqi yu mingwen de zonghe yanjiu}" in manual_bib
    assert "author       = {Zhang, Bingquan}" in manual_bib
    assert "author      = {Henan sheng wenhuachu wenwu gongzuodui}" in manual_bib
    assert "title       = {Zhengzhou Erligang}" in manual_bib
    assert "author       = {Zheng, Dekun}" in manual_bib
    assert "title        = {Gaocheng Taixi Shangdai yizhi faxian de taoqi wenzi}" in manual_bib
    assert "journaltitle = {Wenwu}" in manual_bib

    assert "title        = {Shang wang miao-hao hsin-k'ao}" not in manual_bib
    assert "title        = {Kuan-yu 'Shang-wang miao-hao hsin-k'ao' yi-wen ti pu-ch'ung yi-chien}" not in manual_bib
    assert "title        = {Shang-Chou ch'ing-t'ung-ch'i ch'i-hsing chuang-shih hua-wen yü ming-wen tsung-ho}" not in manual_bib
    assert "title        = {T'an Wang Hai yü Yi Yin ti chi-jih ping tsai-lun Yin-Shang wang-chih}" not in manual_bib
    assert "title       = {Shang-Chou ch'ing-t'ung-ch'i yü ming-wen ti tsung-ho yen-chiu}" not in manual_bib
    assert "author       = {Chang, Ping-ch'uan}" not in manual_bib
    assert "author      = {Ho-nan sheng wen-hua-chu wen-wu kung-tso-tui}" not in manual_bib
    assert "title       = {Cheng-chou Erh-li-kang}" not in manual_bib
    assert "title        = {Kao-ch'eng T'ai-hsi Shang-tai yi-chih fa-hsien ti t'ao-ch'i wen-tzu}" not in manual_bib


def test_c_pinyin_audit_updates_remaining_zhang_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author      = {Zhang, Guangyu}" in manual_bib
    assert "title       = {Weizuo xian Qin yiqi mingwen shuyao}" in manual_bib
    assert "author       = {Zhang, Guangyuan}" in manual_bib
    assert "title        = {Yin Shang jiagu wenzi qiuzhen (xia)}" in manual_bib
    assert "journaltitle = {Gongzhong zazhi}" in manual_bib
    assert "title        = {Yinxu bugui zhi buzhao ji qi youguan wenti}" in manual_bib
    assert "title        = {Bugui fujiadi xushu}" in manual_bib
    assert "title        = {Buci guiwei yueshi de xin zhengju}" in manual_bib
    assert "title       = {Xiaotun dierben: Yinxu wenzi: bingbian. Vol. 1, pt. 1}" in manual_bib
    assert "title        = {Lun chengtao buci}" in manual_bib
    assert "title        = {Jiaguwen de faxian yu gubu xiguan de kaozheng}" in manual_bib
    assert "journaltitle = {Guoli zhongyang yanjiuyuan yuankan}" in manual_bib

    assert "author      = {Chang, Kuang-yu}" not in manual_bib
    assert "title       = {Wei-tso hsien-Ch'in yi-ch'i ming-wen shu-yao}" not in manual_bib
    assert "author       = {Chang, Kuang-yuan}" not in manual_bib
    assert "title        = {Yin-Shang chia-ku wen-tzu ch'iu-chen (hsia)}" not in manual_bib
    assert "journaltitle = {Kung-chung tsa-chih}" not in manual_bib
    assert "title        = {Yin-hsü pu-kuei chih pu-chao chi ch'i yu-kuan wen-ti}" not in manual_bib
    assert "title        = {Pu-kuei fu-chia-ti hsü-shu}" not in manual_bib
    assert "title        = {Pu-tz'u kuei-wei yüeh-shih ti hsin cheng-chü}" not in manual_bib
    assert "title       = {Hsiao-t'un ti-erh-pen: Yin-hsü wen-tzu: ping-pien. Vol. 1, pt. 1}" not in manual_bib
    assert "title        = {Lun ch'eng-t'ao pu-tz'u}" not in manual_bib
    assert "title        = {Chia-ku-wen ti fa-hsien yü ku-pu hsi-kuan ti k'ao-cheng}" not in manual_bib


def test_dh_pinyin_audit_updates_huang_hsiao_hsu_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Huang, Jingxin}" in manual_bib
    assert 'title        = {Qin Han yiqian gu Hanyu zhong de foudingci "fu" "bu" yanjiu}' in manual_bib
    assert "journaltitle = {Yuyan yanjiu}" in manual_bib
    assert "author      = {Huang, Ranwei}" in manual_bib
    assert "title       = {Yinli kaoshi}" in manual_bib
    assert "series      = {Guoli Taiwan daxue wenshi congkan}" in manual_bib
    assert "@book{Huang1967Yinli,\n  author      = {Huang, Ranwei},\n  usera       = {黃然偉},\n  year        = {1967},\n  title       = {Yinli kaoshi},\n  userb       = {殷曆考釋},\n  series      = {Guoli Taiwan daxue wenshi congkan},\n  userc        = {國立臺灣大學文史叢刊}," in manual_bib
    assert "author       = {Huang, Peirong}" in manual_bib
    assert 'title        = {Jiawen "pu-tsai-ming" (?) yi ci de jiantao}' in manual_bib
    assert "journaltitle = {Zhongguo wenzi}" in manual_bib
    assert "author       = {Huang, Caijun}" in manual_bib
    assert "journaltitle = {Zhongguo yuwen}" in manual_bib
    assert "author       = {Xiao, Nan}" in manual_bib
    assert 'title        = {Anyang Xiaotun nandi faxian de "Duizu bujia"---Jian lun "Duizu buci" de shidai ji qi xiangguan wenti}' in manual_bib
    assert "author       = {Xu, Jingcan}" in manual_bib
    assert "author       = {Xu, Zhongshu}" in manual_bib
    assert "author       = {Xu, Jinxiong}" in manual_bib
    assert "title        = {Shi yu}" in manual_bib
    assert 'title        = {Dui Zhang Guangzhi xiansheng de "Shang wang miaohao xinkao" de jidian yijian}' in manual_bib
    assert "title       = {Yin buci zhong wuzhong jisi de yanjiu}" in manual_bib
    assert "title        = {Zuanzuo dui buci duandai de zhongyaoxing}" in manual_bib
    assert "title        = {Yin buci zhong wuzhong jisi yanjiu de xin guannian}" in manual_bib
    assert "title        = {Wuzhong jisi de xin guannian yu Yinli de tantao}" in manual_bib
    assert "title        = {Lue tan zhenren de zaizhi niandai}" in manual_bib
    assert "title        = {Tan zhenren He de niandai}" in manual_bib
    assert "title        = {Cong changzuo de peizhi shifen disan yu disi qi de bugu}" in manual_bib
    assert "title       = {Bugu shang de zuozuan xingtai}" in manual_bib

    assert "author       = {Huang, Ching-hsin}" not in manual_bib
    assert "title        = {Ch'in-Han yi-ch'ien ku Han-yu chung ti fou-ting-tz'u 'fu' 'pu' yen-chiu}" not in manual_bib
    assert "journaltitle = {Yu-yen yen-chiu}" not in manual_bib
    assert "author      = {Huang, Jan-wei}" not in manual_bib
    assert "title       = {Yin-li k'ao-shih}" not in manual_bib
    assert "series      = {Kuo-li T'ai-wan ta-hsueh wen-shih ts'ung-k'an}" not in manual_bib
    assert "author       = {Huang, P'ei-jung}" not in manual_bib
    assert "title        = {Chia-wen 'pu-tsai-ming' (?) yi-tz'u ti chien-t'ao}" not in manual_bib
    assert "author       = {Huang, Tsai-chun}" not in manual_bib
    assert "journaltitle = {Chung-kuo yu-wen}" not in manual_bib
    assert "author       = {Hsiao Nan}" not in manual_bib
    assert "author       = {Hsu, Ching-ts'an}" not in manual_bib
    assert "author       = {Hsu, Chung-shu}" not in manual_bib
    assert "title        = {Shih yu}" not in manual_bib
    assert "title        = {Tui Chang Kuang-chih hsien-sheng ti 'Shang-wang miao-hao hsin-k'ao' ti chi-tien yi-chien}" not in manual_bib
    assert "title       = {Yin pu-tzu chung wu-chung chi-ssu ti yen-chiu}" not in manual_bib
    assert "title        = {Tsuan-tso tui pu-tz'u tuan-tai ti chung-yao-hsing}" not in manual_bib
    assert "title        = {Yin pu-tz'u chung wu-chung chi-ssu yen-chiu ti hsin kuan-nien}" not in manual_bib
    assert "title        = {Wu-chung chi-ssu ti hsin kuan-nien yu Yin-li ti t'an-t'ao}" not in manual_bib
    assert "title        = {Lueh-t'an chen-jen ti tsai-chih nien-tai}" not in manual_bib
    assert "title        = {T'an chen-jen Ho ti nien-tai}" not in manual_bib
    assert "title        = {Ts'ung ch'ang-tso ti p'ei-chih shih-fen ti-san yu ti-ssu ch'i ti pu-ku}" not in manual_bib
    assert "title       = {Pu-ku shang ti tso-tsuan hsing-t'ai}" not in manual_bib


def test_dh_pinyin_audit_updates_hu_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Hu, Houxuan}" in manual_bib
    assert "author      = {Hu, Houxuan}" in manual_bib
    assert "@article{Hu1939Putzu,\n  author       = {Hu, Houxuan},\n  usera        = {胡厚宣},\n  year         = {1939},\n  title        = {Buci zali},\n  userb        = {卜辭雜例},\n  journaltitle = {BIHP},\n  userc        = {中央研究院歷史語言研究所集刊}," in manual_bib
    assert "@article{Hu1939aShih,\n  author       = {Hu, Houxuan},\n  usera        = {胡厚宣},\n  year         = {1939},\n  title        = {Shi ziyong ziyou},\n  userb        = {釋字用字由},\n  journaltitle = {BIHP},\n  userc        = {中央研究院歷史語言研究所集刊}," in manual_bib
    assert "title       = {Wuding shi wuzhong jishi kezi kao}" in manual_bib
    assert "booktitle   = {Jiaguxue Shangshi luncong chuji}" in manual_bib
    assert "title       = {Yindai bugui zhi laiyuan}" in manual_bib
    assert "title       = {Jiaguxue xulun}" in manual_bib
    assert "booktitle   = {Jiaguxue Shangshi luncong erji}" in manual_bib
    assert "@article{Hu1947Putzu,\n  author       = {Hu, Houxuan},\n  usera        = {胡厚宣},\n  year         = {1947},\n  title        = {Buci tongwen li},\n  userb        = {卜辭同文例},\n  journaltitle = {BIHP},\n  userc        = {中央研究院歷史語言研究所集刊}," in manual_bib
    assert "@article{Hu1948Putzu,\n  author       = {Hu, Houxuan},\n  usera        = {胡厚宣},\n  year         = {1948},\n  title        = {Buci jishi wenzi shiguan qianming li},\n  userb        = {卜辭記事文字史官簽名例}," in manual_bib
    assert "title       = {Wushinian jiaguwen faxian de zongjie}" in manual_bib
    assert "title       = {Wushinian jiaguxue lunzhumu}" in manual_bib
    assert "title       = {Yinxu fajue}" in manual_bib
    assert "title        = {Yin buci zhong de Shang Di he Wang Di}" in manual_bib
    assert "journaltitle = {Lishi yanjiu}" in manual_bib
    assert "@article{Hu1964Chiakuwen,\n  author       = {Hu, Houxuan},\n  usera        = {胡厚宣},\n  year         = {1964},\n  title        = {Jiaguwen Shangzu niao tuteng de yiji},\n  userb        = {甲骨文商族鳥圖騰的遺跡},\n  journaltitle = {Lishi luncong},\n  userc        = {歷史論叢}," in manual_bib
    assert "journaltitle = {Lishi luncong}" in manual_bib
    assert "userc        = {歷史論叢}" in manual_bib
    assert "title        = {Yindai de cansang he sizhi}" in manual_bib
    assert "journaltitle = {Wenwu}" in manual_bib
    assert "@article{Hu1972aChuichi,\n  author       = {Hu, Houxuan},\n  usera        = {胡厚宣},\n  year         = {1972},\n  title        = {Zhui ji},\n  userb        = {追記},\n  journaltitle = {KK},\n  userc        = {考古}," in manual_bib
    assert "title        = {Yindai de yuexing}" in manual_bib
    assert "@article{Hu1973Yintai,\n  author       = {Hu, Houxuan},\n  usera        = {胡厚宣},\n  year         = {1973},\n  title        = {Yindai de yuexing},\n  userb        = {殷代的刖刑},\n  journaltitle = {KK},\n  userc        = {考古}," in manual_bib
    assert "title        = {Lintzu Sunshi jiucang jiagu wenzi kaobian}" in manual_bib
    assert "title        = {Jiaguwen suojian Yindai nuli de fan yapo douzheng}" in manual_bib
    assert "author      = {Hu, Xu}" in manual_bib
    assert "title       = {Pufa xiangkao}" in manual_bib
    assert "booktitle   = {Qinding siku quanshu zibu}" in manual_bib

    assert "title        = {Pu-tz'u tsa-li}" not in manual_bib
    assert "title        = {Shih tzu-yung tzu-yu}" not in manual_bib
    assert "title       = {Wu Ting shih wu-chung chi-shih k'e-tz'u k'ao}" not in manual_bib
    assert "booktitle   = {Chia-ku-hsueh Shang-shih lun-ts'ung ch'u-chi}" not in manual_bib
    assert "title       = {Yin-tai pu-kuei chih lai-yuan}" not in manual_bib
    assert "title       = {Chia-ku-hsueh hsii-lun}" not in manual_bib
    assert "booktitle   = {Chia-ku-hsueh Shang-shih lun-ts'ung erh-chi}" not in manual_bib
    assert "title        = {Pu-tz'u t'ung-wen li}" not in manual_bib
    assert "title        = {Pu-tz'u chi-shih wen-tzu shih-kuan ch'ien-ming li}" not in manual_bib
    assert "title       = {Wu-shih-nien chia-ku-wen fa-hsien ti tsung-chieh}" not in manual_bib
    assert "title       = {Wu-shih-nien chia-ku-hsueh lun-chu-mu}" not in manual_bib
    assert "title       = {Yin-hsu fa-chueh}" not in manual_bib
    assert "title        = {Yin pu-tz'u chung ti Shang Ti ho Wang Ti}" not in manual_bib
    assert "journaltitle = {Li-shih yen-chiu}" not in manual_bib
    assert "title        = {Chia-ku-wen Shang-tsu niao t'u-t'eng ti yi-chih}" not in manual_bib
    assert "journaltitle = {Li-shih lun-ts'ung}" not in manual_bib
    assert "title        = {Yin-tai ti ts'an-sang ho ssu-chih}" not in manual_bib
    assert "title        = {Chui chi}" not in manual_bib
    assert "title        = {Yin-tai ti yueh-hsing}" not in manual_bib
    assert "title        = {Lin-tzu Sun-shih chiu ts'ang chia-ku wen-tzu k'ao-pien}" not in manual_bib
    assert "title        = {Chia-ku-wen so-chien Yin-tai nu-li ti fan ya-p'o tou-cheng}" not in manual_bib
    assert "author      = {Hu, Hsu}" not in manual_bib
    assert "title       = {Pu-fa hsiang-k'ao}" not in manual_bib
    assert "booktitle   = {Ch'in-ting ssu-k'u ch'uan-shu tzu-pu}" not in manual_bib


def test_dh_pinyin_audit_updates_tail_fh_entries():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author      = {Fan, Xiangyong}" in manual_bib
    assert "title       = {Guben zhushu jinian jijiao dingbu}" in manual_bib
    assert "author      = {Wang, Xiang}" in manual_bib
    assert "shortauthor = {Fuyin}" in manual_bib
    assert "title       = {Fushi Yinqi zhengwen}" in manual_bib
    assert "location    = {Tianjin}" in manual_bib
    assert "author       = {Jiang, Hong}" in manual_bib
    assert "shortauthor  = {Hong}" in manual_bib
    assert "title        = {Panlongcheng yu Shangchao de nantu}" in manual_bib
    assert "author       = {Xia, Nai}" in manual_bib
    assert "title        = {Tan-14 ceding niandai he Zhongguo shiqian kaoguxue}" in manual_bib
    assert "author       = {Xinhua she}" in manual_bib
    assert "title        = {Shaanxi Zhouyuan faxian zhengui jiagu}" in manual_bib
    assert "journaltitle = {Dagong bao}" in manual_bib
    assert "title        = {Jiaguwen suojian Shangzu niao tuteng de xin zhengju}" in manual_bib

    assert "author      = {Fan, Hsiang-yung}" not in manual_bib
    assert "title       = {Ku-pen chu-shu chi-nien chi-chiao ting-pu}" not in manual_bib
    assert "author      = {Wang, Hsiang}" not in manual_bib
    assert "shortauthor = {Fu-yin}" not in manual_bib
    assert "title       = {Fu-shih Yin-ch'i cheng-wen}" not in manual_bib
    assert "location    = {Tientsin}" not in manual_bib
    assert "author       = {Chiang, Hung}" not in manual_bib
    assert "shortauthor  = {Hung}" not in manual_bib
    assert "title        = {P'an-lung-ch'eng yu Shang-ch'ao ti nan-t'u}" not in manual_bib
    assert "author       = {Hsia, Nai}" not in manual_bib
    assert "title        = {T'an-14 ts'e-ting nien-tai ho Chung-kuo shih-ch'ien k'ao-ku-hsueh}" not in manual_bib
    assert "author       = {Hsinhua-she}" not in manual_bib
    assert "title        = {Shen-hsi Chou-yuan fa-hsien chen-kuei chia-ku}" not in manual_bib
    assert "journaltitle = {Ta kung-pao}" not in manual_bib
    assert "title        = {Chia-ku-wen so-chien Shang-tsu niao t'u-t'eng ti hsin cheng-chu}" not in manual_bib


def test_ik_pinyin_audit_updates_rao_and_rong_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Rao, Zongyi}" in manual_bib
    assert "shortauthor  = {Rao}" in manual_bib
    assert "shortauthor = {Rao}" in manual_bib
    assert "title        = {Haiwai jiagulu yiyu}" in manual_bib
    assert "userb        = {海外甲骨錄遺}" in manual_bib
    assert "title       = {Yindai zhenbu renwu tongkao}" in manual_bib
    assert "userb        = {殷代貞卜人物通考}" in manual_bib
    assert "location    = {Hong Kong}" in manual_bib
    assert "title        = {Yu buchao jishu tuiqiu Yinren duiyu shu de guannian---guibu xiangshu lun}" in manual_bib
    assert "journaltitle = {Zhongyang yanjiuyuan lishi yuyan yanjiusuo waibian}" in manual_bib
    assert "title        = {Lun buci duandai wenti--da Tao Bangnan xiansheng}" in manual_bib
    assert "userb        = {論卜辭斷代問題——答陶邦南先生}" in manual_bib
    assert "author       = {Rong, Geng}" in manual_bib
    assert "title        = {Jiaguxue gaikuang}" in manual_bib
    assert "journaltitle = {Lingnan xuebao}" in manual_bib
    assert "author      = {Rong, Geng}" in manual_bib
    assert "title       = {Jinwenbian}" in manual_bib
    assert "userb        = {金文編}" in manual_bib
    assert "location    = {Beijing}" in manual_bib
    assert "location    = {Nangang}" in manual_bib
    assert "author      = {Rong, Yuan and Rong, Geng}" in manual_bib
    assert "title       = {Jinshishu lumu}" in manual_bib
    assert "usera        = {容媛、容庚}" in manual_bib
    assert "userb        = {金石書錄目}" in manual_bib

    assert "author       = {Jao, Tsung-yi}" not in manual_bib
    assert "shortauthor  = {Jao}" not in manual_bib
    assert "shortauthor = {Jao}" not in manual_bib
    assert "title        = {Hai-wai chia-ku lu-yi}" not in manual_bib
    assert "title       = {Yin-tai chen-pu jen-wu t'ung-k'ao}" not in manual_bib
    assert "title        = {Yu pu-chao chi-shu t'ui-chiu Yin-jen tui-yu shu ti kuan-nien---kuei-pu hsiang-shu lun}" not in manual_bib
    assert "journaltitle = {Chung-yang yen-chiu-yuan li-shih yu-yen yen-chiu-so wai-pien}" not in manual_bib
    assert "title        = {Lun pu-tz'u tuan-tai wen-t'i--ta Tao Pang-nan hsien-sheng}" not in manual_bib
    assert "author       = {Jung, Keng}" not in manual_bib
    assert "title        = {Chia-ku-hsueh kai-k'uang}" not in manual_bib
    assert "journaltitle = {Ling-nan hsueh-pao}" not in manual_bib
    assert "author      = {Jung, Keng}" not in manual_bib
    assert "title       = {Chin-wen-pien}" not in manual_bib
    assert "author      = {Jung, Yuan and Jung, Keng}" not in manual_bib
    assert "title       = {Chin-shih-shu lu-mu}" not in manual_bib


def test_ik_pinyin_audit_updates_early_k_chinese_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Gao, Quxun}" in manual_bib
    assert "title        = {Yinxu chutu zhi niuzhugu kezi}" in manual_bib
    assert (
        "@incollection{Kuo1934Kuchiu,\n"
        "  author      = {Guo, Moruo},\n"
        "  usera        = {郭沫若},\n"
        "  year        = {1934},\n"
        "  title       = {Gujiu kezi zhi yi kaocha},\n"
        "  userb       = {骨臼刻辭之一考察},\n"
    ) in manual_bib
    assert "author       = {Ke, Yiqing}" in manual_bib
    assert "author      = {Guan, Xiechu}" in manual_bib
    assert "title       = {Yinxu jiagu keci de yufa yanjiu}" in manual_bib
    assert "@incollection{Shih1945Hsiaotun,\n  author      = {Shih, Chang-ju},\n  usera       = {石璋如},\n  year        = {1945},\n  title       = {Xiaotun hou wu ci fajue de zhongyao faxian},\n  userb       = {小屯後五次發掘的重要發現},\n  booktitle   = {Liutong bielu shang},\n  userc       = {六同別錄上}," in manual_bib
    assert "author      = {Guo, Moruo}" in manual_bib
    assert "title       = {Gujiu kezi zhi yi kaocha}" in manual_bib
    assert "booktitle   = {Gudai mingke huikao xubian}" in manual_bib
    assert "userc        = {古代銘刻彙考續編}" in manual_bib
    assert "title       = {Liang Zhou jinwenci daxi tulu kaoshi}" in manual_bib
    assert "author       = {Guo, Baojun}" in manual_bib
    assert "@article{KuoBaojun1933Bchu,\n  author       = {Guo, Baojun},\n  usera        = {郭寶鈞},\n  year         = {1933},\n  title        = {B chu fajueji zhi yi},\n  userb        = {B區發掘記之一},\n  journaltitle = {AYFC},\n  userc        = {安陽發掘報告}," in manual_bib
    assert "title        = {B chu fajueji zhi yi}" in manual_bib
    assert "title        = {B chu fajueji zhi er}" in manual_bib
    assert "title        = {Yijiuwulingnian chun Yinxu fajue baogao}" in manual_bib
    assert "journaltitle = {Zhongguo kaogu xuebao}" in manual_bib

    assert "author       = {Kao, Ch'u-hsun}" not in manual_bib
    assert "title        = {Yin-hsu ch'u-t'u chih niu-chu-ku k'e-tz'u}" not in manual_bib
    assert "author       = {Ke, Yi-ch'ing}" not in manual_bib
    assert "author      = {Kuan, Hsieh-ch'u}" not in manual_bib
    assert "title       = {Yin-hsu chia-ku k'e-tz'u ti yu-fa yen-chiu}" not in manual_bib
    assert "author      = {Kuo, Mo-jo}" not in manual_bib
    assert "title       = {Ku-chiu k'e-tz'u chih yi k'ao-ch'a}" not in manual_bib
    assert "booktitle   = {Ku-tai ming-k'e hui-k'ao hsu-pien}" not in manual_bib
    assert "title       = {Liang-Chou chin-wen-tz'u ta-hsi t'u-lu k'ao-shih}" not in manual_bib
    assert "author       = {Kuo, Pao-chun}" not in manual_bib
    assert "title        = {B ch'u fa-chueh-chi chih yi}" not in manual_bib
    assert "title        = {B ch'u fa-chueh-chi chih erh}" not in manual_bib
    assert "title        = {Yi-chiu-wu-ling-nien ch'un Yin-hsu fa-chueh pao-kao}" not in manual_bib


def test_ik_pinyin_audit_updates_li_chinese_scholarship_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Li, Chengfu}" in manual_bib
    assert "title        = {Guwenzishang zhi tiandi xiangyi suyuan}" in manual_bib
    assert "author       = {Li, Jingtan}" in manual_bib
    assert "title        = {Yudong Shangqiu Yongcheng diaocha ji Caolutai Heigudui Caoqiao sanchu xiao fajue}" in manual_bib
    assert "author       = {Li, Fanggui}" in manual_bib
    assert "title        = {Shanggu yin yanjiu}" in manual_bib
    assert "journaltitle = {Qinghua xuebao}" in manual_bib
    assert "author      = {Li, Xiaoding}" in manual_bib
    assert "author       = {Li, Xiaoding}" in manual_bib
    assert "title       = {Jiagu wenzi jishi}" in manual_bib
    assert "series      = {Zhongyang yanjiuyuan lishi yuyan yanjiusuo zhuankan zhi wushi}" in manual_bib
    assert "userc        = {中央研究院歷史語言研究所專刊之五十}" in manual_bib
    assert "location    = {Nangang}" in manual_bib
    assert "title        = {Cong liushu de guandian kan jiagu wenzi}" in manual_bib
    assert "journaltitle = {Nanyang daxue xuebao}" in manual_bib
    assert "title        = {Zhongguo wenzi de yuanshi yu yanbian}" in manual_bib
    assert "author       = {Li, Xueqin}" in manual_bib
    assert "title        = {Tan Anyang Xiaotun yiwai chutu de youzi jiagu}" in manual_bib
    assert "title        = {Ping Chen Mengjia Yinxu buci zongshu}" in manual_bib
    assert "title        = {Di Yi shidai de feiwang buci}" in manual_bib
    assert "title        = {Guanyu jiagu de jichu zhishi}" in manual_bib
    assert "journaltitle = {Lishi jiaoxue}" in manual_bib
    assert "author      = {Li, Yanong}" in manual_bib
    assert "title       = {Yindai shehui shenghuo}" in manual_bib

    assert "author       = {Li, Cheng-fu}" not in manual_bib
    assert "title        = {Ku wen-tzu-shang chih t'ien-ti hsiang-yi su-yuan}" not in manual_bib
    assert "author       = {Li, Ching-tan}" not in manual_bib
    assert "title        = {Yu-tung Shang-ch'iu Yung-ch'eng tiao-ch'a chi Tsao-lu-t'ai Hei-ku-tui Ts'ao-ch'iao san-ch'u hsiao fa-chueh}" not in manual_bib
    assert "author       = {Li, Fang-kuei}" not in manual_bib
    assert "title        = {Shang-ku yin yen-chiu}" not in manual_bib
    assert "journaltitle = {Ch'ing-hua hsueh-pao}" not in manual_bib
    assert "author      = {Li, Hsiao-ting}" not in manual_bib
    assert "author       = {Li, Hsiao-ting}" not in manual_bib
    assert "title       = {Chia-ku wen-tzu chi-shih}" not in manual_bib
    assert "series      = {Chung-yang yen-chiu-yuan li-shih yu-yen yen-chiu-so chuan-k'an chih wu-shih}" not in manual_bib
    assert "title        = {Ts'ung liu-shu ti kuan-tien k'an chia-ku wen-tzu}" not in manual_bib
    assert "journaltitle = {Nan-yang ta-hsueh hsueh-pao}" not in manual_bib
    assert "title        = {Chung-kuo wen-tzu ti yuan-shih yu yen-pien}" not in manual_bib
    assert "author       = {Li, Hsueh-ch'in}" not in manual_bib
    assert "title        = {T'an An-yang Hsiao-t'un yi-wai ch'u-t'u ti yu-tzu chia-ku}" not in manual_bib
    assert "title        = {P'ing Ch'en Meng-chia Yin-hsu pu-tz'u tsung-shu}" not in manual_bib
    assert "title        = {Ti Yi shih-tai ti fei-wang pu-tz'u}" not in manual_bib
    assert "title        = {Kuan-yu chia-ku ti chi-ch'u chih-shih}" not in manual_bib
    assert "journaltitle = {Li-shih chiao-hsueh}" not in manual_bib
    assert "author      = {Li, Ya-nung}" not in manual_bib
    assert "title       = {Yin-tai she-hui sheng-huo}" not in manual_bib


def test_ik_pinyin_audit_updates_late_l_chinese_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Lao, Gan}" in manual_bib
    assert (
        "@article{Lao1957Shih,\n"
        "  author       = {Lao, Gan},\n"
        "  usera        = {勞榦},\n"
        "  year         = {1957},\n"
        "  title        = {Shizi de jiegou ji shiguan de yuanshi zhiwu},\n"
        "  userb        = {史字的結構及史官的原始職務},"
    ) in manual_bib
    assert "title        = {Zhouchu niandai wenti yu yuexiang wenti de xin kanfa}" in manual_bib
    assert "journaltitle = {Xianggang Zhongwen daxue Zhongguo wenhua yanjiusuo xuebao}" in manual_bib
    assert "author      = {Li, Shi}" in manual_bib
    assert "title       = {Yu jiagu quanzheng santai keji caijing yu guanli}" in manual_bib
    assert "author      = {Li, Yan}" in manual_bib
    assert "author       = {Li, Yan}" in manual_bib
    assert "title       = {Yanzhai jiagu zhanlan}" in manual_bib
    assert "title        = {Buci zhenren He zai tongbanzhong zhi yiti}" in manual_bib
    assert "journaltitle = {Lianhe shuyuan xuebao}" in manual_bib
    assert "title        = {Du 'Yinxu buci zonglei' yu Dao Bangnan boshi shangque}" in manual_bib
    assert "title        = {Beimei suojian jiagu xuancui kaoshi}" in manual_bib
    assert "title       = {Du 'guiban wenli yanjiu' (daixu)}" in manual_bib
    assert "booktitle   = {Guiban wenli yanjiu}" in manual_bib
    assert "author       = {Lin, Sheng}" in manual_bib
    assert "title        = {Ji Yi, Qiang, Naxi zu de 'yanggu bu' jilu}" in manual_bib
    assert "title        = {Yunnan Yongsheng xian Yizu (Talu ren) 'yanggu bu' de diaocha he yanjiu}" in manual_bib

    assert "author       = {Lao, Kan}" not in manual_bib
    assert "title        = {Shih-tzu ti chieh-kou chi shih-kuan ti yuan-shih chih-wu}" not in manual_bib
    assert "title        = {Chou-ch'u nien-tai wen-t'i yu yueh-hsiang wen-t'i ti hsin k'an-fa}" not in manual_bib
    assert "journaltitle = {Hsiang-kang Chung-wen ta-hsueh Chung-kuo wen-hua yen-chiu-so hsueh-pao}" not in manual_bib
    assert "author      = {Li, Shih}" not in manual_bib
    assert "title       = {Yu chia-ku ch'uan-cheng san-tai k'e-chi ts'ai-ching yu kuan-li}" not in manual_bib
    assert "title       = {Yen-chai chia-ku chan-lan}" not in manual_bib
    assert "title        = {Pu-tz'u chen-jen Ho tsai t'ung-pan-chung chih yi-t'i}" not in manual_bib
    assert "journaltitle = {Lien-ho shu-yuan hsueh-pao}" not in manual_bib
    assert "title        = {Tu 'Yin-hsu pu-tz'u tsung-lei' yu Tao Pang-nan po-shih shang-chueh}" not in manual_bib
    assert "title        = {Pei-Mei so-chien chia-ku hsuan-ts'ui k'ao-shih}" not in manual_bib
    assert "title       = {Tu 'kuei-pan wen-li yen-chiu' (tai-hsu)}" not in manual_bib
    assert "booktitle   = {Kuei-pan wen-li yen-chiu}" not in manual_bib
    assert "author       = {Lin Sheng}" not in manual_bib
    assert "title        = {Chi Yi, Ch'iang, Na-hsi tsu ti 'yang ku-pu' chi lu}" not in manual_bib
    assert "title        = {Yun-nan Yung-sheng-hsien Yi-tsu (T'a-lu jen) 'yang ku-pu' ti tiao-ch'a ho yen-chiu}" not in manual_bib


def test_ik_pinyin_audit_updates_ling_liu_luo_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Ling, Shunsheng}" in manual_bib
    assert "title        = {Songhuajiang xiayou de Hezhe zu}" in manual_bib
    assert "journaltitle = {Guoli zhongyang yanjiuyuan lishi yuyan yanjiusuo dankan jiazhong}" in manual_bib
    assert "title        = {Zhongguo gudai de guiji wenhua}" in manual_bib
    assert "author       = {Liu, Yuanlin}" in manual_bib
    assert "title        = {Yinxu 'gujian' ji qi youguan wenti}" in manual_bib
    assert "title        = {Bugu de gongzhi jishu yanjin guocheng zhi tantao}" in manual_bib
    assert "author      = {Luo, Zhenyu}" in manual_bib
    assert "title       = {Yinxu shuqi kaoshi}" in manual_bib
    assert "title        = {Goso bokuji ni tsuite no kosatsu}" in manual_bib
    assert "journaltitle = {Chutetsu bungaku kaiho}" in manual_bib

    assert "author       = {Ling Shun-sheng}" not in manual_bib
    assert "title        = {Sung-hua-chiang hsia-yu ti Ho-che tsu}" not in manual_bib
    assert "journaltitle = {Kuo-li chung-yang yen-chiu-yuan li-shih yu-yen yen-chiu-so tan-k'an chia-chung}" not in manual_bib
    assert "title        = {Chung-kuo ku-tai ti kuei-chi wen-hua}" not in manual_bib
    assert "author       = {Liu Yuan-lin}" not in manual_bib
    assert "title        = {Yin-hsu 'ku-chien' chi ch'i yu-kuan wen-t'i}" not in manual_bib
    assert "title        = {Pu-ku ti kung-chih chi-shu yen-chin kuo-ch'eng chih t'an-t'ao}" not in manual_bib
    assert "author      = {Lo Chen-yu}" not in manual_bib
    assert "title       = {Yin-hsu shu-ch'i k'ao-shih}" not in manual_bib


def test_ik_pinyin_audit_updates_late_l_tail_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Tong, Enzheng and Zhang, Shengkai and Chen, Jingchun}" in manual_bib
    assert "title        = {Guanyu shiyong dianzi jisuanji zhuihe Shangdai bujia suipian de chubu baogao}" in manual_bib
    assert "author       = {Yu, Haoliang}" in manual_bib
    assert "shortauthor  = {Haoliang}" in manual_bib
    assert "title        = {Shuo 'yin' zi}" in manual_bib
    assert "author       = {Lu, Shixian}" in manual_bib
    assert "shortauthor  = {Shixian}" in manual_bib
    assert "title        = {Yinqi xinquan zhi er: shipian}" in manual_bib
    assert "journaltitle = {Donghai xuebao}" in manual_bib
    assert "author      = {Long, Yuchun}" in manual_bib
    assert "title       = {Shi jiaguwen chong zi jianjie xizun}" in manual_bib
    assert "userb       = {釋甲骨文虫字兼解犧尊}" in manual_bib
    assert "booktitle   = {Shen Gangbo xiansheng baji rongqing lunwenji}" in manual_bib

    assert "author       = {T'ung, En-cheng and Chang, Sheng-k'ai and Ch'en, Ching-ch'un}" not in manual_bib
    assert "title        = {Kuan-yu shih-yung tien-tzu chi-suan-chi chui-ho Shang-tai pu-chia sui-p'ien ti ch'u-pu pao-kao}" not in manual_bib
    assert "author       = {Yu, Hao-liang}" not in manual_bib
    assert "shortauthor  = {Hao-liang}" not in manual_bib
    assert "title        = {Shuo 'yin' tzu}" not in manual_bib
    assert "author       = {Lu, Shih-hsien}" not in manual_bib
    assert "shortauthor  = {Shih-hsien}" not in manual_bib
    assert "title        = {Yin-ch'i hsin-ch'uan chih erh: shih pien}" not in manual_bib
    assert "journaltitle = {Tung-hai hsueh-pao}" not in manual_bib
    assert "author      = {Lung, Yu-ch'un}" not in manual_bib
    assert "title       = {Shih chia-ku-wen hsi(?) tzu chien-chieh hsi-tsun}" not in manual_bib
    assert "booktitle   = {Shen Kang-po hsien-sheng pa-chih jung-ch'ing lun-wen-chi}" not in manual_bib


def test_ik_pinyin_audit_resolves_mixed_li_ji_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Li, Ji}" in manual_bib
    assert "author      = {Li, Ji}" in manual_bib
    assert "title        = {Minguo shiba nian qiuji fajue Yinxu zhi jingguo ji qi zhongyao faxian}" in manual_bib
    assert "title        = {Anyang zuijin fajue baogao ji liuci gongzuo zhi zong guji}" in manual_bib
    assert "title       = {Chengziyai}" in manual_bib
    assert "location    = {Nanjing}" in manual_bib
    assert "title        = {Ba Yantang zixu}" in manual_bib
    assert "journaltitle = {Zhongguo kaogu xuebao}" in manual_bib
    assert "editor      = {Chen, Hao}" in manual_bib
    assert "title       = {Liji jishuo}" in manual_bib

    assert "@book{LiChi1956Chengtzuyai," in manual_bib
    assert "author      = {Li, Chi and Liang, Ssu-yang and Tung, Tso-pin}" in manual_bib
    assert "@book{LiChi1977Anyang," in manual_bib
    assert "title       = {Anyang}" in manual_bib

    assert "author      = {Li, Chi}" in manual_bib
    assert "title        = {Min-kuo shih-pa-nien ch'iu-chi fa-chueh Yin-hsu chih ching-kuo chi ch'i chung-yao fa-hsien}" not in manual_bib
    assert "title        = {An-yang tsui-chin fa-chueh pao-kao chi liu-tz'u kung-tso chih tsung ku-chi}" not in manual_bib
    assert "title       = {Ch'eng-tzu-yai}" not in manual_bib
    assert "title        = {Pa Yen-t'ang tzu-hsu}" not in manual_bib
    assert "editor      = {Ch'en, Hao}" not in manual_bib
    assert "title       = {Li-chi chi-shuo}" not in manual_bib


def test_ik_pinyin_audit_finishes_remaining_i_l_residue():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Guo, Moruo}" in manual_bib
    assert "title        = {Anyang xin chutu de niujiagu ji qi keci}" in manual_bib
    assert "title        = {Gudai wenzi zhi bianzheng de fazhan}" in manual_bib
    assert "title        = {Yinxu kaogu fajue de youyi zhongyao xin shouhuo---Xiaotun faxian yizuo baocun wanzheng de Yindai wangshi muzang}" in manual_bib
    assert "title        = {Anyang Yinxu wuhao muzang tan jiyao}" in manual_bib
    assert "title        = {Yijiuwuwunian qiu Anyang Xiaotun Yinxu de fajue}" in manual_bib
    assert "author       = {Hu, Houxuan}" in manual_bib
    assert "shortauthor  = {Liulu}" in manual_bib
    assert "title        = {Jiagu liulu}" in manual_bib
    assert "booktitle    = {Jiaguxue Shangshi luncong sanji}" in manual_bib
    assert "location     = {Chengdu}" in manual_bib

    assert "author       = {Kuo, Mo-jo}" not in manual_bib
    assert "title        = {An-yang hsin ch'u-tu ti niu-chia-ku chi ch'i k'e-tz'u}" not in manual_bib
    assert "title        = {Ku-tai wen-tzu chih pien-cheng ti fa-chan}" not in manual_bib
    assert "title        = {Yin-hsu k'ao-ku fa-chueh ti yu-yi chung-yao hsin shou-huo---Hsiao-t'un fa-hsien yi-tso pao-ts'un wan-cheng ti Yin-tai wang-shih mu-tsang}" not in manual_bib
    assert "title        = {An-yang Yin-hsu wu-hao mu-tso t'an chi-yao}" not in manual_bib
    assert "title        = {Yi-chiu-wu-wu-nien ch'iu An-yang Hsiao-t'un Yin-hsu ti fa-chueh}" not in manual_bib
    assert "author       = {Hu, Hou-hsuan}" not in manual_bib
    assert "shortauthor  = {Liu-lu}" not in manual_bib
    assert "title        = {Chia-ku liu-lu}" not in manual_bib
    assert "booktitle    = {Chia-ku-hsueh Shang-shih lun-ts'ung san-chi}" not in manual_bib
    assert "location     = {Ch'eng-tu}" not in manual_bib


def test_late_y_pinyin_audit_normalizes_chinese_y_cluster():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author       = {Yang, Zhongjian and Liu, Dongsheng}" in manual_bib
    assert "title        = {Anyang Yinxu zhi buru dongwu qun buyi}" in manual_bib
    assert "journaltitle = {Zhongguo kaogu xuebao}" in manual_bib
    assert "author       = {Yang, Xizhang and Yang, Baocheng}" in manual_bib
    assert "title        = {Cong Shangdai jisi keng kan Shangdai nuli shehui de rensheng}" in manual_bib
    assert "author      = {Ye, Yusen}" in manual_bib
    assert "title       = {Yinqi gouchen}" in manual_bib
    assert "title       = {Yinxu shuqi qianbian jishi}" in manual_bib
    assert "author       = {Yan, Yiping}" in manual_bib
    assert "title        = {Jiaguwen duandai yanjiu xinli}" in manual_bib
    assert "journaltitle = {Zhongguo wenzi}" in manual_bib
    assert "author       = {Yin, Huanzhang and Zhang, Chengxiang}" in manual_bib
    assert "title        = {Jiangsu Peixian Liulin xinshiqi shidai yizhi diyici fajue}" in manual_bib
    assert "author      = {Yu, Xingwu}" in manual_bib
    assert "title       = {Shuangjianchi Yinqi pinzhi}" in manual_bib
    assert "author       = {Yu, Yongliang}" in manual_bib
    assert "title        = {Xinhuo buci xieben ba}" in manual_bib

    assert "author       = {Yang, Chung-chien and Liu, Tung-sheng}" not in manual_bib
    assert "title        = {An-yang Yin-hsu chih pu-ju tung-wu ch'un pu-yi}" not in manual_bib
    assert "author       = {Yang, Hsi-chang and Yang, Pao-ch'eng}" not in manual_bib
    assert "title        = {Ts'ung Shang-tai chi-ssu k'eng k'an Shang-tai nu-li she-hui ti jen-sheng}" not in manual_bib
    assert "author      = {Yeh, Yu-sen}" not in manual_bib
    assert "title       = {Yin-ch'i kou-ch'en}" not in manual_bib
    assert "title       = {Yin-hsu shu-ch'i ch'ien-pien chi-shih}" not in manual_bib
    assert "author       = {Yen, Yi-p'ing}" not in manual_bib
    assert "title        = {Chia-ku-wen tuan-tai yen-chiu hsin-li}" not in manual_bib
    assert "author       = {Yin, Huan-chang and Chang, Cheng-hsiang}" not in manual_bib
    assert "title        = {Chiang-su P'ei-hsien Liu-lin hsin-shih-ch'i shih-tai yi-chih ti-yi-tz'u fa-chueh}" not in manual_bib
    assert "author      = {Yu, Hsing-wu}" not in manual_bib
    assert "title       = {Shuang-chien-ch'ih Yin-ch'i p'in-chih}" not in manual_bib
    assert "author       = {Yu, Yung-liang}" not in manual_bib
    assert "title        = {Hsin-huo pu-tz'u hsieh-pen pa}" not in manual_bib


def test_late_u_z_pinyin_audit_catches_adjacent_singletons():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "author      = {Wu, Ze}" in manual_bib
    assert "title       = {Gudai shi: Yindai nulizhi shehuishi}" in manual_bib
    assert "author       = {Yi, Gong}" in manual_bib
    assert "title        = {Mantan jiagu wenzi de shufa}" in manual_bib

    assert "author      = {Wu, Tse}" not in manual_bib
    assert "title       = {Ku-tai shih: Yin-tai nu-li-chih she-hui-shih}" not in manual_bib
    assert "author       = {Yi, Kung}" not in manual_bib
    assert "title        = {Man-t'an chia-ku wen-tzu ti shu-fa}" not in manual_bib


def test_late_u_z_pinyin_audit_normalizes_ww_wang_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "title        = {Jiangxi Qingjiang Wucheng Shangdai yizhi fajue jianbao}" in manual_bib
    assert "author      = {Wang, Guowei}" in manual_bib
    assert "title       = {Guantang jilin}" in manual_bib
    assert "location    = {Wucheng, Zhejiang}" in manual_bib
    assert "author      = {Wang, Ziyu}" in manual_bib
    assert "title       = {Jiaguwen}" in manual_bib
    assert "booktitle   = {Xu Anyang xianzhi}" in manual_bib
    assert "location    = {Beiping}" in manual_bib

    assert "title        = {Chiang-hsi Ch'ing-chiang Wu-ch'eng Shang-tai yi-chih fa-chueh chien-pao}" not in manual_bib
    assert "author      = {Wang, Kuo-wei}" not in manual_bib
    assert "title       = {Kuan-t'ang chi-lin}" not in manual_bib
    assert "location    = {Wu-ch'eng, Chekiang}" not in manual_bib
    assert "author      = {Wang, Tzu-yu}" not in manual_bib
    assert "title       = {Chia-ku-wen}" not in manual_bib
    assert "booktitle   = {Hsu An-yang hsien-chih}" not in manual_bib


def test_bibliography_bilingual_fields_use_curated_user_slots():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "usera        = {安志敏}" in manual_bib
    assert "userb        = {一九五二年秋季鄭州二里岡發掘記}" in manual_bib
    assert "userb        = {鄭州市人民公園附近的殷代遺存}" in manual_bib
    assert "userc        = {文物參考資料}" in manual_bib
    assert "usera       = {中國科學院考古研究所}" in manual_bib
    assert "userb       = {甲骨文編}" in manual_bib
    assert "usera        = {郭寶鈞}" in manual_bib
    assert "userb        = {一九五〇年春殷墟發掘報告}" in manual_bib
    assert "userc        = {中國考古學報}" in manual_bib
    assert "usera        = {勞榦}" in manual_bib
    assert "userb        = {周初年代問題與月相問題的新看法}" in manual_bib
    assert "userc        = {香港中文大學中國文化研究所學報}" in manual_bib
    assert "userb        = {第七次殷墟發掘：戊區工作報告}" in manual_bib
    assert "userb       = {小屯後五次發掘的重要發現}" in manual_bib
    assert "userb        = {小屯C區的墓葬群}" in manual_bib
    assert "userb        = {骨卜與龜卜探源：黑陶與白陶的關係}" in manual_bib
    assert "userb        = {殷墟最近之重要發現，附論小屯地層}" in manual_bib
    assert "userb        = {河南安陽小屯殷墓中的動物遺骸}" in manual_bib
    assert "userc        = {國立臺灣大學文史哲學報}" in manual_bib
    assert "usera       = {石璋如}" in manual_bib
    assert "userb       = {小屯第一本：遺址的發現與發掘，乙編：建築遺存}" in manual_bib
    assert "userb       = {十三經注疏}" in manual_bib
    assert "usera       = {董作賓}" in manual_bib
    assert "userb        = {甲骨文材料的總估計}" in manual_bib
    assert "userb        = {新獲卜辭寫本後記}" in manual_bib
    assert "userb        = {商代龜卜之推測}" in manual_bib
    assert "userb        = {新獲卜辭寫本}" in manual_bib
    assert "userb        = {民國十七年十月試掘安陽小屯報告書}" in manual_bib
    assert "userb        = {大龜四版考釋}" in manual_bib
    assert "userb        = {安陽侯家莊出土之甲骨文字}" in manual_bib
    assert "userc        = {田野考古學報}" in manual_bib
    assert "userb        = {古文例}" in manual_bib
    assert "userb       = {小屯第二本：殷墟文字：甲編}" in manual_bib
    assert "userb        = {殷曆譜後記}" in manual_bib
    assert "userb        = {殷墟文字乙編序}" in manual_bib
    assert "userb       = {殷曆譜}" in manual_bib
    assert "userb        = {甲骨文斷代研究例}" in manual_bib
    assert "userb        = {殷墟文字甲編自序}" in manual_bib
    assert "userb        = {論商人以十日為名}" in manual_bib
    assert "userb        = {中國古代文化的認識}" in manual_bib
    assert "userb        = {武王伐紂年月日今考}" in manual_bib
    assert "userb        = {中國古曆與世界古曆}" in manual_bib
    assert "userb        = {殷曆譜的自我檢討}" in manual_bib
    assert "userb        = {大龜甲骨絕非象骨之證}" in manual_bib
    assert "userb        = {殷墟文字乙編摹寫本事例四續}" in manual_bib
    assert "userb        = {殷墟文字乙編摹寫本事例續十一}" in manual_bib
    assert "userb       = {甲骨學六十年}" in manual_bib
    assert "userb       = {董作賓學術論著}" in manual_bib
    assert "usera       = {董作賓、黃然偉}" in manual_bib
    assert "userb       = {續甲骨年表}" in manual_bib
    assert "usera        = {董作賓、金祥恆}" in manual_bib
    assert "userb        = {本系所藏甲骨文字}" in manual_bib
    assert "userc        = {國立臺灣大學考古人類學刊}" in manual_bib
    assert "usera       = {丁山}" in manual_bib
    assert "userb       = {甲骨文所見氏族及其制度}" in manual_bib
    assert "usera        = {鄭德坤}" in manual_bib
    assert "userb        = {藁城台西商代遺址發現的陶器文字}" in manual_bib
    assert "userc        = {文物}" in manual_bib
    assert "usera        = {陳夢家}" in manual_bib
    assert "userb        = {甲骨斷代學甲編}" in manual_bib
    assert "userc        = {燕京學報}" in manual_bib
    assert "userb        = {解放後甲骨的新資料和整理研究}" in manual_bib
    assert "userb        = {商殷與夏周的年代問題}" in manual_bib
    assert "userc        = {歷史研究}" in manual_bib
    assert "usera       = {河南省文化處文物工作隊}" in manual_bib
    assert "userb       = {鄭州二里岡}" in manual_bib
    assert "usera       = {金祥恆}" in manual_bib
    assert "userb       = {續甲骨文編}" in manual_bib
    assert "userb        = {釋又正與正}" in manual_bib
    assert "userb        = {甲骨文通借字舉隅}" in manual_bib
    assert "userb        = {甲骨文又字引義考}" in manual_bib
    assert "userb        = {輔仁大學所藏甲骨文字後言}" in manual_bib
    assert "usera        = {徐中舒}" in manual_bib
    assert "userb        = {再論小屯與仰韶}" in manual_bib
    assert "usera        = {徐敬參}" in manual_bib
    assert "userb        = {簡壽堂殷墟文字考釋補正}" in manual_bib
    assert "userc        = {考古學社社刊}" in manual_bib
    assert "usera        = {許進雄}" in manual_bib
    assert "userb        = {釋又}" in manual_bib
    assert "userb        = {對張光直先生的《商王廟號新考》的幾點意見}" in manual_bib
    assert "userb       = {殷卜辭中五種祭祀的研究}" in manual_bib
    assert "userb        = {鑽鑿對卜辭斷代的重要性}" in manual_bib
    assert "userb        = {殷卜辭中五種祭祀研究的新觀念}" in manual_bib
    assert "userb        = {五種祭祀的新觀念與殷曆的探討}" in manual_bib
    assert "userb        = {略談貞人的在職年代}" in manual_bib
    assert "userb        = {談貞人何的年代}" in manual_bib
    assert "userb        = {從常作的配置試分第三與第四期的卜骨}" in manual_bib
    assert "userb       = {卜骨上的鑽鑿形態}" in manual_bib
    assert "usera       = {國立中央研究院歷史語言研究所}" in manual_bib
    assert "userb       = {安陽發掘報告}" in manual_bib
    assert "usera        = {容庚}" in manual_bib
    assert "userb        = {甲骨學概況}" in manual_bib
    assert "userc        = {嶺南學報}" in manual_bib
    assert "usera        = {李方桂}" in manual_bib
    assert "userb        = {上古音研究}" in manual_bib
    assert "userc        = {清華學報}" in manual_bib
    assert "usera       = {李孝定}" in manual_bib
    assert "userb       = {甲骨文字集釋}" in manual_bib
    assert "userb        = {從六書的觀點看甲骨文字}" in manual_bib
    assert "userc        = {南洋大學學報}" in manual_bib
    assert "usera        = {高去尋}" in manual_bib
    assert "userb        = {殷墟出土之牛豬骨刻字}" in manual_bib
    assert "usera       = {管燮初}" in manual_bib
    assert "userb       = {殷墟甲骨刻辭的語法研究}" in manual_bib
    assert "usera       = {黃然偉}" in manual_bib
    assert "userb       = {殷曆考釋}" in manual_bib
    assert "usera        = {張光遠}" in manual_bib
    assert "userb        = {殷商甲骨文字求真（下）}" in manual_bib
    assert "userc        = {公眾雜誌}" in manual_bib
    assert "usera        = {張光直}" in manual_bib
    assert "userb        = {商周青銅器器形裝飾花紋與銘文綜合}" in manual_bib
    assert "userb        = {談王亥與伊尹的祭日並再論殷商王制}" in manual_bib
    assert "userb       = {商周青銅器與銘文的綜合研究}" in manual_bib
    assert "usera        = {張宗董}" in manual_bib
    assert "userb        = {殷墟卜龜之卜兆及其有關問題}" in manual_bib
    assert "userb        = {卜辭龜為月食的新證據}" in manual_bib
    assert "userb       = {小屯第二本：殷墟文字：丙編}" in manual_bib
    assert "userb        = {論成套卜辭}" in manual_bib
    assert "userb        = {甲骨文的發現與骨卜習慣的考證}" in manual_bib
    assert "userb        = {甲文“pu-tsai-ming(?)”一詞的檢討}" in manual_bib
    assert "userb        = {從甲文、金文量詞的應用考察漢語量詞的起源與發展}" in manual_bib
    assert "userc        = {中國語文}" in manual_bib
    assert "userb        = {庫方二氏甲骨卜辭第一五〇六篇辨偽兼論陳氏二祭譜說}" in manual_bib
    assert "usera        = {郭沫若}" in manual_bib
    assert "userb        = {安陽新出土的牛脛骨及其刻辭}" in manual_bib
    assert "userb        = {古代文字之辨證的發展}" in manual_bib
    assert "usera        = {考古}" in manual_bib
    assert "userb        = {殷墟考古發掘的一個重要新收穫——小屯發現一座保存完整的殷代王室墓葬}" in manual_bib
    assert "userb        = {安陽殷墟五號墓葬探記要}" in manual_bib
    assert "userb        = {一九七三年安陽小屯南地發掘簡報}" in manual_bib
    assert "usera        = {饒宗頤}" in manual_bib
    assert "userb        = {由卜兆基數推求殷人對於數的觀念——龜卜象數論}" in manual_bib
    assert "usera        = {考古學報}" in manual_bib
    assert "userb        = {一九五五年秋安陽小屯殷墟的發掘}" in manual_bib
    assert "usera        = {李成甫}" in manual_bib
    assert "userb        = {古文字上之天地象義溯源}" in manual_bib
    assert "usera        = {李濟}" in manual_bib
    assert "userb        = {民國十八年秋季發掘殷墟之經過及其重要發現}" in manual_bib
    assert "userb        = {跋彥堂自序}" in manual_bib
    assert "userb        = {安陽最近發掘報告及六次工作之總估計}" in manual_bib
    assert "userb        = {豫東商邱永城調查及草廬台黑古堆草橋三處小發掘}" in manual_bib
    assert "userb        = {中國文字的原始與演變}" in manual_bib
    assert "usera        = {李學勤}" in manual_bib
    assert "userb        = {談安陽小屯以外出土的有字甲骨}" in manual_bib
    assert "userb        = {評陳夢家《殷墟卜辭綜述》}" in manual_bib
    assert "userb        = {帝乙時代的非王卜辭}" in manual_bib
    assert "userb        = {關於甲骨的基礎知識}" in manual_bib
    assert "userb        = {卜辭貞人何在銅盤中的異體}" in manual_bib
    assert "userb        = {讀《殷墟卜辭總類》與島邦男博士商榷}" in manual_bib
    assert "userb        = {北美所見甲骨選粹考釋}" in manual_bib
    assert "userc        = {香港中文大學中國文化研究所學報}" in manual_bib
    assert "usera        = {劉源林}" in manual_bib
    assert "userb        = {殷墟「骨鑑」及其有關問題}" in manual_bib
    assert "usera        = {凌純聲}" in manual_bib
    assert "userb        = {松花江下游的赫哲族}" in manual_bib
    assert "usera       = {羅振玉}" in manual_bib
    assert "userb       = {殷墟書契考釋}" in manual_bib
    assert "usera        = {楊鍾健、劉東生}" in manual_bib
    assert "userb        = {安陽殷墟之哺乳動物群補遺}" in manual_bib
    assert "usera       = {葉玉森}" in manual_bib
    assert "userb       = {殷墟書契前編集釋}" in manual_bib
    assert "usera        = {嚴一萍}" in manual_bib
    assert "userb        = {甲骨文斷代研究新例}" in manual_bib
    assert "userb        = {關於文武丁時代一片附甲的兩種綴合}" in manual_bib
    assert "userb        = {甲骨研究辨偽助例}" in manual_bib
    assert "userb        = {關於戰後殷墟出土的新大龜七版}" in manual_bib
    assert "userb        = {說「又」}" in manual_bib
    assert "userb        = {甲骨卜辭綴集中孫氏藏甲骨的真偽問題}" in manual_bib
    assert "userb       = {甲骨古文字研究}" in manual_bib
    assert "usera        = {嚴雲}" in manual_bib
    assert "userb        = {商代卜辭中的業主史料}" in manual_bib
    assert "usera        = {于省吾}" in manual_bib
    assert "userb        = {從甲骨文看商代的農田耕治}" in manual_bib
    assert "userb        = {漫談甲骨文字的書法}" in manual_bib
    assert "userb        = {甲骨六錄}" in manual_bib
    assert "userb        = {殷契新詮之二：釋篇}" in manual_bib
    assert "usera        = {丁山}" in manual_bib
    assert "userb        = {釋豕}" in manual_bib
    assert "userb        = {契文獸類及獸形字釋}" in manual_bib
    assert "userb        = {安陽小屯南地發現的「對組卜甲」——兼論「對組卜辭」的時代及其相關問題}" in manual_bib
    assert "usera        = {屈萬里}" in manual_bib
    assert "@article{Chu1948Shihfa,\n  author       = {Qu, Wanli},\n  usera        = {屈萬里},\n  year         = {1948},\n  title        = {Shifa lanshang yu Yindai lun},\n  userb        = {謚法濫觴於殷代論}," in manual_bib
    assert "@article{Chu1960Yuehyi,\n  author       = {Qu, Wanli},\n  usera        = {屈萬里}," in manual_bib
    assert "@article{Chu1960Yuehyi,\n  author       = {Qu, Wanli},\n  usera        = {屈萬里},\n  year         = {1960},\n  title        = {Yueyi jigu},\n  userb        = {岳義稽古},\n  journaltitle = {Qinghua xuebao},\n  userc        = {清華學報}," in manual_bib
    assert "userb        = {岳義稽古}" in manual_bib
    assert "userb        = {釋河}" in manual_bib
    assert "userb       = {小屯第二本：殷墟文字：甲編考釋}" in manual_bib
    assert "userb        = {史記殷本紀及其他記錄中所在殷商時代的史實}" in manual_bib
    assert "usera       = {季佛陀}" in manual_bib
    assert "userb       = {簡壽堂所藏殷墟文字}" in manual_bib
    assert "usera        = {胡厚宣}" in manual_bib
    assert "userb       = {武丁時五種記事刻辭考}" in manual_bib
    assert "userb       = {殷代卜龜之來源}" in manual_bib
    assert "userb       = {甲骨學緒論}" in manual_bib
    assert "userb       = {五十年甲骨文發現的總結}" in manual_bib
    assert "userb       = {五十年甲骨學論著目}" in manual_bib
    assert "userb       = {殷墟發掘}" in manual_bib
    assert "userb        = {殷卜辭中的上帝和王帝}" in manual_bib
    assert "userc        = {歷史研究}" in manual_bib
    assert "userb        = {殷代的蠶桑和絲織}" in manual_bib
    assert "userb        = {臨淄孫氏舊藏甲骨文字考辨}" in manual_bib
    assert "userb        = {甲骨文所見殷代奴隸的反壓迫鬥爭}" in manual_bib
    assert "userb        = {甲骨文所見商族鳥圖騰的新證據}" in manual_bib
    assert "usera        = {沈文倬}" in manual_bib
    assert "userb        = {𠬝与耤}" in manual_bib
    assert "usera        = {文物}" in manual_bib
    assert "userb        = {江西清江吴城商代遗址发掘简报}" in manual_bib
    assert "usera       = {王國維}" in manual_bib
    assert "userb       = {觀堂集林}" in manual_bib
    assert "usera       = {王子玉}" in manual_bib
    assert "userb       = {甲骨文}" in manual_bib
    assert "userc       = {續安陽縣志}" in manual_bib
    assert "usera        = {唐建元}" in manual_bib
    assert "userb        = {殷墟文字乙編丙編編號對照表}" in manual_bib
    assert "userb        = {續殷墟文字乙編丙編編號對照表}" in manual_bib
    assert "userc        = {中國文字}" in manual_bib
    assert "usera        = {江鴻}" in manual_bib
    assert "userb        = {盤龍城與商朝的南土}" in manual_bib
    assert "usera        = {夏鼐}" in manual_bib
    assert "userb        = {談14C測定年代和中國史前考古學}" in manual_bib
    assert "usera        = {新華社}" in manual_bib
    assert "userb        = {陝西周原發現珍貴甲骨}" in manual_bib
    assert "userc        = {大公報}" in manual_bib
    assert "usera       = {唐蘭}" in manual_bib
    assert "userb       = {古文字導論}" in manual_bib
    assert "userb        = {關於江西清江吳城文化遺址與文字的初步探索}" in manual_bib
    assert "userb        = {何尊銘文解釋}" in manual_bib


def test_bibliography_qa_cleans_remaining_shih_and_dong_residue():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "title        = {Di qi ci Yinxu fajue: E qu gongzuo baogao}" in manual_bib
    assert "title       = {Xiaotun hou wu ci fajue de zhongyao faxian}" in manual_bib
    assert "booktitle   = {Liutong bielu shang}" in manual_bib
    assert "location    = {Lizhuang, Sichuan}" in manual_bib
    assert "title        = {Yinxu zuijin zhi zhongyao faxian, fulun Xiaotun diceng}" in manual_bib
    assert "author      = {{Shisanjing zhushu}}" in manual_bib
    assert "title       = {Shisanjing zhushu}" in manual_bib
    assert "author      = {Dong, Zuobin}" in manual_bib
    assert "title       = {Yinlipu}" in manual_bib
    assert "title        = {Jiaguwen duandai yanjiu li}" in manual_bib
    assert "title       = {Xiaotun dier ben: Yinxu wenzi: jiabian}" in manual_bib
    assert "title        = {Yinxu wenzi jiabian zixu}" in manual_bib
    assert "title       = {Dong Zuobin xueshu lunzhu}" in manual_bib
    assert "author      = {Dong, Zuobin and Huang, Ranwei}" in manual_bib
    assert "author       = {Dong, Zuobin and Jin, Xiangheng}" in manual_bib
    assert "title       = {Jiaguwen suojian shizu ji qi zhidu}" in manual_bib
    assert "location    = {Beijing}" in manual_bib

    assert "title        = {Ti ch'i-tz'u Yin-hsu fa-chueh: E ch'u kung-tso pao-kao}" not in manual_bib
    assert "title       = {Hsiao-t'un hou wu-tz'u fa-chueh ti chung-yao fa-hsien}" not in manual_bib
    assert "booktitle   = {Liu-t'ung pieh-lu shang}" not in manual_bib
    assert "location    = {Li-chuang, Szechwan}" not in manual_bib
    assert "title        = {Yin-hsu tsui-chin chih chung-yao fa-hsien, fu-lun Hsiao-t'un ti-ts'eng}" not in manual_bib
    assert "author      = {{Shih-san-ching chu-shu}}" not in manual_bib
    assert "title       = {Shih-san-ching chu-shu}" not in manual_bib
    assert "author      = {Tung, Tso-pin}" not in manual_bib
    assert "title       = {Yin-li-p'u}" not in manual_bib
    assert "title        = {Chia-ku-wen tuan-tai yen-chiu li}" not in manual_bib
    assert "title       = {Hsiao-t'un ti-erh-pen: Yin-hsu wen-tzu: chia-pien}" not in manual_bib
    assert "title        = {Yin-hsu wen-tzu chia-pien tzu-hsu}" not in manual_bib
    assert "title       = {Tung Tso-pin hsueh-shu lun-chu}" not in manual_bib
    assert "author      = {Tung, Tso-pin and Huang, Jan-wei}" not in manual_bib
    assert "author       = {Tung, Tso-pin and Chin, Hsiang-heng}" not in manual_bib
    assert "title       = {Chia-ku-wen so-chien shih-tsu chi ch'i chih-tu}" not in manual_bib
    assert "location    = {Peking}" not in manual_bib
    assert "location    = {Nankang}" not in manual_bib


def test_bibliography_qa_cleans_remaining_t_block_residue():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "title        = {Fangshexing tansu ceding niandai baogao (yi)}" in manual_bib
    assert "title        = {Fangshexing tansu ceding niandai baogao (erh)}" in manual_bib
    assert "title        = {Fangshexing tansu ceding niandai baogao (san)}" in manual_bib
    assert "title        = {1973 nian Anyang Xiaotun nandi fajue jianbao}" in manual_bib
    assert "author       = {Tang, Jianyuan}" in manual_bib
    assert "title        = {Yinxu wenzi yibian bingbian bianhao duizhaobiao}" in manual_bib
    assert "title        = {Xu Yinxu wenzi yibian bingbian bianhao duizhaobiao}" in manual_bib
    assert "author      = {Tang, Lan}" in manual_bib
    assert "title       = {Guwenzi daolun}" in manual_bib
    assert "title        = {Guanyu Jiangxi Qingjiang Wucheng wenhua yizhi yu wenzi de chubu tansuo}" in manual_bib
    assert "title        = {Hezun mingwen jieshi}" in manual_bib
    assert "author       = {Jin, Xiangheng}" in manual_bib
    assert "title        = {Kufang ershi jiagu buci diyiwulingliupian bianwei jianlun Chenshi Erjiapu shuo}" in manual_bib
    assert "title        = {Shi shi}" in manual_bib
    assert "title        = {Qiwen shoulei ji shouxingzi shi}" in manual_bib
    assert "title        = {Fenghuang yu fengniao}" in manual_bib

    assert "title        = {Fang-she-hsing t'an-su ts'e-ting nien-tai pao-kao (yi)}" not in manual_bib
    assert "title        = {Fang-she-hsing t'an-su ts'e-ting nien-tai pao-kao (erh)}" not in manual_bib
    assert "title        = {Fang-she-hsing t'an-su ts'e-ting nien-tai pao-kao (san)}" not in manual_bib
    assert "title        = {1973 nien An-yang Hsiao-t'un nan-ti fa-chueh chien-pao}" not in manual_bib
    assert "author       = {Tang, Chien-yuan}" not in manual_bib
    assert "title        = {Yin-hsu wen-tzu yi-pien ping-pien pien-hao tui-chao-piao}" not in manual_bib
    assert "title        = {Hsu Yin-hsu wen-tzu yi-pien ping-pien pien-hao tui-chao-piao}" not in manual_bib
    assert "author      = {T'ang Lan}" not in manual_bib
    assert "title       = {Ku wen-tzu tao-lun}" not in manual_bib
    assert "title        = {Kuan-yu Chiang-hsi Wu-ch'eng wen-hua yi-chih yu wen-tzu ti ch'u-pu t'an-so}" not in manual_bib
    assert "title        = {Ho-tsun ming-wen chieh-shih}" not in manual_bib
    assert "author       = {Chin, Hsiang-heng}" not in manual_bib
    assert "title        = {K'u-Fang erh-shih chia-ku pu-tz'u ti-yi-wu-ling-liu-p'ien pien-wei chien-lun Ch'en-shih Erh-chia-p'u shuo}" not in manual_bib
    assert "title        = {Shih shih}" not in manual_bib
    assert "title        = {Ch'i-wen shou-lei chi shou-hsing-tzu shih}" not in manual_bib
    assert "title        = {Feng huang yu feng niao}" not in manual_bib


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
    assert "@article{Hayashi1968Inshu,\n  author       = {Hayashi Minao},\n  year         = {1968},\n  title        = {Inshu jidai no zuzo kigo},\n  journaltitle = {Toho gakuhd},\n  userc        = {東方學報}," in manual_bib
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
    assert "@article{Ikeda1951Keikeiji,\n  author       = {Ikeda, Suetoshi},\n  year         = {1951},\n  title        = {Kei kei ji ko},\n  journaltitle = {Kokotsugaku},\n  userc        = {甲骨學}," in manual_bib
    assert "@article{Ito1956Bokuji,\n  author       = {Ito, Michiharu},\n  shortauthor  = {Ito},\n  year         = {1956},\n  title        = {Bokuji ni mieru sorei kannen ni tsuite},\n  journaltitle = {Toho gakuho},\n  userc        = {東方學報}," in manual_bib
    assert "@book{Ito1975Chugoku," in manual_bib
    assert "@book{Ito1975Chugoku,\n  author      = {Ito, Michiharu},\n  shortauthor = {Ito},\n  year        = {1975},\n  title       = {Chugoku kodai ocho no keisei--shutsudo shiryo o chushin to suru Inshushi no kenkyu},\n  userb       = {中国古代王朝の形成：出土資料を中心とする殷周史の研究}," in manual_bib
    assert "@article{Jao1957Haiwai," in manual_bib
    assert "@article{Jao1957Haiwai,\n  author       = {Rao, Zongyi},\n  usera        = {饒宗頤},\n  shortauthor  = {Rao},\n  year         = {1957/58},\n  sortyear     = {1957},\n  title        = {Haiwai jiagulu yiyu},\n  userb        = {海外甲骨錄遺},\n  journaltitle = {Journal of Oriental Studies},\n  userc        = {東方文化}," in manual_bib
    assert "@article{Jao1961aLun,\n  author       = {Rao, Zongyi},\n  usera        = {饒宗頤},\n  shortauthor  = {Rao},\n  year         = {1961},\n  title        = {Lun buci duandai wenti--da Tao Bangnan xiansheng},\n  userb        = {論卜辭斷代問題——答陶邦南先生},\n  journaltitle = {Toyo gaku},\n  userc        = {東洋學}," in manual_bib

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
    assert "userb        = {山西十年來考古與文物工作的概況}" in manual_bib
    assert "@article{KK1975aJufa," in manual_bib
    assert "userb        = {河南偃師二里頭早商宮殿遺址發掘簡報}" in manual_bib
    assert "@article{KKHP1975bKansu," in manual_bib
    assert "userb        = {鄭州克拉王村遺址發掘報告}" in manual_bib
    assert "@book{Kaizuka1946Chiigoku,\n  author      = {Kaizuka, Shigeki},\n  year        = {1946},\n  title       = {Chiigoku kodai shigaku no hatten},\n  userb       = {中國古代史學の發展}," in manual_bib
    assert "@incollection{KaizukaIto1953Kokotsubun," in manual_bib
    assert "@article{Kane1974Independent," in manual_bib
    assert "@article{Kao1949Yinhsu," in manual_bib
    assert "@article{Hayashi1909Shinkoku,\n  author       = {Hayashi, Taisuke},\n  shortauthor  = {Taisuke},\n  year         = {1909},\n  title        = {Shinkoku Kanansho Toin ken hakken no kikko gyukotsu ni tsukite},\n  userb        = {淸國河南省湯陰縣發見の龜甲牛骨に就て}," in manual_bib

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
    assert "@book{Kuo1957Liang,\n  author      = {Guo, Moruo},\n  usera        = {郭沫若},\n  year        = {1957},\n  title       = {Liang Zhou jinwenci daxi tulu kaoshi},\n  userb        = {兩周金文辭大系圖錄考釋}," in manual_bib

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
    assert "@article{Ling1971Kueichi,\n  author       = {Ling, Shunsheng},\n  usera        = {凌純聲},\n  year         = {1971},\n  title        = {Zhongguo gudai de guiji wenhua},\n  userb        = {中國古代的龜祭文化},\n  journaltitle = {BIE},\n  userc        = {中央研究院民族學研究所集刊}," in manual_bib
    assert "@article{Liu1974Puku,\n  author       = {Liu, Yuanlin},\n  usera        = {劉源林},\n  year         = {1974},\n  title        = {Bugu de gongzhi jishu yanjin guocheng zhi tantao},\n  userb        = {卜骨的攻治技術演進過程之探討},\n  journaltitle = {BIHP},\n  userc        = {中央研究院歷史語言研究所集刊}," in manual_bib
    assert "@book{Lo1914Yinhsu," in manual_bib
    assert "@incollection{LotFalck1968Divination," in manual_bib
    assert "@book{Mao1971Turtles," in manual_bib
    assert "@article{Matsumaru1976Seishu," in manual_bib
    assert "@article{Matsumaru1976Seishu,\n  author       = {Matsumaru, Michio},\n  nameaddon    = {ed.},\n  year         = {1976},\n  title        = {Seishu kimbun no bengi o megutte},\n  journaltitle = {Kokotsugaku},\n  userc        = {甲骨學}," in manual_bib
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
    assert "@book{Shima1958Inkyo,\n  author      = {Shima, Kunio},\n  year        = {1958},\n  title       = {Inkyo bokuji kenkyu},\n  userb       = {殷墟卜辞研究}," in manual_bib
    assert "@book{Shima1967Inkyo," in manual_bib
    assert "@book{Shima1967Inkyo,\n  author      = {Shima, Kunio},\n  year        = {1967},\n  title       = {Inkyo bokuji sorui},\n  userb       = {殷墟卜辭綜類}," in manual_bib
    assert "@book{Shima1971Inkyo,\n  author      = {Shima, Kunio},\n  year        = {1971},\n  title       = {Inkyo bokuji sorui},\n  userb       = {殷墟卜辭綜類},\n  edition     = {2d rev. ed.}," in manual_bib
    assert "@article{Shirakawa1948Bokuji," in manual_bib
    assert "@book{Shirakawa1970Setsubun," in manual_bib
    assert "@book{Shirakawa1971Kimbun,\n  author      = {Shirakawa, Shizuka},\n  year        = {1971},\n  title       = {Kimbun no sekai},\n  userb       = {金文の世界}," in manual_bib
    assert "@book{Shirakawa1972Kokotsubun,\n  author      = {Shirakawa, Shizuka},\n  year        = {1972},\n  title       = {Kokotsubun no sekai---kodai In ocho no kozo},\n  userb       = {甲骨文の世界：古代殷王朝の構造}," in manual_bib
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
    assert "@article{Tung1952Putzu,\n  author       = {Dong, Zuobin},\n  usera        = {董作賓},\n  year         = {1952},\n  title        = {Buci zhong bayue yiyou yueshi kao},\n  userb        = {卜辭中八月乙酉月食考},\n  journaltitle = {Dalu zazhi tekan},\n  userc        = {大陸雜誌特刊}," in manual_bib
    assert "{Tung1951cChinese," in manual_bib
    assert "{Tung1954Work," in manual_bib
    assert "@article{Tung1954Work,\n  author       = {Dong, Zuobin},\n  usera        = {董作賓},\n  year         = {1954},\n  title        = {Gujiu keci zaikao},\n  userb        = {古舊刻辭再考}," in manual_bib
    assert "@article{Tung1954bWuTing,\n  author       = {Dong, Zuobin},\n  usera        = {董作賓},\n  year         = {1954},\n  title        = {Wu Ding shougui buci qianshuo},\n  userb        = {武丁狩龜卜辭淺說},\n  journaltitle = {TLTC},\n  userc        = {大陸雜誌}," in manual_bib
    assert "@article{Tung1962aPutzu,\n  author       = {Dong, Zuobin},\n  usera        = {董作賓},\n  year         = {1962},\n  title        = {Buci zhong zhi daxiao cai yu daxiao shi shuo},\n  userb        = {卜辭中之大小材與大小食說},\n  journaltitle = {Dalu zazhi tekan},\n  userc        = {大陸雜誌特刊}," in manual_bib
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

    assert "author      = {Dong, Zuobin and Huang, Ranwei}" in manual_bib
    assert "@article{Zhang1956Pu,\n  author       = {Zhang, Zongdong},\n  usera        = {張宗董},\n  shortauthor  = {Zongdong},\n  year         = {1956},\n  title        = {Bugui fujiadi xushu},\n  userb        = {卜龜腹甲的序數}," in manual_bib
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
    assert "@article{Yen1951Yinli,\n  author       = {Yan, Yiping},\n  usera        = {嚴一萍},\n  year         = {1951},\n  title        = {Yinlipu xunpu bu},\n  userb        = {殷曆譜「訓譜」補},\n  journaltitle = {TLTC},\n  userc        = {大陸雜誌}," in manual_bib
    assert "@article{Yen1952Cheng,\n  author       = {Yan, Yiping},\n  usera        = {嚴一萍},\n  year         = {1952},\n  title        = {Zheng Riben Sounei Qing shi dui Yinli de wujie},\n  userb        = {正日本藪內清氏對殷曆的誤解}," in manual_bib
    assert "@article{Yen1954Payueh,\n  author       = {Yan, Yiping},\n  usera        = {嚴一萍},\n  year         = {1954},\n  title        = {Bayue yiyou yueshi fujia de pinhe yu kaozheng de jingguo},\n  userb        = {八月乙酉月食腹甲的拼合與考證的經過}," in manual_bib
    assert "@article{Yen1955Yilun,\n  author       = {Yan, Yiping},\n  usera        = {嚴一萍},\n  year         = {1955},\n  title        = {Yilun Yinlipu jiujiao},\n  userb        = {一論「殷曆譜舊校」},\n  journaltitle = {TLTC},\n  userc        = {大陸雜誌}," in manual_bib
    assert "@article{Yen1959Shih,\n  author       = {Yan, Yiping},\n  usera        = {嚴一萍},\n  year         = {1959},\n  title        = {Shi sizuding},\n  userb        = {釋四足鼎}," in manual_bib
    assert "@article{Yen1961Chiaku,\n  author       = {Yan, Yiping},\n  usera        = {嚴一萍},\n  year         = {1961},\n  title        = {Jiaguwen duandai yanjiu xinli},\n  userb        = {甲骨文斷代研究新例},\n  journaltitle = {Lishi yuyan yanjiusuo jikan waibian},\n  userc        = {中央研究院歷史語言研究所集刊外編}," in manual_bib
    assert "@article{Yen1967Chiaku,\n  author       = {Yan, Yiping},\n  usera        = {嚴一萍},\n  year         = {1967},\n  title        = {Jiagu yanjiu bianwei zhuli},\n  userb        = {甲骨研究辨偽助例},\n  journaltitle = {Yushi xuezhi},\n  userc        = {語史學誌}," in manual_bib
    assert "{Yen1974Chia," in manual_bib
    assert "{Yen1976Chiaku," in manual_bib
    assert "{YenYun1973Shangtai," in manual_bib
    assert "{Yetts1933Shang," in manual_bib
    assert "{Yetts1954Shang," in manual_bib
    assert "{Yin1962Chiangsu," in manual_bib
    assert "@book{Yu1940Shuang,\n  author      = {Yu, Xingwu},\n  usera        = {于省吾},\n  year        = {1940},\n  title       = {Shuangjianchi Yinqi pinzhi},\n  userb        = {雙劍誃殷契駢枝}," in manual_bib
    assert "{Yu1972Tsung," in manual_bib
    assert "{Yu1929Hsin," in manual_bib
    assert "userb        = {說「又」}" in manual_bib

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
    assert "@incollection{Lung1976Shih,\n  author      = {Long, Yuchun},\n  year        = {1976},\n  title       = {Shi jiaguwen chong zi jianjie xizun},\n  userb       = {釋甲骨文虫字兼解犧尊},\n  booktitle   = {Shen Gangbo xiansheng baji rongqing lunwenji},\n  userc       = {沈剛伯先生八秩榮慶論文集},\n  pages       = {1--16}," in manual_bib
    assert "Collections Published 1935-1939" in manual_bib
    assert "{Nivison1977aPronominal," in manual_bib
    assert "{Shen1977Fuyu," in manual_bib
    assert "@article{Shen1977Fuyu,\n  author       = {Shen, Wenzhuo},\n  usera        = {沈文倬},\n  shortauthor  = {Wenzhuo},\n  year         = {1977},\n  title        = {Fu yu chi},\n  userb        = {𠬝与耤},\n  journaltitle = {KK},\n  userc        = {考古},\n  volume       = {1977.5},\n  pages        = {335--338, 358}," in manual_bib
    assert "{Takashima1977aExistence," in manual_bib
    assert "{TungEncheng1977Computer," in manual_bib
    assert "{Yu1977Shuo," in manual_bib

    assert "{Chang1977The," not in generated_bib
    assert "{Haven1976Work," not in generated_bib
    assert "{Hsinhuashe1977Shen," not in generated_bib
    assert "{Hsinhuashe1977Chia," not in generated_bib
    assert "{Hsinhuashe1977Work," not in generated_bib
    assert "{REE1976Shih," not in generated_bib
