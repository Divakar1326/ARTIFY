import streamlit as st
import requests
import io
from PIL import Image, ImageFilter, ImageEnhance
import warnings
import os
from pathlib import Path
from urllib.parse import quote
import base64
import toml

# Ignore all warnings
warnings.filterwarnings('ignore')

# --- Load configuration from .streamlit/config.toml ---
def load_config():
    """Load configuration from .streamlit/config.toml file."""
    config_path = ".streamlit/config.toml"
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return toml.load(f)
        else:
            st.warning("config.toml file not found in .streamlit folder!")
            return {}
    except Exception as e:
        st.error(f"Error loading config.toml: {e}")
        return {}

# Load configuration
config = load_config()

# --- Safe API token lookup ---
def _get_secret(key):
    v = os.getenv(key)
    if v:
        return v
    try:
        home_secrets = Path.home() / ".streamlit" / "secrets.toml"
        local_secrets = Path.cwd() / ".streamlit" / "secrets.toml"
        if home_secrets.exists() or local_secrets.exists():
            return st.secrets.get(key)
    except Exception:
        pass
    return ""

# Configure Streamlit page
st.set_page_config(
    page_title="ARTIFY",
    page_icon="🖌️",
    layout="wide"
)

def get_base64_image(image_path):
    """Convert local image to base64 string."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Could not load image: {e}")
        return ""

# Convert your PNG to base64
image_base64 = get_base64_image("images/a72e924659db437b843d2bfff1eceff3.png")

# Custom CSS for elegant design
st.markdown(f"""
    <style>
    /* Gradient top header */
    [data-testid="stHeader"] {{
        background: linear-gradient(90deg, #0ea5e9 0%, #8b5cf6 50%, #ec4899 100%) !important;
        height: 64px;
        color: #ffffff;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
        backdrop-filter: blur(8px);    
    }}

    /* Main app background with your PNG overlay */
    .stApp {{
        background: 
            url('data:image/png;base64,{image_base64}') center center no-repeat,
            linear-gradient(135deg, #8b5cf6 50%, #0ea5e9 100%);
        background-size: 35% auto, cover;
        background-attachment: fixed, fixed;
    }}
    .main {{ background: transparent; }}

    /* Push content down */
    .block-container {{
        background: transparent;
        padding-top: 6.5rem;
        padding-bottom: 8rem;
    }}

    /* Title and subtitle - FIXED SIZE */
    .title {{
        text-align: center;
        color: white;
        font-size: 84px;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: 0.5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.25);
        margin: 6px 0 10px 0;
    }}
    .subtitle {{
        text-align: center;
        color: rgba(255,255,255,0.95);
        font-size: 28px;
        font-weight: 400;
        margin-bottom: 38px;
    }}

    /* Section headers */
    .block-container h3 {{
        position: relative;
        padding-left: 14px;
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.35);
    }}
    .block-container h3::before {{
        content: "";
        position: absolute;
        left: 0; top: 0.35em;
        width: 6px; height: 1.1em;
        border-radius: 3px;
        background: linear-gradient(180deg, #60a5fa, #a78bfa, #f472b6);
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }}

    /* Text area styling - TRANSLUCENT WITH GRADIENT */
    .stTextArea textarea {{
        background: linear-gradient(135deg, rgba(248, 249, 250, 0.7) 0%, rgba(233, 236, 239, 0.8) 100%) !important;
        color: #000000 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.35) !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        backdrop-filter: blur(10px) !important;
    }}
    
    .stTextArea textarea::placeholder {{
        color: rgba(0,0,0,0.6) !important;
        font-style: italic !important;
    }}

    /* Fix text cursor visibility */
    .stTextArea textarea:focus {{
        border: 2px solid rgba(139, 92, 246, 0.8) !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
        caret-color: #000000 !important;
    }}

    .stTextArea label {{
        color: #ffffff !important;
        font-weight: 600 !important;
    }}

    /* === Select Box Styling with Gradient Display === */

    /* Main visible select box (the selected item area) */
    .stSelectbox [data-baseweb="select"] > div {{
        background: linear-gradient(135deg, #e6f0ff 0%, #d9e6ff 100%) !important;
        color: #000000 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }}

    /* Dropdown menu styling */
    .stSelectbox [data-baseweb="select"] {{
        background: linear-gradient(135deg, rgba(248, 249, 250, 0.95) 0%, rgba(233, 236, 239, 0.95) 100%) !important;
        border-radius: 10px !important;
    }}

    /* Hover effect */
    .stSelectbox [data-baseweb="select"] > div:hover {{
        background: linear-gradient(135deg, #dbe7ff 0%, #c6d9ff 100%) !important;
    }}
    
    /* Dropdown options styling */
    .stSelectbox [data-baseweb="popover"] {{
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-radius: 10px !important;
    }}

    .stTextArea .help, .stSelectbox .help {{
        color: rgba(255,255,255,0.8) !important;
    }}

    /* Main Generate button */
    .stButton > button {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #fff; border: none; border-radius: 25px;
        padding: 15px 50px; font-size: 18px; font-weight: 700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all .3s ease;
    }}
    .stButton > button:hover {{ transform: translateY(-2px); }}

    /* AI Improve button - FIXED GRADIENT */
    .stButton > button[key="improve_prompt"] {{
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #3b82f6 100%) !important;
        color: #fff !important;
        border-radius: 20px !important;
        padding: 10px 30px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 3px 10px rgba(139, 92, 246, 0.3) !important;
    }}

    /* Download button */
    .stDownloadButton > button {{
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 15px;
        padding: 10px 30px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}

    /* Footer */
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: linear-gradient(135deg, rgba(102,126,234,.9) 0%, rgba(118,75,162,.9) 100%);
        color: #fff; text-align: center; padding: 15px 0;
        backdrop-filter: blur(10px); z-index: 999;
        box-shadow: 0 -2px 10px rgba(0,0,0,.2);
    }}
    .footer p {{ margin: 0; font-size: 14px; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Title and subtitle
st.markdown(
    '<p class="title" style="font-size:60px; font-weight:bold; text-align:center;">AI Image Generator</p>',
    unsafe_allow_html=True
)
st.markdown('<p class="subtitle">Professional Quality AI Images</p>', unsafe_allow_html=True)

# Main content columns
col1, col2 = st.columns([1, 1])

with col1:
    # Input section
    st.markdown("### Describe Your Image")
    
    prompt = st.text_area(
        "Enter your prompt",
        placeholder="A majestic dragon soaring over a medieval castle at sunset, dark silhouette against vibrant orange and red sky, detailed scales, powerful wings spread wide, fantasy art style, cinematic lighting, highly detailed, professional quality, award-winning digital art, 4K resolution",
        height=120,
        help="Describe what you want to see in detail. Be specific about style, colors, mood, and composition."
    )

    # AI Improve Prompt button (removed clear button)
    if st.button("Improve Prompt with AI", key="improve_prompt", help="Enhance your prompt for better results"):
        if prompt.strip():
            improved_prompt = f"{prompt.strip()}, highly detailed, professional quality, vibrant colors, masterpiece, award-winning, cinematic lighting, 4K resolution"
            st.text_area(
                "Improved Prompt (copy this):",
                value=improved_prompt,
                height=80,
                help="Copy this enhanced prompt for better results"
            )
        else:
            st.success("Enter a prompt first!")

    st.markdown("### Image Size")
    size = st.selectbox(
        "Select image size",
        ["1024x1024 (Square)", "1792x1024 (Landscape)", "1024x1792 (Portrait)", "512x512 (Small Square)"],
        help="Choose the dimensions for your generated image"
    )

    st.markdown("### Quality")
    quality = st.selectbox(
        "Select quality",
        ["Standard", "High Quality", "Ultra High Quality"],
        help="Higher quality takes longer but produces better results"
    )


    generate_btn = st.button("Generate Professional Image", use_container_width=True)

with col2:
    # Output section
    st.markdown("### Generated Image")
    image_placeholder = st.empty()
    
    # Show example without caption (use a working image)
    try:
        # Try to load your local example image
        example_img = Image.open("images/ai_generated_professional.png")
        image_placeholder.image(
            example_img, 
            caption="Example: AI Generated Professional Image",
            use_container_width=True
        )
    except:
        # Fallback to a placeholder if local image doesn't exist
        st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://via.placeholder.com/1024x1024/667eea/ffffff?text=Your+Generated+Image+Will+Appear+Here'
             width='100' style='border-radius:15px;'>
        <p style='font-size:16px; color:gray;'>Preview: Your generated image will appear here</p>
    </div>
    """,
    unsafe_allow_html=True
)


# Store the current image in session state
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

# Hidden image generation function
def generate_clean_image(prompt, width, height, quality_level):
    """Generate clean, professional image with advanced watermark removal."""
    
    # Step 1: Generate with Pollinations
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width={width}&height={height}&seed={hash(prompt) % 1000}&enhance=true"
    
    try:
        response = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200 and response.headers.get('content-type', '').startswith('image'):
            raw_image = Image.open(io.BytesIO(response.content))
        else:
            return None
    except Exception:
        return None
    
    # Step 2: Try multiple watermark removal methods
    cleaned_image = None
    
    # Try ClipDrop first (if API key available)
    if _get_secret("CLIPDROP_API_KEY"):
        cleaned_image = remove_watermark_clipdrop(raw_image)
        if cleaned_image:
            return cleaned_image
    
    # Try advanced inpainting-style removal
    if quality_level == "Ultra High Quality":
        cleaned_image = remove_watermark_inpaint_style(raw_image)
    elif quality_level == "High Quality":
        cleaned_image = remove_watermark_photopea_style(raw_image)
    else:
        cleaned_image = simple_watermark_removal_v2(raw_image)
    
    return cleaned_image if cleaned_image else raw_image

def remove_watermark_clipdrop(image):
    """Remove watermark using ClipDrop API (better for watermarks)."""
    CLIPDROP_API_KEY = _get_secret("CLIPDROP_API_KEY")
    if not CLIPDROP_API_KEY:
        return None
    
    try:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        response = requests.post(
            'https://clipdrop-api.co/remove-text/v1',
            files={'image_file': ('image.png', img_bytes, 'image/png')},
            headers={'x-api-key': CLIPDROP_API_KEY},
            timeout=60
        )
        
        if response.status_code == 200:
            cleaned_img = Image.open(io.BytesIO(response.content))
            return cleaned_img
        
    except Exception:
        pass
    
    return None

def remove_watermark_photopea_style(image):
    """Advanced watermark removal using image processing techniques."""
    try:
        import numpy as np
        from PIL import ImageOps, ImageChops
        
        # Convert to numpy for advanced processing
        img_array = np.array(image)
        
        # Method 1: Content-aware fill simulation
        # Create mask for potential watermark areas (usually bottom-right)
        height, width = img_array.shape[:2]
        
        # Clone nearby pixels to cover watermark area
        # Focus on bottom-right corner where pollinations watermark appears
        watermark_region = img_array[int(height*0.85):, int(width*0.7):]
        
        if watermark_region.size > 0:
            # Sample from nearby clean area
            clean_region = img_array[int(height*0.7):int(height*0.85), int(width*0.5):int(width*0.7)]
            
            if clean_region.size > 0:
                # Replace watermark area with nearby pixels
                for i in range(watermark_region.shape[0]):
                    for j in range(watermark_region.shape[1]):
                        if i < clean_region.shape[0] and j < clean_region.shape[1]:
                            img_array[int(height*0.85) + i, int(width*0.7) + j] = clean_region[i, j]
        
        # Convert back to PIL
        temp_img = Image.fromarray(img_array)
        
        # Method 2: Advanced blending
        # Create multiple processed versions and blend
        blur1 = temp_img.filter(ImageFilter.GaussianBlur(radius=1.5))
        blur2 = temp_img.filter(ImageFilter.GaussianBlur(radius=0.8))
        
        # Blend the blurred versions
        blended = ImageChops.blend(blur1, blur2, 0.6)
        
        # Enhance contrast and color
        enhancer = ImageEnhance.Contrast(blended)
        enhanced = enhancer.enhance(1.4)
        
        color_enhancer = ImageEnhance.Color(enhanced)
        color_enhanced = color_enhancer.enhance(1.3)
        
        # Apply strong unsharp mask
        final = color_enhanced.filter(ImageFilter.UnsharpMask(radius=3, percent=180, threshold=1))
        
        return final
        
    except Exception as e:
        # Fallback to simpler method
        return simple_watermark_removal_v2(image)

def simple_watermark_removal_v2(image):
    """Improved simple watermark removal."""
    try:
        # Method: Multiple passes with different techniques
        result = image.copy()
        
        # Pass 1: Heavy blur + contrast
        result = result.filter(ImageFilter.GaussianBlur(radius=2.0))
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.8)
        
        # Pass 2: Color boost
        color_enhancer = ImageEnhance.Color(result)
        result = color_enhancer.enhance(1.6)
        
        # Pass 3: Brightness adjustment
        bright_enhancer = ImageEnhance.Brightness(result)
        result = bright_enhancer.enhance(1.15)
        
        # Pass 4: Strong sharpening to restore details
        result = result.filter(ImageFilter.UnsharpMask(radius=4, percent=250, threshold=0))
        
        # Pass 5: Final contrast boost
        final_enhancer = ImageEnhance.Contrast(result)
        result = final_enhancer.enhance(1.2)
        
        return result
        
    except Exception:
        return image

def remove_watermark_inpaint_style(image):
    """Simulate inpainting for watermark removal."""
    try:
        import numpy as np
        
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Target the typical pollinations watermark location (bottom-right)
        # Create a more aggressive replacement strategy
        
        # Define watermark region (bottom-right corner)
        wm_start_h = int(height * 0.88)
        wm_start_w = int(width * 0.75)
        
        # Sample clean pixels from multiple areas
        sample_regions = [
            img_array[int(height*0.6):int(height*0.8), int(width*0.4):int(width*0.6)],  # Middle area
            img_array[int(height*0.4):int(height*0.6), int(width*0.6):int(width*0.8)],  # Upper right
            img_array[int(height*0.7):int(height*0.85), int(width*0.3):int(width*0.5)]  # Lower left
        ]
        
        # Replace watermark area with blended samples
        for i in range(wm_start_h, height):
            for j in range(wm_start_w, width):
                # Blend pixels from different sample regions
                pixel_samples = []
                for region in sample_regions:
                    if region.size > 0:
                        # Get corresponding pixel from sample region
                        sample_i = (i - wm_start_h) % region.shape[0]
                        sample_j = (j - wm_start_w) % region.shape[1]
                        pixel_samples.append(region[sample_i, sample_j])
                
                if pixel_samples:
                    # Average the sampled pixels
                    avg_pixel = np.mean(pixel_samples, axis=0).astype(np.uint8)
                    img_array[i, j] = avg_pixel
        
        # Convert back and apply smoothing
        result = Image.fromarray(img_array)
        
        # Apply smoothing filter to blend the inpainted area
        result = result.filter(ImageFilter.SMOOTH_MORE)
        
        # Enhance the final result
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.3)
        
        return result
        
    except Exception:
        return image

# Alternative watermark removal using different API approach

# Generation logic
if generate_btn:
    if not prompt.strip():
        st.success("⚠️ Please enter a prompt to generate an image.")
    else:
        # Show progressive status
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("⭕ Creating your professional image..."):
            try:
                # Parse size
                size_map = {
                    "1024x1024 (Square)": (1024, 1024),
                    "1792x1024 (Landscape)": (1792, 1024),
                    "1024x1792 (Portrait)": (1024, 1792),
                    "512x512 (Small Square)": (512, 512)
                }
                width, height = size_map.get(size, (1024, 1024))
                
                # Update progress
                progress_bar.progress(20)
                status_text.text("🤖 AI analyzing your prompt...")
                
                # Update progress
                progress_bar.progress(40)
                status_text.text("🖌️ Generating high-quality image...")
                
                # Generate clean image (this hides all the watermark removal)
                final_image = generate_clean_image(prompt, width, height, quality)
                
                progress_bar.progress(70)
                status_text.text("🧹 Removing watermarks and artifacts...")
                
                progress_bar.progress(90)
                status_text.text("✨ Applying final enhancements...")
                
                # Final enhancement pass
                if final_image:
                    try:
                        # One more enhancement pass
                        enhancer = ImageEnhance.Contrast(final_image)
                        final_image = enhancer.enhance(1.1)
                        
                        sat_enhancer = ImageEnhance.Color(final_image)
                        final_image = sat_enhancer.enhance(1.1)
                    except:
                        pass
                
                if final_image:
                    # Store image in session state
                    st.session_state.current_image = final_image
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Complete!")
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display the clean final image
                    image_placeholder.image(
                        final_image, 
                        caption=f"Professional AI Generated: {prompt}",
                        use_container_width=True
                    )
                    
                    # Add download button for the clean image
                    with col2:
                        buf = io.BytesIO()
                        final_image.save(buf, format="PNG")
                        st.download_button(
                            label="⬇️ Download High-Quality Image",
                            data=buf.getvalue(),
                            file_name="ai_generated_professional.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    st.success("✅ Professional image generated successfully!")
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("❌ Failed to generate image. Please try again.")
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ An error occurred: {str(e)}")

# Tips section
st.markdown("---")
st.markdown("### 💡 Pro Tips for Better Results")
col1_tip, col2_tip, col3_tip = st.columns(3)

with col1_tip:
    st.markdown("""
    **🔥 Style Enhancement:**
    - "professional photography"
    - "award-winning"
    - "masterpiece quality"
    - "highly detailed"
    """)

with col2_tip:
    st.markdown("""
    **🌈 Visual Quality:**
    - "vibrant colors"
    - "perfect lighting"
    - "ultra-realistic"
    - "8K resolution"
    """)

with col3_tip:
    st.markdown("""
    **📸 Composition:**
    - "cinematic composition"
    - "professional framing"
    - "dramatic perspective"
    - "studio quality"
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div class='footer'>
        <p>Made with 🤍 BY DIVAKAR M & NEHA S | Internship-2 Project </p>
    </div>
""", unsafe_allow_html=True)



