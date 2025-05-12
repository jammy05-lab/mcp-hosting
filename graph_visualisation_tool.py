# from openai import OpenAI
# from langchain.tools import tool
# import os
# from mcp.server.fastmcp import FastMCP
# from dotenv import load_dotenv
 
# load_dotenv()

# mcp = FastMCP("CSV-Visualiser-Server")

# client = OpenAI()

# # registering the tool with the setver
# @mcp.tool()
# def visualize_csv_with_gpt4o(csv_path: str) -> str:
#     """
#     Uploads a CSV file and uses GPT-4o to analyze it,
#     generate a matplotlib visualization, and return a
#     summary of the trends along with the saved image path.

#     Args:
#         csv_path (str): Path to the CSV file.

#     Returns:
#         str: A summary of the visualization and the path to the image file.
#     """

#     # --- Step 1: Upload the CSV file ---
#     file = client.files.create(
#         file=open(csv_path, "rb"),
#         purpose='assistants'
#     )

#     # --- Step 2: Create the Assistant ---
#     assistant = client.beta.assistants.create(
#         name="Data visualizer",
#         description=(
#             "You are great at creating beautiful data visualizations. "
#             "You analyze data present in .csv files, understand trends, "
#             "and come up with data visualizations relevant to those trends. "
#             "You also share a brief text summary of the trends observed."
#         ),
#         model="gpt-4o",
#         tools=[{"type": "code_interpreter"}],
#         tool_resources={
#             "code_interpreter": {
#                 "file_ids": [file.id]
#             }
#         }
#     )

#     # --- Step 3: Create a thread ---
#     thread = client.beta.threads.create()

#     # --- Step 4: Add a user message ---
#     client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role="user",
#         content=(
#             "Please analyze the uploaded CSV file and generate a clear matplotlib visualization "
#             "that highlights key trends or insights in the data. The visualisations can be in whatever "
#             "you deem is most appropriate to convey the essence of the information—be it line graphs, "
#             "bar charts, time series, or any other type of graph."
#         )
#     )

#     # --- Step 5: Run the Assistant on the Thread ---
#     run = client.beta.threads.runs.create_and_poll(
#         thread_id=thread.id,
#         assistant_id=assistant.id,
#         instructions="You are a tool for an agent. The agent will provide you with a csv; you will generate a visualization for the csv and return the image."
#     )

#     # --- Step 6: Extract output if successful ---
#     if run.status == "completed":
#         messages = client.beta.threads.messages.list(thread_id=thread.id)
#         latest_msg = messages.data[0]

#         text_output = ""
#         image_ids = []

#         os.makedirs("downloaded_images", exist_ok=True)

#         # --- Parse content blocks ---
#         for block in latest_msg.content:
#             if block.type == "text":
#                 text_output += block.text.value.strip()
#             elif block.type == "image_file":
#                 image_ids.append(block.image_file.file_id)

#         # --- Download image files ---
#         image_paths = []
#         for i, file_id in enumerate(image_ids):
#             image_data = client.files.content(file_id).content
#             filename = f"downloaded_images/image_{i+1}.png"
#             with open(filename, "wb") as f:
#                 f.write(image_data)
#             image_paths.append(filename)

#         # --- Return formatted result ---
#         return (
#             f"📊 Assistant Summary:\n{text_output}\n\n"
#             f"🖼️ Saved image(s): {', '.join(image_paths)}"
#         )

#     else:
#         return f"⚠️ Run did not complete successfully. Status: {run.status}"


# # Run the server with stdio transport
# if __name__ == "__main__":
#     mcp.run(transport="http")

import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain.tools import tool
from mcp.server.http import HTTPMCPServer

load_dotenv()

client = OpenAI()

# Initialize the HTTP MCP Server
mcp = HTTPMCPServer("CSV-Visualiser-Server")

@mcp.tool()
def visualize_csv_with_gpt4o(csv_path: str) -> str:
    """
    Uploads a CSV file and uses GPT-4o to analyze it,
    generate a matplotlib visualization, and return a
    summary of the trends along with the saved image path.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        str: A summary of the visualization and the path to the image file.
    """
    # --- Step 1: Upload the CSV file ---
    file = client.files.create(
        file=open(csv_path, "rb"),
        purpose='assistants'
    )

    # --- Step 2: Create the Assistant ---
    assistant = client.beta.assistants.create(
        name="Data visualizer",
        description=(
            "You are great at creating beautiful data visualizations. "
            "You analyze data present in .csv files, understand trends, "
            "and come up with data visualizations relevant to those trends. "
            "You also share a brief text summary of the trends observed."
        ),
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}],
        tool_resources={
            "code_interpreter": {
                "file_ids": [file.id]
            }
        }
    )

    # --- Step 3: Create a thread ---
    thread = client.beta.threads.create()

    # --- Step 4: Add a user message ---
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=(
            "Please analyze the uploaded CSV file and generate a clear matplotlib visualization "
            "that highlights key trends or insights in the data. The visualisations can be in whatever "
            "you deem is most appropriate to convey the essence of the information—be it line graphs, "
            "bar charts, time series, or any other type of graph."
        )
    )

    # --- Step 5: Run the Assistant on the Thread ---
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="You are a tool for an agent. The agent will provide you with a csv; you will generate a visualization for the csv and return the image."
    )

    # --- Step 6: Extract output if successful ---
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        latest_msg = messages.data[0]

        text_output = ""
        image_ids = []

        os.makedirs("downloaded_images", exist_ok=True)

        # --- Parse content blocks ---
        for block in latest_msg.content:
            if block.type == "text":
                text_output += block.text.value.strip()
            elif block.type == "image_file":
                image_ids.append(block.image_file.file_id)

        # --- Download image files ---
        image_paths = []
        for i, file_id in enumerate(image_ids):
            image_data = client.files.content(file_id).content
            filename = f"downloaded_images/image_{i+1}.png"
            with open(filename, "wb") as f:
                f.write(image_data)
            image_paths.append(filename)

        # --- Return formatted result ---
        return (
            f"📊 Assistant Summary:\n{text_output}\n\n"
            f"🖼️ Saved image(s): {', '.join(image_paths)}"
        )

    else:
        return f"⚠️ Run did not complete successfully. Status: {run.status}"

# Run the server
if __name__ == "__main__":
    mcp.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))  # critical for Render
    )

