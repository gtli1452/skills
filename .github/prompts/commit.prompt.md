---
agent: agent
---
請根據提供的 Git 變更摘要，產生一個符合 Conventional Commit 1.0.0 標準的 Git 提交訊息，使用繁體中文。訊息應遵循以下格式：

- **格式**：`<type>[optional scope]: <description>`
  - `type`：變更類型，如 `feat` (新功能)、`fix` (錯誤修正)、`docs` (文件更新)、`style` (程式碼風格)、`refactor` (重構)、`test` (測試)、`chore` (雜項)。
  - `scope`：可選，指定變更影響的範圍，如檔案或模組名稱。
  - `description`：簡潔的變更摘要（不超過 50 字元），使用動詞開頭，如「新增」、「修正」、「更新」等。
- **Body**：可選，詳細說明變更內容，包括：
  - 影響的檔案或模組
  - 變更的原因或背景
  - 任何相關的問題或功能請求編號（如果適用）
  - 潛在的影響或注意事項
- **Footer**：可選，用於重大變更 (BREAKING CHANGE) 或關閉問題，如 `BREAKING CHANGE: description` 或 `Closes #123`。

範例：

```
feat: 新增防火牆切換功能

- 影響檔案：background/service-worker.js, popup/popup.js
- 新增了動態切換防火牆狀態的功能，使用 chrome.storage 儲存設定
- 改善了使用者體驗，允許即時切換而不需重新載入頁面
```

```
fix: 修正內容腳本注入失敗的問題

- 影響檔案：content/content-script.js
- 修正了在某些網站上腳本無法注入的錯誤，改用 chrome.scripting API
- 增加了錯誤處理和重試機制
```

```
docs: 更新擴充功能說明文件

- 影響檔案：README.md, manifest.json
- 更新了安裝指南和 API 使用說明
- 加入了 Manifest V3 遷移的詳細步驟
```

```
refactor: 重構 Service Worker 程式碼結構

- 影響檔案：background/service-worker.js
- 將事件監聽器重構為模組化函式，提高程式碼可維護性
- 移除了不必要的全域變數，減少記憶體使用
```

```
test: 新增單元測試覆蓋核心邏輯

- 影響檔案：test/service-worker.test.js
- 為儲存和訊息通訊功能新增測試案例
- 提高了程式碼品質和可靠性
```

```
chore: 更新依賴套件版本

- 影響檔案：package.json
- 將 Chrome Extensions API 更新至最新版本
- 確保相容性和安全性
```