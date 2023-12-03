from core import MissionExtractor
import os

BASE_URL = f"http://localhost:{os.getenv('PORT')}"


async def resolve_extract_mission(_, info, mission_file_path):
    mission_extractor = MissionExtractor()
    mission_extractor.extract_mission(mission_file_path)
    file_saved = mission_extractor.save_file()

    information = f"Mission file json saved in '{BASE_URL}/{file_saved}'"

    return {
        "mission_file_json": f"{BASE_URL}/{file_saved}",
        "information": f"{information}",
    }
