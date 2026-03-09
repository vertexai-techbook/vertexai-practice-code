import pathlib
from typing import Optional
from typing import List
from google.adk.agents import Agent, LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
import io

# ToolContext를 사용하는 도구 함수
def save_location_info(tool_context: ToolContext, locations: List[str]) -> dict[str, str]:
    """사용자가 선택한 명소 목록을 세션 상태에 저장합니다.

    Args:
        tool_context (ToolContext): 현재 도구 실행 컨텍스트.
        locations (List[str]): 추가할 지역 목록.
    Returns:
        dict[str, str]: 성공 메시지.
    """

    # ToolContext를 통해 현재 세션 상태에 접근하여 읽기 및 쓰기 작업을 수행합니다    
    exist_locations = tool_context.state.get("user:locations", []) # user 스코프에 저장
    tool_context.state["user:locations"] = exist_locations + locations
    return {"status": "success", "message": "지역 정보가 성공적으로 저장되었습니다."}

def create_travel_plan_pdf(travel_plan: str, locations: List[str]) -> bytes:
    """여행 계획을 PDF로 생성합니다.
    
    Args:
        travel_plan (str): 여행 계획 텍스트
        locations (List[str]): 방문 장소 목록
        
    Returns:
        bytes: PDF 파일의 바이트 데이터
    """
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Windows 맑은고딕 폰트 등록
    pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
    
    # 여백 설정
    left_margin = 0.75 * inch
    right_margin = width - 0.75 * inch
    max_width = right_margin - left_margin
    
    # 제목
    pdf.setFont('Malgun', 24)
    pdf.drawString(left_margin, height - 1 * inch, "여행 계획")
    
    # 구분선
    pdf.setStrokeColorRGB(0.2, 0.5, 0.8)
    pdf.setLineWidth(2)
    pdf.line(left_margin, height - 1.3 * inch, right_margin, height - 1.3 * inch)
    
    # 방문 장소 (첫 번째 지역만)
    y_position = height - 2 * inch
    pdf.setFont('Malgun', 16)
    pdf.drawString(left_margin, y_position, "방문 장소:")
    
    y_position -= 0.3 * inch
    pdf.setFont('Malgun', 12)
    if locations:
        location_text = locations[0]  # 첫 번째 지역만
        pdf.drawString(left_margin + 0.2 * inch, y_position, location_text)
        y_position -= 0.3 * inch
    
    # 여행 일정
    y_position -= 0.3 * inch
    if y_position < 1 * inch:
        pdf.showPage()
        y_position = height - 1 * inch
    
    pdf.setFont('Malgun', 16)
    pdf.drawString(left_margin, y_position, "여행 일정:")
    
    y_position -= 0.3 * inch
    pdf.setFont('Malgun', 9)
    
    # 텍스트를 줄 단위로 처리하고 자동 줄바꿈
    for line in travel_plan.split('\n'):
        if not line.strip():
            y_position -= 0.15 * inch
            continue
            
        if y_position < 1 * inch:
            pdf.showPage()
            pdf.setFont('Malgun', 9)
            y_position = height - 1 * inch
        
        # 긴 줄은 자동 줄바꿈 (문자 단위)
        words = line.split(' ')
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            # 대략적인 길이 체크 (한글 1자 = 약 9pt, 영문 1자 = 약 5pt)
            estimated_width = len(test_line) * 7  # 평균값
            
            if estimated_width < max_width * 72 / inch:  # 포인트 단위 변환
                current_line = test_line
            else:
                if current_line:
                    pdf.drawString(left_margin + 0.2 * inch, y_position, current_line)
                    y_position -= 0.18 * inch
                    if y_position < 1 * inch:
                        pdf.showPage()
                        pdf.setFont('Malgun', 9)
                        y_position = height - 1 * inch
                current_line = word
        
        if current_line:
            pdf.drawString(left_margin + 0.2 * inch, y_position, current_line)
            y_position -= 0.18 * inch
    
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

# CallbackContext를 사용하는 콜백 함수
async def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """에이전트 실행 후 최종 응답과 상태를 PNG 이미지 아티팩트로 저장하는 콜백 함수."""

    # agent_name = callback_context.agent_name
    # invocation_id = callback_context.invocation_id
    # current_state_info = callback_context.state.to_dict()

    # 최종 응답 및 방문 장소 가져오기
    response_text = callback_context.state.get("final_agent_response", "최종 응답을 가져올 수 없습니다.")
    locations = callback_context.state.get("user:locations", [])
    
    # PDF 생성
    pdf_bytes = create_travel_plan_pdf(response_text, locations)
    
    # 로컬 파일로도 저장 (선택사항)
    output_dir = pathlib.Path("ADK_Artifacts")
    output_dir.mkdir(exist_ok=True)
    artifact_name = "travel_plan.pdf"
    file_path = output_dir / artifact_name
    
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)
    
    # types.Part로 변환하여 아티팩트로 저장
    pdf_artifact = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
    
    try:
        version = await callback_context.save_artifact(
            filename=artifact_name,
            artifact=pdf_artifact
        )
        print(f"여행 계획 PDF '{artifact_name}' (버전 {version})가 아티팩트로 저장되었습니다.")
        print(f"로컬 파일 경로: {file_path.absolute()}")
    except ValueError as e:
        print(f"아티팩트 저장 중 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    
    # 콜백은 원본 응답을 반환하거나 수정된 응답을 반환할 수 있습니다.
    return types.Content(
        parts=[types.Part(text=f"현재 에이전트와의 대화를 기반으로 여행 계획 PDF를 생성하고 '{artifact_name}' 파일로 저장했습니다.")],
        role="model"
    )

# LlmAgent 정의 (여행 플래너 에이전트)
root_agent = LlmAgent(
    name="travel_planner",
    model="gemini-3-flash-preview",
    description="사용자가 방문하고자 하는 장소에 대한 정보를 저장하고 여행 계획을 세웁니다.",
    instruction="""
    당신은 여행플래너 입니다.
    사용자가 방문하고 싶은 장소를 언급하면 'save_location_info' 도구를 사용하여 지역 정보를 저장하고 해당 지역의 랜드마크, 레스토랑, 명소를 찾아 여행 일정을 추천합니다.
    여행지 목록을 요청하면 현재 저장된 위치 목록을 확인하고 가볼 만한 주변 장소를 추가로 추천합니다.
    """,
    tools=[save_location_info], # ToolContext를 사용하는 도구 추가
    output_key="final_agent_response", # 에이전트의 최종 응답을 상태에 저장하도록 output_key 추가
    after_agent_callback=after_agent_callback # CallbackContext를 사용하는 콜백 추가
)