import json
import aiohttp
import os, datetime, re


class Utils:
    @staticmethod
    async def open_file(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Error {response.status}: {response.reason}")
                return await response.json()  # Parse JSON and return the content

    @staticmethod
    def read_file(file_path):
        """
        Reads all content from the specified file and returns it.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            return "File not found."
        except Exception as e:
            return f"An error occurred: {e}"

    @staticmethod
    def save_file(file_name, content, folder_name="data", extension="json"):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{file_name}_{current_time}.{extension}"
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, "w") as file:
            file.write(content)

        return file_path

    @staticmethod
    def extract_blocks(text):
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

    @staticmethod
    def extract_messages(data):
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

    @staticmethod
    def generate_updated_messages(css, messages):
        updated_messages = []

        for message in messages:
            from_prefix = message[
                "from"
            ].lower()  # Lowercase for case-insensitive comparison
            to_prefix = message["to"].lower()

            from_matches = [
                css_item for css_item in css if css_item.lower().startswith(from_prefix)
            ]
            to_matches = [
                css_item for css_item in css if css_item.lower().startswith(to_prefix)
            ]

            for from_match in from_matches:
                for to_match in to_matches:
                    new_message = (
                        message.copy()
                    )  # Create a copy of the original message
                    new_message["from"] = from_match
                    new_message["to"] = to_match
                    updated_messages.append(new_message)

        return updated_messages

    @staticmethod
    def parse_text_to_json(text):
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

    @staticmethod
    def generate_mission(blocks):
        content_json = []
        for i, block in enumerate(blocks, 1):
            messages_from_events = Utils.extract_messages(
                Utils.parse_text_to_json(block)
            )
            # messages_based_on_prefix = Utils.generate_updated_messages(
            #     css_names, messages_from_events
            # )
            content_json.append(messages_from_events)
        return content_json

    # # Example usage
    # items = ["Satellite1", "Satellite2", "DCP1", "DCP2", "Antenna1"]
    # groups = get_groups(items)
    # combinations = generate_combinations(groups)
    # print(combinations)
