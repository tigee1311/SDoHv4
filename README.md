# SDoHv4

Streamlit questionnaire for Social Determinants of Health research testing.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit URL in a browser and allow microphone access when prompted.

## Response storage

Responses are saved persistently to `sdoh_responses.xlsx`. Each hospital writes
to its own Excel sheet, and each save appends rows with timestamp, hospital,
anonymous session ID, status (`partial` or `completed`), completion percentage,
question/category, and response data.

The app currently limits survey sessions to four placeholder hospital choices:
`Hospital A`, `Hospital B`, `Hospital C`, and `Hospital D`.

The workbook persistence layer is suitable for research/testing. For HIPAA or
clinical use, move storage to a secure database with authentication, encryption,
audit logs, backups, and access control.

## Hospital-specific downloads

The download page exports only the currently selected hospital. Configure a
download password through an environment variable or Streamlit secret:

```bash
export SDOH_DOWNLOAD_PASSWORD="..."
```

Do not commit response workbooks, `.env` files, or Streamlit secrets.

## Voice features

- Use the global language selector at the top to switch English / Spanish.
- Click `🔊` beside a question to hear the question read aloud.
- Click `🎤` beside a question to open the recorder, record an answer, then click `Transcribe`.
- Transcribed text fills the matching response field. For radio questions, the app chooses the closest option label.
- Voice output uses gTTS by default and caches repeated audio prompts.
- Voice input prefers OpenAI Whisper when `OPENAI_API_KEY` is set. Without that key, it falls back to `speech_recognition`.

## Question explanations

Click `Why this question?` below a question to show a concise explanation based on NIH and AMA social determinants of health guidance. The explanation text lives in `explanations.py` so it stays separate from the Streamlit UI code.

## Optional API keys

```bash
export OPENAI_API_KEY="..."
export OPENAI_TRANSCRIPTION_MODEL="whisper-1"
```

## Optional Google Drive upload placeholder

Drive upload is disabled by default and does not upload files until real Google
Drive API integration is added. Future configuration should use environment
variables or Streamlit secrets:

```bash
export GOOGLE_DRIVE_FOLDER_ID="..."
export GOOGLE_SERVICE_ACCOUNT_JSON="..."
# or
export GOOGLE_APPLICATION_CREDENTIALS="/secure/path/service-account.json"
```

## Microphone notes

Streamlit records through the browser, so local testing requires a browser with microphone permission. If you deploy remotely, users record audio in their own browser and the app transcribes that recording on the server.

If OpenAI Whisper is not configured, the local fallback depends on the `speech_recognition` package and Google Web Speech recognition. For highest reliability in research testing, set `OPENAI_API_KEY`.
