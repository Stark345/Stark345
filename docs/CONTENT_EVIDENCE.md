# Content evidence — 30 September 2026

This audit covers the final native-text README. Earlier evidence JSON files in
`scripts/evidence/` are retained as historical inputs, not fresh verification.
The public checks in `public-link-checks.json` were performed during this task.

## Identity, education and contact

- S. Jaichandran, the developer title, Chennai, B.Tech IT, the institution,
  graduation year 2026, CGPA 8.3/10 and both training names come from the user's
  supplied instructions. The local portfolio also corroborates the name, IT
  degree, Chennai and 8.3 CGPA. No new completion dates/statuses were inferred.
- GitHub: `https://github.com/Stark345`; public profile confirmed during review.
- LinkedIn: `https://www.linkedin.com/in/jaichandran-s-139a8b354`; this exact URL
  is cross-linked from the public GitHub profile and HCP/IDS READMEs. LinkedIn
  returned HTTP 999 to an automated check, so destination accessibility remains
  unverified, not reported as a broken identity link.
- Portfolio: `https://sjaichandran-portfolio.netlify.app/`; HTTP 200 with the
  matching developer page title. Its public source retains some placeholder
  links; none were copied into this README. Fixing that separate website is
  outside this task.
- Email: `jaichandran20871@gmail.com` is preserved from the pre-existing README.
  Syntax and consistency checked; no email was sent and ownership/delivery was
  not independently tested.
- No IEEE/IGNITE presentation, award, publication, employer or seniority claim
  was added. Notebook comments referring to a paper do not establish authorship.

## Featured project evidence

### AI-Powered HCP CRM

Exact remote: `https://github.com/Stark345/ai-hcp-crm-`.
Local source: `E:/hcp-crm`.

- `frontend/package.json`: React, Redux Toolkit and Vite.
- `backend-python/requirements.txt`: FastAPI, LangGraph, SQLAlchemy and Groq.
- `backend-python/agents/langgraph/graph.py`, `nodes.py` and `tools.py`: intent,
  extraction, tool selection, confirmation gating and database interaction.
- `frontend/src/components/ChatInterface.jsx`: editable extracted entities and
  explicit confirm-save action.
- `backend-node/package.json`, `src/database/connection.js`: Express,
  Sequelize and SQLite.

Omitted README claims such as zero downtime or production-grade availability;
no load test or deployment was performed.

### ProjectPulse

Exact remote: `https://github.com/Stark345/ProjectPulse-`.
Local source: `E:/ProjectPulse`.

- `client/package.json`, `server/package.json`: React, TypeScript, Express,
  Prisma, Socket.IO and node-cron.
- `server/prisma/schema.prisma`: PostgreSQL provider and relational schema.
- `server/src/websocket/socket.service.ts`: role-scoped rooms, online presence,
  missed-event retrieval ordered by `(createdAt, id)`.
- `server/src/services/task.service.ts`: role and task ownership checks.
- `server/src/jobs/overdueScheduler.ts`: scheduled task checks and deduplication.

The advertised demo redirects to Vercel login and is omitted. Test counts and
production-scale claims were not repeated or freshly verified.

### AI-Powered Intrusion Detection System

Exact remote:
`https://github.com/Stark345/AI-Powered-Intrusion-Detection-System-Using-Hybrid-Deep-Learning-Model`.
Local source: `E:/IDS`.

- `src/model.py`: two Conv1D blocks, LSTM and dense binary classifier.
- `src/preprocess.py`: NSL-KDD columns, one-hot encoding, StandardScaler, SMOTE.
- `train.py`: NSL-KDD train/test URLs, preprocessing, training and evaluation.
- `IDS.ipynb`, cell 9 (zero-based): saved output contains accuracy 75.66%,
  ROC-AUC 0.9268 and 22,544 test records. Attack precision 0.91 and recall 0.63
  are included for context, rather than presenting precision as accuracy.
- Notebook cell 10: SHAP KernelExplainer code and saved completion message.
  Cell 12: LIME code using training samples. `src/explain.py` implements a LIME
  helper with a synthetic background; it is not a complete SHAP module.

These are inspected saved outputs, not newly reproduced results. The notebook
has execution-state inconsistencies (for example, cell 3's source repeats data
loading while its saved output describes preprocessing). No new training or
dataset benchmark was run. CICIDS2017, Transformers and autoencoders are not
presented as completed experiments. Promotional 98% accuracy and publication
language from public metadata were not adopted. The model's feature-axis LSTM
is not described as validated temporal attack-sequence detection.

### Blood Cell Cancer Detection System

Exact remote: `https://github.com/Stark345/Blood-cell-image-cancer-detection`.
Local source: `E:/Blood Cell Cancer Screening Tool`.

- `requirements.txt`: Flask, TensorFlow, OpenCV and NumPy.
- `app.py`: loads a saved model, accepts image uploads, converts to grayscale,
  resizes to 256 × 256, normalizes and predicts; rejects invalid image inputs.

The weights file is named `Brain_cancer_cell.h5`. The inspected code does not
establish its training provenance or clinical validity, so neither diagnostic
accuracy nor clinical deployment is claimed. The original project title is kept.

### ASJ Pipe Scaffolding

Exact remote: `https://github.com/Stark345/ASJ-Pipe-Scaffolding-`.
Local source: `E:/asj-pipe-scaffolding-showcase`.

- `index.html`: HTML/CSS/JavaScript, responsive styles, LocalBusiness JSON-LD
  and a Web3Forms submission endpoint.
- Live domain `https://asjpipescaffolding.com` returned 200 and the matching
  contractor page title. No contact form was submitted.

Hosting-provider and SEO-ranking claims are omitted; the source supports form
integration and structured data, not a measured business outcome.

### Personal Portfolio

Exact remote: `https://github.com/Stark345/Stark-Portfolio`.
Public `main/index.html` inspected directly: HTML/CSS/JavaScript, filter buttons
and a Netlify form. The public source differs from the local
`E:/Stark-Portfolio-Personal` variant, which has no origin remote; the public
source determines this project's stack and features.

## Toolbox and capabilities

React/TypeScript/Tailwind/Vite and Docker are supported by ProjectPulse source
and configuration. Python/FastAPI/Flask/Node/Express/SQLite/PostgreSQL derive from
the projects above. Java, MySQL and MongoDB are supported by the supplied profile
and approved hero; the wording does not assert expert proficiency or imply they
power the six featured projects.

TensorFlow/OpenCV/scikit-learn/NumPy/pandas/Matplotlib/SHAP/LIME derive from the ML
source. Git/GitHub and Jupyter are evidenced by repositories and notebooks.
LangGraph, Groq, tool calling and human review derive from HCP CRM.

BM25, ChromaDB and Sentence Transformers are supported by the existing local
`E:/BIS-Assist/requirements.txt` and `backend/retrieval/{bm25_retriever,
embedding_service,vector_store,hybrid_retriever}.py`. This is described as local
retrieval work; no invented public BIS repository link or finished RAG product
is included. Future IDS extensions are explicitly exploratory.

## Activity and presentation

GitHub's public API returned eight public repositories on 30 September 2026.
All six featured repositories are non-archived and enabled. The README uses a
dated count and native profile links, with no live badge, fabricated streak or
contribution snake.

Existing local Devicon v2.17.0 icons are reused unchanged from
`scripts/evidence/icons/`; their URLs and license remain there. The three new
SVGs are code-drawn supporting illustrations; all explanations remain text.
The approved hero and original source artwork are frozen and separately hashed.
