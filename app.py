from flask import Flask, request, jsonify
from lex import detect_qr_and_blocks
from parse import parse_blocks
from eval import generate_output
import cv2
import os
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_image():
    """
    Compile endpoint that processes an uploaded image and returns compilation results.
    
    Expects multipart form data with 'image' file field.
    
    Returns JSON response:
    {
        "success": true/false,
        "is_correct": true/false,
        "output": "compiled output or error message"
    }
    """
    try:
        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "is_correct": False,
                "output": "No image file provided. Please upload an image using 'image' field"
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "is_correct": False,
                "output": "No image file selected"
            }), 400
        
        # Read image data directly from memory
        file_bytes = file.read()
        
        # Convert to numpy array and then to OpenCV image
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({
                "success": False,
                "is_correct": False,
                "output": "Could not read the uploaded image. Please ensure it's a valid image file"
            }), 400
        
        # 1) Detect all QRs (loop, if/else, conditions, actions, colors)
        blocks, loop_count, anchor_x = detect_qr_and_blocks(img)
        
        # 2) Parse into structure
        parsed = parse_blocks(blocks, loop_count)
        
        # 3) Evaluate and get output
        final_output = generate_output(parsed)
        
        # Determine if output is correct based on the presence of "✓ CORRECT:" prefix
        is_correct = final_output.startswith("✓ CORRECT:")
        
        # Clean output for JSON response (remove the ✓ CORRECT: prefix if present)
        clean_output = final_output
        if is_correct:
            clean_output = final_output.replace("✓ CORRECT: ", "")
        
        return jsonify({
            "success": True,
            "is_correct": is_correct,
            "output": clean_output
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "is_correct": False,
            "output": f"Error processing image: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "CT4PWD Compiler API is running"
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "message": "CT4PWD Compiler API",
        "version": "1.0",
        "endpoints": {
            "POST /compile": "Compile visual programming blocks from image",
            "GET /health": "Health check",
            "GET /": "API documentation"
        },
        "usage": {
            "compile": {
                "method": "POST",
                "endpoint": "/compile",
                "content_type": "multipart/form-data",
                "field": "image",
                "description": "Upload image file containing visual programming blocks",
                "example": "curl -X POST -F 'image=@path/to/image.png' https://your-api-url/compile"
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)