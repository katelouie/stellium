# Stellium zh-CN (Mainland/Simplified) Localization: Calque Audit & Terminology Report

## TL;DR
- **The donated file contains five confirmed machine-translation calques that must be replaced:** 热带黄道→**回归黄道** (Tropical), 必要尊贵→**必然尊贵** (Essential Dignities), 视星光度→**视星等** (Apparent Magnitude), 和弦相位→**泛音相位** (Harmonic Aspects), and 地心制→**锥心（分宫）制** (Topocentric — note the astrology term is 锥心, *not* my initially-proposed astronomy term 站心).
- **Most of the donated file is correct and idiomatic** — the sign set, element set, planet set, moon phases, most house-system transliterations, and most aspect names are sound; a handful are "acceptable-but-nonstandard" and could be upgraded to the dominant mainland form (e.g. 宫尖→宫头, 双五分相→倍五分相, 半六分相→十二分相, 基本宫/固定宫/变动宫→基本/固定/变动 for modality).
- **For the missing ~500 keys, mainland-attested renderings exist for most catalog/extended/message-tier terms**, but a real minority (many minor asteroids, the Hayz/Halb/Distributor/Decennials cluster, Almuten transliteration) have **no verifiable mainland usage and should be left untranslated** (English fallback) rather than shipped.

---

## 1. TASK 1 — AUDIT TABLE

| English key | Donated zh-CN | Verdict | Recommended | Source + confidence | Notes |
|---|---|---|---|---|---|
| Tropical | 热带黄道 | **CALQUE-replace** | 回归黄道 | 爱星盘《回归黄道和恒星黄道释义》(ixingpan.com/article/6022): "将这样的黄道系统称为回归黄道（Tropical Zodiac）… 爱星盘的默认黄道系统是回归黄道"; 豆瓣、知乎同. **HIGH** | 热带 = climate-sense tropical; astrology universally uses 回归黄道 |
| Sidereal | 恒星黄道 | Correct | — | Same sources. **HIGH** | Universal |
| Parallel | 合纬 | Acceptable-but-nonstandard | 平行 | 豆瓣古典占星简明教程 uses 赤纬平行. **MED** | 赤纬 aspect; 平行 is the standard word |
| Contraparallel | 对纬 | Acceptable-but-nonstandard | 逆平行 | Same. **MED** | Distinct from antiscia (映点) |
| Cusp | 宫尖 | Acceptable-but-nonstandard | 宫头 | 腾讯《宫位制选修课》"宫头线"; 知乎宫主星文. **HIGH** | 宫头 is the dominant mainland term; 宫始点 also used |
| Cusp ({system}) | 宫始（{system}） | Acceptable | 宫头（{system}） | **MED** | 宫始 intelligible but 宫头 preferred |
| House Cusp / House Cusps | 宫位分界 | Acceptable | 宫头 | **MED** | Descriptive; fine but 宫头 tighter |
| Sesqui-Square / Sesquiquadrate | 倍半四分相 | Acceptable | (or 补八分相) | 爱星盘《相位》: 135度补八分相. **HIGH** | Both 倍半四分相 and 补八分相 attested for 135° |
| Quincunx / Inconjunct | 梅花相 | Correct | 梅花相位 | 爱星盘/搜狐/腾讯: 150度梅花相位, 补十二分相. **HIGH** | Fully idiomatic |
| Decile | 十分相 | Correct | — | 新浪/若道. **HIGH** | 36° |
| Bi-Quintile / Biquintile | 双五分相 | Acceptable-but-nonstandard | 倍五分相 | 新浪《五分相系列》、爱星盘: 144度倍五分相. **HIGH** | 倍五分相 is the attested form |
| Novile | 九分相 | Correct | — | 知乎占星相位研究. **HIGH** | 40° |
| Septile | 七分相 | Correct | — | **HIGH** | ~51.4° |
| Quintile | 五分相 | Correct | — | 新浪. **HIGH** | 72° |
| Semi-Sextile | 半六分相 | Acceptable-but-nonstandard | 十二分相 (or 半六合) | 爱星盘/若道: 30度半六合、十二分相. **HIGH** | Dominant mainland forms are 十二分相 / 半六合 |
| Semi-Square | 半四分相 | Acceptable | (or 八分相) | 若道/爱星盘: 45度八分相. **HIGH** | Both fine |
| Aspectarian | 相位网格 | Acceptable | — | **MED** (descriptive coinage) | No settled mainland term; 相位网格 reasonable |
| Aspect Patterns | 相位图形 | Correct | — | 知乎《相位格局(模式)》; 新月占星"图形相位". **HIGH** | Also 相位格局/相位模式 |
| Pattern | 图形 | Correct | — | **HIGH** | |
| Harmonic Aspects | 和弦相位 | **CALQUE-replace** | 泛音相位 | 豆瓣/知乎《泛音盘 Harmonic》; 新浪《五分相系列》"泛音图(Harmonic)". **HIGH** | 和弦 = musical chord; harmonic = 泛音/倍律 |
| Cross-Chart Aspects (Harmonic) | 跨盘和弦相位 | **CALQUE-replace** | 跨盘泛音相位 | Same. **HIGH** | |
| Essential Dignities | 必要尊贵 | **CALQUE-replace** | 必然尊贵 | 秦瑞生标准译名，爱星盘、占星秘檀、豆瓣通用："行星的必然尊贵和必然无力"; Barbara Dunn《Horary Astrology Re-Examined》中译作"必然（先天）尊贵". **HIGH** | "essential"→必然, not 必要 |
| Chart Ruler | 星盘主星 | Acceptable-but-nonstandard | 命主星 | 新浪《命主星和盘主星》; 爱星盘/2633. **HIGH** | 命主星 = Lord of Ascendant (the standard); note 盘主星 = strongest planet/Almuten Figuris, a *different* concept |
| Chart Sect | 昼夜属性 | Acceptable | 区分 (or keep) | SATA《白天不懂夜的黑》: "区分（Sect）". **HIGH** | Technical term is 区分; 昼夜属性 is a fair gloss |
| Modern Ruler | 现代主星 | Correct | — | **HIGH** | |
| Ruler / Lord | 主星 | Correct | — | **HIGH** | Also 守护星 |
| Direction (message) | 盈亏方向 | Correct (in context) | — | **MED** | Fits moon-phase waxing/waning |
| Illumination | 照明度 | Acceptable-but-nonstandard | 照亮比例 | astronomy 被照亮比例. **MED** | 照明度 reads as engineering "illuminance" |
| Apparent Magnitude | 视星光度 | **CALQUE-replace** | 视星等 | 《英汉天文学名词》(全国科技名词委/中科院)；维基/百度百科视星等条 (符号 m). **HIGH** | 视星光度 is not a real term |
| Apparent Diameter | 视直径 | Correct | — | 天文学名词. **HIGH** | |
| Geocentric Parallax | 地心视差 | Correct | — | **HIGH** | |
| Ayanamsa | 阿亚南萨 | Acceptable | (or 岁差校正值) | **MED** | Transliteration acceptable in 印占 |
| Eclipses | 食相 | Acceptable-but-nonstandard | 日月食 / 交食 | **MED** | 食相 sometimes used but 日月食 clearer |
| Sign Ingresses | 星座换座 | Acceptable | 星座进入 | **MED** | Both intelligible |
| Natal Transits | 本命行运 | Correct | — | 爱星盘运势推测页. **HIGH** | |
| Transit Timeline | 行运时间线 | Correct | — | **MED-HIGH** | |
| Planets (generic label) | 涉及行星 | **Nonstandard-replace** | 行星 | **HIGH** | 涉及行星 = "involved planets"; wrong for a generic column |
| Quality | 性质 | Acceptable | 模式 (if=modality) | **MED** | If this is modality use 模式/三态 |
| Element/Quality | 元素/模式 | Correct | — | **HIGH** | |
| Level / Period / Motion / State / Status | 层级/周期/运动/状态 | Correct | — | **HIGH** | |
| Generated with Stellium | 由 群星 生成 | **Advise not translating brand** | 由 Stellium 生成 | **HIGH (convention)** | 群星 also = the Stellium *aspect pattern* → collision. Chinese software convention keeps Latin product names |
| Mean Apogee | 黑月莉莉斯 | Correct (fix char) | 黑月莉莉丝 | 新月占星/爱星盘: 黑月莉莉丝. **HIGH** | Standard is 莉莉丝 (丝), not 斯 |
| Mean Node | 平均北交点 | Acceptable | 平北交点 | 爱星盘. **MED-HIGH** | |
| True Node | 北交点 | Correct | (或 真北交点) | **HIGH** | |
| Eris | 厄里斯 | Acceptable-but-nonstandard | 阋神星 | 卞毓麟《"阋神星"的来龙去脉》(中国科技术语 2007(4)): 2007-06-16 扬州名词委投票"'阋神星'获得压倒多数票". **HIGH** | 阋神星 is committee-settled & dominant; 厄里斯 is a minority transliteration |
| Topocentric (house system) | 地心制 | **CALQUE-replace** | 锥心（分宫）制 | 爱星盘排盘选项"Topocentric: 锥心分宫制"; 知乎《常见宫位制详解》"锥心分宫制…以出生地的地表为中心". **HIGH** | 地心 = geocentric (wrong). Attested astrology term is 锥心制 (also written 椎心制); 站心制 is astronomy-only |
| Topocentric.short | 站 | Replace | 锥 | **MED** | Match the corrected long form |
| Axial Rotation (house) | 轴向旋转制 | Acceptable | — | **LOW-MED** | Rare system; descriptive, no attested standard |
| Alcabitius | 阿尔卡比提乌斯 | Acceptable | (或 阿卡比特制) | 知乎/爱星盘: 阿卡比特. **MED-HIGH** | 阿卡比特(制) is the common short form |
| Regiomontanus | 雷吉奥蒙塔努斯 | Acceptable | (或 雷氏/芮氏制) | 爱星盘: 雷格蒙坦纳斯/芮氏. **MED-HIGH** | Transliteration varies |
| Placidus | 普拉西度斯 | Correct | (普拉西德) | 爱星盘/腾讯: 普拉西德(斯). **HIGH** | |
| Koch | 科赫 | Correct | — | 腾讯/爱星盘: 科赫. **HIGH** | |
| Campanus | 坎帕努斯 | Correct | (坎帕纳斯) | **HIGH** | |
| Porphyry | 波菲利 | Correct | (波菲力) | 爱星盘: 波菲力/普菲力. **HIGH** | |
| Morinus | 莫里努斯 | Correct | (莫里纳斯) | **HIGH** | |
| Krusinski | 克鲁辛斯基 | Acceptable | — | **MED** | Transliteration |
| Vehlow Equal | 韦洛等宫制 | Acceptable | — | **MED** | |
| Whole Sign | 整宫制 | Correct | — | 爱星盘《分宫制》. **HIGH** | |
| Equal | 等宫制 | Correct | — | **HIGH** | |
| Horizontal | 地平制 | Correct | — | **HIGH** | |
| Cardinal/Fixed/Mutable | 基本宫/固定宫/变动宫 | **Wrong suffix for modality** | 基本/固定/变动 (or 基本星座/固定星座/变动星座) | 12sign/爱星盘 星座列表: 本位/固定/变动星座. **HIGH** | 宫 = house; modality attaches to 星座, not 宫. Bare 基本/固定/变动 or +星座. (开创 also used for cardinal) |
| Sect: Day / Night | 日 / 夜 | Acceptable | 昼 / 夜 | SATA/知乎: 日间盘/夜间盘. **MED-HIGH** | 昼/夜 marginally more idiomatic |
| {sect} Chart | {sect}间盘 | Acceptable | — | 知乎: 日间盘/夜间盘. **HIGH** | Confirmed |
| Waxing Crescent | 娥眉月 | **Replace** | 蛾眉月 | 知乎(上海天文馆八相图)、百度百科: 蛾眉月. **HIGH** | Mainland astronomy/geography standard uses 蛾 (moth radical); 娥 is a variant |
| Moon phase set | 新月/上弦月/盈凸月/满月/亏凸月/下弦月/残月 | Correct | (+蛾眉月) | 上海天文馆/地理教材. **HIGH** | Standard set |
| Sign set | 白羊…双鱼座 | Correct | — | 爱星盘/新浪. **HIGH** | 水瓶座 mainland-standard (宝瓶座 is formal astronomical variant) |
| Element set | 火象/土象/风象/水象 | Correct | — | **HIGH** | 风象 (not 气象) is correct |

---

## 2. TASK 2 — PROPOSALS FOR MISSING TERMS

### Catalog: Aspects
| English | Proposed | Source + confidence | Notes |
|---|---|---|---|
| Semisextile | 十二分相 / 半六合 | 爱星盘/若道. **HIGH** | |
| Semisquare | 八分相 / 半四分相 | 若道. **HIGH** | |
| Sesquisquare | 补八分相 / 倍半四分相 | 爱星盘. **HIGH** | 135° |
| Binovile | 倍九分相 | **MED** (systematic, lightly attested) | 80° — flag |
| Biseptile | 倍七分相 | **LOW-MED** | flag |
| Triseptile | 三七分相 | **LOW-MED** | flag |
| Quadnovile | 四九分相 | **LOW** | poorly attested — consider leaving untranslated |

### Catalog: Dignities (subagent-confirmed, all HIGH)
Domicile **入庙/庙** (also 本垣); Exaltation **旺/擢升** (擢升 mainland-preferred; 耀升 Taiwan); Detriment **失势/陷**; Fall **落陷/弱**; Triplicity **三分性/三分主星**; Term/Bounds **界**; Face/Decan **外观 / 面** (both mainland-standard; 十度 is the technical/Taiwan-flavored variant); Peregrine **游走 / 外来** (also 浮游). *The Detriment=失势 vs Fall=落陷 split is confirmed mainland-standard (爱星盘/占星秘檀/新浪/豆瓣), though the short characters 陷/弱 are sometimes swapped casually.*

### Catalog: Bodies
**Dwarf planets — 2007 天文学名词审定委员会 (HIGH):** Eris 阋神星, Haumea 妊神星, Makemake 鸟神星, Orcus 亡神星, Quaoar 创神星, **Gonggong 共工星** (Chinese-mythology name, first solar-system body given a Chinese name), Sedna 塞德娜/赛德娜, Ixion 伊克西翁, Huya 忽雅. Salacia 蟹神星/漾神星 (**unstable — flag, consider leaving untranslated**), Varuna 伐楼拿 (transliteration, **MED**).

**Main asteroids/centaurs (HIGH):** Ceres 谷神星, Pallas 智神星, Juno 婚神星, Vesta 灶神星, Chiron 凯龙星, Eros 爱神星, Psyche 灵神星, Hygiea 健神星, Pholus 人龙星/佛卢斯(**MED**), Chariklo 女凯龙星/卡瑞克罗(**MED**).

**Uranian/Hamburg School — 爱星盘 汉堡学派虚星 list (HIGH):** Cupido 丘比特, Hades 哈迪斯, Zeus 宙斯, Kronos 克洛诺斯, Apollon 阿波罗, Admetos 阿德门图斯, Vulkanus 弗卡奴斯, Poseidon 波塞东. **Distinguish Apollo (asteroid) 阿波罗神星 from Apollon (Uranian) 阿波罗.**

**Minor asteroids with an IAU Chinese name (MED — astronomy names, rarely used in astrology):** Flora 花神星, Hebe 韶神星, Iris 虹神星, Metis 忑神星 (⚠ collides with 智神星 usage — **leave untranslated**), Urania 天神星, Astraea 司理星, Fortuna 幸运星/命神星.

**No attested mainland astrology usage — RECOMMEND LEAVE UNTRANSLATED (LOW):** Admetos-edge, Amor, Apollo Point / Aries Point, Asbolus, Bacchus, Bienor, Chaos, Deucalion, Diana, Echeclus, Elatus, Hidalgo, Hylonome, Icarus, Logos, Nessus, Okyrhoe, Pandora, Sappho, Toro, Typhon, True/Mean Apogee (except Black Moon Lilith), Vindemiatrix-as-asteroid. Ship English fallback.

### Catalog: Fixed Stars (indigenous names strongly preferred in mainland astrology — Wikipedia 恒星统称/爱星盘《恒星和其他行星产生相位》/知乎占星恒星篇, HIGH)
Achernar 水委一, Alcyone 昴宿六, Aldebaran 毕宿五, Algol 大陵五, Alkaid 摇光/北斗七, Altair 河鼓二 (牛郎星), Antares 心宿二, Arcturus 大角星, Betelgeuse 参宿四, Canopus 老人星, Capella 五车二, Castor 北河二, Deneb 天津四, Fomalhaut 北落师门, Hamal 娄宿三, Polaris 勾陈一 (北极星), Pollux 北河三, Procyon 南河三, Regulus 轩辕十四, Rigel 参宿七, Sirius 天狼星, Spica 角宿一, Vega 织女星/织女一, Vindemiatrix 太微左垣四, Zubenelgenubi 氐宿一, Zubeneschamali 氐宿四. **Recommendation: indigenous name primary; a transliteration gloss is unnecessary — mainland astrological writing overwhelmingly uses 心宿二/轩辕十四/毕宿五/北落师门 etc.**

### Extended: Chart types (爱星盘/新浪/12sign, HIGH)
Natal 本命盘, Transit 行运盘, Synastry 比较盘, Composite 组合(中点)盘, Davison 戴维森盘 (时空中点盘), Solar Return 太阳返照盘, Lunar Return 月亮返照盘, Progressed/Secondary Progression 次限盘/次限推运, Solar Arc Direction 太阳弧(推运), Draconic 龙盘 (**MED**), Harmonic 泛音盘, Horary 卜卦盘, Electional 择时盘 (择日), Mundane 世俗(占星)盘, Relocated 换置盘/迁移盘, Event 事件盘, Primary Direction 主限法, Planetary Return 行星返照盘.

### Extended: Conditions (subagent + searches)
Angular 角宫, Succedent 续宫, Cadent 果宫 (all **HIGH**); Cazimi 日核/核心区, Combust 焦伤/灼伤, Under the Beams 在太阳光束下/日光下, Oriental 东出, Occidental 西入, Rising 上升, Setting 下降/西落, Void of Course 空亡, Feral 在野, Reception 接纳, Mutual Reception 互容, Besieged 围攻/围困, Increasing in Light 渐盈/光增, Decreasing in Light 渐亏/光减, Swift 行速快, Slow 行速慢, Culminating 上中天 (all **HIGH–MED**); Combustion 焦伤; **In Sect 得区分 / Out of Sect 逆区分** (**MED**); Free of the Sun 脱离日光 (**MED, descriptive**); Hayz **得时** (**MED** — transliteration 哈伊兹 unverified, use 得时); **Halb — no attested distinct term, LEAVE UNTRANSLATED**.

### Extended: Directions / Branches / Stems / Wuxing / Zodiac animals (all HIGH, universal)
N 北 / S 南 / E 东 / W 西 / NE 东北 / NW 西北 / SE 东南 / SW 西南 (North 北方 etc.). Branches 子丑寅卯辰巳午未申酉戌亥. Stems 甲乙丙丁戊己庚辛壬癸. Wuxing 木火土金水. Animals 鼠牛虎兔龙蛇马羊猴鸡狗猪.

### Extended: House topics
Classical house names: 1 命宫, 2 财帛宫, 3 兄弟宫, 4 田宅宫, 5 子女宫, 6 疾厄宫/奴仆宫, 7 夫妻宫, 8 疾厄宫→(death)疾厄/死亡, 9 迁移宫, 10 官禄宫/事业宫, 11 福德宫, 12 玄秘宫/相貌宫. **However, the English source strings are modern descriptive ("Self & Identity", "Money & Values"…).** Recommendation: render with modern descriptors that mirror the English (自我与身份, 金钱与价值, 沟通与手足, 家庭与根源, 创造与愉悦, 工作与健康, 伴侣关系, 死亡与转化, 哲学与远行, 事业与声望, 朋友与愿望, 独处与消解) rather than forcing classical palace names; offer classical names only if the UI is 古典-oriented. **MED-HIGH.**

### Extended: Months / Weekdays (HIGH, universal)
一月…十二月; 星期一/星期二/星期三/星期四/星期五/星期六/星期日 (星期天).

### Extended: Nakshatras (MED — FLAG)
Indigenous 宿曜 mansion names exist (娄宿/胃宿/昴宿/毕宿/觜宿/参宿/井宿/鬼宿/柳宿/星宿/张宿/翼宿/轸宿/角宿/亢宿/氐宿/房宿/心宿/尾宿/箕宿/斗宿/女宿/虚宿/危宿/室宿/壁宿/奎宿), attested via 宿曜经 tradition and 12sign/李居明 mapping. **But mainland 印度占星 writing predominantly uses Sanskrit transliterations** (阿斯维尼, 婆罗尼, 克里底迦…). Recommendation: **transliteration primary + mansion gloss**, or leave transliteration only. Note the Shravana ambiguity (女宿 by 27-mansion count vs 牛宿 by determinative star). Because usage is genuinely split and no single mainland standard dominates, mark this whole group **MED and flag for reviewer decision**.

### Extended: Patterns (HIGH unless noted)
Grand Trine 大三角, Grand Cross 大十字, T-Square T三角 (三刑会冲), Yod 上帝之指/上帝的手指, Kite 风筝, Stellium 星群/群星, Mystic Rectangle 神秘长方形, Grand Sextile 大六角, Star of David 大卫星 (= 大六角), Minor Grand Trine 小三角, Cradle 摇篮, Rectangle 长方形, Wedge 楔形 (**MED**), Thor's Hammer 雷神之锤 (**MED**), Hourglass 沙漏 (**MED**).

### Extended: Polarity (HIGH)
Masculine 阳性, Feminine 阴性, Diurnal 昼/日间, Nocturnal 夜/夜间, Positive 正极/阳, Negative 负极/阴.

### Extended: Time units (HIGH — Chinese does not inflect for number; singular = plural)
year/years 年, month/months 月, week/weeks 周 (星期), day/days 天 (日), hour/hours 小时, minute/minutes 分钟, second/seconds 秒.

### Extended: Wuxing (HIGH)
Wood 木, Fire 火, Earth 土, Metal 金, Water 水.

### Message tier (selected; HIGH unless noted)
AM 上午, PM 下午, Retrograde Planets 逆行行星, Fixed Stars 恒星, Declination(s) 赤纬, Right Ascension 赤经, Longitude 经度, Latitude 纬度, Lunar Nodes 月交点, Dispositor 定位星, Final Dispositor 最终定位星, Decan 十度/外观, Dignity 尊贵, Debility 无力/弱势, Rulership 守护/主管, Temperament 气质, Element Balance 元素平衡, Modality Balance 模式平衡, Hemisphere Emphasis 半球侧重, Antiscia 映点, Parallels 平行, Black Moon Lilith 黑月莉莉丝, Combustion 焦伤, Firdaria 法达/法达星限, Primary Directions 主限法, Secondary Progressions 次限法, Solar Arc Directions 太阳弧推运, Time Lords 时主星, Void of Course Moon 月亮空亡, Mutual Reception 互容, Reception 接纳, None 无, N/A 不适用, No data available. 暂无数据, Not calculated. 未计算, Total 合计, Score 分数, Exact 精确, True 是/真, False 否/假, Male 男, Female 女, Pillar 柱, Stem 天干, Branch 地支, Hidden Stems 藏干, Nakshatra 星宿/月宿, Dashas 大运/达沙 (印占), Rectification 生时校正, Object 天体/对象, Composite Chart 组合盘, Progressed Chart 次限盘, Synastry 比较盘, Solar Return 太阳返照, Transits 行运, Houses 宫位, Chart Shape 星盘图形, Chart Patterns 相位图形, Condition 状态, Polarity 极性, Modality Balance 模式平衡.
- **Almuten** 宫神星 (of a house) / **Almuten Figuris** 盘主星 (**MED** — 盘主星 = strongest planet, distinct from 命主星 = Ascendant lord). **Do NOT use transliteration 阿慕田 (unattested).**
- **Pada** — no settled mainland term; use 步 or leave untranslated (**LOW**).
- **Firdaria — do NOT use 菲尔达; use 法达/法达星限 (HIGH).**

### Format tier (verify)
- date `{year}年{month_num}月{day}日` → **correct** for mainland (公历/Gregorian only). **HIGH.**
- time / datetime `{hour24}:{minute}` → **correct**; mainland astrology software uses **24-hour**. Where AM/PM is needed use 上午/下午.
- latitude/longitude `{hemisphere}{value}°` → hemisphere words **北纬/南纬/东经/西经**, placed **before** the value → **correct**. **HIGH.**
- degrees `23°45'` → mainland astrology software uses the symbol form **23°45′** (prime marks); 23度45分 is also readable but less common in software. Recommend symbol form. **MED-HIGH.**
- decimal_sep `.` → **correct** for mainland. **HIGH.**

---

## 3. SUMMARY LISTS

### (a) Confirmed machine-translation calques in the donated file (must replace)
1. **热带黄道 → 回归黄道** (Tropical) — climate-sense vs zodiac-sense.
2. **必要尊贵 → 必然尊贵** (Essential Dignities) — "essential" mistranslated as "necessary/required."
3. **视星光度 → 视星等** (Apparent Magnitude) — invented compound vs standard astronomical term.
4. **和弦相位 → 泛音相位** (Harmonic Aspects) — musical-chord sense vs overtone/harmonic sense.
5. **地心制 → 锥心（分宫）制** (Topocentric) — geocentric vs observer-on-surface; the attested mainland *astrology* term is 锥心制 (not the astronomy term 站心制).

Plus two near-calques / wrong-register items to fix: **涉及行星 → 行星** (generic "Planets" label), and **基本宫/固定宫/变动宫 → 基本/固定/变动** (modality must not take the 宫 "house" suffix). Also fix character: **黑月莉莉斯 → 黑月莉莉丝**.

### (b) Keys with no attested mainland usage → recommend leaving untranslated (English fallback)
- **Bodies:** Amor, Asbolus, Bacchus, Bienor, Chaos, Deucalion, Diana, Echeclus, Elatus, Hidalgo, Hylonome, Icarus, Logos, Nessus, Okyrhoe, Pandora, Sappho, Toro, Typhon, Aries Point/Apollo Point, Salacia (unstable), Metis-as-asteroid (name collision). Ship English.
- **Conditions/techniques:** Halb, Distributor, Decennials — no standard mainland term.
- **Message/technique transliterations to avoid:** 阿慕田 (Almuten), 菲尔达 (Firdaria), 哈伊兹 (Hayz) — use the attested Chinese forms (宫神星, 法达, 得时) or leave untranslated where none exists.
- **Aspects:** Quadnovile (poorly attested); Binovile/Biseptile/Triseptile are MED — acceptable to ship the systematic form but flag.

### (c) Terms where mainland usage genuinely differs from Taiwan/HK (word-level, not just character conversion)
- **Exaltation:** mainland **擢升** (formal) vs Taiwan **耀升**; short form 旺 shared.
- **Waxing Crescent:** mainland-standard **蛾眉月** (moth radical) vs common variant **娥眉月** (woman radical).
- **水瓶座** (mainland general) vs **宝瓶座** (formal astronomical / more common in some TW/astronomy contexts).
- **Face/Decan:** mainland **外观/面** vs Taiwan-flavored **十度**.
- **Authoritative-source caveat:** the single most-cited Chinese classical-astrology author (秦瑞生) and 占星之门 (astrodoor) are Taiwanese, though their vocabulary is widely adopted on the mainland; genuinely mainland-native systematic sources are **爱星盘 (ixingpan)**, **占星秘檀 (zxmt365)**, **若道 (nodoor)**, and practitioner posts on 豆瓣/知乎/新浪. No confirmed *published* Simplified-Chinese translations of Lilly/Brennan/Dykes/Houlding with citable terminology were located online — the circulating Lilly/Dykes material is practitioner/fan translation, so dignity-term citations rest on practitioner consensus (still HIGH by convergence, but not a single canonical book).

### (d) Suspected-but-unconfirmed (flagged, neither silently passed nor condemned)
- **Contraparallel/Parallel 对纬/合纬:** intelligible and possibly a deliberate compact coinage, but I could not confirm 对纬/合纬 in native astrology prose (which uses 逆平行/平行). Not a clear calque; flag for a native reviewer.
- **Illumination 照明度:** reads like the engineering term "illuminance"; suspected register-error but not a hard calque. Recommend 照亮比例; flag.
- **Axial Rotation 轴向旋转制:** literal rendering of a rare house system; no attested mainland form found to confirm or refute. Flag.
- **Ayanamsa 阿亚南萨 / Eclipses 食相 / Sign Ingresses 星座换座:** all "acceptable but I found stronger alternatives" — not calques, but flag for preference (岁差校正值 / 日月食 / 星座进入).
- **Nakshatra whole set:** genuine split between 宿曜 mansion names and Sanskrit transliteration in mainland 印占 — flagged above as a reviewer decision, not an error.