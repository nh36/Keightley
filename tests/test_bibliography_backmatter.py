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
    assert 'title        = {Guanyu "Shang wang miaohao xinkao" yiwen de buchong yijian}' in manual_bib
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
    assert "title        = {Buci zali}" in manual_bib
    assert "title        = {Shi ziyong ziyou}" in manual_bib
    assert "title       = {Wuding shi wuzhong jishi kezi kao}" in manual_bib
    assert "booktitle   = {Jiaguxue Shangshi luncong chuji}" in manual_bib
    assert "title       = {Yindai bugui zhi laiyuan}" in manual_bib
    assert "title       = {Jiaguxue xulun}" in manual_bib
    assert "booktitle   = {Jiaguxue Shangshi luncong erji}" in manual_bib
    assert "title        = {Buci tongwen li}" in manual_bib
    assert "title        = {Buci jishi wenzi shiguan qianming li}" in manual_bib
    assert "title       = {Wushinian jiaguwen faxian de zongjie}" in manual_bib
    assert "title       = {Wushinian jiaguxue lunzhumu}" in manual_bib
    assert "title       = {Yinxu fajue}" in manual_bib
    assert "title        = {Yin buci zhong de Shang Di he Wang Di}" in manual_bib
    assert "journaltitle = {Lishi yanjiu}" in manual_bib
    assert "title        = {Jiaguwen Shangzu niao tuteng de yizhi}" in manual_bib
    assert "journaltitle = {Lishi luncong}" in manual_bib
    assert "title        = {Yindai de cansang he sizhi}" in manual_bib
    assert "journaltitle = {Wenwu}" in manual_bib
    assert "title        = {Zhui ji}" in manual_bib
    assert "title        = {Yindai de yuexing}" in manual_bib
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
    assert "title       = {Yindai zhenbu renwu tongkao}" in manual_bib
    assert "location    = {Hong Kong}" in manual_bib
    assert "title        = {Yu buchao jishu tuiqiu Yinren duiyu shu de guannian---guibu xiangshu lun}" in manual_bib
    assert "journaltitle = {Zhongyang yanjiuyuan lishi yuyan yanjiusuo waibian}" in manual_bib
    assert "title        = {Lun buci duandai wenti--da Tao Bangnan xiansheng}" in manual_bib
    assert "author       = {Rong, Geng}" in manual_bib
    assert "title        = {Jiaguxue gaikuang}" in manual_bib
    assert "journaltitle = {Lingnan xuebao}" in manual_bib
    assert "author      = {Rong, Geng}" in manual_bib
    assert "title       = {Jinwenbian}" in manual_bib
    assert "location    = {Beijing}" in manual_bib
    assert "author      = {Rong, Yuan and Rong, Geng}" in manual_bib
    assert "title       = {Jinshishu lumu}" in manual_bib

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
    assert "author       = {Ke, Yiqing}" in manual_bib
    assert "author      = {Guan, Xiechu}" in manual_bib
    assert "title       = {Yinxu jiagu keci de yufa yanjiu}" in manual_bib
    assert "author      = {Guo, Moruo}" in manual_bib
    assert "title       = {Gujiu kezi zhi yi kaocha}" in manual_bib
    assert "booktitle   = {Gudai mingke huikao xubian}" in manual_bib
    assert "title       = {Liang Zhou jinwenci daxi tulu kaoshi}" in manual_bib
    assert "author       = {Guo, Baojun}" in manual_bib
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
    assert "title        = {Shizi de jiegou ji shiguan de yuanshi zhiwu}" in manual_bib
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
    assert "title       = {Shi jiaguwen xi(?) zi jianjie xicun}" in manual_bib
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
    assert "author       = {Shen, Wenzhuo}" in manual_bib
    assert "shortauthor  = {Wenzhuo}" in manual_bib
    assert "{Takashima1977aExistence," in manual_bib
    assert "{TungEncheng1977Computer," in manual_bib
    assert "{Yu1977Shuo," in manual_bib

    assert "{Chang1977The," not in generated_bib
    assert "{Haven1976Work," not in generated_bib
    assert "{Hsinhuashe1977Shen," not in generated_bib
    assert "{Hsinhuashe1977Chia," not in generated_bib
    assert "{Hsinhuashe1977Work," not in generated_bib
    assert "{REE1976Shih," not in generated_bib
