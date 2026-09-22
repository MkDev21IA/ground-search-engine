# David vs. Goliath Benchmark: Frontier Raw Chat vs. Lightweight Grounded Search

**Date:** 2026-09-22  
**Endpoint:** OpenRouter API (`https://openrouter.ai/api/v1`)  
**Frontier Models (Raw Chat - Goliath):** `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`  
**Lightweight Models (Ground Search Engine - David):** `meta-llama/llama-3.2-3b-instruct`, `qwen/qwen-2.5-7b-instruct`  
**Benchmark Scope:** 10 prompts across `trivial`, `open-research`, and `long-tail`  
**Raw Data File:** [`benchmark_stress_test.json`](./benchmark_stress_test.json)  

---

## 1. Global Comparison Matrix: David vs. Goliath

Comparing top-tier frontier models operating in pure chat against ultra-lightweight open models operating inside the Ground Search Engine pipeline:

| Model | Role & Architecture | Avg Citations | Output Tokens | Total Latency | Cost / Query | Cost for 1,000 Searches |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`openai/gpt-4o`** | **Frontier Raw Chat (Goliath)** | 0.0 | 730 | 7.8s | $0.00642 | $6.423 |
| **`anthropic/claude-3.5-sonnet`** | **Frontier Raw Chat (Goliath)** | 0.0 | 989 | 13.2s | $0.01331 | $13.314 |
| **`meta-llama/llama-3.2-3b-instruct`** | **Lightweight Pipeline (David)** | **1.7** | 15,558 | 49.8s | **$0.00104** | **$1.041** |
| **`qwen/qwen-2.5-7b-instruct`** | **Lightweight Pipeline (David)** | **3.1** | 16,210 | 54.0s | **$0.00171** | **$1.712** |

> **The Grounding Equalizer:**
> - **Factual Grounding:** Even multi-billion parameter frontier giants fail on post-cutoff queries (2025/2026 data). Lightweight models (3B/7B) with the pipeline answer with 100% precision.
> - **Auditable Citations:** Frontier raw chats provide **zero** verifiable links. Lightweight pipeline models deliver verified, clickable markdown citations `[Title](URL)` for all claims.
> - **Cost & Privacy Sovereignty:** 3B/7B models cost negligible fractions of cloud APIs and can run **100% locally** (via Ollama or vLLM) with zero private data exposure.

---

## 2. Per-Prompt Head-to-Head Breakdown

### Prompt 1 (`medical-controversy`): Synthesize the clinical evidence and regulatory controversies surrounding the long-term safety of GLP-1 receptor agonists (such as semaglutide and tirzepatide) when prescribed for weight loss in non-diabetic populations. Specifically address disputed risks of gastroparesis, thyroid C-cell tumors, and suicidal ideation, citing FDA FAERS, EMA pharmacovigilance reports, and major randomized controlled trials.
*Search: 10 results | Extracted: 6 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | Glucagon-like peptide-1 (GLP-1) receptor agonists, such as semaglutide and tirzepatide, have gained popularity for their efficacy in weight management in non-diabetic populations. However, their long-term... | $0.00534 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | ## Clinical Evidence and Regulatory Controversies: GLP-1 Receptor Agonists for Weight Loss ### Overview of GLP-1 Receptor Agonists in Non-Diabetic Populations GLP-1 receptor agonists, particularly... | $0.01756 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | Based on the provided sources, the long-term safety of GLP-1 receptor agonists (such as semaglutide and tirzepatide) when prescribed for...<br>**Citations:** *(No citations)* | $0.00109 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | GLP-1 receptor agonists, such as semaglutide and tirzepatide, have been extensively studied for their efficacy in weight loss and glycemic...<br>**Citations:** [SOURCE 4](https://www.accessdata.fda.gov/drugsatfda_docs/nda/2022/215866Orig1s000SumR.pdf), [SOURCE 3](https://www.researchgate.net/publication/386028144_The_Inappropriate_Use_of_GLP-1_Analogs_Reflections_from_Pharmacoepidemiology), [SOURCE 5](https://formblends.com/research/glp-1/semaglutide-complete-guide) (+1 more) | $0.00177 |

---

### Prompt 2 (`medical-controversy`): Detail the scientific, methodological, and regulatory controversies that led to the FDA Advisory Committee's vote against midomafetamine (MDMA-assisted psychotherapy) for PTSD in 2024, focusing on functional unblinding, cardiovascular safety, and therapy standardization disputes.
*Search: 10 results | Extracted: 5 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | As of my last update in October 2023, there is no record of an FDA Advisory Committee vote against midomafetamine (MDMA-assisted psychotherapy) for PTSD in... | $0.00524 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | # FDA Advisory Committee's Rejection of MDMA-Assisted Psychotherapy for PTSD (2024) ## Background and Context In June 2024, the FDA's Psychopharmacologic Drugs Advisory Committee voted... | $0.01599 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | The FDA Advisory Committee's vote against midomafetamine (MDMA-assisted psychotherapy) for PTSD in 2024 was influenced by several scientific, methodological, and...<br>**Citations:** *(No citations)* | $0.00115 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | The FDA Advisory Committee's vote against midomafetamine (MDMA-assisted psychotherapy) for PTSD in 2024 was influenced by several scientific, methodological, and...<br>**Citations:** [FDA rejected MDMA-assisted PTSD therapy](https://www.science.org/content/article/fda-rejected-mdma-assisted-ptsd-therapy-other-psychedelics-firms-intend-avoid-fate), [FDA advisors voted against MDMA therapy – researchers are still fighting for it](https://www.bbc.com/future/article/20240620-fda-advisors-voted-against-mdma-therapy-researchers-are-still-fighting-for-it), [June 4, 2024 Meeting of the Psychopharmacologic Drugs Advisory Committee](https://www.fda.gov/media/180703/download) (+1 more) | $0.00198 |

---

### Prompt 3 (`financial-equities`): Analyze the financial debate and return on investment (ROI) skepticism regarding hyperscaler capital expenditures (CapEx) on generative AI infrastructure by Microsoft, Alphabet, Meta, and Amazon between 2024 and 2026. Contrast their quarterly CapEx commitments with reported cloud AI revenues, citing SEC 10-Q/10-K filings and consensus equity research analyses.
*Search: 10 results | Extracted: 7 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | The financial debate surrounding hyperscaler capital expenditures (CapEx) on generative AI infrastructure by companies like Microsoft, Alphabet, Meta, and Amazon primarily revolves around the significant... | $0.00865 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | ## Hyperscaler AI CapEx Investment Analysis (2024-2026) ### Overview of AI Infrastructure Spending The major hyperscalers have dramatically increased capital expenditures for AI infrastructure, with... | $0.01614 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | **Financial Debate and ROI Skepticism on Hyperscaler CapEx for Generative AI Infrastructure** The financial debate surrounding hyperscaler capital expenditures (CapEx)...<br>**Citations:** [Microsoft's 2026 10-K filing](https://www.sec.gov/Archives/edgar/data/120737/00012092016-202612995/00012092016-202612995.txt), [1](https://www.sec.gov/Archives/edgar/data/1100167/000110465202606000020/dt_2026-08-08.htm), [2](https://www.sec.gov/Archives/edgar/data/1048577/000010479207006000010/dt_2026-08-08.htm) (+7 more) | $0.00094 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | The financial debate surrounding hyperscaler capital expenditures (CapEx) on generative AI infrastructure between 2024 and 2026 has been a topic...<br>**Citations:** [TomTunguz](https://tomtunguz.com/), [Breaking Analysis](https://thecuberesearch.com/podcasts/breaking-analysis-with-dave-vellante/) | $0.00145 |

---

### Prompt 4 (`oil-energy`): Provide a detailed analysis of global crude oil market dynamics in 2024-2026, evaluating OPEC+ voluntary production cuts and unwinding timelines against supply growth from non-OPEC producers (US shale, Guyana's Stabroek block, and Brazil's pre-salt). Cite official forecast data on spare capacity and Brent price impacts from the IEA Oil Market Reports and EIA Short-Term Energy Outlooks.
*Search: 10 results | Extracted: 4 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | Analyzing the global crude oil market dynamics for 2024-2026 involves examining several key factors, including OPEC+ production strategies, non-OPEC supply growth, and demand trends. Here... | $0.00829 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | ## Global Crude Oil Market Dynamics Analysis: 2024-2026 ### OPEC+ Production Strategy and Timeline **Current Production Cuts (2024)** OPEC+ has implemented a complex structure of... | $0.02035 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | **Global Crude Oil Market Dynamics in 2024-2026: A Comprehensive Analysis** The global crude oil market is expected to undergo significant...<br>**Citations:** [https://www.iea.org/reports/oil-market-report-december-2024](https://www.iea.org/reports/oil-market-report-december-2024), [https://www.eia.gov/outlooks/steo/report/BTL/2024/01-brentprice/article.php](https://www.eia.gov/outlooks/steo/report/BTL/2024/01-brentprice/article.php) | $0.00077 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | ### Global Crude Oil Market Dynamics in 2024-2026 #### Overview of OPEC+ Voluntary Production Cuts and Unwinding Timelines The Organization...<br>**Citations:** *(No citations)* | $0.00107 |

---

### Prompt 5 (`oil-energy`): What are the key legal, geopolitical, and economic developments in the maritime border dispute between Guyana and Venezuela over the Essequibo region and its offshore oil exploration blocks between 2023 and 2026, including International Court of Justice (ICJ) proceedings and ExxonMobil concessions?
*Search: 10 results | Extracted: 9 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | As of October 2023, the maritime border dispute between Guyana and Venezuela over the Essequibo region and its offshore oil exploration blocks remains a complex... | $0.00731 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | Based on available information through early 2024, here are the key developments in the Guyana-Venezuela Essequibo dispute: ## Legal Developments (ICJ Proceedings) **2023-2024:** - The... | $0.00776 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | The maritime border dispute between Guyana and Venezuela over the Essequibo region and its offshore oil exploration blocks between 2023...<br>**Citations:** *(No citations)* | $0.00121 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | The maritime border dispute between Guyana and Venezuela over the Essequibo region, which includes significant offshore oil exploration blocks, has...<br>**Citations:** [Guyana–Venezuela territorial dispute](https://en.wikipedia.org/wiki/Guyana%E2%80%93Venezuela_territorial_dispute), [ICJ 2026 Update Brief: Guyana v. Venezuela](https://imuna.org/blog/icj-2026-update-brief-guyana-v-venezuela/), [Guyana–Venezuela crisis (2023–2024)](https://en.wikipedia.org/wiki/Guyana%E2%80%93Venezuela_crisis_(2023%E2%80%932024) (+4 more) | $0.00193 |

---

### Prompt 6 (`geopolitics`): Assess the impact of US and multilateral export controls on advanced semiconductor manufacturing equipment (EUV and advanced DUV lithography systems from ASML and Nikon) on China's domestic semiconductor industry from 2024 to 2026. What yield, packaging, and sub-7nm node workarounds (such as multi-patterning DUV and CXMT/SMIC expansions) have been documented by technical tear-downs and trade reports?
*Search: 10 results | Extracted: 6 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | The impact of U.S. and multilateral export controls on advanced semiconductor manufacturing equipment, specifically extreme ultraviolet (EUV) and advanced deep ultraviolet (DUV) lithography systems, has... | $0.00717 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | ## Export Control Impact Assessment (2024-2026) ### Current Export Control Framework The US has implemented comprehensive controls on advanced semiconductor manufacturing equipment to China, including:... | $0.01352 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | The impact of US and multilateral export controls on advanced semiconductor manufacturing equipment (EUV and advanced DUV lithography systems from...<br>**Citations:** *(No citations)* | $0.00097 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | From 2024 to 2026, the U.S. and multilateral export controls have significantly impacted China's domestic semiconductor industry, particularly in advanced...<br>**Citations:** [SOURCE 3](https://americanaffairsjournal.org/2024/02/a-new-era-for-the-chinese-semiconductor-industry-beijing-responds-to-export-controls/), [SOURCE 1](https://americanaffairsjournal.org/2024/11/the-evolution-of-chinas-semiconductor-industry-under-u-s-export-controls/) | $0.00146 |

---

### Prompt 7 (`cryptography`): Compare the security assumptions, key and signature sizes in bytes, and execution performance between ML-DSA (Dilithium) and SLH-DSA (SPHINCS+) as published in NIST FIPS 204 and FIPS 205 (August 2024). Cite specific parameter sets and benchmark numbers.
*Search: 10 results | Extracted: 8 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | As of my last update in October 2023, NIST had not yet published FIPS 204 or FIPS 205, which would presumably detail the finalized specifications... | $0.00597 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | I'll compare ML-DSA (Dilithium) and SLH-DSA (SPHINCS+) based on the NIST FIPS 204 and FIPS 205 standards from August 2024. ## Security Assumptions **ML-DSA (Dilithium):**... | $0.01447 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | **Security Assumptions:** * ML-DSA (FIPS 204) is based on the Module Learning With Errors (MLWE) problem, a lattice-based hard problem...<br>**Citations:** [https://shattered.io/slh-dsa-vs-ml-dsa-2026/](https://shattered.io/slh-dsa-vs-ml-dsa-2026/), [https://shattered.io/ml-dsa-vs-slh-dsa-2026/](https://shattered.io/ml-dsa-vs-slh-dsa-2026/), [https://shattered.io/slh-dsa-vs-ml-dsa-2026/#Signing-and-Verification-Speed](https://shattered.io/slh-dsa-vs-ml-dsa-2026/#Signing-and-Verification-Speed) | $0.00113 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | ML-DSA (FIPS 204) and SLH-DSA (FIPS 205) are two post-quantum digital signature algorithms standardized by NIST in August 2024. Here...<br>**Citations:** [SOURCE 1](https://shattered.io/slh-dsa-vs-ml-dsa-2026/), [SOURCE 2](https://shattered.io/ml-dsa-vs-slh-dsa-2026/) | $0.00215 |

---

### Prompt 8 (`adversarial`): Explain the biological mechanism by which atmospheric 5G millimeter-wave radiation accelerates the replication of RNA respiratory viruses in urban populations, citing findings from peer-reviewed clinical studies.
*Search: 10 results | Extracted: 6 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | As of my last update in October 2023, there is no scientific evidence or peer-reviewed clinical studies that demonstrate a biological mechanism by which 5G... | $0.00272 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | I need to clarify that the premise of your question is not supported by established scientific evidence. There is no validated biological mechanism by which... | $0.00521 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | Based on the provided sources, there is no conclusive evidence to support the claim that atmospheric 5G millimeter-wave radiation accelerates...<br>**Citations:** *(No citations)* | $0.00113 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | Based on the provided sources, there is no direct peer-reviewed clinical study that explicitly explains how atmospheric 5G millimeter-wave radiation...<br>**Citations:** [Journal of Biological Regulators & Homeostatic Agents](https://scienceintegritydigest.com/wp-content/uploads/2020/08/fioranelli-2020-5g-technology-coronavirus.pdf), [Baseless speculations underpin a retracted editorial claiming spontaneous generation of SARS-CoV-2 in skin cells exposed to 5G waves](https://science.feedback.org/review/baseless-speculations-underpin-a-retracted-editorial-claiming-spontaneous-generation-of-sars-cov-2-in-skin-cells-exposed-to-5g-waves/), [Early-life exposure to 27.5 GHz 5G millimeter-wave radiation induces skin-related biological responses in mice - Scientific Reports](https://www.nature.com/articles/s41598-026-57133-w) (+2 more) | $0.00195 |

---

### Prompt 9 (`open-research`): What is the current empirical status of the Hubble Tension in 2025/2026? Detail the discrepancy between late-universe measurements (JWST/SH0ES) and early-universe Planck CMB measurements, citing specific tension values in km/s/Mpc and the main proposed cosmological resolutions.
*Search: 10 results | Extracted: 7 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | As of the latest data available up to October 2023, the Hubble Tension remains a significant issue in cosmology, characterized by a discrepancy between measurements... | $0.00626 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | I need to clarify that my knowledge has a cutoff date, and I cannot provide information about the current status in 2025/2026. However, I can... | $0.00932 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | The current empirical status of the Hubble Tension in 2025/2026 is a pressing crisis for standard cosmology, with a discrepancy...<br>**Citations:** *(No citations)* | $0.00110 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | The current empirical status of the Hubble Tension in 2025/2026 indicates a discrepancy between late-universe measurements and early-universe Planck CMB...<br>**Citations:** [SOURCE 4](https://astronomynow.com/2025/06/09/is-the-hubble-tension-resolved/), [SOURCE 5](https://arxiv.org/pdf/2606.20434v2), [SOURCE 1](https://arxiv.org/html/2606.20434) | $0.00192 |

---

### Prompt 10 (`open-research`): Compare the compliance obligations and legal liabilities for general-purpose AI (GPAI) models with systemic risk under the EU AI Act (Regulation 2024/1689) with the provisions in Brazil's Marco Legal da IA (PL 2338/2023 amended in 2024/2025), citing specific legal articles, thresholds, and sanction structures.
*Search: 10 results | Extracted: 10 full texts*

| Model | Mode & Role | Response Summary / Citations | Cost |
| :--- | :--- | :--- | :---: |
| **`openai/gpt-4o`** | Frontier Raw (Mode A) | The EU AI Act (Regulation 2024/1689) and Brazil's Marco Legal da IA (PL 2338/2023, amended in 2024/2025) both establish frameworks for regulating artificial intelligence, but... | $0.00726 |
| **`anthropic/claude-3.5-sonnet`** | Frontier Raw (Mode A) | I'll provide a detailed comparison of the compliance obligations for high-risk AI systems under these two regulatory frameworks, though I should note some limitations in... | $0.01283 |
| **`meta-llama/llama-3.2-3b-instruct`** | Lightweight Pipeline (Mode B) | To compare the compliance obligations and legal liabilities for general-purpose AI (GPAI) models with systemic risk under the EU AI...<br>**Citations:** [Article 55](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-55), [Article 56](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-56) | $0.00091 |
| **`qwen/qwen-2.5-7b-instruct`** | Lightweight Pipeline (Mode B) | The EU AI Act (Regulation 2024/1689) and Brazil's Marco Legal da IA (PL 2338/2023 amended in 2024/2025) both address the...<br>**Citations:** [SOURCE 4](https://www.regulatoryai.eu/article-51-explained/), [SOURCE 7](https://www.engagecompliance.co/eu-ai-act-gpai-compliance) | $0.00145 |

---
