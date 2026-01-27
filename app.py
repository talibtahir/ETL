model_repo_id = "Freepik/F-Lite"
model_name = "F Lite" 

from dotenv import load_dotenv
import gradio as gr
import numpy as np
import random
import os
import logging
import google.generativeai as genai

import spaces
import torch
from f_lite import FLitePipeline

# Trick required because it is not a native diffusers model
from diffusers.pipelines.pipeline_loading_utils import LOADABLE_CLASSES, ALL_IMPORTABLE_CLASSES

from f_lite.pipeline import APGConfig
LOADABLE_CLASSES["f_lite"] = LOADABLE_CLASSES["f_lite.model"] = {"DiT": ["save_pretrained", "from_pretrained"]}
ALL_IMPORTABLE_CLASSES["DiT"] = ["save_pretrained", "from_pretrained"]

load_dotenv()

# Initialize Gemini API if API key is available
if os.getenv("GEMINI_API_KEY"):
    gemini_available = True
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
else:
    gemini_available = False
    logging.warning("GEMINI_API_KEY not found in environment variables. Prompt enrichment will not work.")

device = "cuda" if torch.cuda.is_available() else "cpu"

if torch.cuda.is_available():
    torch_dtype = torch.bfloat16
else:
    torch_dtype = torch.float32

pipe = FLitePipeline.from_pretrained(model_repo_id, torch_dtype=torch_dtype)
# pipe.enable_model_cpu_offload()  # For less memory consumption
pipe.to(device)
pipe.vae.enable_slicing()
pipe.vae.enable_tiling()

MAX_SEED = np.iinfo(np.int32).max
MAX_IMAGE_SIZE = 1600

# Predefined resolutions
RESOLUTIONS = {
  "horizontal": [
    {"width": 1344, "height": 896, "label": "1344×896"},
    {"width": 1152, "height": 768, "label": "1152×768"},
    {"width": 960, "height": 640, "label": "960×640"},
    {"width": 1600, "height": 896, "label": "1600×896"}
  ],
  "vertical": [
    {"width": 896, "height": 1344, "label": "896×1344"},
    {"width": 768, "height": 1152, "label": "768×1152"},
    {"width": 640, "height": 960, "label": "640×960"},
    {"width": 896, "height": 1600, "label": "896×1600"}
  ],
  "square": [
    {"width": 1216, "height": 1216, "label": "1216×1216"},
    {"width": 1024, "height": 1024, "label": "1024×1024"}
  ]
}

# Default resolution
DEFAULT_RESOLUTION = {"width": 1024, "height": 1024, "label": "1024×1024"}

# Create flattened options for the dropdown
resolution_options = []
for category, resolutions in RESOLUTIONS.items():
    resolution_options.append([f"{category.capitalize()}", None])  # Category header
    for res in resolutions:
        resolution_options.append([f"  {res['label']}", f"{category}:{res['width']}:{res['height']}"])

def enrich_prompt_with_gemini(prompt, max_tokens=1024):
    """
    Enrich a prompt using Google's Gemini API.
    
    Args:
        prompt: The original prompt to enrich
        max_tokens: Maximum number of tokens for the response
    
    Returns:
        tuple: (enriched_prompt, error_message)
    """
    try:
        if not os.getenv("GEMINI_API_KEY"):
            return None, "GEMINI_API_KEY not found in environment variables. Please add it to your .env file."
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        enrichment_prompt = f"""
        You are a prompt enhancer for image generation. 
        Take the following basic prompt and make it longer, very descriptive, and detailed. 
        Write the description in a paragraph, avoiding bullet points.
        
        Original prompt: {prompt}
        
        Enhanced prompt:
        """
        
        response = model.generate_content(enrichment_prompt, generation_config={
            "max_output_tokens": max_tokens,
            "temperature": 1,
        })
        
        enriched_prompt = response.text.strip()
        return enriched_prompt, None
        
    except Exception as e:
        error_message = f"Error enriching prompt: {str(e)}"
        logging.error(error_message)
        return None, error_message

# Function to update width and height based on selected resolution
def update_resolution(resolution_value):
    """Updates width and height based on selected resolution value"""
    if not resolution_value:
        return DEFAULT_RESOLUTION["width"], DEFAULT_RESOLUTION["height"]
    
    try:
        category, width, height = resolution_value.split(":")
        return int(width), int(height)
    except:
        return DEFAULT_RESOLUTION["width"], DEFAULT_RESOLUTION["height"]

@spaces.GPU(duration=120)
def infer(
    prompt,
    negative_prompt,
    seed,
    randomize_seed,
    width,
    height,
    guidance_scale,
    num_inference_steps,
    use_prompt_enrichment,
    enable_apg,
    progress=gr.Progress(track_tqdm=True),
):
    enriched_prompt_str = None
    error_message_str = None
    generation_prompt = prompt # Default to original prompt
    
    if use_prompt_enrichment and gemini_available:
        enriched_prompt_str, error_message_str = enrich_prompt_with_gemini(prompt)
        if enriched_prompt_str:
            generation_prompt = enriched_prompt_str # Use enriched prompt if successful
        # If enrichment fails, generation_prompt remains the original prompt

    if randomize_seed:
        seed = random.randint(0, MAX_SEED)

    generator = torch.Generator().manual_seed(seed)

    image = pipe(
        prompt=generation_prompt,
        negative_prompt=negative_prompt,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        width=width,
        height=height,
        generator=generator,
        apg_config=APGConfig(enabled=enable_apg)
    ).images[0]
    
    # Prepare Gradio updates for the enriched prompt display
    enriched_prompt_display_update = gr.update(visible=False)
    enriched_prompt_text_update = gr.update(value="")
    enrichment_error_update = gr.update(visible=False, value="")

    if enriched_prompt_str:
        enriched_prompt_display_update = gr.update(visible=True)
        enriched_prompt_text_update = gr.update(value=enriched_prompt_str)
    elif error_message_str:
        enriched_prompt_display_update = gr.update(visible=True)
        enrichment_error_update = gr.update(visible=True, value=error_message_str)

    return image, seed, enriched_prompt_display_update, enriched_prompt_text_update, enrichment_error_update

examples = [
    ["A photorealistic 3D render of a charming, mischievous young boy, approximately eight years old, possessing the endearingly unusual features of long, floppy donkey ears that droop playfully over his shoulders and a surprisingly small, pink pig nose that twitches slightly.  His eyes, a sparkling, intelligent hazel, are wide with a hint of playful mischief, framed by slightly unruly, sandy-brown hair that falls in tousled waves across his forehead.  He's dressed in a simple, slightly oversized, worn denim shirt and patched-up corduroy trousers, hinting at a life spent playing outdoors. The lighting is soft and natural, casting gentle shadows that highlight the texture of his skin – slightly freckled and sun-kissed, suggesting time spent in the sun.  His expression is one of curious anticipation, his lips slightly parted as if he's about to speak or perhaps is listening intently. The background is a subtly blurred pastoral scene, perhaps a sun-dappled meadow with wildflowers, enhancing the overall whimsical and slightly surreal nature of the character.  The overall style aims for a blend of realistic rendering with a touch of whimsical cartoonishness, capturing the unique juxtaposition of the boy's human features and his animalistic ears and nose.", None],
    ["Two white swans with long necks, gracefully swimming in a still body of water. The swans are positioned in a heart shape, with their necks intertwined, creating a romantic and elegant scene. The water is calm and reflective, reflecting the soft, golden light of the setting sun. The background is a blur of soft, golden hues, suggesting a peaceful and serene environment. The image is likely a photograph, captured with a shallow depth of field, which emphasizes the swans and creates a sense of intimacy. The soft lighting and the gentle curves of the swans create a sense of tranquility and beauty. The overall mood of the image is one of love, peace, and serenity.", None],
    ["""An awe-inspiring landscape of a pristine mountain lake nestled at the foot of a towering alpine range. The still water acts like a mirror, perfectly reflecting the snow-dusted peaks, scattered clouds, and lush forested slopes. The foreground includes rocky outcroppings and patches of wildflowers, adding texture and depth. The lighting is golden-hour soft, casting a warm glow across the scene and highlighting every ridge, tree, and ripple. The sky is vast and vibrant—either a sunrise palette of oranges and pinks, or a deep blue midday dome with wispy clouds. The composition radiates serenity, grandeur, and a connection to the sublime power of nature.""", None],
    ["A captivating photo, shot with a shallow depth of field, of a stunning blonde woman with cascading waves of platinum blonde hair that fall past her shoulders, catching the light. Her eyes, a striking shade of emerald green, are intensely focused on something just off-camera, creating a sense of intrigue.  Sunlight streams softly onto her face, highlighting the delicate curve of her cheekbones and the subtle freckles scattered across her nose. She's wearing a flowing, bohemian-style maxi dress, the fabric a deep sapphire blue that complements her hair and eyes beautifully. The dress is adorned with intricate embroidery along the neckline and sleeves, adding a touch of elegance.  The background is intentionally blurred, suggesting a sun-drenched garden setting with hints of vibrant flowers and lush greenery, drawing the viewer's eye to the woman's captivating features.  The overall mood is serene yet captivating, evoking a feeling of summer warmth and quiet contemplation.  The image should have a natural, slightly ethereal quality, with soft, diffused lighting that enhances her beauty without harsh shadows.", None],
]

css = """
#col-container {
    margin: 0 auto;
    max-width: 1024px;
}
.prompt-row > .gr-form {
    gap: 0.5rem !important; /* Reduce gap between checkbox and button */
    align-items: center; /* Align items vertically */
}
"""

with gr.Blocks(css=css, theme="ParityError/Interstellar") as demo:
    with gr.Column(elem_id="col-container"):
        gr.Markdown(f" # {model_name} Text-to-Image Demo")

        with gr.Row(elem_classes="prompt-row"):
            prompt = gr.Text(
                label="Prompt",
                show_label=False,
                max_lines=1,
                placeholder="Enter your prompt",
                container=False,
                scale=6 # Give prompt more space
            )
            
            use_prompt_enrichment = gr.Checkbox(
                label="Enrich", 
                value=True if gemini_available else False,
                visible=gemini_available, # Hide checkbox if Gemini not available
                scale=1, # Give checkbox some space
                min_width=100 # Ensure label isn't cut off
            )

            run_button = gr.Button("Run", scale=1, variant="primary", min_width=100)

        result = gr.Image(label="Result", show_label=False)
        
        # Enriched prompt display (outside Advanced Settings)
        enriched_prompt_display = gr.Accordion("Enriched Prompt", open=False, visible=False)
        with enriched_prompt_display:
            enriched_prompt_text = gr.Textbox(
                label="Enriched Prompt",
                interactive=False,
                lines=8
            )
            enrichment_error = gr.Textbox(
                label="Error",
                visible=False,
                interactive=False,
            )
        
        with gr.Accordion("Advanced Settings", open=False):
            negative_prompt = gr.Text(
                label="Negative prompt",
                max_lines=1,
                placeholder="Enter a negative prompt",
                visible=True,
            )
            
            with gr.Tabs() as resolution_tabs:
                with gr.TabItem("Preset Resolutions"):
                    resolution_dropdown = gr.Dropdown(
                        label="Resolution",
                        choices=resolution_options,
                        value="square:1024:1024",
                        type="value"
                    )
                
                with gr.TabItem("Custom Resolution"):
                    with gr.Row():
                        width = gr.Slider(
                            label="Width",
                            minimum=256,
                            maximum=MAX_IMAGE_SIZE,
                            step=32,
                            value=DEFAULT_RESOLUTION["width"],
                        )

                        height = gr.Slider(
                            label="Height",
                            minimum=256,
                            maximum=MAX_IMAGE_SIZE,
                            step=32,
                            value=DEFAULT_RESOLUTION["height"],
                        )

            seed = gr.Slider(
                label="Seed",
                minimum=0,
                maximum=MAX_SEED,
                step=1,
                value=42,
            )

            randomize_seed = gr.Checkbox(label="Randomize seed", value=False)

            with gr.Row():
                guidance_scale = gr.Slider(
                    label="Guidance scale",
                    minimum=0.0,
                    maximum=15.0,
                    step=0.1,
                    value=6,
                )
                enable_apg = gr.Checkbox(
                    label="Enable APG",
                    value=True,
                )

                num_inference_steps = gr.Slider(
                    label="Number of inference steps",
                    minimum=1,
                    maximum=50,
                    step=1,
                    value=30,
                )

        # Examples should explicitly target only the prompt input
        max_length = 180

        # Function to handle example clicks - sets prompt and disables enrichment
        def set_example_and_disable_enrichment(example, current_checkbox_value):
            # The current_checkbox_value is not used, but required by Gradio's input mapping
            return example, gr.update(value=False) # Explicitly disable enrichment

        gr.Examples(
            examples=examples,
            # Add use_prompt_enrichment to inputs
            inputs=[prompt, use_prompt_enrichment],
            outputs=[prompt, use_prompt_enrichment],
            fn=set_example_and_disable_enrichment, # Use the updated function
            # Need to adjust example_labels to access the prompt string within the sublist
            example_labels=[ex[0][:max_length] + "..." if len(ex[0]) > max_length else ex[0] for ex in examples]
        )
    
        # Add link to model card
        gr.Markdown(f"[{model_name} Model Card and Weights](https://huggingface.co/{model_repo_id})")

    # Update width and height when resolution dropdown changes
    resolution_dropdown.change(
        fn=update_resolution,
        inputs=resolution_dropdown,
        outputs=[width, height]
    )
    
    gr.on(
        triggers=[run_button.click, prompt.submit],
        fn=infer,
        inputs=[
            prompt,
            negative_prompt,
            seed,
            randomize_seed,
            width,
            height,
            guidance_scale,
            num_inference_steps,
            use_prompt_enrichment,
            enable_apg,
        ],
        outputs=[result, seed, enriched_prompt_display, enriched_prompt_text, enrichment_error],
    )
    

if __name__ == "__main__":
    demo.launch() # server_name="0.0.0.0", share=True)
