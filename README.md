# 🏛️ Enterprise, Venture & Commercial Valuation Engine
## High-Precision Cross-Platform AI Skill Suite & Computational Financial Architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Standard: McKinsey 8th Ed](https://img.shields.io/badge/Standard-McKinsey%208th%20Ed-navy.svg)](#theoretical-foundations)
[![Standards: UNIDO & Damodaran](https://img.shields.io/badge/Standards-UNIDO%20%7C%20Damodaran-orange.svg)](#theoretical-foundations)
[![Multi-Platform AI](https://img.shields.io/badge/AI%20Platforms-Claude%20%7C%20Cursor%20%7C%20Antigravity%20%7C%20Codex-success.svg)](#cross-platform-ai-compatibility)

---

## 📌 Table of Contents / فهرست مطالب
1. [English Documentation](#-english-documentation)
   - [Executive Overview](#1-executive-overview)
   - [Theoretical Foundations](#2-theoretical-foundations)
   - [Repository Architecture](#3-repository-architecture)
   - [Quickstart & CLI Usage](#4-quickstart--cli-usage)
   - [Cross-Platform AI Compatibility](#5-cross-platform-ai-compatibility)
   - [Verification & Automated Test Suite](#6-verification--automated-test-suite)
2. [راهنمای جامع فارسی (Persian Documentation)](#-راهنمای-جامع-به-زبان-فارسی)
   - [معرفی و چارچوب‌های استاندارد](#۱-معرفی-و-چارچوب‌های-استاندارد)
   - [ساختار مخزن و ماژول‌های محاسباتی](#۲-ساختار-مخزن-و-ماژول‌های-محاسباتی)
   - [راهنمای استفاده سریع از خط فرمان (CLI)](#۳-راهنمای-استفاده-سریع-از-خط-فرمان-cli)
   - [نحوه فعال‌سازی در ابزارهای هوش مصنوعی](#۴-نحوه-فعال‌سازی-در-ابزارهای-هوش-مصنوعی)

---

# 🌐 English Documentation

## 1. Executive Overview
**`enterprise-valuation-engine`** is an open-source, mathematically verified valuation architecture built to eliminate heuristic approximations in financial modeling. It executes peer-reviewed formulas across:
- **Corporate Enterprises:** McKinsey & Company (8th Edition - 2025/2026) Key Value Driver DCF, NOPAT adjustments, invested capital reconciliations, ROIC trees, Economic Profit (EVA), AI/digital Capex vs. Opex depreciation dynamics, and higher-for-longer cost of capital adjustments.
- **Mergers & Acquisitions and Acquired Assets (M&A):** Chris M. Mellen & Frank C. Evans (*Valuation for M&A: Building and Measuring Private Company Value*), 5 Levels of Value, risk-adjusted cost and revenue synergies, maximum walk-away purchase price, and ASC 805 / IFRS 3 Purchase Price Allocation (PPA).
- **Private Companies & Marketability Discounts:** Quantified Control Premiums, Discount for Lack of Control (DLOC), and Discount for Lack of Marketability (DLOM) using empirical benchmarks and Chaffe put option models.
- **Distressed Assets & Foreclosure Liquidation:** Orderly Liquidation Value (OLV) vs. Forced Liquidation Value (FLV / fire-sale), net realizable liquidation value (NRLV), and absolute priority claims distribution waterfalls.
- **Emerging & Distressed Debt:** Damodaran risk premiums, synthetic credit rating debt spreads, and dual-state distress overlays.
- **Early-Stage Tech & Ventures:** VC Method, Bill Payne Scorecard, Dave Berkus Method, First Chicago probability-weighted scenarios, and rigorous SaaS unit economics audits.
- **Commercial Projects & Trade:** UNIDO feasibility standards, dynamic Cash Conversion Cycle (CCC), CFADS, bankability debt covenants (DSCR $\ge 1.30x$, LLCR $\ge 1.40x$), and break-even thresholds.
- **Intellectual Property & Patents:** Relief-from-Royalty with Tax Amortization Benefits (TAB), Multi-Period Excess Earnings Method (MPEEM), and Black-Scholes Real Options.
- **Probabilistic Risk:** Monte Carlo simulation engine with Tornado sensitivity rankings.

---

## 2. Theoretical Foundations

### A. Corporate Enterprise Valuation (McKinsey 8th Ed.)
The core valuation equation connects cash flow, growth, and returns:
$$\text{Value} = \frac{\text{NOPAT}_{t+1} \times \left(1 - \frac{g}{\text{ROIC}}\right)}{\text{WACC} - g}$$

Invested Capital reconciliation:
$$\text{Invested Capital} = \text{Operating Cash} + \text{OWC} + \text{Net PP\&E} + \text{Capitalized R\&D} + \text{Capitalized Leases} - \text{NIBCL}$$

### B. High-Growth Tech & SaaS Unit Economics
- **LTV / CAC Ratio:** $\text{LTV} = \frac{\text{ARPU} \times \text{Gross Margin}}{\text{Churn Rate}} \implies \frac{\text{LTV}}{\text{CAC}} \ge 3.0x$
- **CAC Payback Period:** $\frac{\text{CAC}}{\text{Monthly Gross Profit per Account}} < 12 \text{ months}$
- **Rule of 40:** $\text{YoY Revenue Growth Rate} + \text{Free Cash Flow Margin} \ge 40\%$

### C. Commercial Trade & Project Feasibility (UNIDO)
- **Cash Conversion Cycle:** $\text{CCC} = \text{DSO} + \text{DIO} - \text{DPO}$
- **Debt Service Coverage Ratio:** $\text{DSCR}_t = \frac{\text{CFADS}_t}{\text{Debt Service}_t} \ge 1.30x$

### D. Patent & Technology Valuation
- **Relief-from-Royalty (with TAB):**
  $$\text{Value} = \left[ \sum_{t=1}^T \frac{\text{Revenue}_t \times r_{\text{royalty}} \times (1 - T)}{(1 + k_{\text{IP}})^t} \right] \times \text{TAB Factor}$$
- **Black-Scholes Real Options:**
  $$C = S \cdot N(d_1) - K \cdot e^{-rT} \cdot N(d_2)$$

---

## 3. Repository Architecture

```text
enterprise-valuation-engine/
├── .cursorrules                               # Cursor IDE AI agent instructions
├── .codex/
│   └── system_prompt.md                       # OpenAI Codex / GPT-4o / GPT-5 agent prompt
├── .claude/
│   └── skills/
│       ├── enterprise-valuation/SKILL.md      # Claude Code native corporate skill
│       └── mergers-acquisitions-valuation/    # Claude Code native M&A skill
├── .gemini/
│   └── skills/
│       ├── enterprise-valuation/SKILL.md      # Antigravity native corporate skill
│       └── mergers-acquisitions-valuation/    # Antigravity native M&A skill
├── skills/
│   ├── enterprise-valuation/                  # Universal Master Corporate Skill
│   │   ├── SKILL.md                           # Master workflow, triggers & execution logic
│   │   ├── scripts/
│   │   │   ├── dcf_mckinsey.py                # Enterprise DCF, NOPAT, Invested Capital, ROIC, WACC
│   │   │   ├── multiples_valuation.py         # EV/EBITDA, EV/EBIT, P/E, PEG, peer group regression
│   │   │   ├── startup_venture.py             # Scorecard, Berkus, VC Method, SaaS unit economics
│   │   │   ├── commercial_project.py          # Trade feasibility, CCC, DSCR, LLCR, IRR, NPV
│   │   │   ├── ip_patent_val.py               # Relief-from-Royalty, MPEEM, Black-Scholes Real Options
│   │   │   └── monte_carlo_simulator.py       # Probabilistic distribution & sensitivity engine
│   │   └── references/
│   │       ├── mckinsey_8th_edition_core.md   # Mathematical breakdown & AI/Capex/Cost of Capital updates
│   │       ├── damodaran_frameworks.md        # Risk premiums, synthetic debt, distressed assets
│   │       ├── commercial_trade_unido.md      # UNIDO trade & project feasibility standards
│   │       └── patent_intangible_ip.md        # IFRS 13, USPTO, and WIPO valuation methods
│   └── mergers-acquisitions-valuation/        # Universal Master M&A & Acquired Assets Skill
│       ├── SKILL.md                           # M&A workflow, triggers & 5 levels of value
│       ├── scripts/
│       │   ├── ma_synergy_valuation.py        # Cost/revenue synergy PV, haircut & walk-away price
│       │   ├── private_dlom_dloc.py           # DLOC, Chaffe option DLOM & 5 levels of value
│       │   ├── distressed_asset_liquidation.py# Orderly (OLV) vs. Forced (FLV) liquidation waterfall
│       │   └── accretion_dilution.py          # Pro-forma EPS accretion/dilution & financing mix
│       └── references/
│           ├── m_and_a_valuation_mellen_evans.md # Mellen & Evans, DLOC/DLOM, and Synergy haircuts
│           └── purchase_price_allocation_asc805.md # ASC 805 / IFRS 3 PPA & Intangible Fair Value
├── models/                                    # Ready-to-run JSON templates
│   ├── sample_corporate_dcf.json
│   ├── sample_peers_multiples.json
│   ├── sample_startup_saas.json
│   ├── sample_trade_project.json
│   ├── sample_patent_ip.json
│   ├── sample_monte_carlo.json
│   ├── sample_ma_transaction.json
│   └── sample_distressed_liquidation.json
└── tests/
    ├── test_valuation_engine.py               # Corporate, startup, patent, and simulation tests
    └── test_ma_valuation.py                   # M&A, synergy, DLOM/DLOC, and liquidation tests
```
│   ├── sample_trade_project.json
│   ├── sample_patent_ip.json
│   └── sample_monte_carlo.json
├── prompts/                                   # Plug-and-play prompts for various LLM interfaces
│   ├── claude_prompt.md
│   ├── cursor_prompt.md
│   └── chatgpt_prompt.md
├── tests/
│   └── test_valuation_engine.py               # Automated pytest/unittest suite verifying all math formulas
├── LICENSE                                    # MIT License
└── README.md                                  # Complete bilingual documentation & quickstart guide
```

---

## 4. Quickstart & CLI Usage

Run any engine standalone with standard Python 3 (zero heavy dependencies required):

```bash
# 1. Corporate Enterprise DCF (McKinsey 8th Ed.)
python skills/enterprise-valuation/scripts/dcf_mckinsey.py --input models/sample_corporate_dcf.json --format markdown

# 2. Comparable Company Multiples (Harmonic Mean & OLS Regression)
python skills/enterprise-valuation/scripts/multiples_valuation.py --input models/sample_peers_multiples.json --format markdown

# 3. Startup & Venture Capital Valuation (VC Method, Berkus, SaaS Diagnostics)
python skills/enterprise-valuation/scripts/startup_venture.py --input models/sample_startup_saas.json --format markdown

# 4. UNIDO Commercial Project Feasibility (CCC, CFADS, DSCR, LLCR, NPV, IRR)
python skills/enterprise-valuation/scripts/commercial_project.py --input models/sample_trade_project.json --format markdown

# 5. Intellectual Property & Patent Valuation (Relief-from-Royalty, MPEEM, Real Options)
python skills/enterprise-valuation/scripts/ip_patent_val.py --input models/sample_patent_ip.json --format markdown

# 6. Monte Carlo Stochastic Simulation & Tornado Sensitivity
python skills/enterprise-valuation/scripts/monte_carlo_simulator.py --input models/sample_monte_carlo.json --format markdown
```

---

## 5. Cross-Platform AI Compatibility

| AI Assistant / IDE | Native Discovery Path | How It Works |
| :--- | :--- | :--- |
| **Cursor IDE** | `.cursorrules` | Direct instruction injection into Composer & Agent |
| **Claude Code** | `.claude/skills/enterprise-valuation/SKILL.md` | Auto-detected skill in Claude workspace sessions |
| **Google Antigravity** | `.gemini/skills/enterprise-valuation/SKILL.md` | Auto-loaded native skill with CLI tool execution |
| **OpenAI Codex / GPT** | `.codex/system_prompt.md` | System prompt configuration for custom GPTs / API calls |
| **Windsurf / Cline** | `skills/enterprise-valuation/SKILL.md` | Open agent skill specification format |

---

## 6. Verification & Automated Test Suite

The mathematical models are audited through a comprehensive test suite verifying zero algorithmic drift:

```bash
python tests/test_valuation_engine.py
```

Expected output:
```text
...........
----------------------------------------------------------------------
Ran 11 tests in 0.001s

OK
```

---

# 🇮🇷 راهنمای جامع به زبان فارسی

## ۱. معرفی و چارچوب‌های استاندارد
موتور جامع ارزش‌گذاری دارایی‌ها و شرکت‌ها (**`enterprise-valuation-engine`**) یک سامانه محاسباتی تخصصی، متن‌باز و مبتنی بر استاندارد‌های بین‌المللی است که برای حذف خطاهای ناشی از تخمین‌های غیرعلمی در تصمیم‌گیری‌های مالی و سرمایه‌گذاری طراحی شده است.

این موتور بر پایه مراجع استاندارد و طراز اول مالی دنیا پیاده‌سازی شده است:
1. **ارزش‌گذاری شرکت‌های بزرگ و بالغ (ویرایش هشتم مکنزی - ۲۰۲۵/۲۰۲۶):** اثر تیم کولر و مکنزی با پوشش متغیرهای معاصر اقتصاد نظیر هوش مصنوعی (AI Capex vs Opex)، استهلاک شتابان چیپ‌های پردازشی، رژیم نوین نرخ بهره و هزینه سرمایه بالاتر.
2. **ارزش‌گذاری ادغام و تملیک (M&A) و دارایی‌های تملیکی:** بر اساس کتاب معتبر *Valuation for M&A: Building and Measuring Private Company Value* (تألیف کریس ملن و فرانک ایوانز) و استانداردهای حسابداری ASC 805 / IFRS 3 شامل هم‌افزایی درآمدی و هزینه‌ای، قیمت سقف تصاحب (Walk-away price)، و تخصیص قیمت خرید (PPA).
3. **ارزش‌گذاری شرکت‌های خصوصی و تخفیف‌های نقدشوندگی (DLOM / DLOC):** محاسبه ریاضی صرف کنترل و تخفیف عدم کنترل، و تخفیف عدم نقدشوندگی شرکت‌های خصوصی با مدل اختیار فروش Chaffe و شواهد سهام مقید.
4. **دارایی‌های تملیکی و شرایط اضطرار (Distressed & Liquidation):** ارزش انحلال با برنامه (OLV) و ارزش انحلال اجباری (FLV / حراج سریع) همراه با آبشار توزیع مطالبات با اولویت مطلق قانون ورشکستگی.
5. **ارزش‌گذاری استارتاپ‌ها و شرکت‌های داده‌محور:** مدل‌های سرمایه‌گذاری پرریسک (VC Method)، مدل کارت امتیازی (Bill Payne Scorecard)، مدل برکوس (Dave Berkus) و سلامت اقتصاد واحد (SaaS Unit Economics).
6. **امکان‌سنجی پروژه‌ها و تجارت بین‌الملل:** استانداردهای رسمی یونیدو (UNIDO)، چرخه تبدیل وجه نقد (CCC) و نسبت‌های پوشش بدهی بانکی (DSCR و LLCR).
7. **دارایی‌های نامشهود و پتنت‌ها:** روش صرفه‌جویی در حق امتیاز (Relief-from-Royalty) با احتساب مزیت استهلاک مالیاتی (TAB) و ارزش‌گذاری اختیارات واقعی با مدل بلک-شولز (Black-Scholes Real Options).
8. **ارزیابی ریسک با شبیه‌سازی مونت‌کارلو:** تحلیل آماری فواصل اطمینان و رتبه‌بندی حساسیت متغیرها با نمودار گردباد (Tornado Chart).

---

## ۲. ساختار مخزن و ماژول‌های محاسباتی

- **`dcf_mckinsey.py`:** محاسبه جریان نقد تنزیل‌شده، NOPAT، سرمایه به‌کارگرفته‌شده (Invested Capital)، بازده سرمایه (ROIC)، میانگین موزون هزینه سرمایه (WACC) و پل تطبیق ارزش بنگاه با حقوق صاحبان سهام.
- **`multiples_valuation.py`:** ارزش‌گذاری با ضرایب همگن و میانگین هارمونیک (به توصیه مکنزی برای جلوگیری از تورم آماری) و رگرسیون OLS.
- **`startup_venture.py`:** محاسبه ارزش قبل از سرمایه (Pre-Money) و پس از سرمایه (Post-Money)، رقت سهام در راندهای آتی و ممیزی شاخص‌های کلیدی SaaS (مانند LTV/CAC، دوره بازگشت CAC، قانون ۴۰ و نرخ حفظ درآمد خالص NRR).
- **`commercial_project.py`:** امکان‌سنجی صنعتی بر اساس فرمت UNIDO، جریان نقد قابل دسترس برای خدمات بدهی (CFADS)، ارزیابی وثیقه‌پذیری بانکی (DSCR $\ge 1.30$) و تحلیل نقطه سربه‌سر.
- **`ip_patent_val.py`:** ارزش‌گذاری حق اختراع و دارایی‌های نامشهود طبق استاندارد IFRS 13 و مدل اختیار معامله بلک-شولز.
- **`monte_carlo_simulator.py`:** اجرای شبیه‌سازی تصادفی چند هزار باره با توزیع‌های نرمال، مثلثی و یکنواخت برای استخراج صدک‌های P10، P50، P90 و ارزش در معرض ریسک (VaR).

---

## ۳. راهنمای استفاده سریع از خط فرمان (CLI)

تمامی اسکریپت‌ها با پایتون استاندارد (بدون نیاز به پکیج‌های حجیم سنگین) و با دستورات ساده خط فرمان قابل اجرا هستند:

```bash
# اجرای ارزش‌گذاری DCF مکنزی و تولید گزارش تفصیلی به فرمت Markdown
python skills/enterprise-valuation/scripts/dcf_mckinsey.py --input models/sample_corporate_dcf.json --format markdown

# اجرای ارزیابی استارتاپ و بررسی سلامت واحد اقتصادی
python skills/enterprise-valuation/scripts/startup_venture.py --input models/sample_startup_saas.json --format markdown

# اجرای امکان‌سنجی پروژه صنعتی و بررسی شاخص‌های بانکی UNIDO
python skills/enterprise-valuation/scripts/commercial_project.py --input models/sample_trade_project.json --format markdown

# ارزش‌گذاری دارایی نامشهود و پتنت با روش بلک‌شولز و Relief-from-Royalty
python skills/enterprise-valuation/scripts/ip_patent_val.py --input models/sample_patent_ip.json --format markdown

# اجرای شبیه‌سازی ریسک مونت‌کارلو و حساسیت‌سنجی
python skills/enterprise-valuation/scripts/monte_carlo_simulator.py --input models/sample_monte_carlo.json --format markdown
```

---

## ۴. نحوه فعال‌سازی در ابزارهای هوش مصنوعی

این بسته به گونه‌ای طراحی شده که توسط دستیاران هوشمند زیر به صورت خودکار شناسایی و استفاده شود:
- **Claude Code:** فایل مهارت در `.claude/skills/enterprise-valuation/SKILL.md` ذخیره شده است.
- **Google Antigravity:** فایل مهارت در `.gemini/skills/enterprise-valuation/SKILL.md` تعریف شده است.
- **Cursor IDE:** تنظیمات دقیق در `.cursorrules` قرار دارد تا هوش مصنوعی در محیط کدنویسی محاسبات را اجرا کند.
- **OpenAI Codex و ChatGPT:** پرامپت سیستمی آماده در `.codex/system_prompt.md` قرار دارد.
