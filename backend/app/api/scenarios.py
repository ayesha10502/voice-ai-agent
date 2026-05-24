from fastapi import APIRouter, HTTPException
from app.schemas.call import ScenarioInfo
from app.core.scenarios import list_scenarios, get_scenario

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("", response_model=list[ScenarioInfo], summary="List all scenarios")
async def list_all_scenarios():
    """Return all available call scenarios."""
    return list_scenarios()


@router.get("/{scenario_id}", summary="Get scenario details")
async def get_scenario_detail(scenario_id: str):
    """Return full details for a single scenario."""
    scenario = get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return scenario
