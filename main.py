from lex import detect_qr_and_blocks
from parse import parse_blocks
from eval import generate_output
import cv2

if __name__ == "__main__":
    image_path = "test-images/ifelse.png"
    # image_path = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\CT4PWD-Compiler\\CT4PWD-2main\\CT4PWD-Compiler-main\\test-images\\ifelse2.png"

    print("Processing image...")

    img = cv2.imread(image_path)

    # 1) detect all QRs (loop, if/else, conditions, actions, colors)
    blocks, loop_count, anchor_x = detect_qr_and_blocks(img)
    print("Detected blocks:", blocks)
    print("Loop count:", loop_count, "Anchor X:", anchor_x)

    # 2) parse into structure (colors already included from QR parsing)
    parsed = parse_blocks(blocks, loop_count)
    print("Parsed:", parsed)

    # 3) evaluate
    final_output = generate_output(parsed)
    print("\nFinal Output:")
    print(final_output)
