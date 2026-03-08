import logging
import os
from typing import Dict, List, Any
from google.adk.agents import LlmAgent

def get_purchase_history(customer_id: str) -> Dict[str, Any]:
    """
    고객의 구매 내역을 조회합니다. 주문 상태(배송 완료, 배송 중 등)를 포함합니다.

    Args:
        customer_id: 고객 ID입니다.

    Returns:
        과거 주문 내역과 현재 상태가 포함된 딕셔너리를 반환합니다.
    """
    return MOCK_DATA.get(customer_id, {"orders": [], "message": "해당 고객의 구매 내역을 찾을 수 없습니다."})

def issue_refund(order_id: str, reason: str) -> Dict[str, Any]:
    """
    특정 주문에 대해 환불을 처리하고 상태를 업데이트합니다.

    Args:
        order_id: 주문 ID입니다.
        reason: 환불 사유입니다.

    Returns:
        환불 상태와 업데이트된 주문 정보를 포함한 딕셔너리를 반환합니다.
    """
    for customer_id, data in MOCK_DATA.items():
        for order in data["orders"]:
            if order["order_id"] == order_id:
                if order["status"] == "refunded":
                    return {
                        "status": "error",
                        "message": f"주문 {order_id}은(는) 이미 환불 처리되었습니다."
                    }
                order["status"] = "refunded"
                return {
                    "status": "success",
                    "order_id": order_id,
                    "new_status": "refunded",
                    "refund_amount": f"${order['total']} 전액 환불 완료",
                    "message": f"주문 {order_id}에 대한 환불이 다음 사유로 처리되었습니다: {reason}"
                }
   
    return {
        "status": "error",
        "message": f"주문 ID {order_id}를 찾을 수 없거나 환불 대상이 아닙니다."
    }

def lookup_product_info(product_name: str) -> Dict[str, Any]:
    """
    특정 제품에 대한 세부 정보를 조회합니다.

    Args:
        product_name: 조회할 제품의 이름입니다.

    Returns:
        제품 세부 정보가 포함된 딕셔너리를 반환합니다.
    """
    # Mock 데이터
    products = {
        "무선 헤드폰": {
            "price": 120.00,
            "in_stock": True,
            "description": "20시간 배터리 수명을 가진 노이즈 캔슬링 무선 헤드폰입니다."
        },
        "스마트 워치": {
            "price": 250.00,
            "in_stock": False,
            "description": "고급 피트니스 추적 및 알림 기능을 제공하는 스마트 워치입니다."
        },
        "usb-c 케이블": {
            "price": 15.00,
            "in_stock": True,
            "description": "1.8m 길이의 튼튼한 USB-C to USB-C 케이블입니다."
        }
    }

    if product_name in products:
        return products[product_name]
    else:
        return {"message": "제품을 찾을 수 없습니다."}

agent_instruction = """
당신은 유능하고 효율적인 소매 고객 서비스 담당자입니다.
당신의 목표는 고객의 구매 내역 조회, 환불 처리, 제품 문의를 돕는 것입니다.

INSTRUCTIONS:
1.  **고객 식별:** 고객이 구매 내역이나 주문 상태를 물어보면, 고객 ID를 제공하지 않았을 경우 먼저 물어보세요.
2.  **주문 상태 확인:** `get_purchase_history`를 사용하여 주문의 현재 상태(예: 주문됨, 배송됨, 배송 완료, 환불됨)를 확인하세요.
3.  **환불 처리:** 고객이 환불을 원할 경우, 주문 ID와 환불 사유를 물어보세요. `issue_refund` 도구를 사용하세요. 고객이 제품 파손을 언급하면 사유로 "damaged" 혹은 "파손"을 사용하세요.
4.  **제품 문의:** 제품에 대한 질문은 `lookup_product_info`를 사용하세요. 제품이 품절이면 고객에게 알려주세요.
5.  **정중하고 전문적인 태도:** 항상 친절한 어조를 사용하고 적절한 경우 이모티콘을 사용하세요.
6.  **해결 우선:** 사용 가능한 도구를 사용하여 고객의 문제를 신속하게 해결하려고 노력하세요.

TOOLS:
* `get_purchase_history`: 고객의 과거 주문과 현재 상태를 가져옵니다.
* `issue_refund`: 주문에 대한 환불을 처리하고 상태를 업데이트합니다.
* `lookup_product_info`: 제품에 대한 세부 정보를 가져옵니다.
"""

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="CustomerServiceAgent",
    instruction=agent_instruction,
    tools=[
        get_purchase_history,
        issue_refund,
        lookup_product_info,
    ],
)