import streamlit as st

# Place st.set_page_config() as the first Streamlit command
st.set_page_config(
    page_title="Moroccan ID OCR", 
    page_icon="🆔",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://github.com/yourusername/moroccan-id-ocr/wiki',
        'Report a bug': 'https://github.com/yourusername/moroccan-id-ocr/issues',
        'About': """
        ## Moroccan ID OCR Application
        
        **Version:** 1.0.0
        **Purpose:** Intelligent Document Processing for Moroccan ID Cards
        
        Developed with advanced OCR technologies.
        
        ### Features
        - Advanced Text Extraction
        - Multilingual Support (Arabic & French)
        - Intelligent Data Parsing
        
        Created with ❤️ using Streamlit and Tesseract OCR
        """
    }
)

import os
import re
import base64
from io import BytesIO
from PIL import Image
import logging
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import with more robust approach
try:
    from utils.ocr_helper import OCRHelper, LoggerConfig
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.error("Unable to import OCRHelper. Please check your project structure.")
    raise

class EnhancedStreamlitOCR:
    def __init__(self):
        # Setup logging
        try:
            self.logger = LoggerConfig.setup_logger('StreamlitOCR')
            self.logger.info("Application initialized successfully")
        except Exception as e:
            st.error(f"Logging setup failed: {e}")
            self.logger = logging.getLogger('StreamlitOCR')
        
        # Initialize OCR Helper
        try:
            self.ocr_helper = OCRHelper()
            self.logger.info("OCR Helper initialized successfully")
        except Exception as e:
            self.logger.error(f"OCR Helper initialization failed: {e}")
            st.error(f"OCR Helper initialization failed: {e}")
            self.ocr_helper = None

    def preprocess_uploaded_image(self, uploaded_file):
        """
        Preprocess the uploaded image for OCR
        
        Args:
            uploaded_file: Streamlit uploaded file object
        
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Open the image
            image = Image.open(uploaded_file)
            
            # Log image details
            self.logger.info(f"Image uploaded: {uploaded_file.name}")
            self.logger.info(f"Image size: {image.size}")
            self.logger.info(f"Image mode: {image.mode}")
            
            return image
        except Exception as e:
            self.logger.error(f"Image preprocessing error: {e}")
            st.error(f"Error processing image: {e}")
            return None

    def extract_and_parse_text(self, image, language='ara+fra'):
        """
        Extract and parse text from the image
        
        Args:
            image: PIL Image
            language: OCR language configuration
        
        Returns:
            Extracted and parsed text data
        """
        if self.ocr_helper is None:
            st.error("OCR Helper not initialized")
            return None

        try:
            # Temporary save image for OCR processing
            temp_path = 'temp_uploaded_image.jpg'
            image.save(temp_path)
            
            # Extract text using OCR Helper
            extracted_text = self.ocr_helper.extract_text(
                temp_path, 
                language=language
            )
            
            # Remove temporary file
            os.remove(temp_path)
            
            if not extracted_text:
                st.warning("No text could be extracted from the image.")
                return None
            
            # Parse extracted data
            parsed_data = self.parse_extracted_data(extracted_text)
            
            return {
                'full_text': extracted_text,
                'parsed_data': parsed_data
            }
        
        except Exception as e:
            self.logger.error(f"Text extraction error: {e}")
            st.error(f"Error extracting text: {e}")
            return None

    def parse_extracted_data(self, text):
        """
        Advanced parsing of extracted text
        
        Args:
            text: Extracted text
        
        Returns:
            Dictionary of parsed information
        """
        parsed_data = {
            'names': {
                'arabic': None,
                'latin': None
            },
            'cin_number': None,
            'date_of_birth': None,
            'place_of_birth': None,
            'expiry_date': None
        }

        # Regex patterns for extraction
        patterns = {
            'cin_number': r'\b[A-Z]{1,2}\d{6}\b',
            'date_of_birth': r'\d{2}/\d{2}/\d{4}',
            'latin_name': r'[A-Z][a-z]+ [A-Z][a-z]+',
            'arabic_name': r'[\u0600-\u06FF\s]+',
        }

        # Extract information using regex
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                if key == 'latin_name':
                    parsed_data['names']['latin'] = match.group(0)
                elif key == 'arabic_name':
                    parsed_data['names']['arabic'] = match.group(0)
                elif key == 'cin_number':
                    parsed_data['cin_number'] = match.group(0)
                elif key == 'date_of_birth':
                    parsed_data['date_of_birth'] = match.group(0)

        return parsed_data

    def render_application(self):
        """
        Render the Streamlit application UI
        """
        st.title("🆔 Moroccan ID Card OCR")
        st.write("Upload a Moroccan ID card image for intelligent text extraction")

        # File uploader with enhanced configuration
        uploaded_file = st.file_uploader(
            "Choose an image", 
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear, high-resolution image of a Moroccan ID card"
        )

        # Information and guidance section
        with st.expander("ℹ️ How to Use"):
            st.markdown("""
            ### Instructions
            1. Upload a clear photo of a Moroccan ID card
            2. Ensure the entire document is visible
            3. Use high-resolution images for best results
            4. Click "Extract Text" to process the image
            
            ### Supported Features
            - Extracts text from Moroccan ID cards
            - Supports Arabic and French languages
            - Intelligent data parsing
            """)

        if uploaded_file is not None:
            # Preprocess image
            image = self.preprocess_uploaded_image(uploaded_file)
            
            if image:
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Uploaded Image")
                    st.image(image, use_container_width=True)

                with col2:
                    st.subheader("Extracted Information")

                    if st.button("Extract Text", type="primary"):
                        with st.spinner("Processing image..."):
                            # Extract text
                            extraction_result = self.extract_and_parse_text(image)

                            if extraction_result:
                                # Create tabs
                                tab1, tab2, tab3 = st.tabs(["📜 Full Text", "🇲🇦 Details", "🔍 Parsed Info"])

                                with tab1:
                                    st.text(extraction_result['full_text'])

                                with tab2:
                                    st.markdown("#### Extracted Details")
                                    st.json(extraction_result['parsed_data'])

                                with tab3:
                                    st.markdown("##### Parsed Information")
                                    parsed_data = extraction_result['parsed_data']
                                    
                                    # Display parsed information
                                    st.metric("Arabic Name", parsed_data['names']['arabic'] or "Not Found")
                                    st.metric("Latin Name", parsed_data['names']['latin'] or "Not Found")
                                    st.metric("CIN Number", parsed_data['cin_number'] or "Not Found")
                                    st.metric("Date of Birth", parsed_data['date_of_birth'] or "Not Found")

def main():
    # Initialize and run the application
    ocr_app = EnhancedStreamlitOCR()
    ocr_app.render_application()

if __name__ == "__main__":
    main()
