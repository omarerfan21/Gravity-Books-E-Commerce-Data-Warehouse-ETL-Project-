import os
import json
import subprocess
from openai import OpenAI

client = OpenAI()

agent_state = {
    "messages": [
        {
            "role": "system",
            "content": """
You are a helpful coding assistant. Your goal is to help the user with programming tasks.
            
You have access to the following tools:
1. edit_file: Modify files by replacing text or create new files
2. run_command: Execute shell commands
3. list_directory: View the contents of directories
4. read_file_content: Read the content of files

For each user request:
1. Understand what the user is trying to accomplish
2. Break down complex tasks into smaller steps
3. Use your tools to gather information about the codebase when needed
4. Implement solutions by writing or modifying code
5. Explain your reasoning and approach

When modifying code, be careful to maintain the existing style and structure. Test your changes when possible.
If you're unsure about something, ask clarifying questions before proceeding.

You must run and test your changes before reporting success.
""".strip(),
        }
    ],
}


def edit_file(filename: str, find_str: str, replace_str: str) -> bool:
    
    if not os.path.exists(filename) and find_str == "":
        with open(filename, "w") as f:
            f.write(replace_str)
        return True

    
    try:
        with open(filename, "r") as f:
            content = f.read()

        
        if find_str in content:
            new_content = content.replace(find_str, replace_str)

            
            with open(filename, "w") as f:
                f.write(new_content)
            return True
    except FileNotFoundError:
        print(f"File {filename} not found and find_str is not empty.")

    return False


def run_command(command, working_dir) -> tuple[str, int]:
    try:
       
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=working_dir,
        )

       
        output, _ = process.communicate()
        error_code = process.returncode

        if len(output) > 2000:
            output = output[:1000] + "\n\n[...content clipped...]\n\n" + output[-1000:]

        return output, error_code
    except Exception as e:
        return str(e), 1


def list_directory(path: str) -> str:
    try:
        items = os.listdir(path)
        if not items:
            return f"Directory '{path}' is empty."

        result = f"Contents of directory '{path}':\n"
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                item_type = "Directory"
            else:
                item_type = "File"
            result += f"- {item} ({item_type})\n"

        return result.strip()

    except FileNotFoundError:
        return f"Error: Directory '{path}' not found."
    except PermissionError:
        return f"Error: Permission denied to access '{path}'."
    except Exception as e:
        return f"Error listing directory '{path}': {str(e)}"


def read_file_content(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        if len(content) > 2000:
            first_part = content[:1000]
            last_part = content[-1000:]
            content = (
                first_part
                + "\n\n[...content clipped...]\n\n"
                + last_part
            )

        return content

    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except PermissionError:
        return f"Error: Permission denied to access '{path}'."
    except UnicodeDecodeError:
        return f"Error: Cannot decode file '{path}' (probably not a text file)."
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Apply a diff to a file by replacing occurrences of find_str with replace_str.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to modify",
                    },
                    "find_str": {
                        "type": "string",
                        "description": "The string to find in the file",
                    },
                    "replace_str": {
                        "type": "string",
                        "description": "The string to replace with",
                    },
                },
                "required": ["filename", "find_str", "replace_str"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command and return its output and error code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run in the shell",
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "The working directory to run the command in",
                    },
                },
                "required": ["command", "working_dir"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List the contents of a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the directory to list. Defaults to the current directory.",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_content",
            "description": "Read and return the content of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to read. Defaults to the current directory.",
                    },
                },
                "required": ["path"],
            },
        },
    },
]



def is_goal_achieved(state) -> bool:
    if len(state["messages"]) <= 2:
        return False

    last_message = state["messages"][-1]

    return (
        "role" in last_message
        and last_message["role"] == "assistant"
        and "tool_calls" not in last_message
    )
    def ask_user_approval(message: str) -> bool:
        user_approval = input(f"{message} (y/n): ")
    return user_approval.lower() == "y"


def loop(user_input: str):
    agent_state["messages"].append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    while not is_goal_achieved(agent_state) and len(agent_state["messages"]) < 100:
        print(f"[Thinking... step {len(agent_state['messages']) - 1}]")
        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=agent_state["messages"],
            tools=tools,
        )

        agent_state["messages"].append(completion.choices[0].message.model_dump())

        if completion.choices[0].message.tool_calls:
            for tool_call in completion.choices[0].message.tool_calls:
                arguments = json.loads(tool_call.function.arguments)

                if tool_call.function.name == "edit_file":
                    print(f"""Editing file: {arguments["filename"]}""")
                    if arguments["find_str"] != "":
                        print(f"""Content to find\n```\n{arguments["find_str"]}\n```""")
                    if arguments["replace_str"] != "":
                        print(
                            f"""Content to replace with\n```\n{arguments["replace_str"]}\n```"""
                        )
                    if not ask_user_approval("Do you want to edit this file?"):
                        print("File edit cancelled by user.")
                        result = ("File edit cancelled by user.", 0)
                        continue
                    result = edit_file(**arguments)
                    print(result)

                elif tool_call.function.name == "run_command":
                    print(f"""Executing command: {arguments["command"]}""")
                  
                    if not ask_user_approval("Do you want to execute this command?"):
                        print("Command execution cancelled by user.")
                        result = ("Command execution cancelled by user.", 0)
                        continue
                    result = run_command(**arguments)
                    print(result[0])

                elif tool_call.function.name == "list_directory":
                    print(f"""Listing directory: {arguments["path"]}""")
                    result = list_directory(**arguments)
                    print(result)

                elif tool_call.function.name == "read_file_content":
                    print(f"""Reading file: {arguments["path"]}""")
                    result = read_file_content(**arguments)
                    print(result)

                agent_state["messages"].append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    }
                )
                print()


if __name__ == "__main__":
    user_input = input("How can I help you?\n")
    loop(user_input)
    import json
from typing import Dict, Any

def search_flights(params: Dict[str, Any]) -> str:
    origin = params.get("origin", "CAI")
    destination = params.get("destination", "CDG")
    departure_date = params.get("departure_date", "2026-04-10")
    adults = params.get("adults", 1)
    return json.dumps({
        "status": "success",
        "flights": [
            {
                "id": "off1",
                "price": "€ 324",
                "airline": "EGYPTAIR / Air France",
                "depart": f"{departure_date} 08:15 CAI → 11:50 CDG",
                "duration": "4h 35m direct"
            },
            {
                "id": "off2",
                "price": "€ 289",
                "airline": "Aegean + Wizz",
                "depart": f"{departure_date} 04:40 CAI → 14:20 CDG (1 stop)",
                "duration": "9h 40m"
            }
        ]
    }, indent=2)

def confirm_price_and_book(flight_id: str, passenger_info: Dict) -> str:
    return json.dumps({
        "status": "booked",
        "booking_reference": "XYZ789",
        "flight_id": flight_id,
        "total_price": "€ 324",
        "passengers": passenger_info,
        "message": "Booking confirmed (demo mode)"
    })

def ask_user_approval(message: str) -> bool:
    user_input = input(f"{message} (y/n): ").strip().lower()
    return user_input == "y"

agent_state: Dict[str, Any] = {
    "messages": [],
    "collected_info": {
        "origin": None,
        "destination": None,
        "departure_date": None,
        "return_date": None,
        "adults": 1,
        "children": 0,
        "cabin": "ECONOMY",
        "preferred_airline": None,
        "max_price": None,
    },
    "last_search_result": None,
    "selected_flight_id": None,
}

def is_goal_achieved(state: Dict) -> bool:
    return bool(state.get("booking_reference"))

def loop(user_input: str):
    agent_state["messages"].append({"role": "user", "content": user_input})

    while not is_goal_achieved(agent_state) and len(agent_state["messages"]) < 80:
        print(f"\n[Step {len(agent_state['messages']) - 1}]")

        last_user_msg = agent_state["messages"][-1]["content"].lower()

        tool_call = None
        tool_args = {}

        if any(w in last_user_msg for w in ["search", "find", "show flights", "cheap", "from", "to"]):
            tool_call = "search_flights"
            if "from" in last_user_msg and "to" in last_user_msg:
                parts = last_user_msg.split()
                try:
                    from_idx = parts.index("from") + 1
                    to_idx = parts.index("to") + 1
                    agent_state["collected_info"]["origin"] = parts[from_idx].upper()
                    agent_state["collected_info"]["destination"] = parts[to_idx].upper()
                except:
                    pass

            tool_args = {
                "origin": agent_state["collected_info"]["origin"] or "CAI",
                "destination": agent_state["collected_info"]["destination"] or input("→ Destination airport code? "),
                "departure_date": agent_state["collected_info"]["departure_date"] or input("→ Departure date (YYYY-MM-DD)? "),
                "adults": agent_state["collected_info"]["adults"],
            }

        elif any(w in last_user_msg for w in ["book", "reserve", "purchase", "confirm", "pay"]):
            if not agent_state.get("last_search_result"):
                print("→ No search results yet. Please search first.")
                continue

            if not agent_state.get("selected_flight_id"):
                print(agent_state["last_search_result"])
                fid = input("→ Enter flight ID to book (e.g. off1): ").strip()
                agent_state["selected_flight_id"] = fid

            tool_call = "book_flight"
            tool_args = {
                "flight_id": agent_state["selected_flight_id"],
                "passenger_info": {
                    "name": input("→ Passenger full name: "),
                    "email": input("→ Email: "),
 "passport": input("→ Passport number (demo): ")
                }
            }

        elif "clear" in last_user_msg or "reset" in last_user_msg:
            agent_state["collected_info"] = {k: None for k in agent_state["collected_info"]}
            agent_state["last_search_result"] = None
            agent_state["selected_flight_id"] = None
            print("→ Conversation reset.")
            continue

        else:
            print("→ I can help you search or book flights.")
            print("   Try: 'find flights from CAI to DXB'  or  'book the cheapest one'")
            new_input = input("→ Your request: ")
            agent_state["messages"].append({"role": "user", "content": new_input})
            continue

        if tool_call == "search_flights":
            print(f"→ Searching flights: {tool_args}")
            if not ask_user_approval("Proceed with flight search?"):
                print("→ Search cancelled.")
                continue

            result_str = search_flights(tool_args)
            agent_state["last_search_result"] = result_str
            print("\nSearch result:\n" + result_str)

            msg = {"role": "tool", "content": result_str}
            agent_state["messages"].append(msg)

        elif tool_call == "book_flight":
            print(f"→ Booking flight {tool_args['flight_id']}")
            if not ask_user_approval("CONFIRM BOOKING (this is a real action in production!)"):
                print("→ Booking cancelled.")
                continue

            result_str = confirm_price_and_book(**tool_args)
            print("\nBooking result:\n" + result_str)

            try:
                data = json.loads(result_str)
                agent_state["booking_reference"] = data.get("booking_reference")
            except:
                pass

            msg = {"role": "tool", "content": result_str}
            agent_state["messages"].append(msg)

        print("-" * 60)

    if is_goal_achieved(agent_state):
        print("\n" + "="*60)
        print("       🎉  Flight booked successfully!")
        print("       Booking reference →", agent_state.get("booking_reference"))
        print("="*60 + "\n")

if __name__ == "__main__":
    user_input = input("\nHow can I help you today?\n> ").strip()
    loop(user_input)