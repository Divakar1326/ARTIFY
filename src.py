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

# Get API keys
CLIPDROP_API_KEY = _get_secret("CLIPDROP_API_KEY")
CLIPDROP_API_KEY_2 = _get_secret("CLIPDROP_API_KEY_2")  # Add second key
# Create list of ClipDrop API keys
CLIPDROP_KEYS = [key for key in [CLIPDROP_API_KEY, CLIPDROP_API_KEY_2] if key]

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

    /* Select Box Styling with Gradient Display */
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

    .stSelectbox [data-baseweb="select"] {{
        background: linear-gradient(135deg, rgba(248, 249, 250, 0.95) 0%, rgba(233, 236, 239, 0.95) 100%) !important;
        border-radius: 10px !important;
    }}

    .stSelectbox [data-baseweb="select"] > div:hover {{
        background: linear-gradient(135deg, #dbe7ff 0%, #c6d9ff 100%) !important;
    }}
    
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

    /* AI Improve button */
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

# Enhancement functions for ClipDrop images
def enhance_image_quality(image):
    """Enhance ClipDrop image quality without heavy processing."""
    try:
        result = image.copy()
        
        # Light enhancement for already clean images
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.1)
        
        color_enhancer = ImageEnhance.Color(result)
        result = color_enhancer.enhance(1.15)
        
        result = result.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=3))
        
        return result
        
    except Exception as e:
        st.warning(f"Quality enhancement failed: {e}")
        return image

def enhance_image_standard(image):
    """Standard enhancement for ClipDrop images."""
    try:
        result = image.copy()
        
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.05)
        
        color_enhancer = ImageEnhance.Color(result)
        result = color_enhancer.enhance(1.08)
        
        return result
        
    except Exception as e:
        st.warning(f"Standard enhancement failed: {e}")
        return image

# Watermark removal functions for non-ClipDrop images
def advanced_watermark_removal(image):
    """Advanced watermark removal."""
    try:
        result = image.copy()
        
        # Multiple passes of enhancement
        for i in range(3):
            result = result.filter(ImageFilter.GaussianBlur(radius=0.5 + i * 0.3))
            
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.4 + i * 0.1)
            
            color_enhancer = ImageEnhance.Color(result)
            result = color_enhancer.enhance(1.3 + i * 0.1)
        
        result = result.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        return result
        
    except Exception as e:
        st.warning(f"Advanced watermark removal failed: {e}")
        return image

def medium_watermark_removal(image):
    """Medium quality watermark removal."""
    try:
        result = image.copy()
        
        for i in range(2):
            result = result.filter(ImageFilter.GaussianBlur(radius=0.8))
            
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.5)
            
            bright_enhancer = ImageEnhance.Brightness(result)
            result = bright_enhancer.enhance(1.1)
            
            color_enhancer = ImageEnhance.Color(result)
            result = color_enhancer.enhance(1.4)
        
        result = result.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=2))
        
        return result
        
    except Exception as e:
        st.warning(f"Medium watermark removal failed: {e}")
        return image

def simple_watermark_removal_v2(image):
    """Simple watermark removal."""
    try:
        result = image.copy()
        
        result = result.filter(ImageFilter.GaussianBlur(radius=1.0))
        
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.8)
        
        color_enhancer = ImageEnhance.Color(result)
        result = color_enhancer.enhance(1.6)
        
        bright_enhancer = ImageEnhance.Brightness(result)
        result = bright_enhancer.enhance(1.15)
        
        try:
            result = result.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=3))
        except:
            result = result.filter(ImageFilter.SHARPEN)
            result = result.filter(ImageFilter.SHARPEN)
        
        return result
        
    except Exception as e:
        st.warning(f"Simple watermark removal failed: {e}")
        return image

# Main image generation function
def generate_clean_image(prompt, width, height, quality_level):
    """Generate clean, professional image using ClipDrop API with Pollinations fallback."""
    
    final_image = None
    
    # Try ClipDrop first (usually no watermarks)
    if CLIPDROP_KEYS:
        for i, api_key in enumerate(CLIPDROP_KEYS):
            try:
                                      
                headers = {
                    'x-api-key': api_key,
                }
                
                files = {
                    'prompt': (None, prompt),
                }
                
                response = requests.post(
                    "https://clipdrop-api.co/text-to-image/v1",
                    headers=headers,
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200:
                    final_image = Image.open(io.BytesIO(response.content))
                    st.success(f"✅ High-quality image generated)")
                    
                    # Resize to requested dimensions
                    if final_image.size != (width, height):
                        final_image = final_image.resize((width, height), Image.Resampling.LANCZOS)
                    
                    return final_image
                    
                elif response.status_code == 401:
                    continue  # Try next key
                elif response.status_code == 429:
                   continue  # Try next key
                else:
                   continue  # Try next key
                    
            except requests.exceptions.Timeout:
                continue  # Try next key
            except Exception as e:
                continue  # Try next key
        
        else:
          st.warning("⚠️ fallback...")
    
    # Fallback to Pollinations if all ClipDrop keys fail
    fallback_apis = [
        {
            "name": "Pollinations (Enhanced)",
            "url": f"https://image.pollinations.ai/prompt/{quote(prompt)}?width={width}&height={height}&seed={hash(prompt) % 1000}&enhance=true&nologo=true",
            "timeout": 60
        },
        {
            "name": "Pollinations (Standard)",
            "url": f"https://image.pollinations.ai/prompt/{quote(prompt)}?width={width}&height={height}",
            "timeout": 45
        }
    ]
    
    for api in fallback_apis:
        try:
                       
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(api["url"], timeout=api["timeout"], headers=headers)
            
            if response.status_code == 200 and response.headers.get('content-type', '').startswith('image'):
                final_image = Image.open(io.BytesIO(response.content))
                st.success(f"✅ Image generated!")
                break
            else:
               continue
                
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            continue
    
    if not final_image:
        st.error("❌ image generation failed.")
        return None
    
    # Apply enhancement/watermark removal based on source
    try:
        if final_image and any(CLIPDROP_KEYS):  # If we have ClipDrop keys available
            # ClipDrop images are usually clean, just enhance them
            if quality_level == "Ultra High Quality":
                final_image = enhance_image_quality(final_image)
            elif quality_level == "High Quality":
                final_image = enhance_image_standard(final_image)
        else:
            # Apply watermark removal for other APIs
            if quality_level == "Ultra High Quality":
                final_image = advanced_watermark_removal(final_image)
            elif quality_level == "High Quality":
                final_image = medium_watermark_removal(final_image)
            else:
                final_image = simple_watermark_removal_v2(final_image)
                
    except Exception as e:
        st.warning(f"Processing failed: {e}")
    
    return final_image

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
        placeholder="Type here...",
        height=120,
        help="Describe what you want to see in detail. Be specific about style, colors, mood, and composition."
    )

    # AI Improve Prompt button
    if st.button("Improve My Prompt♦️", key="improve_prompt", help="Enhance your prompt for better results"):
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
    
    # Show example image
    try:
        example_img = Image.open("images/ai_generated_professional.png")
        image_placeholder.image(
            example_img, 
            caption="Example: AI Generated Professional Image",
            use_container_width=True
        )
    except:
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

# Generation logic
if generate_btn:
    if not prompt.strip():
        st.warning("⚠️ Please enter a prompt to generate an image.")
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
                status_text.text("🧠 AI analyzing your prompt...")
                
                # Update progress
                progress_bar.progress(40)
                if CLIPDROP_API_KEY:
                    status_text.text("🎨 Generating premium quality image with ClipDrop...")
                else:
                    status_text.text("Your image is getting ready 🖌️")
                
                # Generate clean image
                final_image = generate_clean_image(prompt, width, height, quality)
                
                if final_image:
                    progress_bar.progress(70)
                    if CLIPDROP_API_KEY:
                        status_text.text("✨ Enhancing ClipDrop image...")
                    else:
                        status_text.text("🧹 Removing watermarks and artifacts...")
                    
                    progress_bar.progress(90)
                    status_text.text("✔️ Applying final enhancements...")
                    
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
                    
                   
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("❌ image generation currently unavailable.")
                    st.info("💡 This usually means the servers are busy. Try again in a few minutes.")
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ An unexpected error occurred: {str(e)}")
                st.info("💡 Try refreshing the page or using a simpler prompt.")

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
        <p>Made with 🤍 BY DIVAKAR </p>
    </div>
""", unsafe_allow_html=True)









