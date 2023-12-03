import re
import json
from core.utils import Utils


class MissionExtractor:
    def __init__(self):
        self.content_json = []

    def extract_blocks(self, text):
        blocks = []
        block_start = -1
        nested_level = 0
        last_end = 0  # Position of the last closing brace

        for i, char in enumerate(text):
            if char == "{":
                nested_level += 1
                if nested_level == 1:
                    # Start capturing from the last ending brace or the beginning of the text
                    block_start = last_end
            elif char == "}":
                nested_level -= 1
                if nested_level == 0:
                    blocks.append(text[block_start : i + 1].strip())
                    last_end = i + 1  # Update the position of the last closing brace

        return blocks

    def extract_messages(self, data):
        message_details = []

        def recurse_through_messages(event_data):
            if "messages" in event_data:
                for message in event_data["messages"]:
                    detail = {
                        "from": message.get("from"),
                        "message": message.get("message"),
                        "to": message.get("to"),
                    }
                    message_details.append(detail)

            if "implies" in event_data:
                recurse_through_messages(event_data["implies"])

        recurse_through_messages(data)
        return message_details

    def extract_mission(self, mission_file_path):
        content = Utils.read_file(mission_file_path)
        blocks = self.extract_blocks(content)
        self.generate_mission(blocks)

    def save_file(self, file_name="mission_file_json"):
        return Utils.save_file(file_name, json.dumps(self.content_json, indent=4))

    def parse_text_to_json(self, text):
        # Regular expressions to match key parts of the text
        action_regex = re.compile(r"(\w+\.\w+)\s*=\s*(\w+\.\w+)")
        condition_regex = re.compile(r"eventually before (\w+) time units")

        # Recursive function to parse nested conditions
        def parse_condition(text):
            if "implies" not in text:
                if condition_regex:
                    parts = text.split("{", 1)
                    condition_match = condition_regex.search(parts[0])
                    time_units = condition_match.group(1) if condition_match else None

                    actions = action_regex.findall(parts[0])
                    action_data = [
                        {
                            "from": a.split(".")[0],
                            "message": a.split(".")[1],
                            "to": b.split(".")[0],
                        }
                        for a, b in actions
                    ]
                    return {
                        "type": "eventually before",
                        "time_units": time_units,
                        "messages": action_data,
                    }
                return None

            parts = text.split("{", 1)
            condition_match = condition_regex.search(parts[0])
            time_units = condition_match.group(1) if condition_match else None

            actions = action_regex.findall(parts[0])
            action_data = [
                {
                    "from": a.split(".")[0],
                    "message": a.split(".")[1],
                    "to": b.split(".")[0],
                }
                for a, b in actions
            ]

            implies_data = parse_condition(parts[1])
            return {
                "type": "eventually before",
                "time_units": time_units,
                "messages": action_data,
                "implies": implies_data,
            }

        return parse_condition(text)

    def generate_mission(self, blocks):
        for i, block in enumerate(blocks, 1):
            messages_from_events = self.extract_messages(self.parse_text_to_json(block))
            self.content_json.append(messages_from_events)
