# YouTube Video Transcriber, Comment Scraper, and Summarizer

This Streamlit application allows users to transcribe YouTube videos, extract comments, and generate summaries from a given video URL. It supports multiple languages for transcription and provides downloadable outputs in various formats.

## Features

- Transcribe YouTube videos in multiple languages
- Extract and display video comments
- Generate summaries and action plans from video transcripts
- Download transcripts, comments, and summaries in different formats (TXT, CSV, JSON)
- User-friendly interface built with Streamlit

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube-transcriber-comment-scraper.git
   cd youtube-transcriber-comment-scraper
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```
   Note: The `.env` file is included in `.gitignore` to prevent exposing your API key. Never commit this file to version control.

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Enter a YouTube video URL in the input field.

4. Select your preferred language for transcription.

5. Click the "Process Video" button to start transcribing, extracting comments, and generating a summary.

6. View the transcript, comments, and summary in the app interface.

7. Download the transcript, comments, and summary using the provided download buttons.

## Dependencies

- streamlit
- pandas
- youtube_transcript_api
- pytube
- youtube_comment_downloader
- python-dotenv
- groq

## How It Works

1. The app extracts the video ID from the provided YouTube URL.
2. It attempts to retrieve the transcript in the preferred language using the `youtube_transcript_api`.
3. If the preferred language is not available, it falls back to other available languages.
4. Comments are extracted using the `youtube_comment_downloader` library.
5. The transcript is sent to the Groq API to generate a summary and action plan.
6. The transcript, comments, and summary are displayed in the Streamlit interface and can be downloaded in various formats.

## Limitations

- The app relies on the availability of transcripts and comments on YouTube. Some videos may not have transcripts or may have disabled comments.
- The accuracy of transcripts, especially auto-generated ones, may vary.
- The quality of the summary depends on the Groq API and the content of the video.
- YouTube's terms of service and API usage policies apply.
- Groq API usage is subject to their terms and conditions.

## Security

- The Groq API key is stored in a `.env` file, which is not tracked by git. This prevents accidental exposure of your API key.
- Always keep your API keys secret and never share them publicly.
- If you suspect your API key has been compromised, regenerate it immediately through the Groq platform.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).