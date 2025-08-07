# app.py
import streamlit as st
import os
import glob
from ultralytics import YOLO
from PIL import Image
from io import BytesIO

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="YOLO Object Detection App")

# --- Helper Functions ---


@st.cache_data
def load_image(image_path):
    """Loads an image from a file path."""
    try:
        return Image.open(image_path)
    except Exception as e:
        st.error(f"Error loading image '{image_path}': {e}")
        return None


@st.cache_resource
def load_model(model_path):
    """Loads a YOLO model from a file path."""
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None


def detect_objects(model, image, conf_threshold):
    """Performs object detection on the image."""
    results = model.predict(image, conf=conf_threshold)
    return results[0]


def display_results(results, image_placeholder, caption):
    """Displays the annotated image."""
    annotated_image_bgr = results.plot()
    annotated_image_rgb = annotated_image_bgr[..., ::-1]
    image_placeholder.image(annotated_image_rgb,
                            caption=caption, use_container_width=True)


# --- Path Configuration ---
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

if not os.path.exists(MODEL_DIR):
    st.error(f"Error: The model folder '{MODEL_DIR}' does not exist.")
    st.stop()
if not os.path.exists(IMAGE_DIR):
    st.error(f"Error: The image folder '{IMAGE_DIR}' does not exist.")
    st.stop()

try:
    available_models = sorted([os.path.basename(m)
                               for m in glob.glob(f"{MODEL_DIR}/*.pt")])
    image_paths = sorted(
        glob.glob(f"{IMAGE_DIR}/*.jpg") + glob.glob(f"{IMAGE_DIR}/*.png"))
except Exception as e:
    st.error(f"Error reading folders: {e}")
    st.stop()

if not available_models:
    st.error(f"No YOLO models found in '{MODEL_DIR}'.")
    st.stop()
if not image_paths:
    st.error(f"No images found in '{IMAGE_DIR}'.")
    st.stop()

# --- Session State Management ---
if "selected_image_path" not in st.session_state:
    st.session_state.selected_image_path = None
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None

# --- Streamlit UI ---
st.title("Object Detection with YOLO")
st.markdown("Select a YOLO model and an image (from the thumbnails below or by uploading one) to perform object detection.")

# Sidebar for controls
st.sidebar.header("Configuration")
model_choice = st.sidebar.selectbox("Choose a YOLO model:", available_models)

conf_threshold = st.sidebar.slider(
    "Confidence Threshold:",
    min_value=0.0,
    max_value=1.0,
    value=0.25,
    step=0.05
)

run_all_models = st.sidebar.checkbox("Show all models' results")

uploaded_file = st.sidebar.file_uploader(
    "Upload a new image:",
    type=["jpg", "jpeg", "png"]
)

# --- Main App Logic ---

# Handle file uploader logic and update session state
if uploaded_file:
    # Get uploaded file data and store it in session state
    st.session_state.uploaded_file_data = uploaded_file.getvalue()
    st.session_state.selected_image_path = None  # Reset thumbnail selection
    # Reset pointer after reading to allow other operations
    uploaded_file.seek(0)

# Determine the image to process based on current session state
image_to_process = None
image_caption = ""

if st.session_state.uploaded_file_data:
    # Use the uploaded file data from session state
    image_to_process = Image.open(BytesIO(st.session_state.uploaded_file_data))
    image_caption = "Uploaded Image"
elif st.session_state.selected_image_path:
    # Use the selected thumbnail image
    image_to_process = load_image(st.session_state.selected_image_path)
    image_caption = f"Selected Image from Folder: {os.path.basename(st.session_state.selected_image_path)}"

# Display selected or uploaded image and its detection result
if image_to_process and model_choice:
    # Logic for showing all models or a single model
    if run_all_models:
        st.header("Original Image")
        st.image(image_to_process, caption=image_caption,
                 use_container_width=True)
        st.header("Comparative Detection Results (All Models)")

        cols_per_row = 2
        cols = st.columns(cols_per_row)

        for i, model_name in enumerate(available_models):
            with cols[i % cols_per_row]:
                st.subheader(model_name)
                model = load_model(os.path.join(MODEL_DIR, model_name))
                if model:
                    with st.spinner(f"Running detection with {model_name}..."):
                        results = detect_objects(
                            model, image_to_process, conf_threshold)
                        display_results(results, st.empty(),
                                        f"Result from {model_name}")
                else:
                    st.warning(f"Could not load model: {model_name}")

    else:  # Single model display
        model = load_model(os.path.join(MODEL_DIR, model_choice))

        if model:
            col1, col2 = st.columns(2)

            with col1:
                st.header("Original Image")
                st.image(image_to_process, caption=image_caption,
                         use_container_width=True)

            with col2:
                st.header("Detection Result")
                progress_bar_placeholder = st.empty()
                progress_bar_placeholder.info(
                    "Running object detection... Please wait.")
                results = detect_objects(
                    model, image_to_process, conf_threshold)
                display_results(results, st.empty(),
                                f"Result from {model_choice}")
                progress_bar_placeholder.empty()

# --- Thumbnail Section ---
st.markdown("---")
st.header("Or select an image from the folder:")
cols = st.columns(6)


def on_thumbnail_click(image_path):
    # This callback function directly updates the session state
    st.session_state.selected_image_path = image_path
    st.session_state.uploaded_file_data = None  # Clear uploaded file
    # We don't need st.rerun() here because the button itself triggers a rerun.
    # The logic at the top of the script will pick up the new state.


for i, image_path in enumerate(image_paths):
    with cols[i % 6]:
        with st.container(border=True):
            try:
                image = Image.open(image_path)
                image.thumbnail((150, 150))

                MAX_LENGTH = 30
                caption = (os.path.basename(image_path)[
                           :MAX_LENGTH] + '...') if len(os.path.basename(image_path)) > MAX_LENGTH else os.path.basename(image_path)

                st.image(image, caption=caption, use_container_width=True)

                # The st.button is now using the key and the on_click callback
                st.button(
                    "Select",
                    key=f"select_{i}",
                    use_container_width=True,
                    on_click=on_thumbnail_click,
                    args=(image_path,)
                )

            except Exception as e:
                st.warning(
                    f"Could not create thumbnail for {os.path.basename(image_path)}: {e}")
                st.text(os.path.basename(image_path))

if not st.session_state.uploaded_file_data and not st.session_state.selected_image_path:
    st.info("Please select an image or upload one to get started.")
