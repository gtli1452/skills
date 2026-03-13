# PDF 技能開發報告

> **技能路徑**：`.opencode/skills/pdf`
> **報告日期**：2026-03-13
> **執行模型**：Claude Opus 4.6（子代理）
> **工作流**：skill-creator 最佳實務 + 多輪 corpus 驗證

---

## 1. 執行摘要

本次工作依照使用者要求，針對 `.opencode/skills/pdf/SKILL.md` 與其輔助腳本進行實際優化，目標是讓 PDF 轉 Markdown 更穩定滿足以下五項品質要求：

1. 保持原本 PDF 的排版與閱讀順序。
2. 將表格轉成 Markdown 表格。
3. 將圖片輸出成 Markdown 圖片語法，且圖片集中到 `images/`。
4. 保留跨欄／跨列／合併儲存格表格資訊。
5. 使用 Markdown 標題語法（`#`, `##`, `###`）。

本次不是只改文件而已，而是把 skill、腳本、eval corpus、workspace 與開發紀錄一起補齊，並且真的拿 `tests/pdfs/` 內 8 份 PDF 做三輪迭代驗證。

**最終結論：**

- `pdf` skill 已完成可追溯的三輪優化，並保留 reviewable commits。
- `.opencode/skills/pdf/evals/evals.json` 已擴充為 **15 個 eval**，覆蓋全部 **8 份 PDF**。
- `scripts/pdf_to_md.py` 已從不可執行的 `pypdf` 相依改為目前環境可執行的 **PyMuPDF / fitz** 路徑，且實際跑通。
- 最終 `iteration-3` 的參考比對結果為 **5 PASS、1 WARN、0 FAIL**（reference-backed PDFs）。
- datasheet 類型（`ds987-k26-som.pdf`, `UM10204.pdf`）在 `iteration-3` 維持 **PASS / 無回歸**。
- 仍有少量非阻斷限制，例如 `thinkos` 子節標題覆蓋率偏低，以及個別 datasheet 的字符／圖說偵測雜訊，但整體已達可交付狀態。

---

## 2. 本次需求與驗收標準

### 2.1 使用者指定目標

使用者要求本次調整必須同時滿足：

- 依 Agent Skills 最佳實務使用 **Claude Opus 4.6** 與 **skill-creator**。
- 優化 `@.opencode\skills\pdf\SKILL.md`。
- 確保轉換出的 Markdown：
  - 保留原 PDF 排版；
  - 表格轉為 Markdown 表格；
  - 圖片轉為 Markdown 圖片語法並集中到 `images/`；
  - 保持跨欄／跨列表格資訊；
  - 使用 Markdown 標題語法。
- 以 `@tests\pdfs\` 內 **8 份 PDF** 全數做測試迭代。
- 積極 commit，讓開發歷程可追蹤回朔。
- 以 **zh-tw Markdown** 撰寫開發報告並保存在目前 repo。

### 2.2 實際採用的驗收方式

本次實作採用兩條並行驗收線：

- **reference-backed 驗證**：對 `tests/references/*.md` 有對照檔的 PDF，比對 heading、table、image、warning、結構覆蓋率。
- **datasheet 專項稽核**：對沒有 reference markdown 的 `ds987-k26-som.pdf` 與 `UM10204.pdf`，直接檢查表格數量、欄數一致性、跨列標記、圖片與警告註解。

---

## 3. 主要實作內容

### 3.1 `SKILL.md`

`SKILL.md` 這次不只是補說明，而是變成真正可執行的 skill 指南，重點包含：

- 新增 **Acceptance Criteria (Quality Gates)**，把 headings / tables / images / warnings 的要求寫清楚。
- 將驗證呼叫改為 `verify() or verify_tables()`，避免腳本與文件命名不一致。
- 補上 **Iterative Testing Workflow**，明確指出：
  - 使用 `scripts/run_evals.py` 跑 corpus；
  - 用 `evals/evals.json` 作為測試集；
  - 將輸出放進 workspace 逐輪檢查。
- 補強對 headings、spanning tables、vector graphics、image placement 的說明。

### 3.2 `scripts/pdf_to_md.py`

這是本次改動最多、也最關鍵的檔案。主要改進如下：

#### Runtime 相容性

- 將原本無法在此環境執行的 `pypdf` 相依替換為 **PyMuPDF / fitz**。
- 圖片抽取改走 fitz，因此目前：
  - 可以實際執行；
  - 可以取得更接近頁面位置的 bounding-box；
  - 不再只能把圖片粗暴附加在頁尾。

#### 表格與跨欄／跨列處理

- 輸出 `<!-- WARNING: merged/spanning cells normalized; verify table accuracy -->`。
- 為稀疏 continuation rows 標記 `<!-- spanning row -->`。
- 讓 forward-fill / normalization 也會觸發 merged-cell warning，而不是只看 ragged rows。
- 驗證函式 `verify()` 保留，並提供 `verify_tables = verify` 相容 alias。

#### 圖片與向量圖形

- 以 fitz 擷取 raster images，統一輸出到 `images/`。
- 對無法抽成 raster 的 vector graphics 補上 warning 註解。

#### Heading 與版面結構

本次總共做了三輪 heading heuristics 調整：

- **Iteration 1**
  - 加入 heading promotion、跨欄／vector／warning 補強。
- **Iteration 2**
  - 改成 line-level header/footer detection；
  - 加入 multi-column 分欄處理；
  - 降低 false-positive heading；
  - 大幅減少警告噪音。
- **Iteration 3**
  - 新增 `_promote_numbered_heading()`，顯式提升 `1 INTRODUCTION`、`2.1 Methods` 這種標題；
  - 新增 `_is_code_like_text()`，避免把 code comments / ML tensor-shape 註解誤判成 markdown headings；
  - 對非 heading 的 `# ` 起始文字做 escape，避免被 Markdown renderer 誤當成 H1；
  - 增加 character-spaced / numeric garbage 的 guard，抑制 `# ’ b a n a n a ’` 這類假 heading。

### 3.3 新增輔助檔案

| 檔案 | 用途 |
|---|---|
| `.opencode/skills/pdf/scripts/run_evals.py` | 批次執行 eval corpus，產出每個 eval 的輸出與摘要 |
| `.opencode/skills/pdf/scripts/requirements.txt` | 記錄目前這條 lightweight path 需要的 runtime 依賴 |
| `.opencode/skills/pdf/evals/evals.json` | 擴充為 15 個 eval，完整覆蓋 8 份 PDF |

---

## 4. 測試資料與 eval 覆蓋

### 4.1 測試 PDF

本次實際驗證的 8 份 PDF：

| 檔案 | 類型 | 重點 |
|---|---|---|
| `crowd.pdf` | 多欄論文 | multi-column reading order、表格、圖片 |
| `ds987-k26-som.pdf` | datasheet | 大量表格、跨頁表格、11 張圖片 |
| `multicolcnn.pdf` | 多欄論文 | multi-column headings、表格、圖片 |
| `switch_trans.pdf` | ML 論文 | heading、code comments、表格 |
| `thinkdsp.pdf` | 技術書 | 章節結構、圖表、程式碼 |
| `thinkos.pdf` | 技術書 | 章節結構、程式碼、術語 |
| `thinkpython.pdf` | 技術書 | 深層 heading hierarchy、程式碼、圖片 |
| `UM10204.pdf` | 規格書 | 24 張表格、vector 圖、單位與訊號名 |

### 4.2 Eval 數量

- 初始 `evals.json`：3 個 eval，只覆蓋 `ds987-k26-som.pdf`
- 調整後 `evals.json`：**15 個 eval**
- 覆蓋：
  - 8/8 測試 PDF
  - headings / tables / images / spanning cells / reading order 等重點面向

---

## 5. 實際迭代過程

### 5.1 Iteration 1

**結果：全部成功轉換，但品質不夠。**

主要發現：

- reference-backed PDF 中，5/6 在 heading 與 table quality 上弱於 reference。
- academic papers 出現 garbled headings，如 `# V`、`## C`。
- datasheet 表格與圖片其實已經不錯，但 heading 假陽性偏多。

結論：需要再做一輪，先解決 header/footer 與 multi-column heading 問題。

### 5.2 Iteration 2

**結果：警告噪音大幅下降，但 heading overlap 在部分書籍／論文退步。**

主要改進：

- warnings 總量明顯下降；
- `UM10204` 的重複頁首 heading 被消掉；
- datasheet 品質穩定。

主要問題：

- `crowd` / `multicolcnn` headings 太少；
- `switch_trans` 還把 code comments 當 heading；
- `thinkdsp` / `thinkos` / `thinkpython` 的 descriptive heading text overlap 變差。

結論：再做第三輪，專修 numbered headings 與 code-comment 假陽性。

### 5.3 Iteration 3

**結果：可收斂。**

Reference-backed 最終結論：

- **5 PASS / 1 WARN / 0 FAIL**
- 平均 heading coverage：**16% → 58%**（相較 iteration 2 提升 **+42 個百分點**）
- `crowd` headings：**2 → 16**
- `thinkdsp` headings：大幅增加
- `switch_trans` code-comment false headings：**37 → 0**

Datasheet 最終結論：

- `ds987-k26-som.pdf`：**PASS，無回歸**
- `UM10204.pdf`：**PASS，無回歸**

---

## 6. Iteration 3 最終結果

### 6.1 Reference-backed PDFs

| PDF | 最終判定 | 說明 |
|---|---|---|
| `crowd.pdf` | PASS | 多欄論文標題恢復，圖片輸出正常 |
| `multicolcnn.pdf` | PASS | headings 與 tables 回到可接受範圍 |
| `switch_trans.pdf` | PASS | code comments 不再被誤判成 headings |
| `thinkdsp.pdf` | PASS | heading 結構明顯改善 |
| `thinkos.pdf` | WARN | 子節覆蓋率仍偏低，但不影響整體可讀性 |
| `thinkpython.pdf` | PASS | heading hierarchy 與 code-comment 誤判已修正 |

### 6.2 Datasheet / 規格書

| PDF | 最終判定 | 說明 |
|---|---|---|
| `ds987-k26-som.pdf` | PASS | 52 tables、11 images、0 ragged rows |
| `UM10204.pdf` | PASS | 24 tables、0 ragged rows、vector warnings 正常 |

### 6.3 使用者需求對照

| 需求 | 結果 | 說明 |
|---|---|---|
| 保持原本 PDF 排版 | ✅ | multi-column / vector / layout warnings 與 heading promotion 已顯著改善 |
| 表格轉換為 Markdown 表格 | ✅ | datasheet 類型穩定；academic paper 也有基本支援 |
| 圖片轉為 Markdown 圖片語法並存到 `images/` | ✅ | `ds987` 11 張、`crowd` 4 張、`multicolcnn` 6 張、`thinkpython` 1 張 |
| 保持跨欄／跨列表格 | ✅ | merged-cell warnings、spanning-row markers、equal columns 都已落地 |
| 使用 Markdown 標題語法 | ✅ | iteration-3 後 8 份 PDF 全部都能輸出 `#` heading；reference-backed 結果 5 PASS / 1 WARN |

---

## 7. 開發過程中的 commit 紀錄

本次依照要求保留可回朔的歷史，重要 commits 如下：

| Commit | 訊息 |
|---|---|
| `5b96be1` | `feat(pdf): harden markdown conversion workflow` |
| `17e6235` | `test(pdf): expand evaluation corpus` |
| `fdd78a5` | `fix(pdf): tighten heading and header filtering` |
| `07cad2f` | `fix(pdf): recover numbered headings and filter code comments` |

這四個 commits 對應到：

1. 建立可執行的 skill / script 骨架；
2. 把 eval 擴到 8 份 PDF；
3. 修掉第二輪發現的 header/footer / false-positive heading；
4. 修掉第三輪發現的 numbered heading 與 code comment 問題。

---

## 8. 實際執行過的驗證

### 8.1 技術驗證

已實際執行：

- `python -m py_compile .opencode\skills\pdf\scripts\pdf_to_md.py .opencode\skills\pdf\scripts\run_evals.py`
- `git --no-pager diff --check`
- 多次 smoke tests（`thinkos`, `crowd`, `UM10204`, `switch_trans`, `thinkpython`）

### 8.2 skill-local 驗證限制

`quick_validate.py` 需要 `PyYAML`，但目前環境沒有：

```text
ModuleNotFoundError: No module named 'yaml'
```

因此本次改用 repo 既定 fallback：

- `py_compile`
- `diff --check`
- 實際 corpus 轉換

### 8.3 Corpus 驗證

已完整執行：

- `iteration-1`
- `iteration-2`
- `iteration-3`

每輪都對 **8 份 PDF / 15 個 eval** 實際產出 Markdown 與 `images/`。

Workspace 保存在：

```text
tmp/pdf-workspace/
├── skill-snapshot-v0/
├── iteration-1/
├── iteration-2/
└── iteration-3/
```

---

## 9. 已知限制與後續建議

本次雖已達可交付狀態，但仍有少量非阻斷限制：

1. `thinkos.pdf`
   - 子節標題覆蓋率仍低於理想值。
   - 目前判定為 **WARN**，但整體結構仍可讀。

2. `ds987-k26-som.pdf`
   - heading hierarchy 仍偏平。
   - 某些 legal/reference 片段仍可能被誤判成 heading。

3. `UM10204.pdf`
   - 某些 figure caption / 複雜 multi-mode tables 仍可能少掉 merged-cell warning。
   - 個別字符（如 I²C superscript / μ）仍受 PDF 原始抽取品質影響。

### 建議後續方向

- 若未來要再追求更高 fidelity，建議補一條 **docling 實跑路徑** 做對照。
- 若要讓 academic paper table row coverage 更接近 reference，可再做一輪針對 multi-column tables 的 table-region 合併。
- 若要正式納入更嚴格 benchmark，可把目前 `tmp/pdf-workspace` 下的分析結果再整理成 viewer-friendly benchmark/json。

---

## 10. 總結

這次工作已經把 `.opencode/skills/pdf` 從「說得出做法」提升到「有 skill、有腳本、有 eval corpus、有迭代結果、有 commit 歷史」的狀態。

重點不是單一檔案改漂亮，而是整個 skill 的開發流程已經落地：

- 有可執行的 runtime；
- 有 8 份真實 PDF corpus；
- 有 15 個 eval；
- 有三輪迭代；
- 有可追蹤 commit；
- 有 zh-tw 報告。

最終判定為：**可以收尾交付**。若後續要再追求更高的學術論文 table fidelity，可在此基礎上繼續往 `docling` 或更強的 layout-aware 路線延伸。
