# == 1.1. 이미지 분석 == #
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="vertexai-books", location="global")

# 로컬 이미지 파일 읽기
with open("apple.png", "rb") as f:
    image_bytes = f.read()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        "이 로고 이미지의 디자인 요소와 사용된 색상을 3줄 이내로 분석해주세요."
    ]
)

print(response.text)

# == 1.2. 여러 이미지 업로드 == #
# 첫 번째 이미지
with open("soccer1.jpg", "rb") as f:
    soccer1_bytes = f.read()

# 두번 째 이미지
with open("soccer2.jpg", "rb") as f:
    soccer2_bytes = f.read()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        "두 축구공의 상태가 어떻게 다른지 2줄 요약해주세요.",
        types.Part.from_bytes(data=soccer1_bytes, mime_type="image/jpeg"),
        types.Part.from_bytes(data=soccer2_bytes, mime_type="image/jpeg")
    ]
)

print(response.text)

# == 1.3. 객체 탐지 (Object Detection) == #
from PIL import Image
import json

prompt = "이미지에서 모든 사람을 탐지해주세요. box_2d는 [ymin, xmin, ymax, xmax] 형식으로 0-1000 사이로 정규화해주세요."

image = Image.open("event.jpg")

config = types.GenerateContentConfig(
    response_mime_type="application/json"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[image, prompt],
    config=config
)

# 좌표 변환
width, height = image.size
detections = json.loads(response.text)

for detection in detections:
    box = detection["box_2d"]
    abs_y1 = int(box[0] / 1000 * height)
    abs_x1 = int(box[1] / 1000 * width)
    abs_y2 = int(box[2] / 1000 * height)
    abs_x2 = int(box[3] / 1000 * width)
    print(f"{detection['label']}: ({abs_x1}, {abs_y1}) ~ ({abs_x2}, {abs_y2})")

# == 1.4. 세그멘테이션 (Segmentation) == #
prompt = """
이미지에서 모든 가구를 세그멘테이션 해주세요.
각 항목에 대해 2D 바운딩 박스("box_2d"), 세그멘테이션 마스크("mask"),
텍스트 라벨("label")을 포함한 JSON 형식으로 출력해주세요.
"""

image = Image.open("bedroom.jpg")

config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0)
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[prompt, image],
    config=config
)

print(response.text)

# == 2.1. 동영상 분석 == #
with open("tiny.mp4", "rb") as f:
    video_bytes = f.read()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"),
        "이 영상엔 뭐가 나오나요?"
    ]
)

print(response.text)

# == 2.2. YouTube URL 직접 전달 == #
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_uri(
            file_uri="https://www.youtube.com/watch?v=G2fqAlgmoPo&pp=ygUNR2VuZXJhdGl2ZSBBSQ%3D%3D",
            mime_type="video/mp4"
        ),
        "해당 강의에 대해서 강의록을 작성해주세요."
    ]
)

print(response.text)

# == 2.3. 동영상 클리핑 == #
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part(
            file_data=types.FileData(
                file_uri="https://www.youtube.com/watch?v=G2fqAlgmoPo&pp=ygUNR2VuZXJhdGl2ZSBBSQ%3D%3D",
                mime_type="video/mp4"
            ),
            video_metadata=types.VideoMetadata(
                start_offset="120s",  # 2분부터
                end_offset="300s"     # 5분까지
            )
        ),
        "이 구간에서 설명하는 내용을 4줄 요약해주세요."
    ]
)

print(response.text)

# == 2.4. 프레임 레이트 설정 == #
with open("golden_boots.mp4", "rb") as f:
    video_bytes = f.read()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part(
            inline_data=types.Blob(data=video_bytes, mime_type="video/mp4"),
            video_metadata=types.VideoMetadata(fps=5)  # 초당 5프레임
        ),
        "이 스포츠 경기에서 결정적인 순간들을 한글로 간략하게 분석해주세요."
    ]
)

print(response.text)

# == 3.1. 오디오 파일 업로드 및 분석 == #
with open("introduction.mp3", "rb") as f:
    audio_bytes = f.read()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        "이 음성 메모를 텍스트로 변환해주세요.",
        types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
    ]
)

print(response.text)

# == 3.2. 전사 및 화자 분리 == #
# 오디오 파일 업로드
with open("interview.mp3", "rb") as f:
    audio_bytes = f.read()

prompt = """
오디오 파일을 처리하여 상세한 전사본을 생성해주세요.

요구사항:
1. 화자를 구분해주세요 (예: 화자 1, 화자 2 또는 문맥상 이름).
2. 각 구간에 정확한 타임스탬프를 제공해주세요 (형식: MM:SS).
3. 해당 구간에서 화자의 주요 감정을 식별해주세요 (행복, 슬픔, 분노, 중립 중 하나).
"""

config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema={
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "오디오 내용의 간략한 요약"
            },
            "segments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "speaker": {"type": "string"},
                        "timestamp": {"type": "string"},
                        "content": {"type": "string"},
                        "emotion": {
                            "type": "string",
                            "enum": ["happy", "sad", "angry", "neutral"]
                        }
                    },
                    "required": ["speaker", "timestamp", "content", "emotion"]
                }
            }
        },
        "required": ["summary", "segments"]
    }
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        prompt,
        types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
    ],
    config=config
)

print(response.text)