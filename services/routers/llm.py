from fastapi import APIRouter, HTTPException
from models.schemas import CodeExplainRequest, AIResponse
from core.llm_provider import llm_provider

router = APIRouter(prefix="/api/v1/llm", tags=["LLM Services"])

@router.post("/explain", response_model=AIResponse)
async def explain_code(payload: CodeExplainRequest):
    try:
        prompt = f"Please explain the following {payload.language} code in detail:\n\n```{payload.language}\n{payload.code}\n```"
        if payload.context:
            prompt += f"\nContext: {payload.context}"

        explanation = llm_provider.generate_response(
            prompt=prompt,
            system_instruction="You are a senior software developer specializing in code documentation and code review."
        )
        return AIResponse(success=True, data={"explanation": explanation})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
