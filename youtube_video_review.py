# Description: Fetch and review YouTube video content using transcript + NLP

# pip install youtube-transcript-api
# pip install textblob
# pip install nltk

# Resources:
#   youtube-transcript-api: https://github.com/jdepoix/youtube-transcript-api
#   TextBlob: https://textblob.readthedocs.io/en/dev/

import re
import sys
import nltk
from textblob import TextBlob
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import YouTubeRequestFailed, NoTranscriptFound

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# YouTube video URL
url = 'https://youtu.be/9ToOfgZ4qqQ'

# Extract video ID from URL (supports youtu.be and youtube.com/watch?v= formats)
match = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', url)
video_id = match.group(1)
print(f'Video ID: {video_id}')

# Fetch the transcript (v1.x API requires instantiation)
try:
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
except (YouTubeRequestFailed, NoTranscriptFound) as e:
    print(f'\nCould not fetch transcript: {e}')
    print('Note: YouTube may block requests from cloud/server environments.')
    print('Run this script locally for full functionality.')
    sys.exit(1)

# Join all transcript segments into a single text block
text = ' '.join(entry.text for entry in transcript)

# Calculate basic statistics
word_count = len(text.split())
total_seconds = int(transcript[-1].start + transcript[-1].duration)
minutes, seconds = divmod(total_seconds, 60)

print(f'Transcript length: {word_count:,} words')
print(f'Video duration: {minutes}m {seconds}s')
print()

# Create a TextBlob object for NLP
blob = TextBlob(text)

# Extract key noun phrases (topics covered)
noun_phrases = list(set(blob.noun_phrases))[:10]
print('Key Topics:')
for phrase in noun_phrases:
    print(f'  - {phrase}')
print()

# Get sentiment of the full transcript
sentiment = blob.sentiment.polarity
if sentiment > 0.05:
    label = 'Positive'
elif sentiment < -0.05:
    label = 'Negative'
else:
    label = 'Neutral'

print(f'Sentiment: {sentiment:.2f} ({label})')
print()

# Print first 500 characters as a transcript preview
print('Transcript Preview:')
print(text[:500] + '...')
