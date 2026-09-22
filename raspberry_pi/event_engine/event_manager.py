from pathlib import Path
import json
from datetime import datetime

PRIORITY_FILE = Path("../config/priorities.json")
OUTPUT_DIR = Path("../storage/events")

with open(PRIORITY_FILE, "r") as f:
    PRIORITY = json.load(f)

class EventManager:

    def __init__(self):
        self.counter = 1

    def create_event(self, hazard, confidence,
                     latitude=0, longitude=0, altitude=0):

        event_id = f"EVT_{self.counter:05d}"
        self.counter += 1

        folder = OUTPUT_DIR / event_id
        folder.mkdir(parents=True, exist_ok=True)

        metadata = {
            "event_id": event_id,
            "hazard": hazard,
            "confidence": round(confidence,3),
            "priority": PRIORITY[hazard],
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "timestamp": datetime.now().isoformat(),
            "image_path": str(folder / "frame.jpg")
        }

        with open(folder / "metadata.json","w") as f:
            json.dump(metadata,f,indent=4)

        return metadata


if __name__ == "__main__":

    manager = EventManager()

    event = manager.create_event(
        hazard="fire",
        confidence=0.92
    )

    print(json.dumps(event,indent=4))