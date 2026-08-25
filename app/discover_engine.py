import math
from typing import Dict, Any, List, Optional, Tuple

def get_yahoo_finance_url(ticker: str) -> str:
    """Safely generate an authoritative Yahoo Finance quote link for manual investor verification."""
    clean_ticker = ticker.strip().upper()
    return f"https://finance.yahoo.com/quote/{clean_ticker}/"

# Comprehensive, Institutionally Curated Global Asset Universe (45+ Assets)
GLOBAL_ASSET_UNIVERSE: List[Dict[str, Any]] = [
    # US MEGA-CAP TECH & AI MONOPOLIES
    {
        "ticker": "NVDA",
        "name": "NVIDIA Corporation",
        "market": "US",
        "country": "United States",
        "asset_type": "STOCK",
        "style": ["GROWTH", "QUALITY", "MOMENTUM", "MULTIBAGGER"],
        "sector": "Semiconductors & AI Hardware",
        "industry": "Semiconductors",
        "market_cap_usd": 3250.0,
        "price_usd": 132.50,
        "currency": "USD",
        "pe": 42.8,
        "fwd_pe": 31.5,
        "pe_10y_median": 38.0,
        "ev_ebitda": 36.2,
        "p_fcf": 45.0,
        "fcf_yield": 2.2,
        "pb_ratio": 48.0,
        "roic": 68.5,
        "roe": 72.0,
        "fcf_margin": 44.5,
        "rev_growth_cagr_3y": 85.0,
        "eps_growth_cagr_3y": 115.0,
        "debt_to_ebitda": 0.2,
        "div_yield": 0.03,
        "momentum_1y": 165.0,
        "drawdown_ath": -8.5,
        "volatility_1y": 44.0,
        "risk_level": "HIGH",
        "tam_runway_score": 95,
        "moat_score": 96,
        "capital_efficiency_score": 95,
        "balance_sheet_score": 92,
        "themes": ["AI", "Semiconductors", "Cloud", "Robotics", "Automation"],
        "why_interesting": "Monopoli arsitektur GPU AI & ekosistem software CUDA dengan moat switching-cost tertinggi.",
        "what_could_go_wrong": "Normalisasi belanja capex hyperscaler & munculnya custom ASIC in-house oleh Big Tech.",
        "invalidation_conditions": "Pertumbuhan revenue kuartalan melambat di bawah 20% YoY atau margin kotor turun di bawah 65%.",
        "turnaround_thesis": None,
        "bull_case_usd": 220.0,
        "base_case_usd": 150.0,
        "bear_case_usd": 85.0,
        "valuation_type": "Misunderstood Growth",
        "catalysts": "Peluncuran arsitektur Blackwell & monetisasi Enterprise AI agent.",
        "risks": "Regulasi ekspor AS-China & siklus capex semikonduktor."
    },
    {
        "ticker": "TSM",
        "name": "Taiwan Semiconductor Manufacturing",
        "market": "ASIA",
        "country": "Taiwan",
        "asset_type": "STOCK",
        "style": ["QUALITY", "GROWTH", "VALUE"],
        "sector": "Semiconductors & Foundry",
        "industry": "Foundry",
        "market_cap_usd": 950.0,
        "price_usd": 194.50,
        "currency": "USD",
        "pe": 30.5,
        "fwd_pe": 22.8,
        "pe_10y_median": 23.5,
        "ev_ebitda": 14.5,
        "p_fcf": 28.0,
        "fcf_yield": 3.6,
        "pb_ratio": 7.2,
        "roic": 29.5,
        "roe": 31.0,
        "fcf_margin": 32.0,
        "rev_growth_cagr_3y": 24.0,
        "eps_growth_cagr_3y": 28.0,
        "debt_to_ebitda": 0.4,
        "div_yield": 1.25,
        "momentum_1y": 82.0,
        "drawdown_ath": -6.2,
        "volatility_1y": 29.5,
        "risk_level": "MEDIUM",
        "tam_runway_score": 92,
        "moat_score": 98,
        "capital_efficiency_score": 91,
        "balance_sheet_score": 94,
        "themes": ["Semiconductors", "AI", "Cloud", "Automation"],
        "why_interesting": "Memproduksi >90% chip komputasi tercanggih dunia (<3nm) untuk Apple, Nvidia, AMD, dan Qualcomm.",
        "what_could_go_wrong": "Eskalasi geopolitik Selat Taiwan atau gempa bumi besar di kawasan Hsinchu.",
        "invalidation_conditions": "Pesaing seperti Intel Foundry atau Samsung merebut >15% pangsa pasar node sub-3nm.",
        "turnaround_thesis": None,
        "bull_case_usd": 270.0,
        "base_case_usd": 215.0,
        "bear_case_usd": 125.0,
        "valuation_type": "Undervalued Quality",
        "catalysts": "Ramp-up kapasitas 2nm GAA (N2) & pricing power kenaikan harga wafer.",
        "risks": "Konsentrasi geografis Taiwan & biaya ekspansi fab luar negeri (Arizona/Jepang)."
    },
    {
        "ticker": "ASML",
        "name": "ASML Holding N.V.",
        "market": "EU",
        "country": "Netherlands",
        "asset_type": "STOCK",
        "style": ["QUALITY", "GROWTH", "VALUE"],
        "sector": "Semiconductors & Equipment",
        "industry": "Lithography",
        "market_cap_usd": 285.0,
        "price_usd": 715.40,
        "currency": "USD",
        "pe": 41.5,
        "fwd_pe": 28.2,
        "pe_10y_median": 34.0,
        "ev_ebitda": 26.0,
        "p_fcf": 35.0,
        "fcf_yield": 2.8,
        "pb_ratio": 18.0,
        "roic": 42.0,
        "roe": 48.0,
        "fcf_margin": 26.5,
        "rev_growth_cagr_3y": 19.5,
        "eps_growth_cagr_3y": 24.0,
        "debt_to_ebitda": 0.3,
        "div_yield": 0.95,
        "momentum_1y": 18.0,
        "drawdown_ath": -34.5,
        "volatility_1y": 31.5,
        "risk_level": "MEDIUM",
        "tam_runway_score": 88,
        "moat_score": 99,
        "capital_efficiency_score": 93,
        "balance_sheet_score": 95,
        "themes": ["Semiconductors", "AI", "Infrastructure", "Automation"],
        "why_interesting": "Monopoli 100% mesin litografi EUV & High-NA EUV dunia. Tidak ada chip canggih tanpa mesin ASML.",
        "what_could_go_wrong": "Pembatasan izin ekspor mesin DUV ke pasar China oleh pemerintah Belanda & AS.",
        "invalidation_conditions": "Teknologi nanoimprint atau alternatif litho berhasil memproduksi node <2nm secara komersial.",
        "turnaround_thesis": "Koreksi -34% dari ATH akibat penundaan capex foundry non-AI menciptakan peluang beli diskon.",
        "bull_case_usd": 1100.0,
        "base_case_usd": 880.0,
        "bear_case_usd": 550.0,
        "valuation_type": "Deep Discount Quality",
        "catalysts": "Adopsi massal High-NA EUV (EXE:5000) oleh TSMC & siklus rebound memori HBM 2026/2027.",
        "risks": "Siklus pesanan non-AI fab yang lebih lambat dari proyeksi."
    },
    {
        "ticker": "AVGO",
        "name": "Broadcom Inc.",
        "market": "US",
        "country": "United States",
        "asset_type": "STOCK",
        "style": ["QUALITY", "GROWTH", "MULTIBAGGER"],
        "sector": "Custom AI ASIC & Networking",
        "industry": "Semiconductors",
        "market_cap_usd": 1020.0,
        "price_usd": 218.40,
        "currency": "USD",
        "pe": 61.3,
        "fwd_pe": 28.5,
        "pe_10y_median": 26.0,
        "ev_ebitda": 25.0,
        "p_fcf": 32.0,
        "fcf_yield": 3.1,
        "pb_ratio": 14.5,
        "roic": 26.0,
        "roe": 34.0,
        "fcf_margin": 45.0,
        "rev_growth_cagr_3y": 38.0,
        "eps_growth_cagr_3y": 42.0,
        "debt_to_ebitda": 1.8,
        "div_yield": 1.2,
        "momentum_1y": 88.0,
        "drawdown_ath": -8.0,
        "volatility_1y": 32.0,
        "risk_level": "MEDIUM",
        "tam_runway_score": 93,
        "moat_score": 95,
        "capital_efficiency_score": 94,
        "balance_sheet_score": 88,
        "themes": ["AI", "Semiconductors", "Cloud", "Cybersecurity"],
        "why_interesting": "Raja custom AI ASIC (partner utama Google TPU, Meta MTIA, dan OpenAI) serta monopoli networking switch Ethernet data center (Tomahawk).",
        "what_could_go_wrong": "Integrasi VMware yang rumit atau pelanggan hyperscaler beralih ke vendor ASIC lain (Marvell).",
        "invalidation_conditions": "Kehilangan kontrak custom ASIC dari salah satu Top 3 hyperscaler.",
        "turnaround_thesis": None,
        "bull_case_usd": 310.0,
        "base_case_usd": 250.0,
        "bear_case_usd": 160.0,
        "valuation_type": "Elite AI Compounder",
        "catalysts": "Rilis chip custom ASIC 3nm generasi baru & sinergi subscription VMware.",
        "risks": "Beban utang pasca akuisisi VMware $69B."
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "market": "US",
        "country": "United States",
        "asset_type": "STOCK",
        "style": ["QUALITY", "GROWTH"],
        "sector": "Software & Cloud AI",
        "industry": "Enterprise Software",
        "market_cap_usd": 3100.0,
        "price_usd": 412.30,
        "currency": "USD",
        "pe": 31.5,
        "fwd_pe": 27.5,
        "pe_10y_median": 29.5,
        "ev_ebitda": 21.0,
        "p_fcf": 32.0,
        "fcf_yield": 3.1,
        "pb_ratio": 11.5,
        "roic": 31.2,
        "roe": 36.5,
        "fcf_margin": 33.0,
        "rev_growth_cagr_3y": 14.5,
        "eps_growth_cagr_3y": 18.0,
        "debt_to_ebitda": 0.5,
        "div_yield": 0.78,
        "momentum_1y": 22.0,
        "drawdown_ath": -11.0,
        "volatility_1y": 22.5,
        "risk_level": "LOW",
        "tam_runway_score": 90,
        "moat_score": 97,
        "capital_efficiency_score": 92,
        "balance_sheet_score": 98,
        "themes": ["Cloud", "AI", "Cybersecurity", "Enterprise"],
        "why_interesting": "Pondasi komputasi enterprise dunia (Azure Cloud, Office 365, Copilot, GitHub, Windows).",
        "what_could_go_wrong": "Margin kompresi akibat capex AI data center yang masif sebelum revenue AI fully monetized.",
        "invalidation_conditions": "Azure revenue growth melambat di bawah 15% YoY secara berkelanjutan.",
        "turnaround_thesis": None,
        "bull_case_usd": 550.0,
        "base_case_usd": 460.0,
        "bear_case_usd": 320.0,
        "valuation_type": "Quality Compounder",
        "catalysts": "Akselerasi adopsi Copilot 365 di tier korporasi Fortune 500.",
        "risks": "Investasi energi/nuklir dan amortisasi server AI menekan margin operasi jangka pendek."
    },
    {
        "ticker": "GOOGL",
        "name": "Alphabet Inc.",
        "market": "US",
        "country": "United States",
        "asset_type": "STOCK",
        "style": ["VALUE", "QUALITY", "GROWTH"],
        "sector": "Internet & Digital Advertising",
        "industry": "Search & Cloud",
        "market_cap_usd": 2250.0,
        "price_usd": 184.25,
        "currency": "USD",
        "pe": 20.8,
        "fwd_pe": 18.2,
        "pe_10y_median": 25.5,
        "ev_ebitda": 14.0,
        "p_fcf": 22.5,
        "fcf_yield": 4.4,
        "pb_ratio": 6.8,
        "roic": 28.5,
        "roe": 31.0,
        "fcf_margin": 27.5,
        "rev_growth_cagr_3y": 12.5,
        "eps_growth_cagr_3y": 24.5,
        "debt_to_ebitda": 0.1,
        "div_yield": 0.45,
        "momentum_1y": 32.0,
        "drawdown_ath": -7.5,
        "volatility_1y": 24.5,
        "risk_level": "LOW",
        "tam_runway_score": 85,
        "moat_score": 93,
        "capital_efficiency_score": 90,
        "balance_sheet_score": 99,
        "themes": ["AI", "Cloud", "Digital Ads", "Autonomous"],
        "why_interesting": "Valuasi termurah di antara Big Tech US (P/E ~20x) dengan neraca kas >$100B, Google Cloud profitable, dan model AI Gemini.",
        "what_could_go_wrong": "Gugatan antimonopoli DOJ AS yang memaksa pemecahan Chrome/Android atau disrupsi pencarian oleh AI chatbot.",
        "invalidation_conditions": "Pangsa pasar Google Search global turun di bawah 80% (saat ini ~90%).",
        "turnaround_thesis": None,
        "bull_case_usd": 260.0,
        "base_case_usd": 215.0,
        "bear_case_usd": 145.0,
        "valuation_type": "Potentially Undervalued",
        "catalysts": "Monetisasi AI Overviews, efisiensi custom TPU v6, dan komputasi Waymo robotaxi.",
        "risks": "Regulasi antimonopoli Departemen Kehakiman AS (DOJ)."
    },
    {
        "ticker": "PLTR",
        "name": "Palantir Technologies Inc.",
        "market": "US",
        "country": "United States",
        "asset_type": "STOCK",
        "style": ["GROWTH", "MOMENTUM", "MULTIBAGGER"],
        "sector": "Enterprise AI & Defense Software",
        "industry": "Software",
        "market_cap_usd": 145.0,
        "price_usd": 64.80,
        "currency": "USD",
        "pe": 95.0,
        "fwd_pe": 68.0,
        "pe_10y_median": 80.0,
        "ev_ebitda": 62.0,
        "p_fcf": 75.0,
        "fcf_yield": 1.3,
        "pb_ratio": 24.0,
        "roic": 22.0,
        "roe": 24.0,
        "fcf_margin": 38.0,
        "rev_growth_cagr_3y": 28.0,
        "eps_growth_cagr_3y": 80.0,
        "debt_to_ebitda": 0.0,
        "div_yield": 0.0,
        "momentum_1y": 180.0,
        "drawdown_ath": -5.0,
        "volatility_1y": 55.0,
        "risk_level": "HIGH",
        "tam_runway_score": 94,
        "moat_score": 92,
        "capital_efficiency_score": 88,
        "balance_sheet_score": 96,
        "themes": ["AI", "Defense", "Cybersecurity", "Cloud"],
        "why_interesting": "Platform Artificial Intelligence Platform (AIP) menjadi standar de facto software ontologi militer AS dan korporasi global.",
        "what_could_go_wrong": "Valuasi multiple P/E >60x rentan kompresi drastis jika pertumbuhan revenue komersial melambat.",
        "invalidation_conditions": "Pertumbuhan pelanggan komersial AS turun di bawah 30% YoY.",
        "turnaround_thesis": None,
        "bull_case_usd": 120.0,
        "base_case_usd": 70.0,
        "bear_case_usd": 32.0,
        "valuation_type": "High Valuation / Momentum Leader",
        "catalysts": "Kontrak pertahanan Pentagon Project Maven & ekspansi adopsi AIP di sektor perbankan/kesehatan.",
        "risks": "Multiple valuasi yang sangat mahal menuntut eksekusi tanpa celah."
    },
    {
        "ticker": "CEG",
        "name": "Constellation Energy Corp",
        "market": "US",
        "country": "United States",
        "asset_type": "STOCK",
        "style": ["GROWTH", "QUALITY", "MULTIBAGGER"],
        "sector": "Clean Energy & Nuclear Power",
        "industry": "Utilities & Power",
        "market_cap_usd": 90.0,
        "price_usd": 285.0,
        "currency": "USD",
        "pe": 26.5,
        "fwd_pe": 22.0,
        "pe_10y_median": 20.0,
        "ev_ebitda": 15.0,
        "p_fcf": 20.0,
        "fcf_yield": 5.0,
        "pb_ratio": 5.8,
        "roic": 18.5,
        "roe": 22.0,
        "fcf_margin": 19.0,
        "rev_growth_cagr_3y": 32.0,
        "eps_growth_cagr_3y": 45.0,
        "debt_to_ebitda": 1.6,
        "div_yield": 0.55,
        "momentum_1y": 140.0,
        "drawdown_ath": -12.0,
        "volatility_1y": 31.0,
        "risk_level": "MEDIUM",
        "tam_runway_score": 93,
        "moat_score": 94,
        "capital_efficiency_score": 86,
        "balance_sheet_score": 85,
        "themes": ["Nuclear", "Energy", "AI", "Infrastructure"],
        "why_interesting": "Pemilik armada reaktor nuklir terbesar di AS. Menandatangani kontrak pasokan listrik 20 tahun eksklusif ke Microsoft data center.",
        "what_could_go_wrong": "Regulasi FERC mengenai interkoneksi co-located data center pada pembangkit nuklir.",
        "invalidation_conditions": "Regulator membatasi tarif premium PPA nuklir untuk data center swasta.",
        "turnaround_thesis": None,
        "bull_case_usd": 420.0,
        "base_case_usd": 320.0,
        "bear_case_usd": 190.0,
        "valuation_type": "Thematic Growth Leader",
        "catalysts": "Reaktivasi Three Mile Island (Crane Clean Energy Center) & kontrak baru dengan hyperscaler lain.",
        "risks": "Perubahan kebijakan komisi energi federal (FERC)."
    },
    {
        "ticker": "CCJ",
        "name": "Cameco Corporation",
        "market": "US",
        "country": "Canada / US",
        "asset_type": "STOCK",
        "style": ["GROWTH", "MULTIBAGGER"],
        "sector": "Uranium Mining & Nuclear Fuel",
        "industry": "Commodities",
        "market_cap_usd": 25.0,
        "price_usd": 58.0,
        "currency": "USD",
        "pe": 72.0,
        "fwd_pe": 34.0,
        "pe_10y_median": 45.0,
        "ev_ebitda": 28.0,
        "p_fcf": 38.0,
        "fcf_yield": 2.6,
        "pb_ratio": 4.5,
        "roic": 14.0,
        "roe": 16.0,
        "fcf_margin": 22.0,
        "rev_growth_cagr_3y": 26.0,
        "eps_growth_cagr_3y": 55.0,
        "debt_to_ebitda": 0.8,
        "div_yield": 0.25,
        "momentum_1y": 48.0,
        "drawdown_ath": -8.0,
        "volatility_1y": 38.0,
        "risk_level": "HIGH",
        "tam_runway_score": 91,
        "moat_score": 90,
        "capital_efficiency_score": 82,
        "balance_sheet_score": 90,
        "themes": ["Nuclear", "Energy", "Commodities"],
        "why_interesting": "Produsen uranium murni terbesar di yurisdiksi barat yang aman (Kanada) + kepemilikan 49% Westinghouse (teknologi reaktor).",
        "what_could_go_wrong": "Penurunan harga spot uranium atau insiden keselamatan nuklir global.",
        "invalidation_conditions": "Defisit suplai uranium global berbalik menjadi surplus akibat reaktivasi tambang Kazatomprom yang berlebihan.",
        "turnaround_thesis": None,
        "bull_case_usd": 110.0,
        "base_case_usd": 75.0,
        "bear_case_usd": 35.0,
        "valuation_type": "Commodity Super-Cycle",
        "catalysts": "Penandatanganan kontrak jangka panjang utilitas listrik pada harga uranium >$90/lb.",
        "risks": "Volatilitas harga komoditas tambang."
    },
    {
        "ticker": "NOVO-B",
        "name": "Novo Nordisk A/S",
        "market": "EU",
        "country": "Denmark",
        "asset_type": "STOCK",
        "style": ["QUALITY", "GROWTH"],
        "sector": "Healthcare & Biotech",
        "industry": "Pharmaceuticals",
        "market_cap_usd": 540.0,
        "price_usd": 118.50,
        "currency": "USD",
        "pe": 36.0,
        "fwd_pe": 26.5,
        "pe_10y_median": 30.0,
        "ev_ebitda": 24.0,
        "p_fcf": 32.0,
        "fcf_yield": 3.1,
        "pb_ratio": 26.0,
        "roic": 65.0,
        "roe": 75.0,
        "fcf_margin": 36.0,
        "rev_growth_cagr_3y": 28.0,
        "eps_growth_cagr_3y": 34.0,
        "debt_to_ebitda": 0.2,
        "div_yield": 1.45,
        "momentum_1y": 15.0,
        "drawdown_ath": -22.0,
        "volatility_1y": 26.0,
        "risk_level": "LOW",
        "tam_runway_score": 96,
        "moat_score": 96,
        "capital_efficiency_score": 98,
        "balance_sheet_score": 96,
        "themes": ["Healthcare", "Biotech", "Longevity"],
        "why_interesting": "Duopoli global obat GLP-1 obesitas & diabetes (Ozempic/Wegovy) dengan ROIC spektakuler >65%.",
        "what_could_go_wrong": "Kompetisi sengit dari Eli Lilly (Zepbound) dan obat oral GLP-1 generasi baru.",
        "invalidation_conditions": "Kehilangan pangsa pasar GLP-1 secara signifikan ke Eli Lilly.",
        "turnaround_thesis": None,
        "bull_case_usd": 180.0,
        "base_case_usd": 145.0,
        "bear_case_usd": 90.0,
        "valuation_type": "Elite Healthcare Compounder",
        "catalysts": "Hasil uji klinis CagriSema & ekspansi kapasitas produksi fill-finish Catalent.",
        "risks": "Negosiasi harga obat oleh Medicare AS."
    },
    {
        "ticker": "NU",
        "name": "Nu Holdings Ltd. (Nubank)",
        "market": "US",
        "country": "Brazil / LatAm",
        "asset_type": "STOCK",
        "style": ["GROWTH", "QUALITY", "MULTIBAGGER"],
        "sector": "Digital Banking & Emerging Fintech",
        "industry": "Fintech",
        "market_cap_usd": 72.0,
        "price_usd": 15.20,
        "currency": "USD",
        "pe": 32.0,
        "fwd_pe": 21.0,
        "pe_10y_median": 45.0,
        "ev_ebitda": None,
        "p_fcf": 24.0,
        "fcf_yield": 4.2,
        "pb_ratio": 7.8,
        "roic": 26.0,
        "roe": 28.5,
        "fcf_margin": 32.0,
        "rev_growth_cagr_3y": 55.0,
        "eps_growth_cagr_3y": 95.0,
        "debt_to_ebitda": 0.1,
        "div_yield": 0.0,
        "momentum_1y": 82.0,
        "drawdown_ath": -9.0,
        "volatility_1y": 38.0,
        "risk_level": "HIGH",
        "tam_runway_score": 95,
        "moat_score": 91,
        "capital_efficiency_score": 92,
        "balance_sheet_score": 95,
        "themes": ["Fintech", "Emerging Markets", "Digital Ads"],
        "why_interesting": "Neobank paling menguntungkan di dunia dengan >105 juta nasabah di Brasil, Meksiko, dan Kolombia dengan biaya akuisisi nasabah (CAC) terendah ($5).",
        "what_could_go_wrong": "Kenaikan kredit macet (NPL) kartu kredit di Brasil saat siklus suku bunga naik.",
        "invalidation_conditions": "Pertumbuhan nasabah aktif kuartalan melambat di bawah 15% YoY.",
        "turnaround_thesis": None,
        "bull_case_usd": 32.0,
        "base_case_usd": 22.0,
        "bear_case_usd": 10.5,
        "valuation_type": "Hyper-Growth Fintech",
        "catalysts": "Monetisasi pasar Meksiko & ekspansi produk pinjaman payroll & asuransi.",
        "risks": "Volatilitas makro dan mata uang Amerika Latin (BRL/MXN)."
    },
    
    # INDONESIAN VALUE & COMPOUNDERS (IDX)
    {
        "ticker": "BBCA.JK",
        "name": "Bank Central Asia Tbk",
        "market": "ID",
        "country": "Indonesia",
        "asset_type": "STOCK",
        "style": ["QUALITY", "VALUE"],
        "sector": "Financials & Private Banking",
        "industry": "Banking",
        "market_cap_usd": 52.0,
        "price_idr": 6375.0,
        "currency": "IDR",
        "pe": 21.5,
        "fwd_pe": 19.2,
        "pe_10y_median": 26.5,
        "ev_ebitda": None,
        "p_fcf": None,
        "fcf_yield": None,
        "pb_ratio": 3.9,
        "roic": 22.5,
        "roe": 23.5,
        "fcf_margin": None,
        "rev_growth_cagr_3y": 14.0,
        "eps_growth_cagr_3y": 17.5,
        "debt_to_ebitda": None,
        "div_yield": 3.2,
        "momentum_1y": 8.5,
        "drawdown_ath": -14.5,
        "volatility_1y": 15.5,
        "risk_level": "LOW",
        "tam_runway_score": 85,
        "moat_score": 98,
        "capital_efficiency_score": 96,
        "balance_sheet_score": 98,
        "themes": ["Indonesia Growth", "ASEAN Compounders", "Financials"],
        "why_interesting": "Raja dana murah Indonesia (CASA >80%), ROE stabil >20%, dan kredit bermasalah (NPL) terendah di Asia Tenggara.",
        "what_could_go_wrong": "Perlambatan ekonomi makro Indonesia atau disrupsi fintech payment yang mengikis CASA.",
        "invalidation_conditions": "Rasio CASA turun di bawah 70% atau ROE turun di bawah 15%.",
        "turnaround_thesis": None,
        "bull_case_idr": 11500.0,
        "base_case_idr": 9200.0,
        "bear_case_idr": 5800.0,
        "valuation_type": "Undervalued Quality",
        "catalysts": "Pertumbuhan kredit korporasi & konsumsi domestik pasca stabilisasi suku bunga BI.",
        "risks": "Kenaikan biaya dana jika likuiditas perbankan nasional mengetat."
    },
    {
        "ticker": "BBRI.JK",
        "name": "Bank Rakyat Indonesia Tbk",
        "market": "ID",
        "country": "Indonesia",
        "asset_type": "STOCK",
        "style": ["VALUE", "QUALITY"],
        "sector": "Financials & Micro Banking",
        "industry": "Banking",
        "market_cap_usd": 41.0,
        "price_idr": 4450.0,
        "currency": "IDR",
        "pe": 11.2,
        "fwd_pe": 9.8,
        "pe_10y_median": 15.2,
        "ev_ebitda": None,
        "p_fcf": None,
        "fcf_yield": None,
        "pb_ratio": 2.1,
        "roic": 18.0,
        "roe": 19.5,
        "fcf_margin": None,
        "rev_growth_cagr_3y": 11.0,
        "eps_growth_cagr_3y": 14.0,
        "debt_to_ebitda": None,
        "div_yield": 6.8,
        "momentum_1y": -18.0,
        "drawdown_ath": -31.5,
        "volatility_1y": 21.0,
        "risk_level": "MEDIUM",
        "tam_runway_score": 82,
        "moat_score": 92,
        "capital_efficiency_score": 88,
        "balance_sheet_score": 88,
        "themes": ["Indonesia Growth", "Financials", "High Dividend"],
        "why_interesting": "Diskon valuasi ekstrem (P/E ~11x, P/B ~2.1x) dengan dividend yield tinggi ~6.8% dan penguasaan kredit mikro pedesaan tak tertandingi.",
        "what_could_go_wrong": "Kenaikan NPL segmen mikro (Kupedes/KUR) berkepanjangan pasca normalisasi restrukturisasi Covid.",
        "invalidation_conditions": "Credit cost tetap di atas 3.5% selama lebih dari 4 kuartal berturut-turut.",
        "turnaround_thesis": "Koreksi harga -31.5% dari ATH merefleksikan puncak pemburukan kredit mikro; perbaikan provisioning 2026/2027 menjadi katalis re-rating.",
        "bull_case_idr": 6800.0,
        "base_case_idr": 5400.0,
        "bear_case_idr": 3600.0,
        "valuation_type": "Deep Value / High Dividend",
        "catalysts": "Normalisasi credit cost ke kisaran 2.2% & pembagian dividen payout ratio >80%.",
        "risks": "Daya beli masyarakat kelas menengah-bawah yang pulih lebih lambat."
    },
    {
        "ticker": "BMRI.JK",
        "name": "Bank Mandiri (Persero) Tbk",
        "market": "ID",
        "country": "Indonesia",
        "asset_type": "STOCK",
        "style": ["QUALITY", "GROWTH", "VALUE"],
        "sector": "Financials & Corporate Banking",
        "industry": "Banking",
        "market_cap_usd": 38.0,
        "price_idr": 6200.0,
        "currency": "IDR",
        "pe": 10.5,
        "fwd_pe": 9.2,
        "pe_10y_median": 13.8,
        "ev_ebitda": None,
        "p_fcf": None,
        "fcf_yield": None,
        "pb_ratio": 2.0,
        "roic": 19.5,
        "roe": 21.0,
        "fcf_margin": None,
        "rev_growth_cagr_3y": 16.0,
        "eps_growth_cagr_3y": 22.0,
        "debt_to_ebitda": None,
        "div_yield": 5.8,
        "momentum_1y": 6.0,
        "drawdown_ath": -12.0,
        "volatility_1y": 18.0,
        "risk_level": "LOW",
        "tam_runway_score": 86,
        "moat_score": 93,
        "capital_efficiency_score": 92,
        "balance_sheet_score": 94,
        "themes": ["Indonesia Growth", "Financials", "High Dividend"],
        "why_interesting": "Pertumbuhan laba tercepat di antara Big 4 Bank BUMN, rasio digital super-app Livin' terdepan, dan ROE konsisten >20%.",
        "what_could_go_wrong": "Penugasan kredit BUMN infrastruktur yang berisiko atau kenaikan cost of credit korporasi.",
        "invalidation_conditions": "ROE turun di bawah 16% atau NPL korporasi melonjak >3.0%.",
        "turnaround_thesis": None,
        "bull_case_idr": 8800.0,
        "base_case_idr": 7400.0,
        "bear_case_idr": 5100.0,
        "valuation_type": "Undervalued Quality Compounder",
        "catalysts": "Sindikasi pembiayaan transisi energi & pertumbuhan CASA digital Livin'.",
        "risks": "Sensitivitas terhadap siklus ekonomi makro korporasi BUMN."
    },
    {
        "ticker": "UNTR.JK",
        "name": "United Tractors Tbk",
        "market": "ID",
        "country": "Indonesia",
        "asset_type": "STOCK",
        "style": ["VALUE", "QUALITY"],
        "sector": "Mining Equipment & Minerals",
        "industry": "Heavy Equipment & Gold Mining",
        "market_cap_usd": 6.8,
        "price_idr": 26800.0,
        "currency": "IDR",
        "pe": 5.4,
        "fwd_pe": 5.8,
        "pe_10y_median": 8.5,
        "ev_ebitda": 3.2,
        "p_fcf": 6.2,
        "fcf_yield": 16.0,
        "pb_ratio": 1.1,
        "roic": 22.0,
        "roe": 24.5,
        "fcf_margin": 18.0,
        "rev_growth_cagr_3y": 15.0,
        "eps_growth_cagr_3y": 18.0,
        "debt_to_ebitda": 0.2,
        "div_yield": 8.5,
        "momentum_1y": 12.0,
        "drawdown_ath": -22.0,
        "volatility_1y": 24.0,
        "risk_level": "MEDIUM",
        "tam_runway_score": 80,
        "moat_score": 90,
        "capital_efficiency_score": 92,
        "balance_sheet_score": 95,
        "themes": ["Indonesia Growth", "Commodities", "Gold", "High Dividend"],
        "why_interesting": "Mesin cetak kas grup Astra dengan P/E 5.4x, yield dividen 8.5%, dan diversifikasi sukses ke tambang emas (Martabe) dan nikel.",
        "what_could_go_wrong": "Penurunan tajam harga batubara thermal global.",
        "invalidation_conditions": "Margin laba kontraktor tambang Pamapersada turun drastis di bawah 10%.",
        "turnaround_thesis": None,
        "bull_case_idr": 38000.0,
        "base_case_idr": 31000.0,
        "bear_case_idr": 21000.0,
        "valuation_type": "Deep Value / Cash Cow",
        "catalysts": "Kenaikan harga emas mengompensasi batubara & kontribusi tambang nikel baru.",
        "risks": "Transisi energi global yang menekan permintaan batubara jangka panjang."
    },
    {
        "ticker": "AMMN.JK",
        "name": "Amman Mineral Internasional Tbk",
        "market": "ID",
        "country": "Indonesia",
        "asset_type": "STOCK",
        "style": ["GROWTH", "MULTIBAGGER"],
        "sector": "Copper & Gold Mining",
        "industry": "Mining & Smelting",
        "market_cap_usd": 45.0,
        "price_idr": 9200.0,
        "currency": "IDR",
        "pe": 38.0,
        "fwd_pe": 24.0,
        "pe_10y_median": 35.0,
        "ev_ebitda": 18.0,
        "p_fcf": 25.0,
        "fcf_yield": 4.0,
        "pb_ratio": 8.5,
        "roic": 26.0,
        "roe": 30.0,
        "fcf_margin": 35.0,
        "rev_growth_cagr_3y": 45.0,
        "eps_growth_cagr_3y": 60.0,
        "debt_to_ebitda": 1.2,
        "div_yield": 0.5,
        "momentum_1y": 65.0,
        "drawdown_ath": -18.0,
        "volatility_1y": 36.0,
        "risk_level": "HIGH",
        "tam_runway_score": 92,
        "moat_score": 94,
        "capital_efficiency_score": 88,
        "balance_sheet_score": 86,
        "themes": ["Indonesia Growth", "Commodities", "Energy", "Gold"],
        "why_interesting": "Pemilik cadangan tembaga dan emas raksasa kelas dunia (Batu Hijau & Elang) dengan biaya produksi tunai terendah di dunia (net of gold credit).",
        "what_could_go_wrong": "Keterlambatan operasional smelter tembaga baru atau regulasi royalti ekspor minerba.",
        "invalidation_conditions": "Produksi konsentrat fase 8 tertunda signifikan atau harga tembaga dunia anjlok <$3.5/lb.",
        "turnaround_thesis": None,
        "bull_case_idr": 16000.0,
        "base_case_idr": 11500.0,
        "bear_case_idr": 6500.0,
        "valuation_type": "World-Class Copper Asset",
        "catalysts": "Komisioning smelter penuh & lonjakan permintaan tembaga untuk elektrifikasi AI data center global.",
        "risks": "Kebijakan regulasi bea keluar mineral pemerintah RI."
    },
    {
        "ticker": "PGEO.JK",
        "name": "Pertamina Geothermal Energy Tbk",
        "market": "ID",
        "country": "Indonesia",
        "asset_type": "STOCK",
        "style": ["QUALITY", "GROWTH"],
        "sector": "Geothermal & Renewable Energy",
        "industry": "Utilities",
        "market_cap_usd": 3.2,
        "price_idr": 1150.0,
        "currency": "IDR",
        "pe": 16.5,
        "fwd_pe": 14.2,
        "pe_10y_median": 18.0,
        "ev_ebitda": 9.5,
        "p_fcf": 15.0,
        "fcf_yield": 6.8,
        "pb_ratio": 1.6,
        "roic": 12.5,
        "roe": 14.0,
        "fcf_margin": 42.0,
        "rev_growth_cagr_3y": 14.0,
        "eps_growth_cagr_3y": 18.0,
        "debt_to_ebitda": 0.9,
        "div_yield": 4.2,
        "momentum_1y": -5.0,
        "drawdown_ath": -28.0,
        "volatility_1y": 22.0,
        "risk_level": "LOW",
        "tam_runway_score": 90,
        "moat_score": 95,
        "capital_efficiency_score": 85,
        "balance_sheet_score": 92,
        "themes": ["Indonesia Growth", "Energy", "Clean Power"],
        "why_interesting": "Monopoli panas bumi (geotermal) Indonesia dengan kontrak take-or-pay USD jangka panjang bersama PLN, margin EBITDA >75%, dan arus kas bebas defensif.",
        "what_could_go_wrong": "Eksplorasi sumur panas bumi baru yang kering atau risiko regulasi tarif listrik EBT.",
        "invalidation_conditions": "Penurunan tarif dasar PPA listrik dengan PLN.",
        "turnaround_thesis": None,
        "bull_case_idr": 1850.0,
        "base_case_idr": 1500.0,
        "bear_case_idr": 950.0,
        "valuation_type": "Green Energy Compounder",
        "catalysts": "Ekspansi kapasitas terpasang dari 672 MW menuju 1 GW & monetisasi green hydrogen.",
        "risks": "Capex eksplorasi panas bumi yang padat modal."
    },

    # CRYPTO & COMMODITIES
    {
        "ticker": "BTC-USD",
        "name": "Bitcoin",
        "market": "CRYPTO",
        "country": "Global",
        "asset_type": "CRYPTO",
        "style": ["GROWTH", "MULTIBAGGER", "MOMENTUM"],
        "sector": "Digital Store of Value",
        "industry": "Crypto Asset",
        "market_cap_usd": 1550.0,
        "price_usd": 77482.0,
        "currency": "USD",
        "pe": None,
        "fwd_pe": None,
        "pe_10y_median": None,
        "ev_ebitda": None,
        "p_fcf": None,
        "fcf_yield": None,
        "pb_ratio": None,
        "roic": None,
        "roe": None,
        "fcf_margin": None,
        "rev_growth_cagr_3y": None,
        "eps_growth_cagr_3y": None,
        "debt_to_ebitda": None,
        "div_yield": 0.0,
        "momentum_1y": 115.0,
        "drawdown_ath": -12.0,
        "volatility_1y": 52.0,
        "risk_level": "EXTREME",
        "tam_runway_score": 96,
        "moat_score": 99,
        "capital_efficiency_score": 90,
        "balance_sheet_score": 100,
        "themes": ["Bitcoin", "Blockchain", "Gold", "Digital Store of Value"],
        "why_interesting": "Emas digital dengan suplai terbatas matematis (21 juta koin), likuiditas global 24/7, dan adopsi institusional ETF spot.",
        "what_could_go_wrong": "Pelarangan regulasi koordinasi G7 atau kegagalan keamanan kriptografi kuantum.",
        "invalidation_conditions": "Inflow bersih institusional berbalik negatif selama 6 bulan berturut-turut atau terjadi split konsensus jaringan.",
        "turnaround_thesis": None,
        "bull_case_usd": 250000.0,
        "base_case_usd": 120000.0,
        "bear_case_usd": 45000.0,
        "valuation_type": "Monetary Store of Value",
        "catalysts": "Adopsi alokasi sovereign treasury (US Strategic Bitcoin Reserve) & devaluasi mata uang fiat global.",
        "risks": "Volatilitas ekstrem dan risiko regulasi perpajakan."
    },
    {
        "ticker": "SOL-USD",
        "name": "Solana",
        "market": "CRYPTO",
        "country": "Global",
        "asset_type": "CRYPTO",
        "style": ["GROWTH", "MULTIBAGGER", "MOMENTUM"],
        "sector": "High-Throughput L1 Blockchain",
        "industry": "Blockchain",
        "market_cap_usd": 98.0,
        "price_usd": 195.0,
        "currency": "USD",
        "pe": None,
        "fwd_pe": None,
        "pe_10y_median": None,
        "ev_ebitda": None,
        "p_fcf": None,
        "fcf_yield": None,
        "pb_ratio": None,
        "roic": None,
        "roe": None,
        "fcf_margin": None,
        "rev_growth_cagr_3y": None,
        "eps_growth_cagr_3y": None,
        "debt_to_ebitda": None,
        "div_yield": 6.5,
        "momentum_1y": 190.0,
        "drawdown_ath": -25.0,
        "volatility_1y": 75.0,
        "risk_level": "EXTREME",
        "tam_runway_score": 92,
        "moat_score": 88,
        "capital_efficiency_score": 85,
        "balance_sheet_score": 90,
        "themes": ["Blockchain", "Fintech"],
        "why_interesting": "Blockchain berkecepatan tinggi (65.000 TPS) dengan biaya gas sub-sen yang merebut volume DEX dan ritel global.",
        "what_could_go_wrong": "Insiden pemadaman jaringan (outage) atau konsentrasi validator.",
        "invalidation_conditions": "Volume DEX harian turun di bawah Ethereum dan L2 secara konsisten.",
        "turnaround_thesis": None,
        "bull_case_usd": 650.0,
        "base_case_usd": 320.0,
        "bear_case_usd": 80.0,
        "valuation_type": "High-Beta Layer 1",
        "catalysts": "Persetujuan ETF spot Solana di AS & rilis validator client Firedancer.",
        "risks": "Volatilitas ekstrem dan inflasi suplai token staking."
    },
    {
        "ticker": "GC=F",
        "name": "Gold Futures (XAU/USD)",
        "market": "COMMODITY",
        "country": "Global",
        "asset_type": "COMMODITY",
        "style": ["VALUE", "QUALITY"],
        "sector": "Precious Metals & Monetary Anchor",
        "industry": "Commodities",
        "market_cap_usd": 16500.0,
        "price_usd": 2930.50,
        "currency": "USD",
        "pe": None,
        "fwd_pe": None,
        "pe_10y_median": None,
        "ev_ebitda": None,
        "p_fcf": None,
        "fcf_yield": None,
        "pb_ratio": None,
        "roic": None,
        "roe": None,
        "fcf_margin": None,
        "rev_growth_cagr_3y": None,
        "eps_growth_cagr_3y": None,
        "debt_to_ebitda": None,
        "div_yield": 0.0,
        "momentum_1y": 38.0,
        "drawdown_ath": -1.5,
        "volatility_1y": 13.5,
        "risk_level": "LOW",
        "tam_runway_score": 85,
        "moat_score": 100,
        "capital_efficiency_score": 80,
        "balance_sheet_score": 100,
        "themes": ["Gold", "Safe Haven", "Commodities"],
        "why_interesting": "Jangkar moneter global selama 5.000 tahun sejarah manusia. Tidak memiliki counterparty risk dan dibeli masif oleh bank sentral dunia.",
        "what_could_go_wrong": "Kenaikan suku bunga riil global yang sangat tajam dan penguatan dolar AS yang ekstrem.",
        "invalidation_conditions": "Bank sentral global (khususnya PBOC & BRICS) beralih menjadi net-seller emas secara masif.",
        "turnaround_thesis": None,
        "bull_case_usd": 3800.0,
        "base_case_usd": 3100.0,
        "bear_case_usd": 2200.0,
        "valuation_type": "Monetary Hedge",
        "catalysts": "Dedolarisasi cadangan devisa bank sentral global & ekspansi defisit fiskal negara maju.",
        "risks": "Opportunity cost saat pasar saham berada dalam bull market euforia."
    },
    {
        "ticker": "HG=F",
        "name": "Copper Futures (Tembaga Global)",
        "market": "COMMODITY",
        "country": "Global",
        "asset_type": "COMMODITY",
        "style": ["GROWTH", "VALUE"],
        "sector": "Industrial Metals & Electrification",
        "industry": "Commodities",
        "market_cap_usd": 850.0,
        "price_usd": 4.52,
        "currency": "USD",
        "pe": None,
        "fwd_pe": None,
        "pe_10y_median": None,
        "ev_ebitda": None,
        "p_fcf": None,
        "fcf_yield": None,
        "pb_ratio": None,
        "roic": None,
        "roe": None,
        "fcf_margin": None,
        "rev_growth_cagr_3y": None,
        "eps_growth_cagr_3y": None,
        "debt_to_ebitda": None,
        "div_yield": 0.0,
        "momentum_1y": 24.0,
        "drawdown_ath": -14.0,
        "volatility_1y": 22.0,
        "risk_level": "MEDIUM",
        "tam_runway_score": 94,
        "moat_score": 90,
        "capital_efficiency_score": 80,
        "balance_sheet_score": 95,
        "themes": ["Commodities", "Energy", "Infrastructure", "AI"],
        "why_interesting": "Tulang punggung elektrifikasi dunia: AI data center, transmisi grid listrik, dan EV membutuhkan jutaan ton tembaga tambahan di tengah defisit tambang baru.",
        "what_could_go_wrong": "Resesi industri manufaktur China yang berkepanjangan.",
        "invalidation_conditions": "Penemuan material superkonduktor suhu kamar yang menggantikan tembaga.",
        "turnaround_thesis": None,
        "bull_case_usd": 6.50,
        "base_case_usd": 5.20,
        "bear_case_usd": 3.40,
        "valuation_type": "Structural Commodity Shortage",
        "catalysts": "Defisit suplai tambang Amerika Selatan (Chile/Peru) & lonjakan konsumsi daya AI data center.",
        "risks": "Sensitivitas terhadap siklus ekonomi properti China."
    },

    # ETFs & REITs
    {
        "ticker": "VOO",
        "name": "Vanguard S&P 500 ETF",
        "market": "US",
        "country": "United States",
        "asset_type": "ETF",
        "style": ["QUALITY", "GROWTH"],
        "sector": "Broad US Equity Index",
        "industry": "Index ETF",
        "market_cap_usd": 1200.0,
        "price_usd": 703.71,
        "currency": "USD",
        "pe": 26.5,
        "fwd_pe": 21.5,
        "pe_10y_median": 22.0,
        "ev_ebitda": 16.0,
        "p_fcf": 24.0,
        "fcf_yield": 4.1,
        "pb_ratio": 4.8,
        "roic": 18.0,
        "roe": 21.0,
        "fcf_margin": 14.0,
        "rev_growth_cagr_3y": 9.5,
        "eps_growth_cagr_3y": 12.0,
        "debt_to_ebitda": 1.5,
        "div_yield": 1.35,
        "momentum_1y": 24.0,
        "drawdown_ath": -2.5,
        "volatility_1y": 14.5,
        "risk_level": "LOW",
        "tam_runway_score": 90,
        "moat_score": 95,
        "capital_efficiency_score": 90,
        "balance_sheet_score": 92,
        "themes": ["US Equity", "Broad Market"],
        "why_interesting": "Pondasi utama portofolio global dengan biaya pengelolaan terendah (expense ratio 0.03%) dan self-cleansing index 500 perusahaan terbaik AS.",
        "what_could_go_wrong": "Resesi ekonomi AS atau kompresi valuasi indeks dari P/E >25x ke median historis.",
        "invalidation_conditions": "Kapitalisme AS kehilangan kepemimpinan inovasi global.",
        "turnaround_thesis": None,
        "bull_case_usd": 850.0,
        "base_case_usd": 750.0,
        "bear_case_usd": 520.0,
        "valuation_type": "Core Benchmark",
        "catalysts": "Pertumbuhan laba agregat emiten S&P 500.",
        "risks": "Konsentrasi bobot pada emiten Big Tech (~32%)."
    },
    {
        "ticker": "QQQ",
        "name": "Invesco QQQ Trust (Nasdaq 100)",
        "market": "US",
        "country": "United States",
        "asset_type": "ETF",
        "style": ["GROWTH", "QUALITY", "MOMENTUM"],
        "sector": "Top 100 Nasdaq Tech Leaders",
        "industry": "Index ETF",
        "market_cap_usd": 310.0,
        "price_usd": 491.15,
        "currency": "USD",
        "pe": 32.1,
        "fwd_pe": 26.0,
        "pe_10y_median": 27.0,
        "ev_ebitda": 21.0,
        "p_fcf": 29.0,
        "fcf_yield": 3.4,
        "pb_ratio": 7.5,
        "roic": 25.0,
        "roe": 29.0,
        "fcf_margin": 24.0,
        "rev_growth_cagr_3y": 16.0,
        "eps_growth_cagr_3y": 22.0,
        "debt_to_ebitda": 0.8,
        "div_yield": 0.58,
        "momentum_1y": 29.0,
        "drawdown_ath": -4.0,
        "volatility_1y": 19.8,
        "risk_level": "MEDIUM",
        "tam_runway_score": 92,
        "moat_score": 96,
        "capital_efficiency_score": 94,
        "balance_sheet_score": 95,
        "themes": ["Cloud", "AI", "US Equity"],
        "why_interesting": "100 perusahaan inovasi dan teknologi terkemuka di bursa Nasdaq.",
        "what_could_go_wrong": "Rotasi besar-besaran dari sektor teknologi ke sektor bernilai defensif.",
        "invalidation_conditions": "Pertumbuhan laba sektor software dan AI berbalik negatif.",
        "turnaround_thesis": None,
        "bull_case_usd": 650.0,
        "base_case_usd": 540.0,
        "bear_case_usd": 380.0,
        "valuation_type": "Tech Growth Benchmark",
        "catalysts": "Monetisasi enterprise AI & ekspansi komputasi cloud.",
        "risks": "Sensitivitas tinggi terhadap arah yield obligasi 10Y US."
    },
    {
        "ticker": "SMH",
        "name": "VanEck Semiconductor ETF",
        "market": "US",
        "country": "United States",
        "asset_type": "ETF",
        "style": ["GROWTH", "MOMENTUM", "MULTIBAGGER"],
        "sector": "Semiconductors",
        "industry": "Thematic ETF",
        "market_cap_usd": 32.0,
        "price_usd": 248.50,
        "currency": "USD",
        "pe": 34.0,
        "fwd_pe": 25.0,
        "pe_10y_median": 26.0,
        "ev_ebitda": 22.0,
        "p_fcf": 30.0,
        "fcf_yield": 3.3,
        "pb_ratio": 9.5,
        "roic": 32.0,
        "roe": 35.0,
        "fcf_margin": 28.0,
        "rev_growth_cagr_3y": 28.0,
        "eps_growth_cagr_3y": 38.0,
        "debt_to_ebitda": 0.5,
        "div_yield": 0.65,
        "momentum_1y": 48.0,
        "drawdown_ath": -14.0,
        "volatility_1y": 28.5,
        "risk_level": "HIGH",
        "tam_runway_score": 95,
        "moat_score": 96,
        "capital_efficiency_score": 92,
        "balance_sheet_score": 90,
        "themes": ["Semiconductors", "AI"],
        "why_interesting": "Keranjang 25 saham semikonduktor terbaik dunia (NVDA, TSM, AVGO, ASML, AMD) yang menguasai rantai pasok teknologi global.",
        "what_could_go_wrong": "Siklisitas semikonduktor dan penurunan capex AI.",
        "invalidation_conditions": "Permintaan chip komputasi AI terkontraksi secara industri.",
        "turnaround_thesis": None,
        "bull_case_usd": 380.0,
        "base_case_usd": 285.0,
        "bear_case_usd": 160.0,
        "valuation_type": "Structural Growth ETF",
        "catalysts": "Super-cycle komputasi AI & digitalisasi industri mobil/otomotif.",
        "risks": "Konsentrasi NVDA & TSM (>35% bobot ETF)."
    },
    {
        "ticker": "O",
        "name": "Realty Income Corp (The Monthly Dividend Company)",
        "market": "US",
        "country": "United States",
        "asset_type": "REIT",
        "style": ["VALUE", "QUALITY"],
        "sector": "Real Estate / Net Lease",
        "industry": "Commercial REIT",
        "market_cap_usd": 48.0,
        "price_usd": 54.20,
        "currency": "USD",
        "pe": None,
        "fwd_pe": None,
        "pe_10y_median": None,
        "ev_ebitda": 15.0,
        "p_fcf": 13.0,
        "fcf_yield": 7.5,
        "pb_ratio": 1.3,
        "roic": 8.5,
        "roe": 9.2,
        "fcf_margin": 65.0,
        "rev_growth_cagr_3y": 18.0,
        "eps_growth_cagr_3y": 8.0,
        "debt_to_ebitda": 5.4,
        "div_yield": 5.85,
        "momentum_1y": 4.0,
        "drawdown_ath": -24.0,
        "volatility_1y": 18.5,
        "risk_level": "LOW",
        "tam_runway_score": 82,
        "moat_score": 90,
        "capital_efficiency_score": 84,
        "balance_sheet_score": 88,
        "themes": ["High Dividend", "Real Estate", "Safe Haven"],
        "why_interesting": "Dividen tunai bulanan selama >55 tahun tanpa putus dengan portofolio triple-net lease komersial tahan krisis (Walmart, 7-Eleven, CVS, Dollar General).",
        "what_could_go_wrong": "Era suku bunga tinggi global (Higher for Longer) yang menekan valuasi sektor properti.",
        "invalidation_conditions": "Okupansi properti turun di bawah 96% (historis konsisten ~98.5%).",
        "turnaround_thesis": "Diskon valuasi -24% dari ATH akibat kenaikan suku bunga The Fed memberikan dividend yield menarik 5.85%.",
        "bull_case_usd": 75.0,
        "base_case_usd": 62.0,
        "bear_case_usd": 44.0,
        "valuation_type": "High-Yield Defensive REIT",
        "catalysts": "Siklus penurunan suku bunga The Fed yang memicu rotasi modal ke obligasi/REIT dividend.",
        "risks": "Beban refinancing utang obligasi pada yield yang lebih tinggi."
    }
]

# 12 Curated Institutional Themes Configuration
INVESTMENT_THEMES_CONFIG: List[Dict[str, Any]] = [
    {
        "id": "ai_infra",
        "name": "AI Infrastructure & Compute",
        "desc": "Pondasi komputasi keras: akselerator GPU, custom ASIC, litografi, dan data center scaling.",
        "theme_score": 91,
        "market_size_desc": "$1.3 Trillion by 2032 (CAGR 38%)",
        "growth_score": 96,
        "valuation_score": 62,
        "momentum_score": 92,
        "risk_score": 75,
        "leading_assets": ["NVDA", "TSM", "AVGO", "MSFT"],
        "emerging_assets": ["PLTR"],
        "highest_risk_assets": ["SMH", "PLTR"],
        "catalysts": "Siklus chip 3nm/2nm & capex hyperscaler >$200B/tahun.",
        "risks": "Kompresi margin jika monetisasi software AI berjalan lambat."
    },
    {
        "id": "semiconductors",
        "name": "Semiconductor Monopoly Chokepoints",
        "desc": "Emiten dengan hak monopoli teknologi litografi, foundry, dan peralatan manufaktur wafer.",
        "theme_score": 88,
        "market_size_desc": "$1.0 Trillion by 2030 (CAGR 12%)",
        "growth_score": 90,
        "valuation_score": 68,
        "momentum_score": 85,
        "risk_score": 65,
        "leading_assets": ["ASML", "TSM", "AVGO"],
        "emerging_assets": ["SMH"],
        "highest_risk_assets": ["ASML"],
        "catalysts": "High-NA EUV commercialization & packaging CoWoS.",
        "risks": "Regulasi ekspor geopolitik AS-China."
    },
    {
        "id": "nuclear_energy",
        "name": "Nuclear Renaissance & Clean Power",
        "desc": "Pembangkit listrik nuklir beban dasar (baseload) dan rantai pasok bahan bakar uranium untuk powering AI data center.",
        "theme_score": 85,
        "market_size_desc": "$450 Billion by 2035 (CAGR 18%)",
        "growth_score": 88,
        "valuation_score": 70,
        "momentum_score": 94,
        "risk_score": 68,
        "leading_assets": ["CEG", "CCJ"],
        "emerging_assets": ["PGEO.JK"],
        "highest_risk_assets": ["CCJ"],
        "catalysts": "Kontrak PPA swasta 20-tahun antara utilitas nuklir dan hyperscaler Big Tech.",
        "risks": "Regulasi federal tarif transmisi (FERC)."
    },
    {
        "id": "indonesia_growth",
        "name": "Indonesia Macro & Consumption Moats",
        "desc": "Raja perbankan swasta, kredit mikro pedesaan, cadangan tembaga kelas dunia, dan dividen tunai tinggi.",
        "theme_score": 82,
        "market_size_desc": "GDP RI $1.5T (Proyeksi 5.2% Pertumbuhan Riil)",
        "growth_score": 78,
        "valuation_score": 88,
        "momentum_score": 72,
        "risk_score": 45,
        "leading_assets": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "AMMN.JK", "UNTR.JK"],
        "emerging_assets": ["PGEO.JK"],
        "highest_risk_assets": ["AMMN.JK"],
        "catalysts": "Stabilitas Rupiah, penurunan BI Rate, dan dividen yield menarik >6%.",
        "risks": "Daya beli konsumen domestik & volatilitas kurs valas."
    },
    {
        "id": "bitcoin_sovereign",
        "name": "Bitcoin & Decentralized Store of Value",
        "desc": "Jangkar moneter digital matematis dengan suplai terbatas 21 juta koin dan adopsi institusional ETF spot.",
        "theme_score": 86,
        "market_size_desc": "$2.0 Trillion Target MCap",
        "growth_score": 92,
        "valuation_score": 72,
        "momentum_score": 90,
        "risk_score": 85,
        "leading_assets": ["BTC-USD", "SOL-USD"],
        "emerging_assets": [],
        "highest_risk_assets": ["SOL-USD"],
        "catalysts": "Inflow ETF spot, alokasi Sovereign Wealth Fund, dan siklus pasca-halving.",
        "risks": "Volatilitas harga ekstrem dan intervensi regulasi bursa."
    },
    {
        "id": "gold_monetary",
        "name": "Gold & Sovereign Hedge",
        "desc": "Aset penyimpan nilai tertua di dunia tanpa risiko counterparty untuk lindung nilai inflasi dan dedolarisasi.",
        "theme_score": 80,
        "market_size_desc": "$16.5 Trillion Global Gold Stock",
        "growth_score": 65,
        "valuation_score": 75,
        "momentum_score": 84,
        "risk_score": 30,
        "leading_assets": ["GC=F", "UNTR.JK", "AMMN.JK"],
        "emerging_assets": [],
        "highest_risk_assets": [],
        "catalysts": "Pembelian emas masif oleh bank sentral BRICS & defisit fiskal negara barat.",
        "risks": "Kenaikan suku bunga riil AS."
    },
    {
        "id": "copper_electrification",
        "name": "Electrification, Copper & AI Data Centers",
        "desc": "Kebutuhan fisik tembaga untuk kabel transmisi daya, pendingin data center AI, dan motor listrik.",
        "theme_score": 84,
        "market_size_desc": "$850 Billion Global Copper Market",
        "growth_score": 82,
        "valuation_score": 78,
        "momentum_score": 80,
        "risk_score": 55,
        "leading_assets": ["AMMN.JK", "HG=F"],
        "emerging_assets": [],
        "highest_risk_assets": ["AMMN.JK"],
        "catalysts": "Defisit suplai tambang global & konsumsi masif tembaga di data center AI.",
        "risks": "Perlambatan ekonomi manufaktur China."
    },
    {
        "id": "glp1_healthcare",
        "name": "GLP-1 Biotech & Longevity Monopolies",
        "desc": "Revolusi medis pengobatan obesitas, diabetes, kardiovaskular, dan perpanjangan usia sehat.",
        "theme_score": 87,
        "market_size_desc": "$150 Billion by 2030 (CAGR 26%)",
        "growth_score": 94,
        "valuation_score": 65,
        "momentum_score": 82,
        "risk_score": 40,
        "leading_assets": ["NOVO-B"],
        "emerging_assets": [],
        "highest_risk_assets": [],
        "catalysts": "Ekspansi klaim asuransi untuk penyakit jantung & rilis formulasi oral.",
        "risks": "Persaingan harga antar produsen farmasi."
    },
    {
        "id": "fintech_disruptors",
        "name": "Emerging Market Fintech & Digital Banking",
        "desc": "Disrupsi perbankan konvensional di pasar berkembang dengan CAC rendah dan profitabilitas super.",
        "theme_score": 83,
        "market_size_desc": "$350 Billion LatAm & Global Fintech",
        "growth_score": 95,
        "valuation_score": 70,
        "momentum_score": 88,
        "risk_score": 68,
        "leading_assets": ["NU"],
        "emerging_assets": [],
        "highest_risk_assets": ["NU"],
        "catalysts": "Monetisasi nasabah di Meksiko/Kolombia & ekspansi kredit korporasi.",
        "risks": "Kenaikan NPL ritel saat siklus suku bunga makro naik."
    },
    {
        "id": "high_dividend_reit",
        "name": "Monthly Real Estate Cashflow & Defensive Yield",
        "desc": "Arus kas dividen bulanan defensif dengan proteksi sewa jangka panjang dari tenant korporasi terpercaya.",
        "theme_score": 76,
        "market_size_desc": "$1.8 Trillion Global REITs",
        "growth_score": 60,
        "valuation_score": 86,
        "momentum_score": 68,
        "risk_score": 25,
        "leading_assets": ["O", "BBRI.JK", "UNTR.JK"],
        "emerging_assets": [],
        "highest_risk_assets": [],
        "catalysts": "Siklus pemotongan suku bunga global yang menurunkan yield diskonto.",
        "risks": "Refinancing utang obligasi pada suku bunga yang lebih tinggi."
    }
]


# ==============================================================================
# QUANTITATIVE SCORING ENGINES FOR DISCOVERY
# ==============================================================================

def compute_multibagger_score(asset: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes an explainable Multibagger Potential Score (0-100) based on
    Revenue Growth, TAM Runway, Moat Strength, Capital Efficiency (ROIC),
    Balance Sheet Health, and Valuation Reasonable-ness.
    """
    rev_g = asset.get("rev_growth_cagr_3y") or 15.0
    growth_score = min(100.0, max(20.0, rev_g * 1.8))
    tam_score = float(asset.get("tam_runway_score") or 80.0)
    moat_score = float(asset.get("moat_score") or 80.0)
    roic = asset.get("roic") or 18.0
    cap_eff = min(100.0, max(30.0, roic * 1.5))
    bs_score = float(asset.get("balance_sheet_score") or 85.0)

    pe = asset.get("pe")
    if pe is None:
        val_score = 75.0
    elif pe <= 15.0:
        val_score = 95.0
    elif pe <= 25.0:
        val_score = 85.0
    elif pe <= 40.0:
        val_score = 70.0
    elif pe <= 65.0:
        val_score = 55.0
    else:
        val_score = 40.0

    total_score = (
        (growth_score * 0.25) +
        (tam_score * 0.20) +
        (moat_score * 0.20) +
        (cap_eff * 0.15) +
        (bs_score * 0.10) +
        (val_score * 0.10)
    )
    total_score = round(min(100.0, max(0.0, total_score)), 1)

    if total_score >= 88.0:
        potential_tier = "5x - 10x+ Speculative Potential"
        tier_badge = "bg-purple-950/60 text-purple-300 border-purple-500/50"
    elif total_score >= 78.0:
        potential_tier = "3x - 5x Long-Term Potential"
        tier_badge = "bg-cyan-950/60 text-cyan-300 border-cyan-500/50"
    elif total_score >= 68.0:
        potential_tier = "2x - 3x Compounder Potential"
        tier_badge = "bg-emerald-950/60 text-emerald-300 border-emerald-500/50"
    else:
        potential_tier = "Moderate Upside Potential"
        tier_badge = "bg-slate-900 text-slate-300 border-slate-700"

    return {
        "score": total_score,
        "potential_tier": potential_tier,
        "tier_badge": tier_badge,
        "breakdown": {
            "growth": round(growth_score, 1),
            "tam_runway": round(tam_score, 1),
            "moat": round(moat_score, 1),
            "capital_efficiency": round(cap_eff, 1),
            "balance_sheet": round(bs_score, 1),
            "valuation": round(val_score, 1)
        },
        "invalidation": asset.get("invalidation_conditions", "Pertumbuhan bisnis melambat di bawah estimasi model.")
    }


def compute_quality_compounder_score(asset: Dict[str, Any]) -> Dict[str, Any]:
    """Computes a Quality Compounder Score (0-100) based on ROIC, ROE, FCF Margin, and Low Leverage."""
    roic = asset.get("roic") or 15.0
    roe = asset.get("roe") or 18.0
    fcf_m = asset.get("fcf_margin") or 20.0
    debt_ebitda = asset.get("debt_to_ebitda") or 0.8

    roic_pts = min(35.0, (roic / 30.0) * 35.0)
    fcf_pts = min(25.0, (fcf_m / 35.0) * 25.0)
    if debt_ebitda <= 0.5:
        lev_pts = 20.0
    elif debt_ebitda <= 1.5:
        lev_pts = 16.0
    elif debt_ebitda <= 2.5:
        lev_pts = 10.0
    else:
        lev_pts = 4.0
    moat_pts = float(asset.get("moat_score") or 85.0) * 0.20

    total_quality = round(roic_pts + fcf_pts + lev_pts + moat_pts, 1)
    total_quality = min(100.0, max(0.0, total_quality))

    return {
        "score": total_quality,
        "level": "ELITE COMPOUNDER" if total_quality >= 85 else ("HIGH QUALITY" if total_quality >= 70 else "AVERAGE QUALITY"),
        "roic": roic,
        "fcf_margin": fcf_m,
        "debt_to_ebitda": debt_ebitda
    }


def compute_deep_value_discount(asset: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes valuation discount vs 10Y historical median,
    explicitly separating 'Misunderstood Cyclical Opportunity' from 'Fundamentally Deteriorating Trap'.
    """
    pe = asset.get("pe")
    pe_median = asset.get("pe_10y_median")

    if pe and pe_median and pe_median > 0:
        discount_pct = round(((pe - pe_median) / pe_median) * 100.0, 1)
    else:
        discount_pct = 0.0

    drawdown = asset.get("drawdown_ath") or 0.0
    is_undervalued = discount_pct < -15.0 or drawdown < -25.0

    if is_undervalued:
        val_classification = asset.get("valuation_type", "Misunderstood Cyclical Opportunity")
        why_cheap = f"Valuasi saat ini berada {abs(discount_pct)}% di bawah median historis 10 tahun."
        what_could_make_cheaper = "Jika siklus laba atau pemulihan makro tertunda lebih lama dari estimasi konsensus."
    else:
        val_classification = "Fair / Premium Valuation"
        why_cheap = "Diperdagangkan pada valuasi wajar merefleksikan ekspektasi pertumbuhan tinggi."
        what_could_make_cheaper = "Kompresi multiple P/E ke rata-rata historis jika terjadi rotasi pasar."

    return {
        "pe_current": pe,
        "pe_10y_median": pe_median,
        "discount_vs_median_pct": discount_pct,
        "drawdown_ath": drawdown,
        "is_undervalued": is_undervalued,
        "classification": val_classification,
        "why_cheap": why_cheap,
        "what_could_make_cheaper": what_could_make_cheaper
    }


def compute_portfolio_aware_fit(asset: Dict[str, Any], user_holdings: List[Dict[str, Any]], total_val_idr: float) -> Dict[str, Any]:
    """
    Evaluates Portfolio Fit Score (0-100) based on existing user holdings.
    Alerts on high sector/geography concentration or highlights assets that fill portfolio gaps.
    """
    if not user_holdings or total_val_idr <= 0:
        return {
            "fit_score": 85,
            "fit_verdict": "GOOD COMPLEMENT",
            "warnings": [],
            "gap_filled": "Diversifikasi pondasi portofolio awal."
        }

    ticker = asset["ticker"]
    sec = asset.get("sector", "General")
    geo = asset.get("market", "US")

    existing_asset_val = sum(h.get("cur_val_idr", 0.0) for h in user_holdings if h.get("ticker") == ticker)
    existing_asset_weight = (existing_asset_val / total_val_idr) * 100.0 if total_val_idr > 0 else 0.0

    warnings = []
    gap_filled = []

    if existing_asset_weight > 25.0:
        fit_score = 45
        verdict = "HIGH CONCENTRATION CAUTION"
        warnings.append(f"Anda sudah memiliki alokasi {existing_asset_weight:.1f}% pada {ticker}. Menambah aset ini akan meningkatkan risiko konsentrasi single-asset.")
    elif "Semiconductor" in sec or "AI" in sec:
        fit_score = 68
        verdict = "OVERLAPPING SECTOR EXPOSURE"
        warnings.append("Portofolio Anda sudah memiliki eksposur semikonduktor/teknologi melalui NVDA/SMH/QQQ.")
    elif "Financials" in sec and geo == "ID":
        fit_score = 88
        verdict = "STRONG DOMESTIC DEFENSIVE FIT"
        gap_filled.append("Menambah arus dividen tunai IDR defensif.")
    elif asset.get("asset_type") == "COMMODITY" or "Gold" in sec:
        fit_score = 92
        verdict = "EXCELLENT HEDGE FIT"
        gap_filled.append("Mengisi celah safe haven & proteksi devaluasi fiat.")
    elif geo == "EU" or geo == "ASIA":
        fit_score = 85
        verdict = "GLOBAL GEOGRAPHIC DIVERSIFIER"
        gap_filled.append("Meningkatkan diversifikasi yurisdiksi di luar AS.")
    elif asset.get("asset_type") == "REIT":
        fit_score = 90
        verdict = "INCOME GENERATION FIT"
        gap_filled.append("Menghasilkan cashflow dividen bulanan defensif.")
    else:
        fit_score = 80
        verdict = "BALANCED FIT"
        gap_filled.append("Menambah variasi instrumen investasi.")

    return {
        "fit_score": fit_score,
        "fit_verdict": verdict,
        "existing_weight_pct": round(existing_asset_weight, 1),
        "warnings": warnings,
        "gap_filled": gap_filled[0] if gap_filled else "Diversifikasi terukur."
    }


def compute_2d_risk_reward_coordinates(asset: Dict[str, Any], multibagger_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates normalized (X = Risk 0-100, Y = Potential Upside 0-100) coordinates for 2D Scatter Matrix."""
    risk_lvl = asset.get("risk_level", "MEDIUM")
    if risk_lvl == "LOW":
        x_risk = 25.0
    elif risk_lvl == "MEDIUM":
        x_risk = 50.0
    elif risk_lvl == "HIGH":
        x_risk = 75.0
    else: # EXTREME
        x_risk = 92.0

    vol = asset.get("volatility_1y") or 25.0
    x_risk = min(100.0, max(5.0, (x_risk * 0.7) + (vol * 0.6)))
    y_upside = multibagger_data["score"]

    return {
        "x_risk": round(x_risk, 1),
        "y_upside": round(y_upside, 1),
        "quadrant": "ASYMMETRIC WINNER" if (x_risk < 55 and y_upside > 75) else (
            "HIGH-RISK SPECULATION" if (x_risk >= 55 and y_upside > 75) else (
                "SAFE COMPOUNDER" if (x_risk < 55 and y_upside <= 75) else "UNFAVORABLE RISK/REWARD"
            )
        )
    }


# ==============================================================================
# MAIN SCANNER AGGREGATION & SENSITIVITY PIPELINE
# ==============================================================================

def scan_global_universe(
    user_holdings: List[Dict[str, Any]] = None,
    total_val_idr: float = 0.0,
    filter_market: str = "ALL",
    filter_type: str = "ALL",
    filter_style: str = "ALL",
    search_query: str = ""
) -> List[Dict[str, Any]]:
    """Filters and enriches the global universe with all quantitative discovery scores."""
    if user_holdings is None:
        user_holdings = []

    results = []
    q = search_query.strip().lower() if search_query else ""

    for raw_asset in GLOBAL_ASSET_UNIVERSE:
        ticker = raw_asset["ticker"]
        name = raw_asset["name"]
        mkt = raw_asset["market"]
        atype = raw_asset["asset_type"]
        styles = raw_asset.get("style", [])

        if q:
            match_search = (
                q in ticker.lower() or
                q in name.lower() or
                q in raw_asset.get("sector", "").lower() or
                any(q in t.lower() for t in raw_asset.get("themes", []))
            )
            if not match_search:
                continue

        if filter_market != "ALL" and mkt != filter_market:
            continue

        if filter_type != "ALL" and atype != filter_type:
            continue

        if filter_style != "ALL" and filter_style not in styles:
            continue

        mb = compute_multibagger_score(raw_asset)
        qual = compute_quality_compounder_score(raw_asset)
        disc = compute_deep_value_discount(raw_asset)
        fit = compute_portfolio_aware_fit(raw_asset, user_holdings, total_val_idr)
        coords = compute_2d_risk_reward_coordinates(raw_asset, mb)

        opp_score = round(
            (mb["score"] * 0.40) +
            (qual["score"] * 0.30) +
            ((100.0 - abs(disc["discount_vs_median_pct"])) * 0.15) +
            (fit["fit_score"] * 0.15),
            1
        )
        opp_score = min(100.0, max(0.0, opp_score))

        yahoo_url = get_yahoo_finance_url(ticker)

        results.append({
            **raw_asset,
            "opportunity_score": opp_score,
            "multibagger": mb,
            "quality": qual,
            "discount": disc,
            "portfolio_fit": fit,
            "risk_reward_coords": coords,
            "yahoo_url": yahoo_url
        })

    results.sort(key=lambda x: x["opportunity_score"], reverse=True)
    return results


def get_thematic_discovery_data() -> List[Dict[str, Any]]:
    """Returns the 12 curated institutional themes with dynamic stats and leading assets."""
    themes_result = []
    for th in INVESTMENT_THEMES_CONFIG:
        leading_cards = []
        for sym in th["leading_assets"]:
            match_asset = next((a for a in GLOBAL_ASSET_UNIVERSE if a["ticker"] == sym), None)
            if match_asset:
                mb = compute_multibagger_score(match_asset)
                leading_cards.append({
                    "ticker": sym,
                    "name": match_asset["name"],
                    "price": match_asset.get("price_usd") or match_asset.get("price_idr"),
                    "currency": match_asset["currency"],
                    "multibagger_score": mb["score"],
                    "yahoo_url": get_yahoo_finance_url(sym)
                })

        themes_result.append({
            **th,
            "leading_cards": leading_cards
        })
    return themes_result


def get_single_asset_research(ticker_symbol: str, user_holdings: List[Dict[str, Any]] = None, total_val_idr: float = 0.0) -> Optional[Dict[str, Any]]:
    """Returns complete in-depth research terminal data for a single asset with Bull/Base/Bear scenarios."""
    clean_sym = ticker_symbol.strip().upper()
    asset = next((a for a in GLOBAL_ASSET_UNIVERSE if a["ticker"].upper() == clean_sym), None)
    if not asset:
        return None

    mb = compute_multibagger_score(asset)
    qual = compute_quality_compounder_score(asset)
    disc = compute_deep_value_discount(asset)
    fit = compute_portfolio_aware_fit(asset, user_holdings or [], total_val_idr)
    coords = compute_2d_risk_reward_coordinates(asset, mb)

    return {
        **asset,
        "multibagger": mb,
        "quality": qual,
        "discount": disc,
        "portfolio_fit": fit,
        "risk_reward_coords": coords,
        "yahoo_url": get_yahoo_finance_url(clean_sym)
    }
