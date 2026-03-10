# Anthropic Skills → OpenCode 深度分析報告（第一階段）

- **報告日期**：2026-03-09
- **來源倉庫**：`D:\Projects\coding-agent\skills`
- **目標執行環境**：OpenCode
- **目標模型**：`gpt-oss-120b`
- **預設目標技能樹**：`D:\Projects\coding-agent\.opencode\skills\`
- **工作邊界**：保留原始 `D:\Projects\coding-agent\skills` 為唯讀分析對象；所有 OpenCode 適配版技能應建立在平行目錄，不回寫原始 Anthropic skills 倉庫。

---

## 1. 前言

這份報告是 **Anthropic skills → OpenCode 改寫計畫的第一階段深度分析結案稿**。目標不是立刻改寫任何單一 skill，而是先把 Anthropic skills 的結構、設計哲學、執行假設、相依工具、風險邊界與 OpenCode 遷移方式看清楚，避免後續進入「邊改邊猜」的狀態。

本次分析採用的預設前提如下：

1. **原始 `skills` 倉庫不動**，只當作參考來源。
2. **OpenCode 版本另建於** `D:\Projects\coding-agent\.opencode\skills\`。
3. **遇到 Anthropic 專屬內容時要泛化**，不能把 Anthropic 品牌、Claude UI 假設、Claude SDK 指令原封不動搬過去。
4. **`web-artifacts-builder` 的目標語意改讀為**：本機瀏覽器可開啟的頁面、單檔 HTML、或靜態網站 bundle，而不是 claude.ai artifact 容器。
5. **文件技能 (`docx` / `pdf` / `pptx` / `xlsx`) 一律視為本機／內部使用技能**，不把它們當成可公開散佈、可直接再授權的 OpenCode 公用技能。
6. **模型是 `gpt-oss-120b`**，因此技能設計要偏向顯式步驟、工具導向、驗證清楚、少依賴隱性推理與 Claude 專屬能力。

本報告的核心判斷可以先濃縮成一句話：

> **Anthropic skills 的外殼格式大致能被 OpenCode 接住，但內部工作流、輸出語意與執行假設不能直接照搬。**

也就是說，這不是「搬檔案」工程，而是「保留技能架構、重寫技能語義」工程。

---

## 2. Anthropic skills 實作總覽

### 2.1 倉庫層級與組成

從本次直接檢視的內容來看，`D:\Projects\coding-agent\skills` 的核心結構如下：

- `README.md`：說明什麼是 skills、如何在 Claude Code / Claude.ai / API 中使用。
- `.claude-plugin\marketplace.json`：把技能包成 marketplace plugin 的分組清單。
- `spec\agent-skills-spec.md`：實際上只是轉址到外部 `agentskills.io`，倉庫內沒有完整自足的規格文件。
- `template\SKILL.md`：最小化技能模板。
- `skills\`：真正的技能目錄。

本機直接統計觀察到：

- **17 個 skill 目錄**
- **整個來源 repo 約 375 個檔案**
- **`skills\skills\` 子樹約 369 個檔案**

這代表 Anthropic skills 不是只有幾個簡單 prompt；其中不少技能其實是 **說明文件 + 執行腳本 + 參考資料 + 模板資產** 的組合。

### 2.2 Marketplace / skill family 的實際分組

`.claude-plugin\marketplace.json` 把技能分成三組：

1. **`document-skills`**
   - `xlsx`
   - `docx`
   - `pptx`
   - `pdf`

2. **`example-skills`**
   - `algorithmic-art`
   - `brand-guidelines`
   - `canvas-design`
   - `doc-coauthoring`
   - `frontend-design`
   - `internal-comms`
   - `mcp-builder`
   - `skill-creator`
   - `slack-gif-creator`
   - `theme-factory`
   - `web-artifacts-builder`
   - `webapp-testing`

3. **`claude-api`**
   - `claude-api`

### 2.3 以職能重新分類，比 marketplace 分組更有遷移意義

若從「OpenCode 要怎麼重寫」的角度看，較合理的分類是：

#### A. 基礎設計 / 風格系統
- `brand-guidelines`
- `theme-factory`
- `frontend-design`

#### B. 創意輸出 / 視覺產物
- `algorithmic-art`
- `canvas-design`
- `web-artifacts-builder`
- `slack-gif-creator`

#### C. 開發 / 技術技能
- `claude-api`
- `mcp-builder`
- `webapp-testing`
- `skill-creator`

#### D. 協作 / 溝通技能
- `doc-coauthoring`
- `internal-comms`

#### E. 文件處理技能（內部線）
- `docx`
- `pdf`
- `pptx`
- `xlsx`

### 2.4 最值得保留的總體特徵

Anthropic skills 值得保留的，不是「Claude」本身，而是下面幾種做法：

1. **技能是資料夾，不是單一 prompt**：這讓技能可以攜帶腳本、參考資料、範例、模板、資產。
2. **以 `description` 決定觸發條件**：這是技能體驗的真正入口。
3. **把重複、確定性高的工作外包給腳本**：例如驗證、打包、轉換、格式化。
4. **用 `SKILL.md` 當流程樞紐**：真正的執行規範寫在這裡，其他檔案按需讀取。
5. **大型技能有明顯的層級化資源設計**：`references/`、`scripts/`、`assets/`、`examples/` 等。

這些都是 OpenCode 應該保留的「技能作法」，不是只屬於 Claude 的東西。

---

## 3. 每個 skill 的共同結構與設計模式

### 3.1 共同最小結構

Anthropic skills 的最低配結構非常簡單：

```text
skill-name\
  SKILL.md
```

`SKILL.md` 內通常以 YAML frontmatter 開頭：

```yaml
---
name: skill-id
description: 何時觸發、做什麼
license: （可選）
compatibility: （可選）
---
```

然後才是 markdown 指令內容。

### 3.2 複雜技能的常見結構

較大型技能則常見下列層級：

```text
skill-name\
  SKILL.md
  LICENSE.txt
  scripts\
  references\
  assets\
  templates\
  examples\
  agents\
```

### 3.3 Anthropic skills 的核心設計模式

| 設計模式 | 來源特徵 | 是否保留 | OpenCode 遷移方式 |
| --- | --- | --- | --- |
| `description` 兼具用途與觸發詞 | 幾乎所有 `SKILL.md` | **保留** | 仍以 `description` 當主要 trigger，但改成 OpenCode / gpt-oss-120b 可理解的描述，不寫 Claude 專屬語彙。 |
| `SKILL.md` 當主流程、其他檔案按需載入 | `skill-creator`、`mcp-builder`、`webapp-testing` 等 | **保留** | 沿用層級式載入；長內容搬到 `references\`。 |
| 腳本負責確定性工作 | `web-artifacts-builder`、`docx`、`xlsx`、`webapp-testing` | **保留** | 但腳本要改成 OpenCode / Windows 友善、跨平台、可能力檢查。 |
| 模板與資產打包 | `algorithmic-art`、`theme-factory`、`canvas-design` | **保留** | 保留「模板／資產」概念，但去掉 Anthropic 品牌鎖定。 |
| 輸出格式很明確 | 例如 `.html`、`.png`、`.pdf`、`.gif` | **保留** | OpenCode 版要更明確寫「輸出到本機檔案」，不要假設 Claude UI 自動展示。 |
| artifact-first workflow | `algorithmic-art`、`web-artifacts-builder`、`doc-coauthoring` | **重寫** | 改成 file-first / browser-first workflow。 |
| sub-agent fan-out | `skill-creator`、`doc-coauthoring`、`pptx` QA | **重寫** | 改為順序式檢查、背景任務、或明確的 review checklist。 |
| 品牌／模型／產品名硬編碼 | `brand-guidelines`、`claude-api`、`algorithmic-art` 模板 | **移除或泛化** | 用 vendor-neutral 內容取代。 |
| 對外部 binary 有強假設 | `LibreOffice`、`pandoc`、`markitdown`、`bash` | **重寫** | 加 capability check、fallback、或改寫成 Python/Node 工作流。 |

### 3.4 最重要的遷移洞見

Anthropic skills 的真正價值在於 **把複雜工作拆成可重複的作業說明**；因此在 OpenCode 中，最該保留的是：

- 清楚的觸發邏輯
- 明確的步驟
- 工具 / 腳本 / 範本的協作關係
- 最終產物與驗證方式

最不該直接繼承的是：

- 對 Claude UI 的想像
- 對 Claude model / SDK 的指定
- 對 Anthropic 品牌與產品能力的依附
- 對 sub-agent 與 artifact 系統的隱性依賴

---

## 4. Claude 專屬假設與為何不能直接搬到 OpenCode

以下是這批 skills 中最常見、也最需要切斷的 Claude 專屬假設：

| Claude / Anthropic 假設 | 具體例子 | 為何不能直接搬到 OpenCode | 我們的處理方式 |
| --- | --- | --- | --- |
| **Claude / Opus 模型是預設真理** | `claude-api` 明寫 `claude-opus-4-6`、adaptive thinking、Agent SDK | 這是供應商專屬知識，不是 OpenCode 共通能力 | 改寫成 `opencode-llm-api` 或 provider-neutral API skill。 |
| **claude.ai artifacts 會承接輸出** | `web-artifacts-builder`、`algorithmic-art`、`doc-coauthoring` | OpenCode 是工具/執行環境，不保證有 claude.ai artifact 容器 | 改為本機檔案、單檔 HTML、靜態 bundle、browser-first。 |
| **可以直接叫 sub-agent 幫忙** | `skill-creator`、`doc-coauthoring`、`pptx` QA | OpenCode 不應假設存在 Claude Code 那種 sub-agent API 與語意 | 改成順序式 reviewer checklist、背景任務、或人工可驗證輸出。 |
| **Anthropic 品牌必須保留** | `brand-guidelines`、`algorithmic-art` 模板要求 Poppins/Lora、固定色票 | OpenCode 版本不應綁 Anthropic 視覺身分 | 泛化成使用者品牌 token 或中立主題系統。 |
| **Claude 專用工具名稱存在** | `create_file`、`str_replace`、`AskUserQuestion`、connector 整合敘述 | OpenCode 的工具面與命名不同，不能硬綁 | 改寫成 OpenCode 通用 read/edit/write/search/todo 流程。 |
| **Office / binary 能力必然存在** | `LibreOffice`、`pandoc`、`markitdown`、`pdftoppm` | 這些在不同機器上不一定存在，尤其目前工作環境是 Windows | 改成 capability check + fallback，必要時降階功能。 |
| **Bash / Unix 路徑預設可用** | `bundle-artifact.sh`、`/tmp/inspect.png`、`nohup` | 目前執行環境是 Windows；OpenCode 也常跨平台 | 把腳本改成 Node / Python 或 PowerShell 可替代流程。 |
| **技能可以寫得很長、很詩性，模型仍能穩定執行** | `algorithmic-art`、`canvas-design` 大量工藝/美學重複語句 | `gpt-oss-120b` 的技能應偏向短、明、可檢查 | 保留概念，壓縮語氣，增加操作步驟與驗證規則。 |

### 4.1 最關鍵的一句話

**OpenCode 很可能能讀這些 skill 資料夾，但不代表它能照 Anthropic 的工作流執行。**

格式層面相容，不代表行為層面相容。遷移工作的主體，是把 skill 的「隱含執行前提」改寫成 OpenCode 可落地的工作規範。

---

## 5. OpenCode + gpt-oss-120b 的技能設計原則

### 5.1 先講結論：OpenCode 版 skill 的外形可以很像 Anthropic，但內容語義必須重新定義

從既有 OpenCode 研究結果來看，OpenCode 會把 skills 視為 Markdown 型知識與作業規範，並能從例如 `.opencode\skills\...`、`.claude\skills\...` 等位置探索技能。這代表：

- **skill 目錄 + `SKILL.md`** 這個外型可以沿用。
- 真正需要重寫的是 **trigger wording、工具假設、輸出語意、驗證流程、相依腳本**。

### 5.2 建議的 OpenCode 目標技能形狀

```text
D:\Projects\coding-agent\.opencode\skills\
  <skill-id>\
    SKILL.md
    references\
    scripts\
    assets\
    examples\
```

其中：

- `SKILL.md`：保持短而清楚，最好把主要流程壓在可讀範圍內。
- `references\`：放長文件、規範、語法細節。
- `scripts\`：放可執行、可重複、可驗證的 helper。
- `assets\`：主題、字體、模板、圖示等。
- `examples\`：示例輸入/輸出與測試案例。

### 5.3 針對 OpenCode + `gpt-oss-120b` 的具體設計原則

1. **步驟要顯式，不要靠暗示。**  
   Anthropic skills 很多地方把高階審美與隱性判斷寫得很重；OpenCode 版要改成可執行步驟與清楚的 done criteria。

2. **多用 checklists，少用重複修辭。**  
   尤其在 `algorithmic-art`、`canvas-design` 這種技能裡，保留美學方向即可，不要重複十幾次「像頂尖大師般精雕細琢」。

3. **以工具與檔案為主，不以 UI 容器為主。**  
   所有輸出都應明示為本機檔案、資料夾、HTML 或靜態 bundle，不依賴 chat UI 自動 render。

4. **先寫 capability check，再談進階功能。**  
   例如 `LibreOffice`、`pandoc`、`markitdown`、`ffmpeg` 這些要先檢查可用性；不可用時要有 fallback。

5. **跨平台優先，至少要在 Windows 可落地。**  
   目前環境就是 Windows，因此新技能不要把 Bash-only 流程當預設。

6. **保留 trigger description 的強度，但改成 vendor-neutral。**  
   Anthropic skill 很會把「什麼情境要觸發」寫清楚，這點要保留。

7. **資源分層保留，但 body 要更精簡。**  
   長篇內容應拆去 `references\`，主 skill 只留下流程骨架與何時讀參考檔的規則。

8. **把驗證步驟內建進 skill。**  
   不只是告訴模型「做完」，而要說明「怎麼驗證做對了」。

9. **Anthropic-specific name 一律改名或泛化。**  
   尤其是 `claude-api` 這種名稱，進 OpenCode 後應直接換掉，不保留 vendor 名。

10. **文件技能走 internal-only 分支。**  
   這些技能可以保留能力目標，但應在命名、說明與散佈邊界上明確標註為內部/本機用途。

### 5.4 我們應保留的 OpenCode 技能品質標準

每一個 OpenCode skill 最好都回答下面四件事：

1. **什麼時候要觸發？**
2. **要讀哪些檔案／腳本？**
3. **產出什麼？存在哪裡？**
4. **怎麼驗證結果不是壞的？**

只要這四件事沒有寫清楚，技能在 OpenCode 端就容易變成「看似有知識、實際很飄」。

---

## 6. 所有 skills 的分類與改寫地圖

> 以下表格中的「保留 / 重寫 / 移除」是以 **OpenCode 改寫版** 為目標，不是要回頭修改原始 Anthropic skills repo。

### 6.1 基礎設計 / 風格系統

| Skill | OpenCode 目標 | 保留 | 重寫 | 移除 | 判定 |
| --- | --- | --- | --- | --- | --- |
| `brand-guidelines` | `.opencode\skills\brand-guidelines` | 「把品牌規則套用到輸出」這個概念 | 改成讀取使用者提供的品牌 token、色票、字體、logo 規則；若無品牌資料則要求先蒐集 | Anthropic 色票、字體、品牌名稱、Anthropic 專屬語句 | **重大改寫** |
| `theme-factory` | `.opencode\skills\theme-factory` | 預設主題資料庫、主題套用流程、theme data-driven 做法 | 主題格式統一成可供 HTML / PDF / PPTX / docs 共用的 design tokens | 任何對 Anthropic 品牌的依附 | **輕量泛化** |
| `frontend-design` | `.opencode\skills\frontend-design` | 高品質 UI 指南、避免廉價模板感、重視 typography / motion / composition | 加入 OpenCode / gpt-oss-120b 可執行的設計 checklist、可及性與 responsive 明確驗證 | 「Claude 很會做創意」這類自我宣告、過度倚賴特定流行字體的否定式修辭 | **輕量泛化** |

### 6.2 創意輸出 / 視覺產物

| Skill | OpenCode 目標 | 保留 | 重寫 | 移除 | 判定 |
| --- | --- | --- | --- | --- | --- |
| `algorithmic-art` | `.opencode\skills\algorithmic-art` | philosophy → algorithm → output 的流程、seeded randomness、p5.js / generative art 核心 | 輸出改成本機 HTML 檔；模板改為中立版；用更短、更可執行的流程與驗收條件 | 「必須從 Anthropic 模板開始」「保留 Anthropic branding」等硬規則 | **重大改寫** |
| `canvas-design` | `.opencode\skills\canvas-design` | philosophy → PDF/PNG 視覺輸出、PIL / ReportLab 流程、視覺主導思路 | 字體改為可選；補能力檢查；把超長美學修辭壓成操作規則與 QA 清單 | 過度誇飾的 craftsmanship 重複語句、硬依賴本機字體資產 | **重大改寫** |
| `web-artifacts-builder` | `.opencode\skills\web-artifacts-builder` | React + TypeScript + Tailwind + component system 的建構思路 | 重新定義為本機瀏覽器輸出技能：支援 `single-html` 與 `static-bundle`；腳本改成 Node / Python / cross-platform | 「share artifact in Claude conversation」這類 claude.ai 語意、Bash-only 預設 | **重大改寫** |
| `slack-gif-creator` | `.opencode\skills\slack-gif-creator` | PIL / imageio 工作流、Slack GIF 參數與驗證工具、動畫概念庫 | 補 Windows 友善範例與依賴檢查；整理成本機檔案輸出流程 | 不可攜的假設路徑與過度依賴 chat artifact 的敘述（幾乎沒有） | **小幅改寫** |

### 6.3 開發 / 技術技能

| Skill | OpenCode 目標 | 保留 | 重寫 | 移除 | 判定 |
| --- | --- | --- | --- | --- | --- |
| `claude-api` | `.opencode\skills\opencode-llm-api` | 語言偵測、依需求讀不同 reference、分 use case 選擇介面的思路 | 全面改寫成 OpenCode + `gpt-oss-120b` / provider-neutral / OpenAI-compatible 風格的 API 技能 | Anthropic SDK、Agent SDK、Claude model ID、adaptive thinking 等專屬內容 | **替代重寫（非直接移植）** |
| `mcp-builder` | `.opencode\skills\mcp-builder` | 四階段流程（研究→實作→測試→評估）、MCP 最佳實踐 | 把評估段改成 OpenCode 可執行流程；補 OpenCode + MCP 的使用脈絡 | 如果有任何暗含 Anthropic 客戶端能力的敘述就移除 | **輕量泛化** |
| `webapp-testing` | `.opencode\skills\webapp-testing` | Playwright 腳本化測試、with_server helper、recon-then-action pattern | 例子改成 Windows / cross-platform 路徑；明示輸出截圖、log、報告的保存位置 | `/tmp/...` 之類 Unix 路徑慣性 | **輕量泛化** |
| `skill-creator` | `.opencode\skills\skill-creator` | 訪談→草稿→測試案例→評估→迭代的 meta-skill 核心流程 | 所有 eval orchestration 重寫成 OpenCode todos + 順序/背景任務；review viewer 改成 markdown 或靜態 HTML | sub-agent fan-out、Claude 專用 viewer 假設、`nohup` / `/skill-test` 類依賴 | **重大改寫** |

### 6.4 協作 / 溝通技能

| Skill | OpenCode 目標 | 保留 | 重寫 | 移除 | 判定 |
| --- | --- | --- | --- | --- | --- |
| `internal-comms` | `.opencode\skills\internal-comms` | 依文類選 template、依範例檔引導輸出、內部溝通框架 | 範例內容改成中立公司場景；讓 tone / audience / format 更清楚 | Anthropic 或特定公司脈絡的例子 | **輕量泛化** |
| `doc-coauthoring` | `.opencode\skills\doc-coauthoring` | Stage 1 蒐集脈絡、Stage 2 逐段精修、以文件為中心的協作節奏 | Stage 3 reader testing 改為 checklist / blind self-review / 可選第二輪 session；檔案操作改成 OpenCode read/edit/write 語意 | `create_file`、`str_replace`、connector 必然存在、sub-agent 必然存在等假設 | **中度改寫** |

### 6.5 文件技能（內部 / 本機專用線）

> 這四個技能不建議當成「對外公開的 OpenCode skill 套件」處理；建議改寫為 **internal-only** 版本，並用新文案重新撰寫，不直接搬原始 source-available / proprietary 指示內容。

| Skill | OpenCode 目標 | 保留 | 重寫 | 移除 | 判定 |
| --- | --- | --- | --- | --- | --- |
| `docx` | `.opencode\skills\docx-internal` | Word 文件建立/讀取/編修需求、OOXML 工作知識、`python-docx` / `docx-js` 方向 | 改成 internal-only skill；把 LibreOffice 變成可選；明確寫 fallback；改用全新 OpenCode 文案 | 公開散佈前提、硬保證 `LibreOffice` 存在、原始 proprietary 文案直搬 | **內部重寫** |
| `pdf` | `.opencode\skills\pdf-internal` | `pypdf` / `pdfplumber` / `reportlab` 的基礎工作流、表單/擷取/合併能力 | 以本機 PDF 工具鏈為主重寫；OCR / 表單 / 進階驗證設為可選功能 | 公開再授權想像、任何 vendor-specific 假設 | **內部重寫** |
| `pptx` | `.opencode\skills\pptx-internal` | deck 建立/編修/QA 的知識、`python-pptx` / `pptxgenjs` 方向 | 改成本機簡報 skill；把 QA 改成順序式檢查；不再依賴 sub-agent；LibreOffice 只作可選項 | Claude sub-agent QA、公開散佈前提、硬性 LibreOffice 流程 | **內部重寫** |
| `xlsx` | `.opencode\skills\xlsx-internal` | 公式優先、openpyxl / pandas 工作流、格式化規則、金融模型細節 | 把 recalculation 改成 capability-based；寫清楚無法重算時的警告與降階策略 | `LibreOffice Required` 這種硬承諾、公開可散佈假設 | **內部重寫** |

### 6.6 總結成一句話

- **保留**：技能資料夾結構、trigger 設計、腳本/參考檔/資產分層、明確輸出與驗證。
- **重寫**：所有 runtime 假設、Claude 專屬工具/模型/產品語言、artifact/sub-agent 流程、Bash-only 腳本。
- **移除**：Anthropic 品牌鎖定、Claude model ID、直接分享 artifact 到 claude.ai 的語義、把專有文件技能當成可公開搬運內容的假設。

---

## 7. 高風險技能與關鍵決策

### 7.1 `claude-api`：這不是移植，是替換

**關鍵決策**：不做 `claude-api` 的原樣 port，而是建立新的 `opencode-llm-api` skill。

原因：

- 名稱本身就已綁供應商。
- 內容深度依賴 Anthropic SDK / Agent SDK。
- 連 model defaults 都是 Claude 專用。

因此要保留的是「API integration skill 的職能」，不是 `claude-api` 這個內容本身。

### 7.2 `skill-creator`：要等其他技能先有一批，才值得重寫

**關鍵決策**：`skill-creator` 不應第一個改，應該在 3–5 個 OpenCode 技能改完後再做。

原因：

- 它本質上是「評估別的 skill 的 skill」。
- 若沒有可用的 OpenCode skills 作為測試母體，很難把評估流程重寫對。
- 它原本最重的優勢（sub-agent fan-out + HTML review viewer）在 OpenCode 上都不能直接假設存在。

### 7.3 文件技能：不公開移植，走 internal-only、fresh-authoring 路線

**關鍵決策**：`docx` / `pdf` / `pptx` / `xlsx` 進 OpenCode 時一律走 internal-only 線，並以**重新撰寫的 skill** 方式落地。

原因：

- README 已明講這批 document skills 不是 open source，而是 source-available / proprietary。
- 它們又高度依賴 `LibreOffice`、`pandoc`、`markitdown` 等外部能力。
- 就算概念要留，也不應把原技能內容視為可直接轉貼的公用資產。

### 7.4 `web-artifacts-builder`：輸出語意要先定義清楚

**關鍵決策**：OpenCode 版 `web-artifacts-builder` 應支援兩種明確模式：

1. **`single-html`**：單檔 HTML，可直接用瀏覽器打開。
2. **`static-bundle`**：完整靜態網站目錄，可用一般 dev server / static host 開啟。

原因：

- 這能對應使用者給的預設：「local browser / single-file HTML / static web bundle」。
- 也能讓 `algorithmic-art`、互動式 demo、前端 prototype 共用同一套交付語意。

### 7.5 `algorithmic-art` / `canvas-design`：保留靈魂，壓縮修辭

**關鍵決策**：保留 philosophy-first 的創作框架，但大幅壓縮冗餘修辭，換成可執行 QA 規則。

原因：

- 原技能很有創意，但有些段落更像在刺激 Claude 的藝術自我定位。
- 對 `gpt-oss-120b` 來說，更有效的 skill 會是：
  - 設計方向
  - 參數邊界
  - 輸出格式
  - 品質檢查點

### 7.6 `doc-coauthoring`：Reader Testing 要從「另一個 Claude」改成「可重複的讀者檢查流程」

**關鍵決策**：Stage 3 不再假設可以叫「新鮮的 Claude」來測，而是改成：

- 讀者問題清單
- 盲讀檢查
- 缺漏 / 歧義 / 前置知識依賴盤點
- 必要時再用第二輪 session 或人工 reviewer 補強

### 7.7 `brand-guidelines`：不要跟 `theme-factory` 合併，但兩者要重新分工

**關鍵決策**：

- `brand-guidelines`：專門處理**有品牌資料時**如何套用品牌。
- `theme-factory`：專門處理**沒有品牌資料時**提供現成中立主題。

這樣比把兩者硬合成一個 skill 更清楚，也更符合真實工作情境。

---

## 8. 我們採用的預設改寫策略

### 8.1 目錄與安全邊界

1. **所有新技能都寫到** `D:\Projects\coding-agent\.opencode\skills\`。
2. **原始 `D:\Projects\coding-agent\skills` 只讀不改**。
3. **供應商專屬 skill 改名**；非供應商專屬 skill 儘量保留原功能名。
4. **文件技能採 `-internal` 命名**，例如：
   - `docx-internal`
   - `pdf-internal`
   - `pptx-internal`
   - `xlsx-internal`

### 8.2 全域保留 / 全域重寫 / 全域移除

| 類別 | 內容 |
| --- | --- |
| **全域保留** | 技能目錄結構、`SKILL.md` frontmatter、trigger description、references/scripts/assets 分層、明確輸出格式、驗證思路。 |
| **全域重寫** | OpenCode 工具語意、Windows / cross-platform 指令、artifact → file/browser 流程、sub-agent → checklist / 背景任務流程、能力檢查與 fallback。 |
| **全域移除** | Anthropic 品牌、Claude model IDs、Agent SDK 專屬敘述、claude.ai artifact 語言、直接假設 connectors / sub-agents / LibreOffice 一定存在。 |

### 8.3 Web 類技能的統一交付策略

對 OpenCode 版網頁技能，我們採以下預設：

- **首選交付物**：本機 HTML、CSS、JS 或靜態輸出目錄。
- **可選交付模式**：
  - 單檔 HTML
  - 靜態 bundle
  - 小型 React/TS 專案
- **不再使用的語意**：
  - 「把 artifact share 回對話」
  - 「claude.ai 會直接渲染」

### 8.4 文件技能的處理策略

文件技能不是不做，而是 **隔離做**：

- 僅視為本機／內部工作流。
- 新版 skill 文案應重新撰寫，不直接搬 proprietary 指示文字。
- 功能必須分層：
  - 基礎能力（讀、寫、抽取、格式化）
  - 進階能力（轉檔、重算、視覺預覽、驗證）
- 進階能力要有 capability check，不能把 `LibreOffice`、`pandoc` 等視為必然存在。

### 8.5 `gpt-oss-120b` 導向的 prompt 風格

OpenCode 版 skill 的文風應改成：

- 多用 **步驟**、**規則**、**例外處理**
- 少用重複的「這要像大師作品」式修辭
- 多寫 **做完怎麼驗證**
- 多寫 **失敗時怎麼退回簡化流程**
- 盡量把長 reference 拆到外部檔案，而不是把整份美學或 SDK 文檔塞進 `SKILL.md`

### 8.6 不採用的策略

這次我們明確**不採用**以下做法：

1. 不直接把 `skills\skills\*` 複製後只做字串置換。
2. 不把 Anthropic 品牌與 Claude 產品名留在 OpenCode 技能中。
3. 不把 document skills 當作可公開散佈的開源成果處理。
4. 不把 Bash-only 腳本當作 Windows / OpenCode 的預設工作流。

---

## 9. 後續改寫執行順序

### 9.1 建議總順序

我建議以「先建立共用底座，再處理高耦合技能，最後收 document internal 線」為順序。

### 9.2 具體 phase 規劃

| Phase | 優先技能 | 目的 | 為何這時做 |
| --- | --- | --- | --- |
| **Phase 0** | 共用遷移模板、OpenCode skill skeleton | 先統一命名、frontmatter、folder shape、驗證規則 | 若沒有共同骨架，後面每個 skill 都會各自長歪。 |
| **Phase 1** | `brand-guidelines`、`theme-factory`、`frontend-design` | 建立視覺與風格底座 | 後續創意與 web 技能都會用到。 |
| **Phase 2** | `webapp-testing`、`internal-comms`、`mcp-builder`、`slack-gif-creator` | 先拿低風險技能做 OpenCode 版範例 | 可快速建立遷移節奏與驗證方式。 |
| **Phase 3** | `web-artifacts-builder` | 建立 browser / single-html / static-bundle 的統一輸出語意 | `algorithmic-art` 與其他 web 輸出會依賴它。 |
| **Phase 4** | `algorithmic-art`、`canvas-design` | 處理高價值創意技能 | 此時已有主題、前端與輸出方式可共用。 |
| **Phase 5** | `doc-coauthoring` | 把協作式文件工作流改成 OpenCode 友善版本 | 依賴先前建立好的 file-first workflow。 |
| **Phase 6** | `claude-api` → `opencode-llm-api` | 完成供應商專屬技能的替換 | 範圍大但獨立，可與 Phase 2–5 部分並行。 |
| **Phase 7** | `skill-creator` | 重建技能自我改良與評估能力 | 最好等前面已有數個改寫完成的技能，才有真實樣本可驗證。 |
| **Phase 8** | `pdf-internal`、`xlsx-internal`、`docx-internal`、`pptx-internal` | 收斂 internal-only 文件技能線 | 這批最吃環境、相依最多，放最後最務實。 |

### 9.3 若要排成實際一條龍順序

若要列出一個更具體的單列順序，我會建議：

1. 建立 OpenCode skill template / migration rubric  
2. `brand-guidelines`  
3. `theme-factory`  
4. `frontend-design`  
5. `webapp-testing`  
6. `internal-comms`  
7. `mcp-builder`  
8. `slack-gif-creator`  
9. `web-artifacts-builder`  
10. `algorithmic-art`  
11. `canvas-design`  
12. `doc-coauthoring`  
13. `claude-api` → `opencode-llm-api`  
14. `skill-creator`  
15. `pdf-internal`  
16. `xlsx-internal`  
17. `docx-internal`  
18. `pptx-internal`

### 9.4 可以並行的部分

可並行處理的群組：

- `brand-guidelines` / `theme-factory` / `frontend-design`
- `webapp-testing` / `internal-comms` / `slack-gif-creator`
- `algorithmic-art` / `canvas-design`
- `pdf-internal` / `xlsx-internal`（若工具鏈獨立）

不建議太早並行的：

- `skill-creator`（因為它依賴前面技能的成熟度）
- `web-artifacts-builder` 與所有 web 類 skill 的最終交付約定（要先把規格定死）

---

## 10. 結論

Anthropic skills 值得學的地方很多，但真正能直接帶進 OpenCode 的，主要是 **技能封裝方式**、**作業分層方式**、**描述觸發方式**，不是 Claude 專屬工作流本身。

因此，後續改寫應遵守三個核心原則：

1. **保留技能架構，不保留 Claude 假設。**
2. **保留能力目標，不保留 Anthropic 品牌與供應商綁定。**
3. **保留文件 / web / 測試 / 創意等 skill 家族，但用 OpenCode + `gpt-oss-120b` 的可執行方式重寫。**

若用一句話總結第一階段分析：

> **這是一個很值得遷移的技能庫，但遷移方法必須是「重新定義執行語意」而不是「直接平移 prompt 與腳本」。**

對後續實作而言，最務實的路線是：

- 先把共用 skill skeleton 與 cross-platform 腳本策略定好；
- 再用低風險技能建立 OpenCode 版風格；
- 最後處理高風險的 API、meta-skill 與 internal-only document skills。

---

## 11. 參考來源 / 檢視檔案

### 11.1 倉庫與總覽檔案

- `D:\Projects\coding-agent\skills\README.md`
- `D:\Projects\coding-agent\skills\.claude-plugin\marketplace.json`
- `D:\Projects\coding-agent\skills\spec\agent-skills-spec.md`
- `D:\Projects\coding-agent\skills\template\SKILL.md`

### 11.2 直接檢視的 skill 檔案

- `D:\Projects\coding-agent\skills\skills\algorithmic-art\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\brand-guidelines\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\canvas-design\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\claude-api\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\doc-coauthoring\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\docx\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\frontend-design\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\internal-comms\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\mcp-builder\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\pdf\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\pptx\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\skill-creator\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\slack-gif-creator\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\theme-factory\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\web-artifacts-builder\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\webapp-testing\SKILL.md`
- `D:\Projects\coding-agent\skills\skills\xlsx\SKILL.md`

### 11.3 補充檢視的參考 / 腳本檔案

- `D:\Projects\coding-agent\skills\skills\web-artifacts-builder\scripts\bundle-artifact.sh`
- `D:\Projects\coding-agent\skills\skills\webapp-testing\scripts\with_server.py`
- `D:\Projects\coding-agent\skills\skills\mcp-builder\reference\evaluation.md`
- `D:\Projects\coding-agent\skills\skills\skill-creator\agents\analyzer.md`

### 11.4 OpenCode 目標環境參考

- `D:\Projects\coding-agent\reports\2026-03-08-opencode-report-zh-tw.md`

### 11.5 本次額外觀察

- 直接列舉 `D:\Projects\coding-agent\skills\skills\` 下全部 skill 目錄
- 以 PowerShell 統計各 skill 檔案數與大致行數
- 確認 OpenCode 目標目錄 `D:\Projects\coding-agent\.opencode\skills\` 存在，且可作為平行技能樹位置

