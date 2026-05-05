# Credit Union Intelligence — React Frontend

## Setup

```bash
# Install dependencies
npm install

# Start dev server (requires backend on port 8080)
npm run dev

# Open browser
open http://localhost:3000
```

## Requirements
- Node.js 18+
- Backend running on http://localhost:8080

## Project Structure
```
src/
  api/          ← All API calls (centralized)
  components/   ← Reusable UI components
    UI.jsx          ← Spinner, Badge, StatCard, Toast, etc.
    Topbar.jsx      ← Navigation header
    Sidebar.jsx     ← Model selector, filters, action buttons
    StatsBar.jsx    ← Stats numbers bar
    MemberTable.jsx ← Member table with expandable SHAP rows
    ChatPanel.jsx   ← AI chat with NLP parser
    ResultCards.jsx ← All result card types
  hooks/        ← Custom hooks
    useNLP.js       ← Natural language parser
  pages/        ← Route pages
    Dashboard.jsx   ← Main page
    Members.jsx     ← Full member table
    Jobs.jsx        ← Job triggers + history
    Health.jsx      ← Model health
  store/        ← Zustand global state
    index.js
```

## Pages
- **Dashboard** → Smart query + all buttons + AI chat
- **Members** → Full paginated member table with SHAP reasons
- **Jobs** → Trigger predictions/retrain per model, run history
- **Health** → Model AUC, version, training date

## Chat NLP Examples
- "top 1000 high risk attrition members"
- "Hartford branch propensity report"
- "run predictions for loan model"
- "check model health status"
- "show branch chart for attrition"
- "top 500 members above 80% probability"
