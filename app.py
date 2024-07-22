import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
import json
import re
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize variables
client = None
GROQ_AVAILABLE = False

# Check if the API key is set
if not GROQ_API_KEY:
    raise ValueError("Groq API key not found. Please set it in the .env file.")
else:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        GROQ_AVAILABLE = True
    except ImportError:
        st.warning("The 'groq' package is not installed. Summarization feature will be disabled.")
    except Exception as e:
        st.error(f"An error occurred while initializing the Groq client: {str(e)}")

def get_video_id(url):
    video_id = None
    if 'youtube.com' in url:
        video_id = re.search(r'v=([^&]+)', url)
    elif 'youtu.be' in url:
        video_id = re.search(r'youtu.be/([^?]+)', url)
    
    if video_id:
        return video_id.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

def get_video_info(video_id):
    try:
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        return {
            'title': yt.title,
            'description': yt.description
        }
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def transcribe_video(video_id, preferred_language='id-ID'):
    try:
        # Get the list of available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Check if the preferred language is available
        if preferred_language in [t.language_code for t in transcript_list]:
            transcript = transcript_list.find_transcript([preferred_language])
        else:
            # If preferred language is not available, try to get Indonesian or any available transcript
            available_languages = [t.language_code for t in transcript_list]
            if 'id' in available_languages:
                transcript = transcript_list.find_transcript(['id'])
            else:
                transcript = transcript_list[0]
        
        # Fetch the transcript data
        transcript_data = transcript.fetch()
        
        # Join all the text entries to create a full transcript
        full_transcript = " ".join([entry['text'] for entry in transcript_data])
        
        return full_transcript, transcript.language_code
    
    except Exception as e:
        st.error(f"Error retrieving transcript: {str(e)}")
        available_languages = [t.language_code for t in YouTubeTranscriptApi.list_transcripts(video_id)]
        st.info(f"Available languages: {', '.join(available_languages)}")
        video_info = get_video_info(video_id)
        if video_info:
            return f"Title: {video_info['title']}\n\nDescription: {video_info['description']}", None
        return None, None

def extract_comments(video_id):
    try:
        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(f'https://www.youtube.com/watch?v={video_id}', sort_by=SORT_BY_RECENT)
        return list(comments)
    except Exception as e:
        st.error(f"Error extracting comments: {str(e)}")
        return None

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def summarize_transcript(transcript):
    if not GROQ_AVAILABLE:
        return "Summarization is not available because the Groq client could not be initialized."
    
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI assistant tasked with creating a summary and action plan from a YouTube video transcript. Your goal is to distill the key information from the transcript and provide actionable steps based on the content.\n\nHere is the transcript of the YouTube video:\n\n{transcript}\n\nPlease follow these steps to create a summary and action plan:\n\n1. Carefully read and analyze the entire transcript.\n\n2. Create a summary of the video content:\n   - Identify the main topic or theme of the video\n   - List the key points discussed in the video\n   - Highlight any important facts, statistics, or examples mentioned\n   - Note any significant conclusions or takeaways\n\n3. Develop an action plan based on the video content:\n   - Identify the main objective or goal presented in the video\n   - List 3-5 actionable steps that viewers can take to implement the ideas or advice given in the video\n   - For each step, provide a brief explanation of why it's important and how it relates to the video's content\n   - If applicable, suggest any resources or tools mentioned in the video that could help with implementing the action plan\n\n4. Present your summary and action plan in the following format:\n\n<summary>\n[Insert your summary here, using bullet points for key information]\n</summary>\n\n<action_plan>\nObjective: [State the main objective]\n\n1. [Action step 1]\n   - Explanation: [Brief explanation]\n\n2. [Action step 2]\n   - Explanation: [Brief explanation]\n\n3. [Action step 3]\n   - Explanation: [Brief explanation]\n\n[Add more steps if necessary]\n\nResources:\n- [List any relevant resources or tools mentioned in the video]\n</action_plan>\n\nEnsure that your summary is concise yet comprehensive, capturing the essence of the video content. The action plan should be practical and directly related to the video's main message or purpose. Use clear and straightforward language throughout your response."
                },
                {
                    "role": "assistant",
                    "content": ""
                }
            ],
            temperature=0.5,
            max_tokens=2030,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error summarizing transcript: {str(e)}")
        return None

st.title("YouTube Video Transcriber, Comment Scraper, and Summarizer")

url = st.text_input("Enter YouTube Video URL:")
preferred_language = st.selectbox("Preferred language", ['id-ID', 'en', 'ja', 'ko', 'zh-Hans'])  # Add more language codes as needed

if url:
    try:
        video_id = get_video_id(url)

        if st.button("Process Video"):
            st.subheader("Video Transcript or Info")
            transcript, actual_language = transcribe_video(video_id, preferred_language)
            if transcript:
                if actual_language:
                    st.info(f"Transcript language: {actual_language}")
                    if actual_language != preferred_language:
                        st.warning(f"Preferred language '{preferred_language}' was not available. Using '{actual_language}' instead.")
                st.text_area("Transcript:", transcript, height=300)
                
                # Save transcript to file
                with open("transcript.txt", "w", encoding="utf-8") as f:
                    f.write(transcript)
                st.download_button("Download Transcript", transcript, "transcript.txt")

                # Summarize transcript
                if GROQ_AVAILABLE:
                    st.subheader("Video Summary and Action Plan")
                    summary = summarize_transcript(transcript)
                    if summary:
                        st.markdown(summary)
                        st.download_button("Download Summary", summary, "summary.txt")
                    else:
                        st.warning("Unable to generate summary for this video.")
                else:
                    st.warning("Summarization feature is not available due to Groq client initialization issues.")

            else:
                st.warning("No transcript available for this video.")

            # Extract comments
            st.subheader("Video Comments")
            comments = extract_comments(video_id)
            if comments:
                # Convert comments to a more manageable format
                formatted_comments = []
                for comment in comments:
                    formatted_comments.append({
                        'username': comment.get('author', ''),
                        'content': comment.get('text', ''),
                        'likes': comment.get('votes', 0),
                        'published_at': format_timestamp(comment.get('time_parsed', 0))
                    })

                df = pd.DataFrame(formatted_comments)
                st.dataframe(df)

                # Save comments to CSV
                df.to_csv("comments.csv", index=False)
                st.download_button("Download Comments (CSV)", df.to_csv(index=False), "comments.csv")

                # Save comments to JSON
                with open("comments.json", "w", encoding="utf-8") as f:
                    json.dump(formatted_comments, f, ensure_ascii=False, indent=4)
                st.download_button("Download Comments (JSON)", json.dumps(formatted_comments, ensure_ascii=False, indent=4), "comments.json")

    except ValueError as ve:
        st.error(str(ve))
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.warning("Please enter a YouTube URL to proceed.")