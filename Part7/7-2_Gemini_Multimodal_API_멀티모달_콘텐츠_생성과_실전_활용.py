# == 1.1.1. 기본 이미지 생성 == #
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client(vertexai=True, project="vertexai-books", location="global")

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="현대적인 사무실에서 노트북으로 작업하는 개발자의 모습",
)

for part in response.parts:
    if part.inline_data is not None:
        image = part.as_image()
        image.save("developer_workspace.png")

# == 1.1.2. 이미지 편집 == #
# 원본 이미지 불러오기
original_image = Image.open("developer_workspace.png")

prompt = "이 사무실 사진에 큰 화분을 추가하고, 창문 밖으로 도시 야경이 보이도록 변경해줘"

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt, original_image],
)

for part in response.parts:
    if part.inline_data is not None:
        edited_image = part.as_image()
        edited_image.save("developer_workspace_edit.png")

# == 1.1.3. Multi-turn 대화를 통한 이미지 반복 수정 == #
message_1 = "식물이 가장 좋아하는 음식 레시피처럼 광합성을 설명하는 생동감 넘치는 인포그래픽을 제작하세요. 재료(햇빛, 물, 이산화탄소)와 완성된 요리(당분/에너지)를 보여주세요. 스타일은 4학년 학생에게 적합한 다채로운 어린이 요리책 한 페이지처럼 표현해야 합니다."

chat = client.chats.create(
    model="gemini-2.5-flash-image",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

response_1 = chat.send_message(message_1)

for part in response_1.parts:
    if part.text is not None:
        print(part.text)
    elif image:= part.as_image():
        image.save("photosynthesis_v1.png")

message_2 = "이 인포그래픽을 스페인어로 업데이트하세요. 이미지의 다른 요소는 변경하지 마세요."

response_2 = chat.send_message(message_2)

for part in response_2.parts:
    if part.text is not None:
        print(part.text)
    elif image:= part.as_image():
        image.save("photosynthesis_v2.png")

# == 1.1.4.1. 고해상도 및 비율 조정 == #
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="르네상스 시대 화풍으로 그린 나비의 해부학적 스케치",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="1:1",
            image_size="4K"
        ),
    )
)

for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("butterfly_sketch_4k.png")

# == 1.1.4.2. 레퍼런스 이미지 활용 == #
# 여러 사람의 사진을 레퍼런스로 제공
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "이 사람들이 함께 재미있는 표정으로 사무실 단체 사진을 찍고 있는 모습",
        Image.open('person1.jpg'),
        Image.open('person2.jpg'),
        Image.open('person3.jpg'),
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="5:4",
            image_size="2K"
        ),
    )
)

for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("team_photo.png")

# == 1.1.5. Google Search 도구와 연동 == #
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="서울의 앞으로 5일간 날씨 예보를 보기 좋은 인포그래픽으로 만들어줘. 각 날짜별로 적절한 옷차림도 추천해줘",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
        ),
        tools=[{"google_search": {}}]
    )
)

for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("seoul_weather_forecast.png")

# == 1.1.6.Google Image Search를 사용한 이미지 생성 == #
from google import genai
from google.genai import types

prompt = "루브르 박물관의 이미지를 분필 스케치 형태로 그려줘. 먼저 시각적 참고 자료를 검색한 후 제작해야 해."

client = genai.Client(vertexai=True, project="vertexai-books", location="global")

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        tools=[
            types.Tool(google_search=types.GoogleSearch(
                search_types=types.SearchTypes(
                    web_search=types.WebSearch(),
                    image_search=types.ImageSearch()
                )
            ))
        ]
    )
)

# 생성된 이미지 저장
for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("museum.png")

# 그라운딩 소스 표시
if response.candidates and response.candidates[0].grounding_metadata:
    metadata = response.candidates[0].grounding_metadata

    # 이미지 검색 쿼리
    if metadata.image_search_queries:
        print("## 이미지 검색 쿼리")
        for query in metadata.image_search_queries:
            print(f"  - {query}")

    # 참조 소스
    if metadata.grounding_chunks:
        print("\n## 참조 소스")
        for i, chunk in enumerate(metadata.grounding_chunks):
            if chunk.image:
                title = chunk.image.title.replace("<b>", "").replace("</b>", "")
                print(f"  [{i}] {title}")
                print(f"  - 소스 페이지: {chunk.image.source_uri}")
                print(f"  - 이미지 URL: {chunk.image.image_uri[:80]}...")

# == 1.2. Imagen - 전문 이미지 생성 모델 == #
response = client.models.generate_images(
    model='imagen-4.0-generate-001',
    prompt='카페 테라스에서 책을 읽고 있는 고양이',
    config=types.GenerateImagesConfig(
        number_of_images=4,  # 최대 4장까지 생성 가능
        aspect_ratio="1:1",  # "1:1", "3:4", "4:3", "9:16", "16:9"
        image_size="2K"      # "1K" 또는 "2K"
    )
)

for i, generated_image in enumerate(response.generated_images):
    generated_image.image.save(f"cat_reading_{i+1}.png")

# == 1.3.4. 네거티브 프롬프트 활용 == #
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="붉은 단풍잎 하나",
    config=types.GenerateContentConfig(
        negative_prompt="어수선한 배경, 여러 객체, 텍스트, 워터마크"
    )
)

# == 2.2. 텍스트에서 영상 생성하기 == #
import time

client = genai.Client(api_key="<API Key>")

# 영상 생성 작업 시작
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="숲 속 오솔길을 따라 걷는 사람의 시점에서 촬영한 영상. 나무 사이로 햇살이 비추고, 발걸음 소리와 새소리가 들린다.",
)

# 작업이 완료될 때까지 대기
while not operation.done:
    print("영상 생성 중...")
    time.sleep(10)  # 10초마다 상태 확인
    operation = client.operations.get(operation)

# 완성된 영상 다운로드
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("forest_walk.mp4")
print("영상이 forest_walk.mp4로 저장되었습니다.")

# == 2.3. 대화와 효과음이 포함된 영상 == #
prompt = """
암호가 새겨진 벽을 바라보는 두 사람의 클로즈업. 횃불이 깜빡인다.
남자가 속삭인다, "이게 바로 그거야. 비밀 코드가 맞아."
여자가 그를 바라보며 흥분된 목소리로 말한다, "뭘 찾았어?"
"""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
)

# 작업 완료 대기
while not operation.done:
    print("영상 생성 중...")
    time.sleep(10)
    operation = client.operations.get(operation)

# 영상 저장
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("dialogue_scene.mp4")

# == 2.4. 이미지에서 영상 생성하기 == #
prompt = "고양이가 느리게 움직이며 탁자 위에서 하품을 한다."

# 이미지 생성 작업 시작
image = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt,
    config={"response_modalities":['IMAGE']}
)

# 영상 생성 작업 시작
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    image=image.parts[0].as_image(),
)

# 작업이 완료될 때까지 대기
while not operation.done:
    print("영상 생성 중...")
    time.sleep(10)
    operation = client.operations.get(operation)

# 완성된 영상 다운로드
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3_with_image_input.mp4")
print("영상이 veo3_with_image_input.mp4로 저장되었습니다.")

# == 2.5. 시작과 끝 프레임 지정 (보간) == #
prompt_first = "안개 낀 숲속 달빛 아래 그네에 앉아있는 흰 머리의 유령 같은 여인"
prompt_last = "빈 그네만 흔들리고 있는 장면"

# Nano Banana로 첫 프레임 이미지 생성
first_frame_response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt_first,
    config={"response_modalities":['IMAGE']}
)

# Nano Banana로 마지막 프레임 이미지 생성
last_frame_response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt_last,
    config={"response_modalities":['IMAGE']}
)

# 두 프레임을 사용하여 보간 영상 생성
interpolation_prompt = """
영화 같은 으스스한 영상. 달빛이 비치는 안개 낀 숲속 공터에서 유령 같은
흰 머리의 여인이 로프 그네에 앉아 부드럽게 흔들리고 있다. 안개가 짙어지며
그녀가 천천히 희미해지다가 완전히 사라진다. 같은 장소에 빈 그네만 으스스한 고요 속에 흔들린다.
"""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=interpolation_prompt,
    image=first_frame_response.parts[0].as_image(),  # 첫 프레임
    config=types.GenerateVideosConfig(
        last_frame=last_frame_response.parts[0].as_image()  # 마지막 프레임
    ),
)

# 작업 완료 대기
while not operation.done:
    print("영상 생성 중...")
    time.sleep(10)
    operation = client.operations.get(operation)

# 영상 저장
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("ghost_disappearing.mp4")

# == 2.6. 레퍼런스 이미지로 일관성 유지하기 == #
# Nano Banana로 레퍼런스 이미지들 생성
dress_response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="레이어드된 핑크와 푸시아 색상의 플라밍고 깃털 드레스",
    config={"response_modalities":['IMAGE']}
)

glasses_response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="핑크색 하트 모양 선글라스",
    config={"response_modalities":['IMAGE']}
)

woman_response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="따뜻한 갈색 눈을 가진 검은 머리의 아름다운 여성 초상화",
    config={"response_modalities":['IMAGE']}
)

# 레퍼런스 이미지 구성
dress_ref = types.VideoGenerationReferenceImage(
    image=dress_response.parts[0].as_image(),
    reference_type="asset"
)
glasses_ref = types.VideoGenerationReferenceImage(
    image=glasses_response.parts[0].as_image(),
    reference_type="asset"
)
woman_ref = types.VideoGenerationReferenceImage(
    image=woman_response.parts[0].as_image(),
    reference_type="asset"
)

# 레퍼런스 이미지를 사용하여 영상 생성
prompt = """
아름다운 흑발의 여성이 레이어드된 핑크 플라밍고 드레스와 하트 모양 선글라스를
착용하고 햇살 가득한 석호의 맑은 물속을 자신감 있게 걸어간다. 카메라가
천천히 뒤로 물러나며 드레스의 긴 트레인이 우아하게 물 위에 떠다니는 장면을
포착한다. 영화 같고 몽환적인 분위기.
"""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    config=types.GenerateVideosConfig(
        reference_images=[dress_ref, glasses_ref, woman_ref],
    ),
)

# 작업 완료 대기
while not operation.done:
    print("영상 생성 중...")
    time.sleep(10)
    operation = client.operations.get(operation)

# 영상 저장
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("fashion_scene.mp4")

# == 2.7. 영상 확장하기 == #
# 먼저 원본 영상 생성
original_prompt = "종이접기 나비가 날개를 펄럭이며 프렌치 도어 밖 정원으로 날아간다."

previous_operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=original_prompt,
)

# 원본 영상 생성 완료 대기
while not previous_operation.done:
    print("원본 영상 생성 중...")
    time.sleep(10)
    previous_operation = client.operations.get(previous_operation)

print("원본 영상 생성 완료!")

# 원본 영상 저장
original_video = previous_operation.response.generated_videos[0]
client.files.download(file=original_video.video)
original_video.video.save("butterfly_original.mp4")

# 생성된 영상을 확장
extension_prompt = "나비를 따라 정원 안으로 이동하며 나비가 주황색 종이 꽃 위에 앉는다. 하얀 강아지가 달려와 꽃을 부드럽게 친다."

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=previous_operation.response.generated_videos[0].video,  # 확장할 기존 영상
    prompt=extension_prompt,
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        resolution="720p"
    ),
)

# 확장 작업 완료 대기
while not operation.done:
    print("영상 확장 중...")
    time.sleep(10)
    operation = client.operations.get(operation)

# 확장된 영상 저장
extended_video = operation.response.generated_videos[0]
client.files.download(file=extended_video.video)
extended_video.video.save("butterfly_extended.mp4")
print("확장된 영상 생성 완료!")

# == 3.1. 단일 화자 음성 생성 == #
import wave

# WAV 파일로 저장하는 헬퍼 함수
def save_wave_file(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents="명랑한 목소리로 '좋은 하루 되세요!'라고 말해줘.",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name='Kore',  # 30가지 목소리 중 선택
                )
            )
        ),
    )
)

# 음성 데이터 추출 및 저장
audio_data = response.candidates[0].content.parts[0].inline_data.data
save_wave_file('greeting.wav', audio_data)

# == 3.2. 다중 화자 음성 생성 == #
client = genai.Client(api_key="<API Key>")

prompt = """다음 대화를 TTS로 변환해줘:
민수: 오늘 프로젝트 진행은 어때?
지영: 생각보다 순조로워. 내일까지는 완성할 수 있을 것 같아."""

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker='민수',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name='Kore',
                            )
                        )
                    ),
                    types.SpeakerVoiceConfig(
                        speaker='지영',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name='Puck',
                            )
                        )
                    ),
                ]
            )
        )
    )
)

# 음성 데이터 추출 및 저장
audio_data = response.candidates[0].content.parts[0].inline_data.data
save_wave_file('conversation.wav', audio_data)

# == 3.4. Gemini로 스크립트 생성 후 TTS 변환 == #
client = genai.Client(api_key="<API Key>")

# 1단계: Gemini로 팟캐스트 스크립트 생성
script_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""
    흥분한 파충류 학자들의 팟캐스트에서 발췌한 것처럼 읽히는 약 100단어 분량의
    짧은 대본을 생성해줘. 진행자 이름은 Dr. 안야와 리암이야.
    """
)

transcript = script_response.text

# 2단계: 생성된 스크립트를 TTS로 변환
tts_response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=transcript,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker='Dr. 안야',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name='Kore',
                            )
                        )
                    ),
                    types.SpeakerVoiceConfig(
                        speaker='리암',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name='Puck',
                            )
                        )
                    ),
                ]
            )
        )
    )
)

# 음성 저장
audio_data = tts_response.candidates[0].content.parts[0].inline_data.data
save_wave_file('podcast_clip.wav', audio_data)