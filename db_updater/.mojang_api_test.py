

# NOTE: Not used in the project yet.
# It has some bungs, mainly that some faces (debuggyo's)
# are still transparent for some reason.



import requests
from PIL import Image
from io import BytesIO
import os
import base64

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def fetch_skin_head_with_helmet(uuid, output_path="head_with_helmet.png"):
    # NOTE: Mojang API is rate limited to 600 requests per 10 minutes
    try:
        # Fetch player profile (the Mojang API buries the skin texture URL in the profile)
        profile_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        profile_response = requests.get(profile_url)
        profile_response.raise_for_status()
        profile_data = profile_response.json()
        
        # Texture URL is base64 encoded in the profile data
        properties = profile_data.get("properties", [])
        skin_data = next((prop for prop in properties if prop["name"] == "textures"), None)

        if not skin_data:
            raise ValueError("Skin texture data not found in Mojang player profile.")
        
        textures = base64.b64decode(skin_data["value"]).decode("utf-8")
        skin_url = eval(textures)["textures"]["SKIN"]["url"]
        
        skin_response = requests.get(skin_url)
        skin_response.raise_for_status()
        skin_image = Image.open(BytesIO(skin_response.content))
        
        head = skin_image.crop((8, 8, 16, 16))
        helmet = skin_image.crop((40, 8, 48, 16))
        

        # Combine the head and helmet layers
        combined = Image.new("RGBA", (8, 8))
        head = head.convert("RGBA")
        helmet = helmet.convert("RGBA")
        combined.paste(head, (0, 0))
        combined.paste(helmet, (0, 0), helmet)
        
        combined.save(output_path)
        print(f"Player head with helmet saved to {output_path}.")
    except Exception as e:
        print(f"Error occurred: {e}")

player_uuid = "62a76d79-c37c-4c0d-b121-5a463d19f9a3"
fetch_skin_head_with_helmet(player_uuid, output_path="player_head_with_helmet.png")
