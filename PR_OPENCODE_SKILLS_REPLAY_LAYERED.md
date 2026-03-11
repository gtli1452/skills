# PR 說明：將 OpenCode adaptations 分層重放到 `.opencode/skills/`

## 建議 PR 標題

`Replay OpenCode skill adaptations into .opencode/skills with per-skill commits`

## PR 內文（可直接貼到 GitHub PR）

### 背景

目前這個 fork 需要同時滿足兩個目標：

- 保留 repo root 的 `skills/` 作為 Anthropic upstream skill tree，之後可以直接 sync fork
- 把 OpenCode 版本的改寫放在 `.opencode/skills/`，並保留「每個 skill 一個 commit」的 review 歷史，方便看出各 skill 相對 upstream 到底改了哪些地方

先前雖然已完成技能改寫，但 history 對 reviewer 來說不夠理想。這個分支改成從 `main` / `b0cbd3d` 重新建立一條乾淨的 replay history：

- 先用 1 個 setup commit 把 upstream `skills/` 正確複製到 `.opencode/skills/`
- 再依序把 14 個既有 rewrite commit 重放到 `.opencode/skills/<skill>`，每個 skill 各自一個 commit

### 這個 PR 做了什麼

- 新增 `.opencode/skills/` 作為 OpenCode skill tree
- 保持 repo root 的 `skills/` 與 `main` / `upstream/main` 一致，不在這條分支直接修改 upstream skill tree
- 建立 15 個新 commit：
  - 1 個 setup commit：複製 upstream skills 到 `.opencode/skills/`
  - 14 個 replay commits：逐 skill 重放 OpenCode adaptations
- 所有新 commit 都只落在 `.opencode/skills/`，沒有把改動混進 repo root 的 `skills/`

### 為什麼這樣做

- **未來 sync upstream 更乾淨**：`skills/` 保持 Anthropic 原貌，後續同步 upstream 時不容易和本地 adaptations 打架
- **review 更清楚**：reviewer 可以從 setup commit 看 baseline，再逐 commit 看每個 skill 的差異
- **維護更可控**：之後若 upstream 某個 skill 更新，可以直接對照 `.opencode/skills/<skill>` 的對應 commit 歷史來補調整

### 這個 PR 沒有做什麼

- 沒有修改 repo root 的 `skills/`
- 沒有額外改 README、`spec/`、`template/` 或其他 repo-level 檔案
- 沒有替 `pdf`、`slack-gif-creator`、`webapp-testing` 補做獨立 rewrite commit；它們只存在於 setup copy 中，因為原始 `b0cbd3d..c8d9fb8` 範圍本來就沒有這三個 skill 的對應改寫 commit

### 驗證

- 分支：`feat/opencode-skills-replay-layered`
- base：`main` (`b0cbd3d`)
- 新增 commit 數：15
- `.opencode/skills/` 路徑正確，沒有錯誤的 `.opencode/skills/skills/...` 巢狀結構
- repo root `skills/` 與 `main` 無差異
- 所有新 commit 都只改 `.opencode/skills/`
- 15 個新 commit 都包含 `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`

### 建議 reviewer 的閱讀順序

1. 先看 `7709e93`，確認 `.opencode/skills/` baseline copy 是正確的
2. 再依序看 14 個 replay commits，逐 skill 確認 OpenCode adaptation 是否合理
3. 最後確認 repo root `skills/` 沒被碰到

---

## 每個 commit 的 diff 重點

### `7709e93` — `chore(opencode-skills): copy upstream skills into .opencode/skills`

- 把 upstream `skills/` 正確複製到 `.opencode/skills/`，建立 OpenCode skill tree baseline
- baseline 包含 17 個 skills 與其附屬資產、範本、授權檔與腳本
- 這個 commit 的目的不是改寫內容，而是先建立「可被後續逐 skill 改寫」的對照基線
- 後續 reviewer 應以這個 commit 為起點，看每個 replay commit 相對 baseline 改了什麼

### `9fdb7f2` — `rewrite(claude-api): retarget skill for opencode`

- 將 `claude-api` 從 Anthropic SDK / Claude API 導向，改為 OpenCode provider / model workflow 導向
- 刪除語言別教學樹與 Anthropic 專屬參考內容，例如 Python / TypeScript / Go / Java / Ruby / C# / PHP 範例與部分 shared docs
- 新增 OpenCode 對應說明文件，聚焦 `/connect`、`/models`、`opencode.json`、`provider/model-id`、`gpt-oss-120b` 與 migration guidance
- 讓 skill 的用途從「教你怎麼用 Claude API」轉成「教你怎麼在 OpenCode 中設定 provider/model 與遷移既有 Claude 使用方式」

### `786eb86` — `rewrite(algorithmic-art): remove anthropic runtime assumptions`

- 更新 `SKILL.md`，把輸出改成可在本機直接使用的哲學說明檔與 standalone `viewer.html`
- 用「implementation pass」取代對 Claude runtime 的隱含依賴，降低平台耦合
- 調整 `templates/generator_template.js` 與 `templates/viewer.html`，使生成結果更偏向本機可預覽、可攜帶的 HTML / JS 輸出
- 讓這個 skill 不再假設作品會在 Anthropic 特定執行環境中運作

### `9136c90` — `rewrite(brand-guidelines): generalize brand system guidance`

- 把原本偏 Anthropic 品牌套用的 skill，改成可抽取與套用任意專案品牌系統的通用流程
- 新流程聚焦：尋找既有品牌來源、萃取 colors / typography / spacing、轉成 reusable tokens、必要時再 fallback 到 OpenCode 風格參考
- 移除 Anthropic 專屬色票、字體與品牌預設
- 讓 brand-guidelines 可作為更一般化的「品牌系統轉譯 skill」

### `8137365` — `rewrite(canvas-design): retarget outputs for opencode`

- 將輸出定義明確改成可被標準工具開啟的本機 `.md`、`.pdf`、`.png` 檔案
- 把敘述從 Claude-specific phase wording 改成更一般化的「next phase」與 implementation-oriented 語氣
- 強化「交付可攜檔案」而非依賴特定平台渲染結果的定位
- 保留設計哲學，但把交付形式調整成更符合 OpenCode / 本機工作流

### `ba6bc0d` — `rewrite(doc-coauthoring): align workflow with opencode`

- 將 doc co-authoring 流程重新整理成更精簡的 OpenCode 導向三階段流程
- 將「fresh Claude」語意轉成更適合 OpenCode 的「fresh reader session / child agent」驗證方式
- 把工具來源描述調整為 connected tools / MCP servers，而不是抽象的 integrations
- 明確提醒讀者只會看到文件文字內容，強化 alt-text / 文件可讀性的要求

### `bbe06b0` — `rewrite(docx): neutralize assistant metadata defaults`

- 將 `docx` skill 中硬編碼的 `Claude` metadata 預設改成 `Assistant`
- 變更包含 `SKILL.md` 範例與多個 Python 腳本，例如 `comment.py`、`pack.py`、`validate.py`、`redlining` 相關 helper
- `comment.py` 額外加入更一般化的 initials 推導邏輯，降低 Anthropic branding 滲入輸出文件的機會
- 讓 DOCX 相關輸出更 provider-agnostic

### `c457081` — `rewrite(frontend-design): retarget skill wording for opencode`

- 把 frontend-design 的定位從偏靜態展示 / artifact 語境，改為更強調 runnable local code 與 preview-ready assets
- `SKILL.md` 加強本機預覽與交付可執行檔案的要求，例如 `open index.html`、`pnpm dev`
- 移除對 Claude 特性的直接敘述，改成 OpenCode / local-first 的語氣
- 讓 skill 更符合實際前端開發與本機迭代流程

### `4a6f298` — `rewrite(internal-comms): generalize internal comms guidance`

- 將 internal-comms 從較公司內部既定格式語氣，改成更一般化的組織內部溝通 skill
- 擴充 trigger / keyword，納入 leadership update、project update、internal newsletter、incident report 等更通用的用法
- 加入先參考 `AGENTS.md` 或既有 template 的提示，避免對特定公司語境做過多假設
- 讓這個 skill 能在不同團隊與組織情境下重用

### `566d2f8` — `rewrite(mcp-builder): retarget evaluations for opencode`

- 把 evaluation flow 從 Anthropic / Claude 依賴改成 OpenAI-compatible / provider-agnostic 模式
- `scripts/evaluation.py` 改為接受 `--llm-base-url`、`--llm-model`、`--llm-api-key` 等通用參數，也支援相對應環境變數
- `requirements.txt` 移除 `anthropic` 依賴，留下較中性的 runtime 需求
- 相關 reference 文件同步改寫，釐清 MCP transport 與 LLM endpoint 是分開設定的

### `b03735a` — `rewrite(pptx): neutralize assistant metadata defaults`

- 與 `docx` 類似，將 `pptx` skill 中硬編碼的 `Claude` metadata 預設改為 `Assistant`
- 影響多個 Office 相關 Python 腳本與 redlining / packing / validating 流程
- 主要目的是避免在輸出的簡報文件中留下 Anthropic / Claude 特定識別
- 變更範圍小，但對輸出中立性很重要

### `64029f9` — `rewrite(skill-creator): retarget tooling for opencode`

- 將 `skill-creator` 從原本較偏 Claude / Anthropic workflow 的設計，改寫為 OpenCode skill lifecycle
- `SKILL.md` 重點改成：description trigger、progressive disclosure、`AGENTS.md`、`.opencode/skills/`、`opencode run`
- 支援腳本如 `run_eval.py`、`run_loop.py`、`improve_description.py`、`generate_report.py` 改為較符合 OpenCode 本機工作流
- 讓 skill-creator 可以直接用於 OpenCode skill 的撰寫、驗證與疊代

### `568b0db` — `rewrite(theme-factory): retarget themes for local delivery`

- 把 theme-factory 的適用範圍擴大到 decks、docs、web pages、reports 等本機交付物
- 強化 token-first workflow，鼓勵輸出 CSS variables / JSON design tokens，而不只針對簡報或 artifact
- 弱化必須展示 PDF showcase 的要求，改成更適合本機迭代與快速預覽的交付方式
- 新增自訂主題與 local delivery 導向內容，讓 skill 更適合 OpenCode 工作流

### `2e31739` — `rewrite(web-artifacts-builder): retarget builder for local apps`

- 將 `web-artifacts-builder` 從 Claude artifact 語境改寫成 local web app 語境
- 腳本重新命名：`init-artifact.sh` → `init-web-app.sh`，`bundle-artifact.sh` → `bundle-web-app.sh`
- 流程改為以 `pnpm dev` 本機預覽為主，`bundle.html` / 單檔輸出為可選步驟
- 說明文字改成更符合本機開發、瀏覽器開啟與 handoff 的用法

### `4b7d625` — `rewrite(xlsx): neutralize assistant metadata defaults`

- 與 `docx` / `pptx` 相同，把 `xlsx` skill 中的 `Claude` metadata 預設改為 `Assistant`
- 影響 redlining / pack / validate 等 Office helper 腳本
- 目標是讓 Excel 相關輸出保持中性，不暴露特定 AI 產品識別
- 這是一個小而明確的 metadata neutralization commit

---

## 補充說明

- `.opencode/skills/` 現在有 17 個 top-level skills，其中：
  - 14 個有對應 replay rewrite commit
  - 3 個（`pdf`、`slack-gif-creator`、`webapp-testing`）只有 baseline copy，沒有後續 rewrite
- 如果 reviewer 想專注在真正的 OpenCode adaptation，建議從 `9fdb7f2` 開始逐 commit 看，而不是只看整體 aggregate diff
