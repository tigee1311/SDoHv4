"""Local FAQ matching and floating chatbot UI for the SDoH app."""

from __future__ import annotations

import difflib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


FAQ_DATA_PATH = Path(__file__).with_name("faq_answers.json")
UNKNOWN_ANSWER = "I do not have that answer."
MIN_MATCH_SCORE = 0.62

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "could",
    "do",
    "does",
    "for",
    "from",
    "have",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "who",
    "why",
    "will",
    "with",
    "you",
    "your",
}

TOKEN_SYNONYMS = {
    "boss": "employer",
    "company": "employer",
    "clinic": "care",
    "confidential": "private",
    "data": "answers",
    "doctor": "care",
    "food": "food",
    "groceries": "food",
    "healthcare": "care",
    "home": "housing",
    "house": "housing",
    "information": "answers",
    "internet": "connection",
    "job": "employer",
    "physician": "care",
    "private": "private",
    "ride": "transportation",
    "transport": "transportation",
}


@lru_cache(maxsize=1)
def load_faq_entries() -> tuple[dict[str, Any], ...]:
    """Load supervisor-reviewed FAQ rows that are allowed in the chatbot."""
    with FAQ_DATA_PATH.open(encoding="utf-8") as faq_file:
        return tuple(json.load(faq_file))


def find_faq_answer(query: str, min_score: float = MIN_MATCH_SCORE) -> tuple[str, dict[str, Any] | None]:
    """Return the best approved FAQ answer, or the fixed fallback answer."""
    best_entry = None
    best_score = 0.0

    for entry in load_faq_entries():
        score = max(_score_phrase(query, phrase) for phrase in _entry_phrases(entry))
        if score > best_score:
            best_entry = entry
            best_score = score

    if best_entry is None or best_score < min_score:
        return UNKNOWN_ANSWER, None
    return str(best_entry["answer"]), best_entry


def render_faq_chatbot() -> None:
    """Render a fixed bottom-right chatbot using the local FAQ library."""
    payload = [
        {
            "id": entry["id"],
            "category": entry["category"],
            "question": entry["question"],
            "alternate_questions": entry.get("alternate_questions", []),
            "answer": entry["answer"],
            "search_terms": list(_entry_phrases(entry)),
        }
        for entry in load_faq_entries()
    ]
    html = _chatbot_html(payload)
    components.html(html, height=0, scrolling=False)


def _entry_phrases(entry: dict[str, Any]) -> tuple[str, ...]:
    phrases = [str(entry.get("question", ""))]
    phrases.extend(str(item) for item in entry.get("alternate_questions", []))
    return tuple(phrase for phrase in phrases if phrase.strip())


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _tokens(text: str) -> set[str]:
    tokens = set()
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        if len(token) <= 1 or token in STOPWORDS:
            continue
        tokens.add(TOKEN_SYNONYMS.get(token, token))
    return tokens


def _score_phrase(query: str, phrase: str) -> float:
    query_norm = _normalize_text(query)
    phrase_norm = _normalize_text(phrase)
    if not query_norm or not phrase_norm:
        return 0.0

    if query_norm == phrase_norm:
        return 1.0
    if len(query_norm) >= 8 and query_norm in phrase_norm:
        return 0.9
    if len(phrase_norm) >= 8 and phrase_norm in query_norm:
        return 0.9

    query_tokens = _tokens(query_norm)
    phrase_tokens = _tokens(phrase_norm)
    if not query_tokens or not phrase_tokens:
        return difflib.SequenceMatcher(None, query_norm, phrase_norm).ratio()

    shared = query_tokens & phrase_tokens
    query_coverage = len(shared) / len(query_tokens)
    phrase_coverage = len(shared) / len(phrase_tokens)
    jaccard = len(shared) / len(query_tokens | phrase_tokens)
    token_score = (query_coverage * 0.65) + (phrase_coverage * 0.25) + (jaccard * 0.10)
    sequence_score = difflib.SequenceMatcher(None, query_norm, phrase_norm).ratio()
    if len(shared) < 2 and token_score < MIN_MATCH_SCORE:
        sequence_score = min(sequence_score, token_score)
    return max(token_score, sequence_score)


def _chatbot_html(payload: list[dict[str, Any]]) -> str:
    html = r"""
<script>
(function () {
  const FAQ_ENTRIES = __FAQ_ENTRIES__;
  const UNKNOWN_ANSWER = __UNKNOWN_ANSWER__;
  const MIN_MATCH_SCORE = __MIN_MATCH_SCORE__;
  const STOPWORDS = new Set(__STOPWORDS__);
  const TOKEN_SYNONYMS = __TOKEN_SYNONYMS__;
  const widgetId = "sdoh-faq-chatbot";
  const styleId = "sdoh-faq-chatbot-style";
  const doc = window.parent.document;

  const oldWidget = doc.getElementById(widgetId);
  if (oldWidget) oldWidget.remove();
  const oldStyle = doc.getElementById(styleId);
  if (oldStyle) oldStyle.remove();

  const style = doc.createElement("style");
  style.id = styleId;
  style.textContent = `
    #sdoh-faq-chatbot {
      position: fixed;
      right: 22px;
      bottom: 62px;
      z-index: 2147483000;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #172033;
    }
    #sdoh-faq-chatbot * { box-sizing: border-box; }
    .sdoh-chat-toggle {
      border: 1px solid #0f766e;
      border-radius: 999px;
      background: #0f766e;
      color: #fff;
      box-shadow: 0 12px 30px rgba(15, 118, 110, 0.28);
      cursor: pointer;
      font-size: 14px;
      font-weight: 700;
      min-height: 44px;
      padding: 0 18px;
    }
    .sdoh-chat-panel {
      display: none;
      width: min(368px, calc(100vw - 32px));
      max-height: min(540px, calc(100vh - 48px));
      overflow: hidden;
      border: 1px solid #d8e0e7;
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 18px 52px rgba(17, 24, 39, 0.24);
    }
    #sdoh-faq-chatbot.is-open .sdoh-chat-panel {
      display: flex;
      flex-direction: column;
    }
    #sdoh-faq-chatbot.is-open .sdoh-chat-toggle { display: none; }
    .sdoh-chat-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid #e5ebf1;
      padding: 12px 14px;
      background: #f8fafc;
      font-size: 14px;
    }
    .sdoh-chat-close {
      width: 30px;
      height: 30px;
      border: 0;
      border-radius: 999px;
      background: transparent;
      color: #465366;
      cursor: pointer;
      font-size: 22px;
      line-height: 1;
    }
    .sdoh-chat-log {
      display: flex;
      flex: 1;
      flex-direction: column;
      gap: 8px;
      min-height: 180px;
      overflow-y: auto;
      padding: 14px;
      background: #fbfdff;
    }
    .sdoh-chat-message {
      max-width: 88%;
      border-radius: 8px;
      padding: 9px 11px;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.38;
      font-size: 14px;
    }
    .sdoh-chat-user {
      align-self: flex-end;
      background: #0f766e;
      color: #fff;
    }
    .sdoh-chat-bot {
      align-self: flex-start;
      border: 1px solid #e2e8f0;
      background: #fff;
      color: #172033;
    }
    .sdoh-chat-form {
      display: flex;
      gap: 8px;
      border-top: 1px solid #e5ebf1;
      padding: 10px;
      background: #fff;
    }
    .sdoh-chat-input {
      flex: 1;
      min-width: 0;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      color: #172033;
      font-size: 14px;
      outline: none;
      padding: 10px 11px;
    }
    .sdoh-chat-input:focus {
      border-color: #0f766e;
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
    }
    .sdoh-chat-submit {
      border: 1px solid #0f766e;
      border-radius: 8px;
      background: #0f766e;
      color: #fff;
      cursor: pointer;
      font-weight: 700;
      padding: 0 14px;
    }
    @media (max-width: 520px) {
      #sdoh-faq-chatbot {
        right: 16px;
        bottom: 56px;
      }
      .sdoh-chat-panel {
        width: calc(100vw - 32px);
      }
    }
  `;
  doc.head.appendChild(style);

  const root = doc.createElement("section");
  root.id = widgetId;
  root.innerHTML = `
    <button type="button" class="sdoh-chat-toggle" aria-expanded="false">Ask a question</button>
    <div class="sdoh-chat-panel" role="dialog" aria-label="SDoH help">
      <div class="sdoh-chat-header">
        <strong>SDoH Help</strong>
        <button type="button" class="sdoh-chat-close" aria-label="Close">&times;</button>
      </div>
      <div class="sdoh-chat-log" role="log" aria-live="polite"></div>
      <form class="sdoh-chat-form">
        <input class="sdoh-chat-input" type="text" autocomplete="off" aria-label="Question" placeholder="Type a question" />
        <button type="submit" class="sdoh-chat-submit">Ask</button>
      </form>
    </div>
  `;
  doc.body.appendChild(root);

  const toggle = root.querySelector(".sdoh-chat-toggle");
  const close = root.querySelector(".sdoh-chat-close");
  const form = root.querySelector(".sdoh-chat-form");
  const input = root.querySelector(".sdoh-chat-input");
  const log = root.querySelector(".sdoh-chat-log");

  function normalizeText(text) {
    return String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").replace(/\s+/g, " ").trim();
  }

  function tokens(text) {
    const out = new Set();
    for (const token of normalizeText(text).split(" ")) {
      if (!token || token.length <= 1 || STOPWORDS.has(token)) continue;
      out.add(TOKEN_SYNONYMS[token] || token);
    }
    return out;
  }

  function diceScore(a, b) {
    const left = normalizeText(a);
    const right = normalizeText(b);
    if (left.length < 2 || right.length < 2) return 0;
    const grams = (value) => {
      const result = new Map();
      for (let i = 0; i < value.length - 1; i += 1) {
        const gram = value.slice(i, i + 2);
        result.set(gram, (result.get(gram) || 0) + 1);
      }
      return result;
    };
    const leftGrams = grams(left);
    const rightGrams = grams(right);
    let overlap = 0;
    for (const [gram, count] of leftGrams.entries()) {
      overlap += Math.min(count, rightGrams.get(gram) || 0);
    }
    return (2 * overlap) / (Math.max(left.length - 1, 1) + Math.max(right.length - 1, 1));
  }

  function phraseScore(query, phrase) {
    const qNorm = normalizeText(query);
    const pNorm = normalizeText(phrase);
    if (!qNorm || !pNorm) return 0;
    if (qNorm === pNorm) return 1;
    if (qNorm.length >= 8 && pNorm.includes(qNorm)) return 0.9;
    if (pNorm.length >= 8 && qNorm.includes(pNorm)) return 0.9;

    const qTokens = tokens(qNorm);
    const pTokens = tokens(pNorm);
    if (!qTokens.size || !pTokens.size) return diceScore(qNorm, pNorm);

    const shared = [...qTokens].filter((token) => pTokens.has(token));
    const union = new Set([...qTokens, ...pTokens]);
    const queryCoverage = shared.length / qTokens.size;
    const phraseCoverage = shared.length / pTokens.size;
    const jaccard = shared.length / union.size;
    const tokenScore = (queryCoverage * 0.65) + (phraseCoverage * 0.25) + (jaccard * 0.10);
    let textScore = diceScore(qNorm, pNorm);
    if (shared.length < 2 && tokenScore < MIN_MATCH_SCORE) {
      textScore = Math.min(textScore, tokenScore);
    }
    return Math.max(tokenScore, textScore);
  }

  function bestAnswer(query) {
    let best = { score: 0, answer: UNKNOWN_ANSWER };
    for (const entry of FAQ_ENTRIES) {
      const phrases = entry.search_terms || [entry.question, ...(entry.alternate_questions || [])];
      const score = Math.max(...phrases.map((phrase) => phraseScore(query, phrase)));
      if (score > best.score) {
        best = { score, answer: entry.answer };
      }
    }
    return best.score >= MIN_MATCH_SCORE ? best.answer : UNKNOWN_ANSWER;
  }

  function addMessage(text, role) {
    const message = doc.createElement("div");
    message.className = `sdoh-chat-message sdoh-chat-${role}`;
    message.textContent = text;
    log.appendChild(message);
    log.scrollTop = log.scrollHeight;
  }

  toggle.addEventListener("click", () => {
    root.classList.add("is-open");
    toggle.setAttribute("aria-expanded", "true");
    setTimeout(() => input.focus(), 0);
  });
  close.addEventListener("click", () => {
    root.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
  });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question) return;
    addMessage(question, "user");
    addMessage(bestAnswer(question), "bot");
    input.value = "";
    input.focus();
  });
})();
</script>
"""
    return (
        html.replace("__FAQ_ENTRIES__", json.dumps(payload, ensure_ascii=False))
        .replace("__UNKNOWN_ANSWER__", json.dumps(UNKNOWN_ANSWER))
        .replace("__MIN_MATCH_SCORE__", json.dumps(MIN_MATCH_SCORE))
        .replace("__STOPWORDS__", json.dumps(sorted(STOPWORDS)))
        .replace("__TOKEN_SYNONYMS__", json.dumps(TOKEN_SYNONYMS, sort_keys=True))
    )
