# NLP / Text Skill

## Repo patterns
- Libraries: NLTK, TextBlob, BeautifulSoup, gTTS, SpeechRecognition
- Existing work: sentiment analysis (`Article_Sentiment.py`, `article_sentiment.py`, `sentiment.py`), text-to-speech (`text_to_speech.py`), speech recognition (`SpeechRecognition.py`), web scraping (`scrape.py`, `news_article.py`)

## Text preprocessing sequence
1. Strip HTML tags (BeautifulSoup or regex)
2. Normalize whitespace
3. Lowercase (unless case carries signal)
4. Remove or handle special characters and URLs
5. Tokenize → apply task-specific processing (stopwords, stemming/lemmatization)

## Sentiment analysis
- Return polarity score (float) AND label (positive/negative/neutral) — not just the label
- For TextBlob: also return subjectivity score
- When comparing multiple articles: normalize scores to the same scale before comparing
- Flag when sentiment score is near neutral boundary (e.g. |polarity| < 0.1)

## Web scraping
- Check `robots.txt` before scraping a new domain
- Add rate limiting between requests (`time.sleep(1)` minimum)
- Handle HTTP errors explicitly — don't silently fail on 4xx/5xx
- Use `User-Agent` headers to identify the scraper

## Text-to-speech / speech recognition
- TTS: check output file path exists before writing; specify language code explicitly
- STR: log confidence score when available; handle `UnknownValueError` and `RequestError` separately
