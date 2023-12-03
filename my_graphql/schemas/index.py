type_defs = """
        type Query {
                extract_mission(mission_file_path: String!): mission_file_output!
        }

        type mission_file_output @key(fields: "mission_file_json") {
                mission_file_json: String!
                information: String!
        }
"""
