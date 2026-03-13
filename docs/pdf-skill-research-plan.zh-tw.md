# PDF 技能研究與開發計畫報告

> **技能路徑**：`.opencode/skills/pdf`
> **文件日期**：2026-03-12
> **語言**：繁體中文（zh-TW）

---

## 1. 執行摘要

本報告記錄 `.opencode/skills/pdf` 技能的完整研究、設計與驗證過程。目標是讓 AI 編碼助手能將 PDF 轉換為高品質 Markdown，保留結構、表格與圖片參照。

**研究結論**：

- 上游三個參考技能（Anthropic / OpenAI / antigravity 的 pdf skill）均未內建真正的 PDF→Markdown 轉換流程。
- 四個開源轉換引擎經完整評估後，**docling** 為整體最佳主引擎，markitdown 與輕量腳本為輕量備選，marker / MinerU 為進階可選。
- 下游技能已大幅改寫，新增工具決策樹、比較矩陣、五條轉換路徑與後處理表格驗證。
- 實際測試以輕量腳本轉換 AMD Kria K26 SOM 資料表（ds987），成功擷取 **49 個表格、11 張圖片**，並產生 47 條多欄排版提示。
- 輕量腳本 **部分滿足** 排版保留需求——缺乏標題層級推斷且圖片附加於頁尾；若嚴格要求版面精確還原，docling 為推薦路徑。

---

## 2. 參考技能深度調研

### 2.1 調查對象

| 技能來源 | 技能名稱 | 主要定位 |
|---|---|---|
| Anthropic (上游 `skills/pdf`) | pdf | 通用 PDF 處理：合併、拆分、旋轉、表單填寫、加密 |
| OpenAI | pdf (ChatGPT Plugins 生態) | 表單填寫、文字擷取、基本操作 |
| antigravity | pdf | 類似功能，專注 reportlab 建立與 pypdf 操作 |

### 2.2 共同特徵

- 以 **pypdf / pdfplumber / reportlab** 為核心依賴。
- 聚焦「對 PDF 做事」（合併、拆分、加密），而非「將 PDF 轉為別的格式」。
- 皆提供 OCR 段落作為附帶指引（pytesseract + pdf2image），但未整合完整 Markdown 管線。
- 無一技能內建 **docling / markitdown / marker / MinerU** 的呼叫示範或決策流程。

### 2.3 為何三者未採用 OSS 轉換引擎

| 因素 | 說明 |
|---|---|
| **範疇定義** | 上游技能定位為「PDF 操作工具箱」，PDF→Markdown 不在核心 use case |
| **依賴體積** | docling / marker / MinerU 都帶 ML 模型權重（數百 MB 至數 GB），與輕量技能設計理念不合 |
| **授權顧慮** | marker (GPL-3.0 + cc-by-nc-sa 模型) 與 MinerU (AGPL-3.0) 在商用部署有限制 |
| **GPU 預設** | marker / MinerU 在無 GPU 環境效能急遽下降，AI 助手執行環境通常無 GPU |
| **出現時序** | docling 與 markitdown 較新（2024），部分技能在更早版本鎖定設計 |

---

## 3. 四大 OSS 轉換引擎比較

### 3.1 比較矩陣

| 特性 | markitdown | 輕量腳本 (pdfplumber + pypdf) | docling | marker | MinerU |
|---|---|---|---|---|---|
| 文字層 PDF | ✅ | ✅ | ✅ | ✅ | ✅ |
| 掃描 PDF (OCR) | ❌ | ❌ | ✅ (tesseract) | ✅ | ✅ |
| 表格 → Markdown | ⚠️ 不可靠 | ✅ pdfplumber | ✅ TableFormer | ✅ | ✅ |
| 圖片擷取 | ❌ | ✅ 僅光柵圖 | ✅ | ✅ | ✅ 原生 |
| 公式 (LaTeX) | ❌ | ❌ | ⚠️ 部分 | ✅ | ✅ |
| 標題層級推斷 | ⚠️ 基本 | ❌ | ✅ 語義模型 | ✅ | ✅ |
| 版面重建 | ❌ | ⚠️ 僅多欄偵測 | ✅ 完整 | ✅ | ✅ |
| GPU 需求 | 否 | 否 | 否 | 建議 ≥4 GB VRAM | 建議 ≥8 GB VRAM |
| 安裝體積 | 極小 | 小 | 中 | 大 | 極大 |
| 授權 | MIT | MIT 依賴 | MIT | GPL-3.0 | AGPL-3.0 |

### 3.2 使用者需求對照

使用者核心需求：

1. **PDF→Markdown 轉換** — 所有四者皆支援。
2. **Markdown 表格** — markitdown 不可靠；其餘三者及輕量腳本可用。
3. **圖片擷取至 images/ 資料夾** — markitdown 不支援；其餘皆可。
4. **版面保留（標題層級、閱讀順序）** — docling / marker / MinerU 佳；輕量腳本僅部分滿足。
5. **無 GPU 可用** — 排除 marker / MinerU 作為預設路徑。
6. **MIT 授權偏好** — 排除 marker (GPL-3.0) 與 MinerU (AGPL-3.0) 作為企業預設。

### 3.3 引擎選擇結論

| 角色 | 引擎 | 理由 |
|---|---|---|
| **主引擎（推薦預設）** | docling | 表格最佳、支援 OCR、MIT 授權、無需 GPU |
| **輕量備選** | markitdown | 純文字快速路徑，零模型 |
| **中量備選** | 輕量腳本 (pdfplumber + pypdf) | 需表格與圖片但不想裝 ML 模型時使用 |
| **進階可選 (書籍/論文)** | marker | 高精度版面辨識，但 GPL + 商用模型限制 |
| **進階可選 (科學/公式)** | MinerU | LaTeX 公式最強，但 AGPL + 極大安裝體積 |

---

## 4. 需求符合度重新評估

### 4.1 評估矩陣

| 需求 | 狀態 | 說明 |
|---|---|---|
| PDF→Markdown 轉換 | ✅ **完全滿足** | SKILL.md 提供五條路徑，含 CLI 與 Python API 範例 |
| Markdown 表格 | ✅ **完全滿足** | pdfplumber 與 docling 皆產出 `\| col \|` 語法；含後處理驗證腳本 |
| 圖片擷取至 images/ | ✅ **完全滿足** | 輕量腳本與 docling 均輸出 `![](images/…)` 參照 |
| 版面保留（標題層級） | ⚠️ **部分滿足** | docling 路徑完全支援；輕量腳本不推斷 `#` / `##` 層級 |
| 多欄排版閱讀順序 | ⚠️ **部分滿足** | 輕量腳本偵測多欄並插入 WARNING 註解，但不重排順序 |
| 掃描 PDF | ✅ **完全滿足** | 決策樹明確導向 docling / marker / MinerU |
| 表格驗證 | ✅ **完全滿足** | `verify_tables()` 函式 + pdfplumber 回退機制 |
| 批次轉換 | ✅ **完全滿足** | CLI `--batch` 模式與 docling 原生批次 |

### 4.2 推薦路徑 vs. 實際測試路徑的差距

這是本次評估最重要的坦白說明：

| 面向 | docling（推薦路徑） | 輕量腳本（實際測試路徑） |
|---|---|---|
| 標題層級 | ✅ 語義模型推斷 `#` / `##` / `###` | ❌ 輸出為純文字段落，無標題標記 |
| 表格品質 | ✅ TableFormer 模型，跨頁表格支援 | ✅ pdfplumber 在簡單表格表現良好 |
| 圖片定位 | ✅ 圖片內嵌於語義位置 | ⚠️ 圖片附加於頁尾（pypdf 無可靠 bbox） |
| 閱讀順序 | ✅ ML 版面分析重建 | ⚠️ 僅依 y 座標排序，多欄時可能交錯 |
| 安裝門檻 | 中（需下載模型權重） | 低（三個 pip 套件） |
| 轉換速度 | 中 | 快 |

**結論**：對於使用者嚴格的品質目標（尤其是資料表等複雜排版文件），**docling 是更合適的路徑**。本次保留的實際轉換使用了輕量腳本，在表格與圖片擷取方面表現合格，但在標題層級與圖片定位方面有明確差距。

---

## 5. 開發計畫與現況

### 5.1 已完成的變更

`.opencode/skills/pdf` 中以下內容已完成：

| 檔案 | 變更內容 |
|---|---|
| `SKILL.md` | 全面改寫：新增 PDF→Markdown 導向的描述、工具決策樹、五條轉換路徑（markitdown / docling / 輕量腳本 / marker / MinerU）、比較矩陣、忠實度警告規範、後處理表格驗證 |
| `reference.md` | 新增進階參考：pdfplumber 調校、OCR 準備、嵌入圖片擷取、加密/損壞 PDF 處理、效能建議 |
| `scripts/pdf_to_md.py` | 新建輕量轉換腳本：掃描偵測、pdfplumber 表格擷取、pypdf 圖片擷取、多欄偵測、CLI 介面、批次模式、驗證函式 |
| `evals/evals.json` | 新建評估用例：結構保留轉換、表格擷取、圖片擷取三個場景 |

### 5.2 目前狀態

| 項目 | 狀態 |
|---|---|
| SKILL.md 設計與撰寫 | ✅ 完成 |
| 輕量腳本開發 | ✅ 完成 |
| 參考文件 | ✅ 完成 |
| 評估用例定義 | ✅ 完成 |
| 實際 PDF 轉換測試（輕量腳本） | ✅ 完成 |
| docling 路徑實際驗證 | ⏳ 尚未執行 |
| marker / MinerU 路徑實際驗證 | ⏳ 尚未執行 |

### 5.3 後續改善建議（依優先順序）

| 優先順序 | 改善項目 | 預期效益 |
|---|---|---|
| **P0** | 執行 docling 實際轉換並與輕量腳本結果比較 | 驗證推薦路徑的實際表現，量化品質差距 |
| **P1** | 輕量腳本加入標題層級推斷（字體大小→ `#` 層級） | 大幅改善版面保留，縮小與 docling 的差距 |
| **P1** | 改善圖片定位——嘗試用 pdfplumber 的 `page.images` bbox 代替 pypdf | 圖片能出現在語義正確位置而非頁尾 |
| **P2** | 加入多欄閱讀順序重建（基於 x 座標分群） | 改善多欄文件的閱讀順序 |
| **P2** | 在 evals/ 中加入自動化驗證腳本（非僅 JSON 描述） | 可重複執行的品質回歸測試 |
| **P3** | 探索 marker / MinerU 在 CPU 模式下的表現 | 擴展 GPU 不可用場景的選項 |

---

## 6. 保留的轉換結果

### 6.1 來源文件

- **PDF**：`tmp/ds987-k26-som.pdf`（AMD Kria™ K26 SOM 資料表，DS987 v1.5）

### 6.2 轉換工具

- 輕量腳本 `pdf_to_md.py`（pdfplumber + pypdf + Pillow）

### 6.3 輸出位置

```
tmp/ds987-k26-som-markdown/
├── ds987-k26-som.md        # 約 124 KB Markdown 文件
└── images/                 # 11 張 PNG 圖片
    ├── page1_img1.png      (155 KB)
    ├── page1_img2.png      (329 KB)
    ├── page41_img1.png     (16 KB)
    ├── page43_img1.png     (27 KB)
    ├── page43_img2.png     (37 KB)
    ├── page47_img1.png     (6 KB)
    ├── page48_img1.png     (14 KB)
    ├── page48_img2.png     (4 KB)
    ├── page48_img3.png     (39 KB)
    ├── page48_img4.png     (33 KB)
    └── page48_img5.png     (27 KB)
```

### 6.4 轉換統計

| 指標 | 數值 | 說明 |
|---|---|---|
| Markdown 表格 | 49 | 涵蓋訂購資訊、電氣規格、腳位定義等 |
| 圖片參照 | 11 | 均以 `![](images/…)` 語法內嵌 |
| 警告/備註 | 47 | 主要為多欄排版偵測備註 (`<!-- NOTE: … -->`) |
| 輸出檔案大小 | ~124 KB | 純文字 Markdown |

### 6.5 轉換品質觀察

- **成功面**：文件開頭正確顯示標題「Kria K26 SOM Data Sheet」、產品概述段落、第一張訂購資訊表格。表格語法正確，可被標準 Markdown 渲染器解析。
- **限制面**：
  - 標題（Overview、Module Description 等）以純文字出現，未標記為 `#` / `##`。
  - 圖片集中於各頁尾部而非原始語義位置。
  - 多欄頁面的閱讀順序可能交錯（已有 NOTE 註解標示）。

---

## 7. 總結

`.opencode/skills/pdf` 已從「通用 PDF 操作工具箱」轉型為「以 PDF→Markdown 為核心的轉換技能」。技能設計涵蓋五條轉換路徑與完整決策樹，能因應從簡單文字擷取到複雜科學論文的不同場景。

實際轉換驗證顯示輕量腳本在表格與圖片擷取方面表現可靠，但在標題層級推斷與圖片定位方面有待改善。對於追求最高版面還原度的使用場景，應優先使用 docling 路徑。

**下一步最高價值行動**：執行 docling 實際轉換以量化與輕量腳本的品質差距，並在輕量腳本中加入字體大小→標題層級的啟發式推斷。
