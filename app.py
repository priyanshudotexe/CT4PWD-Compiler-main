from flask import Flask, request, jsonify
from lex import detect_qr_and_blocks
from parse import parse_blocks
from eval import generate_output
import cv2
import os

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_image():
    """
    Compile endpoint that processes an image and returns compilation results.
    
    Expected JSON payload:
    {
        "image_path": "path/to/image.png"
    }
    
    Returns JSON response:
    {
        "success": true/false,
        "is_correct": true/false,
        "output": "compiled output or error message",
        "details": {
            "detected_blocks": [...],
            "loop_count": int,
            "anchor_x": int,
            "parsed": {...}
        }
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'image_path' not in data:
            return jsonify({
                "success": False,
                "is_correct": False,
                "output": "Missing image_path in request body",
                "details": None
            }), 400
        
        image_path = data['image_path']
        
        # Check if file exists
        if not os.path.exists(image_path):
            return jsonify({
                "success": False,
                "is_correct": False,
                "output": f"Image file not found: {image_path}",
                "details": None
            }), 404
        
        # Load and process the image
        img = cv2.imread(image_path)
        
        if img is None:
            return jsonify({
                "success": False,
                "is_correct": False,
                "output": f"Could not read image file: {image_path}",
                "details": None
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
            "output": clean_output,
            "details": {
                "detected_blocks": blocks,
                "loop_count": loop_count,
                "anchor_x": anchor_x,
                "parsed": parsed,
                "raw_output": final_output
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "is_correct": False,
            "output": f"Error processing image: {str(e)}",
            "details": None
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
                "content_type": "application/json",
                "body": {
                    "image_path": "string - path to the image file"
                },
                "example": {
                    "image_path": "test-images/ifelse.png"
                }
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)