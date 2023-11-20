from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import httpx
 # Install using: pip install gensim

app = FastAPI()

youtube_api_key = "AIzaSyBf7Oy_B9JBS1r_wD0gzIRLsrjJ3yBDB0M"
youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos"
# Templates configuration
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/summarize")
async def summarize(request: Request, video_url: str = Form(...)):
    # video_info = fetch_video_title(video_url)
    video_info="Video_Title"
    # Extract transcript from video
    transcript = get_video_transcript(video_url)

    result = ''.join([i['text'] if isinstance(i, dict) and 'text' in i else str(i) for i in transcript])

    model_name = "sshleifer/distilbart-cnn-12-6"
    revision = "a4f8f3e"
    summarizer = pipeline("summarization", model=model_name, revision=revision)

    num_iters = int(len(result)/1000)
    summarized_text = []
    for i in range(0, num_iters + 1):
        start = 0   
        start = i * 1000
        end = (i + 1) * 1000
        out = summarizer(result[start:end],min_length=10,max_length=100)
        out = out[0]
        # out = out['[']
        # out = out[']']
        # out = out['"']
        out = out['summary_text']
        summarized_text.append(out)
    
    # Summarize using gensim
    #summary = summarize(transcript, ratio=0.2)
    return templates.TemplateResponse("index.html", {"request": request,"title": video_info,"summary": summarized_text})

# async def fetch_video_title(video_id: str):
#     params = {
#         "part": "snippet",
#         "id": video_id,
#         "key": youtube_api_key,
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.get(youtube_api_url, params=params)
#         data = response.json()

#         if "items" in data and data["items"]:
#             video_title = data["items"][0]["snippet"]["title"]
#             return {"video_title": video_title}
#         else:
#             return {"error": "Video not found"}

# @app.get("/get_video_title/{video_id}")
# async def get_video_title_endpoint(video_id: str):
#     return await fetch_video_title(video_id)

def get_video_transcript(video_url):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_url)
        text = ' '.join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return "Error fetching transcript"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
