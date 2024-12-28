import os
import requests
import base64
import cv2

api_host = 'https://api.stability.ai'
api_key = os.environ.get("STABILITY_KEY")
# engine_id = 'stable-diffusion-xl-beta-v2-2-2'
engine_id = 'stable-diffusion-xl-1024-v1-0'
percent_transparent = 0.62


def getModelList():
    url = f"{api_host}/v1/engines/list"
    response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})

    if response.status_code == 200:
        payload = response.json()
        print(payload)


def make_semi_transparent_version_of_image(in_path, out_path):
    img = cv2.imread(in_path)
    # Add alpha layer with OpenCV
    bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    # Set alpha layer semi-transparent with Numpy indexing, B=0, G=1, R=2, A=3
    bgra[..., 3] = int(256 * percent_transparent)
    # Save result
    cv2.imwrite(out_path, bgra)


def generate_stable_diffusion_image(path, text, fake_gen=True):
    i_path = "/".join(path.split("/")[:-1])
    prefix = path.split("/")[-1]
    if any([i.startswith(prefix) for i in os.listdir(i_path)]):
        return
    if fake_gen or not text:
        # shutil.copyfile("place_holder.png", f"{path}_0.png")
        return
    prompt = 'A stylish illustration of ' + text + ", bright colors, whimsical, detailed"
    steps = 50
    url = f"{api_host}/v1/generation/{engine_id}/text-to-image"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # must be chosen from options here https://dreamstudio.com/api/
    height = 832
    width = 1216

    payload = {}
    payload['text_prompts'] = [{"text": f"{prompt}"}]
    payload['cfg_scale'] = 11 #scale from 7-13 how close image is to prompt
    payload['clip_guidance_preset'] = 'FAST_BLUE'
    payload['height'] = height
    payload['width'] = width
    payload['samples'] = 2
    payload['steps'] = steps

    response = requests.post(url, headers=headers, json=payload)

    # Processing the response
    if response.status_code == 200:
        data = response.json()
        for i, image in enumerate(data["artifacts"]):
            image_path = f"{path}_{i}.png"
            transparent_path = f"{path}_{i}_t.png"
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image["base64"]))
            make_semi_transparent_version_of_image(image_path, transparent_path)
