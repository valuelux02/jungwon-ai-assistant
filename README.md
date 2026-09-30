# Jungwon University AI Student Assistant — Step 8 Integrated Prototype

This step combines the earlier prototype parts into one Flask website.

## Included
- AI Chatbot interface (`/api/chat`, interactive web chat)
- Student Administrative Guide: 휴학, 복학, 증명서, 장학금, 졸업요건, 기숙사
- University Notice Search using `data/notices.json`
- Korean / English / Khmer language selector (translation integration is a next-step connection)
- Search across administrative guide and notices (Unified search)
- Health endpoint (`/health`)

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:5008

Windows: run `run_windows.bat`.
macOS/Linux: run `bash run_mac_linux.sh`.

## Important
The source project document specifies the functions, but it does not provide the actual Jungwon University administrative deadlines, fees, or requirements. Therefore the administrative entries are clearly prototype placeholders. Replace them with official school PDFs/notices before presenting real procedures.

The project architecture is designed to connect the PDF extraction/RAG, real AI API, multilingual translation, notices, schedule, facilities and international-student support in later steps.
