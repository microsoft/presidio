from fastapi import APIRouter

from models import DecisionRequest, DecisionType

router = APIRouter(prefix="/api/decision", tags=["decision"])

# In-memory state
_decision_state: dict = {}


@router.post("")
async def save_decision(request: DecisionRequest):
    _decision_state.update(request.model_dump())

    if request.decision == DecisionType.approve:
        return {
            "status": "approved",
            "message": "Configuration approved! Ready for full dataset anonymization.",
            "artifacts": [
                "Approved Presidio Configuration",
                "Golden Dataset",
                "Evaluation Report",
                "Audit Trail",
            ],
        }

    return {
        "status": "iterating",
        "message": f"Iteration started with {len(request.selected_improvements)} improvements.",
        "improvements": request.selected_improvements,
        "next_step": "/sampling",
    }


@router.get("/improvements")
async def list_improvements():
    return [
        {
            "id": "threshold",
            "label": "Lower CREDIT_CARD confidence threshold to 0.60",
            "impact": "+12 detections",
        },
        {
            "id": "medical",
            "label": "Add MEDICAL_CONDITION custom recognizer",
            "impact": "+9 detections",
        },
        {
            "id": "ssn",
            "label": "Expand SSN pattern variations",
            "impact": "+8 detections",
        },
        {
            "id": "insurance",
            "label": "Add INSURANCE_POLICY recognizer",
            "impact": "+6 detections",
        },
    ]


@router.post("/save-artifacts")
async def save_artifacts():
    return {
        "status": "saved",
        "message": "Evaluation artifacts saved for audit and compliance.",
    }
