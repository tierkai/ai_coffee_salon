# GitHub咖啡相关开源项目调研与AI咖啡知识沙龙系统借鉴分析

## 摘要与研究目标

围绕“知识库—制作工具—社区平台—数据分析”四条主线,本报告系统梳理GitHub上的咖啡相关开源生态,选取具有代表性的项目进行功能、技术与数据结构的深度剖析,并在此基础上提出面向AI咖啡知识沙龙系统的模块化集成方案与落地路线图。研究范围覆盖知识库与协作维基、配方与制作工具(含烘焙控制)、移动端应用、打印与票据输出、API与数据服务,以及数据分析与可视化。样本项目包括:Docmost(协作式维基)、escpos-coffee(Java票据打印)、coffee-recipe-tracker-api(Node.js配方追踪API)、Coffee Water Calculator(浏览器水质计算器PWA)、Artisan(烘焙HMI/Scope)、Arduino Controlled Coffee Roaster(Arduino烘焙控制)、AetherRoast(Python PID控制)、RoastGenie(烘焙PID与豆温测量)、CoffeeMobileApp(Kotlin/Android咖啡店移动应用)、wca-coffeetracker(React咖啡追踪器前端)、Coffee Sales数据分析与Coffee Export数据分析,以及若干咖啡/咖啡馆数据API项目(Flask、.NET等)。[^1][^2][^3][^4][^5][^6][^7][^8][^9][^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36]

本报告聚焦回答以下问题:生态全景与分类边界如何划分;各项目的功能特点、技术架构与数据结构设计;可复用到AI咖啡知识沙龙系统的模块与集成方式;烘焙控制与移动端/前端项目的架构启示;数据分析项目的方法论与可复用成果;知识库/维基与社区平台如何支撑知识沉淀与互动;以及在许可与维护性约束下的落地路线图与风险控制。

## 方法论与样本选择

本研究以GitHub主题页与官方文档为主要来源,辅以项目Wiki与示例仓库。样本纳入标准为:与咖啡知识、制作、社区或数据分析存在明确相关性;具备清晰的README或文档;技术栈可识别;数据结构或接口设计可获取;维护状态可评估。数据来源以项目主页与官方文档为主,避免依赖第三方非验证信息。局限性方面,少数仓库存在页面加载不完整或README缺失,导致技术细节难以核实;此外,烘焙硬件项目的PID参数、传感器型号与控制算法公开度不一,需在后续实测中补强。[^1][^2][^3][^4][^5][^6][^7][^8][^9][^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36]

## 生态全景与分类框架

从功能与使用场景出发,可将生态划分为六大类:知识库/维基;制作工具与烘焙控制;移动端应用;打印与票据输出;API与数据服务;数据分析与可视化。知识库/维基承载长期知识沉淀与协作;制作工具与烘焙控制连接物理世界与数据化曲线;移动端应用面向用户侧交互与行为记录;打印与票据输出打通线下场景;API与数据服务提供结构化数据能力;数据分析与可视化则将分散数据转化为洞察。

为便于整体把握,下表给出分类—项目—技术栈—许可证—最近更新的总览。为遵守报告格式规范,表中以参考编号标注来源,URL统一见文末参考文献。

表1 生态分类总览(项目—技术栈—许可证—最近更新—参考)

| 分类 | 代表项目 | 主要技术栈 | 许可证 | 最近更新时间(可得时) | 参考 |
|---|---|---|---|---|---|
| 知识库/维基 | Docmost | 开源协作维基/Docs | 未核验 | 未核验 | [^1] |
| 知识库/维基 | Gollum | Git-backed Wiki | 未核验 | 未核验 | [^2] |
| 制作工具/烘焙控制 | Artisan | HMI/Scope可视化 | 未核验 | 活跃(2024-11-26) | [^3] |
| 制作工具/烘焙控制 | Arduino Controlled Coffee Roaster | Arduino/TC4/Artisan协议 | 未核验 | 未核验 | [^4][^5][^6] |
| 制作工具/烘焙控制 | AetherRoast | Python PID控制 | 未核验 | 未核验 | [^7] |
| 制作工具/烘焙控制 | RoastGenie | PID + 豆温测量 | 未核验 | 未核验 | [^8] |
| 移动端应用 | CoffeeMobileApp | Kotlin/Android | 未核验 | 未核验 | [^9][^10][^11][^12] |
| 前端追踪器 | wca-coffeetracker | React/TypeScript SPA | 未核验 | 未核验 | [^13] |
| 打印/票据输出 | escpos-coffee | Java/ESC•POS | MIT | 活跃(2021后仍有维护) | [^14][^15][^16][^17][^18][^19][^20][^21] |
| 配方追踪API | coffee-recipe-tracker-api | Node.js/Express/Knex/JWT | 未核验 | 未核验 | [^22][^23][^24] |
| 数据API | cafe-api(多实现) | Flask/SQLAlchemy 或 .NET EF Core | 未核验 | 未核验 | [^25][^26][^27][^28][^29][^30] |
| 数据分析 | Coffee Sales | Excel/BI分析 | 未核验 | 未核验 | [^31][^32] |
| 数据分析 | Coffee Export | 全球出口数据分析 | 未核验 | 未核验 | [^33] |
| 制作工具(水质) | Coffee Water Calculator | HTML/JS(PWA) | 未核验 | 2025-08-01 | [^34][^35] |
| 制作工具(配比) | Espresso Time | 多冲泡方法配比计算 | 未核验 | 未核验 | [^36] |

从表1可见,生态呈现出“轻量工具—专业控制—前后端服务—数据洞察”的层次化结构:浏览器端轻量工具(如水质计算器)便于快速验证与教学;烘焙控制类项目与Artisan生态深度耦合;API层提供可复用的数据模型与鉴权机制;前端与移动端承载用户交互;打印库打通票据与线下服务;数据分析将运营与技艺转化为可视化与模型。知识库/维基则作为跨域基础设施,支撑体系化知识沉淀与协作。

## 重点项目深度分析

### escpos-coffee(Java ESC/POS打印库)

escpos-coffee提供面向ESC/POS指令的Java封装,支持文本、图像与多种条形码(含QR、PDF417)输出,并可配置多语言字符表。项目将所有命令写入OutputStream,天然支持跨平台输出重定向(打印机、文件、网络),便于在Linux、Windows、macOS与Android环境中统一集成。图像打印提供BitonalThreshold与有序抖动(BitonalOrderedDither)两类算法;文本样式支持字体大小、对齐、粗体等;票据排版可通过HTML/CSS生成并打印。项目遵循语义化版本(SemVer)与MIT许可,文档与示例完善,包含独立示例仓库与Wiki。[^14][^15][^16][^17][^18][^19][^20][^21]

为便于系统集成,表2与表3分别总结核心类/方法与功能矩阵。

表2 escpos-coffee核心类与方法一览

| 类/模块 | 关键方法/能力 | 说明 |
|---|---|---|
| EscPos | writeLF(), feed(), cut(), setCharacterCodeTable(), write(), close() | 核心命令序列,负责文本、换行、进纸、切割、字符表与关闭 |
| PrinterOutputStream | getListPrintServicesNames(), getPrintServiceByName() | 打印服务发现与绑定,支持跨平台 |
| Style | setFontSize(), setJustification() | 文本样式(字号、对齐) |
| BarCode | write() | 条形码写入(含QR/PDF417等) |
| ImageWrapper | setJustification() | 图像对齐与布局 |
| EscPosImage | 构造:EscPosImage(CoffeeImageImpl, algorithm) | 图像封装与抖动算法选择 |
| 字符表配置 | setCharacterCodeTable(…) | 多语言字符集(如CP863等) |

表3 escpos-coffee功能矩阵

| 功能域 | 支持要点 | 备注 |
|---|---|---|
| 文本 | 样式、对齐、进纸、换行、切割 | Style与EscPos组合 |
| 图像 | BitonalThreshold、OrderedDither | 适合低分辨率热敏打印 |
| 条形码 | Code128等常见码制、QR、PDF417 | 覆盖票据常见需求 |
| 字符表 | 多语言字符集配置 | 适配不同地区 |
| 输出重定向 | 打印机/文件/网络 | OutputStream抽象 |
| 票据排版 | HTML/CSS生成后打印 | 简化模板设计 |

集成建议:在AI咖啡知识沙龙系统中,escpos-coffee可用于活动签到凭证、配方卡片、课程结业证书与现场订单票据。考虑跨平台部署,推荐以服务化方式暴露打印接口(统一输出到OutputStream),同时在容器环境中封装驱动与CUPS(通用UNIX打印系统)配置,降低环境差异带来的不确定性。[^14][^15][^16][^17][^18][^19][^20][^21]

### coffee-recipe-tracker-api(Node.js/Express/Knex)

该项目为家庭咖啡制作提供配方追踪能力,支持对不同制作方式的参数记录与质量评级,帮助用户在迭代中优化口感。技术栈采用Node.js与Express,数据库抽象使用Knex,支持SQLite与PostgreSQL;认证使用JSON Web Tokens(JWT),密码哈希使用bcryptjs;并通过Jest与Supertest实现后端测试。数据验证通过Express中间件完成,迁移与种子数据由Knex管理。项目仓库包含API文档与数据模型说明,便于二次开发与对接。[^22][^23][^24]

表4 技术栈与依赖

| 组件 | 技术/库 |
|---|---|
| 运行时/框架 | Node.js / Express |
| 数据库/迁移 | Knex(SQLite/PostgreSQL) |
| 认证 | JWT |
| 安全 | bcryptjs |
| 测试 | Jest / Supertest |
| 验证 | Express中间件 |
| 默认端口 | 5000 |

表5 API端点类别与鉴权

| 端点类别 | 典型操作 | 鉴权 |
|---|---|---|
| 用户管理 | 注册/登录 | JWT |
| 配方管理 | 创建/读取/更新/删除 | JWT |
| 冲泡记录 | 记录参数与评分 | JWT |
| 评分与笔记 | 质量评级与备注 | JWT |
| 工具/预设 | 通用参数预设 | 视实现而定 |

表6 实体与关系(高层)

| 实体 | 关系 | 说明 |
|---|---|---|
| User | 1—N Records | 用户与冲泡记录 |
| Recipe | 1—N Records | 配方与记录 |
| Record | N—1 Recipe, N—1 User | 记录关联配方与用户 |
| Note/Review | 1—N Records | 记录附注与评分 |

借鉴意义:该API提供了配方—记录—评分—笔记的通用骨架,可直接复用到AI咖啡知识沙龙的知识图谱与个人学习路径中。Knex迁移与种子机制便于快速构建演示环境;JWT与bcryptjs为用户体系与隐私合规提供基础。[^22][^23][^24]

### Coffee Water Calculator(浏览器水质计算器PWA)

该项目面向冲泡用水的矿物配比计算,支持MgSO₄·7H₂O、NaHCO₃、CaCl、KHCO₄等储备溶液配置,基于目标离子浓度(ppm)计算每升所需添加体积,并输出总硬度与总碱度。技术实现为纯前端(HTML/JS),提供PWA离线能力、预设导入/导出与本地存储,适合教学与工作坊场景。部署方式灵活,可经GitHub Pages发布或本地直接打开。[^34][^35]

表7 储备溶液参数与目标水质指标

| 储备溶液 | 关键离子 | 目标指标(输入) |
|---|---|---|
| MgSO₄·7H₂O | Mg²⁺ | Mg²⁺ ppm |
| NaHCO₃ | Na⁺、HCO₃⁻ | Na⁺ ppm、HCO₃⁻(计算输出) |
| CaCl | Ca²⁺ | Ca²⁺ ppm |
| KHCO₃ | K⁺、HCO₃⁻ | K⁺ ppm、HCO₃⁻(计算输出) |

表8 输出指标说明

| 指标 | 含义 |
|---|---|
| 各储备溶液添加量(mL/L) | 达到目标离子浓度所需的体积 |
| 总硬度(CaCO₃计) | 反映水的硬度水平 |
| 总碱度(CaCO₃计) | 反映碳酸氢盐总量 |

在AI咖啡知识沙龙系统中,该模块可作为“水质与矿物配比计算”的教学工具,与配方追踪API联动,将水质参数作为配方记录的一部分,支持预设分享与工作坊离线使用。[^34][^35]

### Artisan与烘焙控制生态(Arduino/AetherRoast/RoastGenie)

Artisan作为烘焙HMI与Scope,支持曲线记录、分析与设备控制,并与 thermocouple 数据记录器或TC4等硬件生态协同工作。其可视化能力使 ET(环境温度)与 BT(豆温)等关键曲线得以实时呈现与回放。[^3] Arduino Controlled Coffee Roaster项目提供了与Artisan兼容的Arduino固件,支持将爆米花机改造成计算机控制的咖啡烘焙机,核心在于遵循Artisan通信协议并在ET/BT通道中正确配置设备。[^4][^5][^6] AetherRoast以Python实现模块化PID控制,包含自动温控、风机管理与可定制烘焙曲线;RoastGenie聚焦于在Gene Cafe等设备上实现PID控制与豆温测量,强调控制策略与传感布置的工程细节。[^7][^8]

表9 烘焙控制项目对比

| 项目 | 控制算法 | 传感器 | 接口/协议 | 可视化 | 维护状态 |
|---|---|---|---|---|---|
| Artisan | 软件HMI/Scope | 热电偶/TC4等 | 与TC4/设备通信 | 强 | 活跃(2024-11-26) |
| Arduino Roaster | PID/控制逻辑 | 热电偶(MAX6675等) | Artisan协议 | 依赖Artisan | 社区维护 |
| AetherRoast | Python PID | 温度/风机传感 | 可与Artisan或自建HMI | 自定义/可扩展 | 社区维护 |
| RoastGenie | PID + 豆温测量 | 豆温/环境温 | 与烘焙机适配 | 依赖生态 | 社区维护 |

集成建议:在AI咖啡知识沙龙系统中,可构建“烘焙数据接入层”,标准化ET/BT与设备状态事件,统一落库与可视化;对接Artisan导出的曲线数据或实时流式数据,用于课程演示与模型训练(如曲线特征点识别与烘焙度预测)。[^3][^4][^5][^6][^7][^8]

### CoffeeMobileApp(Kotlin/Android)

该项目为咖啡店移动应用模板,使用Kotlin与Android Studio构建,从构建脚本可见采用Hilt依赖注入与Google服务配置。仓库包含模块化结构与Gradle配置,便于扩展订单、会员与门店功能。尽管完整功能说明有限,但技术栈清晰,适合作为移动端基线模板。[^9][^10][^11][^12]

表10 关键Gradle模块与依赖

| 模块/配置 | 要点 |
|---|---|
| settings.gradle.kts | 项目结构与模块入口 |
| app/build.gradle.kts | 应用插件、Kotlin、Android、依赖 |
| google-services.json | Firebase/Google服务配置 |
| Hilt | 依赖注入(从构建脚本推断) |

表11 技术栈清单

| 组件 | 技术 |
|---|---|
| 语言/框架 | Kotlin / Android |
| 依赖注入 | Hilt(推断) |
| 云服务 | Google服务(配置存在) |
| 构建工具 | Gradle |

借鉴意义:该模板可快速搭建AI咖啡知识沙龙的移动端入口,结合配方追踪API与烘焙数据接入层,实现“课程签到—知识学习—实操记录—证书打印”的闭环体验。[^9][^10][^11][^12]

### wca-coffeetracker(React/TypeScript前端)

该项目为桌面优化的React SPA,提供咖啡记录、目标追踪与订阅等前端能力,适合作为Web端用户仪表盘与行为记录入口。数据结构与后端接口需结合API项目对齐,但其前端架构与交互模式可直接复用到知识沙龙系统的Web端。[^13]

### 咖啡/咖啡馆数据API项目(Flask/.NET等)

围绕“咖啡馆数据”出现了多种RESTful API实现:Flask+SQLAlchemy提供CRUD、搜索与安全删除;.NET 8.0版本提供咖啡消费追踪的Web API;另有SQLite+EF Core的ASP.NET Core实现与轻量数据API项目。这些实现语言不同、风格各异,但共同提供了实体抽象与端点组织范式,可作为知识沙龙系统数据服务层的参考或直接对接。[^25][^26][^27][^28][^29][^30]

表12 API项目对比

| 项目 | 技术栈 | 数据库 | 端点风格 | 鉴权 |
|---|---|---|---|---|
| cafe-RESTful-API-Development | Flask/SQLAlchemy | SQLite | CRUD/搜索/删除 | 未说明 |
| CoffeeTrackerWebApi | .NET 8.0 | 未说明 | 消费记录管理 | 未说明 |
| coffee-shop-api | ASP.NET Core/EF Core | SQLite | 咖啡店数据 | 未说明 |
| cafe-api(多实现) | Flask/.NET | SQLite/其他 | 随机/检索/更新 | 未说明 |
| coffee-data-api | 轻量实现 | 轻量DB | 少量端点 | 未说明 |

### 数据分析项目(Coffee Sales/Coffee Export)

Coffee Sales项目面向咖啡店销售数据的Excel/BI分析,目标是揭示销售趋势、爆款产品与时段性规律,属于典型运营分析范式。Coffee Export项目聚焦全球咖啡出口数据,跟踪主要出口国、目的地与贸易格局变化,为宏观洞察与供应链分析提供基础。两者方法论可迁移到知识沙龙系统的“课程参与度—转化率—满意度—社群活跃度”等指标体系构建。[^31][^32][^33]

表13 数据分析项目对比

| 项目 | 数据来源 | 方法 | 产出 | 可视化 |
|---|---|---|---|---|
| Coffee Sales | 销售明细 | 趋势/对比/分组 | 销售洞察 | BI/图表 |
| Coffee Export | 全球出口 | 地理/时序/结构 | 贸易格局 | 地图/时序 |

## 技术架构与数据结构设计模式

从样本项目可提炼出若干可复用的架构与数据模式:

- API层:Node.js/Express+Knex(JWT/bcryptjs)提供配方追踪与用户管理的成熟范式;迁移与种子机制便于快速迭代;.NET/Flask路径证明多语言等价实现的可行性。[^22][^23][^24][^25][^26][^27][^28][^29][^30]
- 前端层:React/TypeScript SPA适合桌面优化的行为记录与仪表盘;Android/Kotlin+Hilt适合移动端高频交互与离线缓存。[^13][^9][^10][^11][^12]
- 打印层:Java ESC/POS通过OutputStream抽象实现跨平台输出,图像抖动与字符表配置提升票据质量。[^14][^15][^16][^17][^18][^19][^20][^21]
- 烘焙控制层:Artisan作为HMI/Scope的事实标准,Arduino/Python项目提供设备侧控制与数据采集,ET/BT曲线是共同语言。[^3][^4][^5][^6][^7][^8]
- PWA工具层:浏览器端水质计算器以轻量、可离线、预设共享为特色,适合教学与工作坊。[^34][^35]

表14 架构模式映射

| 场景 | 技术栈 | 关键组件 | 可复用性 |
|---|---|---|---|
| 配方追踪API | Node.js/Express/Knex | JWT、bcryptjs、迁移/种子 | 高 |
| Web前端 | React/TS SPA | 路由、状态管理、图表 | 高 |
| 移动端 | Kotlin/Android | Hilt、网络/存储 | 中-高 |
| 打印服务 | Java ESC/POS | OutputStream、样式/图像 | 高 |
| 烘焙控制 | Artisan+Arduino/Python | ET/BT曲线、PID | 中(需硬件) |
| 轻量工具 | PWA(HTML/JS) | 预设、离线、导入/导出 | 高 |

数据结构方面,配方追踪API的“配方—记录—评分—笔记”模型覆盖了个体学习的关键闭环;咖啡馆数据API的“店铺—商品—价格—地理属性”等实体可扩展为“门店—课程—讲师—活动—签到”的活动域模型;烘焙数据的“时间序列—事件点(开始/一爆/二爆/出锅)—设备状态”适合时间序列库与事件表存储,并以曲线特征工程支撑模型训练与课程演示。[^22][^23][^24][^25][^26][^27][^28][^29][^30][^3][^4][^5][^6][^7][^8]

表15 实体—关系高层设计

| 领域 | 核心实体 | 关系 | 说明 |
|---|---|---|---|
| 配方与记录 | User、Recipe、Record、Note/Review | User—Record、Recipe—Record | 评分与笔记增强迭代 |
| 咖啡馆数据 | Cafe、Product、Price、Location | Cafe—Product、Product—Price | 适配门店/课程运营 |
| 烘焙数据 | RoastSession、Curve(ET/BT)、Event | Session—Curve、Curve—Event | 一爆/二爆等事件标注 |

## 可借鉴功能模块与AI咖啡知识沙龙系统集成方案

围绕“知识沉淀—工具赋能—数据洞察—线下闭环”,建议采用模块化集成策略:

- 知识库与协作:引入Docmost或基于Gollum的Git维基,承载课程教材、标准配方、SOP与FAQ;与GitHub Wiki机制一致的编辑流程可降低学习成本。[^1][^2][^37][^38][^39][^40]
- 配方追踪API:采用Node.js/Express+Knex骨架,支持JWT与bcryptjs,作为系统“个人学习与记录”域的底座。[^22][^23][^24]
- 水质计算器:以PWA形式内嵌Web端与移动端WebView,支持预设分享与离线教学。[^34][^35]
- 打印服务:基于escpos-coffee输出活动票据、证书与配方卡片,统一OutputStream对接不同打印后端。[^14][^15][^16][^17][^18][^19][^20][^21]
- 移动端与Web前端:Android(Kotlin)与React TS分别承载移动与桌面端交互,连接API与数据接入层。[^9][^10][^11][^12][^13]
- 烘焙数据接入:对接Artisan生态或自建采集服务,标准化ET/BT曲线与事件标注,用于课程演示与模型训练。[^3][^4][^5][^6][^7][^8]
- 数据分析与可视化:复用Coffee Sales/Export范式,构建“参与度—转化—满意度—活跃度”仪表盘,支撑运营与教学改进。[^31][^32][^33]

表16 功能模块映射

| 模块 | 对应项目 | 集成接口 | 数据流 | 优先级 |
|---|---|---|---|---|
| 知识库/协作 | Docmost/Gollum | Web/SDK | 文档—版本—评论 | 高 |
| 配方追踪API | coffee-recipe-tracker-api | REST/JWT | 用户—配方—记录—评分 | 高 |
| 水质计算器 | Coffee Water Calculator | Web嵌入/PWA | 预设—计算—导出 | 中 |
| 打印服务 | escpos-coffee | 服务化API | 票据—OutputStream—设备 | 中 |
| 移动端 | CoffeeMobileApp | HTTP/本地存储 | 登录—记录—同步 | 中 |
| Web前端 | wca-coffeetracker | REST | 仪表盘—图表—导出 | 中 |
| 烘焙接入 | Artisan/Arduino/AetherRoast/RoastGenie | 文件/流 | 曲线—事件—特征 | 中 |
| 分析可视化 | Coffee Sales/Export | 批处理/BI | 指标—图表—洞察 | 中 |

## 实施路线图与风险控制

建议分阶段推进,先以“知识库+API+前端”构建最小可用系统(MVP),再迭代接入移动端与打印服务,最后引入烘焙数据接入与数据分析。

表17 实施路线图

| 阶段 | 里程碑 | 交付物 | 依赖 | 验收标准 |
|---|---|---|---|---|
| MVP | 知识库上线 | Docmost/Gollum、基础文档 | 容器/存储 | 文档可检索、可协作 |
| MVP | 配方API可用 | Express+Knex、JWT | 数据库 | 注册/登录/记录/评分 |
| MVP | Web前端仪表盘 | React TS | API | 记录展示、目标追踪 |
| 迭代 | 移动端 | Kotlin/Android | API/缓存 | 登录、记录、离线缓存 |
| 迭代 | 打印服务 | escpos-coffee | 打印后端 | 票据/证书稳定输出 |
| 迭代 | 烘焙接入 | Artisan/自建采集 | 硬件/驱动 | ET/BT曲线可视化 |
| 迭代 | 数据分析 | 指标与图表 | 数据仓库 | 仪表盘上线、周期报表 |

风险与缓解:
- 许可与合规:escpos-coffee为MIT许可,其他项目需逐一核验;对外API需明确鉴权与数据使用边界。[^14][^15][^16][^17][^18][^19][^20][^21]
- 维护性:多语言与多仓库并存,需建立模块化接口与契约测试,避免耦合扩散。[^22][^25][^26][^27][^28][^29][^30]
- 硬件依赖:烘焙控制依赖传感器与设备驱动,需准备仿真/回放方案以降低测试成本。[^3][^4][^5][^6][^7][^8]
- 数据质量:分析模块依赖数据治理与指标口径统一,需建立数据字典与质量监控。[^31][^32][^33]

## 结论与后续工作

本次调研显示,GitHub咖啡生态已形成从知识沉淀、制作工具、移动端、打印到数据服务的完整链条。面向AI咖啡知识沙龙系统,最具性价比的集成路径是:以Docmost/Gollum承载知识库;以Express+Knex承载配方追踪API;以React/Kotlin承载用户交互;以escpos-coffee打通线下票据;以PWA水质计算器赋能教学工作坊;以Artisan/Arduino等生态承接烘焙数据,最终以数据分析闭环驱动运营与教学优化。[^1][^22][^34][^14][^3]

后续工作建议:补齐样本项目的许可证核验与维护状态评估;扩展社区平台与知识图谱的联动;在真实设备与多打印后端环境中验证稳定性;建立烘焙曲线特征工程与模型库;完善数据治理与隐私合规(特别是用户记录与打印日志的脱敏与留存策略)。

---

## 参考文献

[^1]: Docmost - Open-source collaborative wiki and documentation software. https://github.com/Docmost/docmost  
[^2]: Gollum - A simple, Git-powered wiki. https://github.com/gollum/gollum  
[^3]: Visual scope for coffee roasters - Artisan. https://github.com/DCodius/artisan-roastery-hmi  
[^4]: Arduino Controlled Coffee Roaster. https://github.com/lukeinator42/coffee-roaster  
[^5]: coffee-roaster log: roasting-profile.alog. https://github.com/lukeinator42/coffee-roaster/blob/master/logs/roasting-profile.alog  
[^6]: coffee-roaster README. https://github.com/lukeinator42/coffee-roaster/blob/master/README.md  
[^7]: AetherRoast - Python-based PID control for coffee roasting. https://github.com/czseventeen/AetherRoast  
[^8]: RoastGenie - PID Control + Bean Mass Temperature Measurement. https://github.com/evquink/RoastGenie  
[^9]: Coffee Shop Mobile App with Kotlin and Android Studio. https://github.com/ossbk/CoffeeMobileApp  
[^10]: CoffeeMobileApp README. https://github.com/ossbk/CoffeeMobileApp/blob/master/README.md  
[^11]: CoffeeMobileApp settings.gradle.kts. https://github.com/ossbk/CoffeeMobileApp/blob/master/settings.gradle.kts  
[^12]: CoffeeMobileApp app/build.gradle.kts. https://github.com/ossbk/CoffeeMobileApp/blob/master/app/build.gradle.kts  
[^13]: wca-coffeetracker - React coffee tracker frontend. https://github.com/WaffleCodeApp/wca-coffeetracker  
[^14]: escpos-coffee - Java library for ESC/POS printer. https://github.com/anastaciocintra/escpos-coffee  
[^15]: escpos-coffee Wiki. https://github.com/anastaciocintra/escpos-coffee/wiki  
[^16]: escpos-coffee-samples. https://github.com/anastaciocintra/escpos-coffee-samples  
[^17]: escpos-coffee project site. https://anastaciocintra.github.io/escpos-coffee  
[^18]: Maven Central: escpos-coffee 4.0.1. https://central.sonatype.com/artifact/com.github.anastaciocintra/escpos-coffee/4.0.1  
[^19]: Maven Repository: escpos-coffee. https://mvnrepository.com/artifact/com.github.anastaciocintra/escpos-coffee  
[^20]: escpos-coffee-samples: CoffeeBitmap.java. https://github.com/anastaciocintra/escpos-coffee-samples/blob/master/misCELLaneous/CoffeeBitmap/src/main/java/CoffeeBitmap.java  
[^21]: escpos-coffee Wiki - Character Code Table. https://github-wiki-see.page/m/anastaciocintra/escpos-coffee/wiki/Character-Code-Table  
[^22]: coffee-recipe-tracker-api. https://github.com/no-deadline/coffee-recipe-tracker-api  
[^23]: Coffee Recipe Tracker API Docs. https://github.com/daveskull81/coffee-recipe-tracker-api/blob/master/docs/APIDOCS.md  
[^24]: Coffee Recipe Tracker Data Model. https://github.com/daveskull81/coffee-recipe-tracker-api/blob/master/docs/DATAMODEL.md  
[^25]: cafe-RESTful-API-Development (Flask/SQLAlchemy). https://github.com/cesardeltoral/cafe-RESTful-API-Development  
[^26]: Coffee Tracker Web API (.NET 8.0). https://github.com/DLee211/CoffeeTrackerWebApi  
[^27]: coffee-shop-api (ASP.NET Core/EF Core/SQLite). https://github.com/alex-alaliwi/coffee-shop-api  
[^28]: cafe-api (Flask). https://github.com/matanohana433/cafe-api  
[^29]: cafe-api (Flask) - random cafe, location search. https://github.com/Screachail/cafe-api  
[^30]: coffee-data-api. https://github.com/raspberry5442/coffee-data-api  
[^31]: Coffee Sales — Professional Data Science Project. https://github.com/mehmetkayia/coffee-shop-business-intelligence  
[^32]: Coffee Sales Data Analysis (Excel Project). https://github.com/gloriatheanalyst/coffee-sales-analysis  
[^33]: coffee-export-project. https://github.com/quangnhat1504/coffee-export-project  
[^34]: Coffee Water Calculator. https://github.com/cseka7/coffeewatercalculator  
[^35]: Coffee Water Calculator (Demo). https://cseka7.github.io/coffeewatercalculator/  
[^36]: Espresso Time - Coffee Scripts Repository. https://github.com/mr-pablinho/espresso-time  
[^37]: GitHub Docs: About wikis. https://docs.github.com/en/community/documenting-your-project-with-wikis/about-wikis  
[^38]: What is a GitHub Wiki and How Do You Use it? https://www.freecodecamp.org/news/what-is-a-github-wiki-and-how-do-you-use-it/  
[^39]: How I Use GitHub’s Wiki Feature for API Documentation. https://medium.com/@stephanemcbride/how-i-use-github-s-wiki-feature-for-api-documentation-996a640d270  
[^40]: GitHub Topics: coffee. https://github.com/topics/coffee