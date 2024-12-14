import os
from flask import Blueprint, render_template, request
from PIL import Image
import cv2
from skimage.metrics import structural_similarity

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route("/upload", methods=["POST"])
def upload_file():
    if "image" not in request.files or request.files["image"].filename == "":
        msg = "No image part in the request or no image uploaded"
        return render_template("index.html", msg=msg), 400

    file = request.files["image"]
    upload_folder = 'uploads'
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

   
    original_path = os.path.join(upload_folder, 'original.jpg')
    
    if not os.path.exists(original_path):
        msg = "Original image not found for comparison"
        return render_template("index.html", msg=msg), 400
   

    original = Image.open(original_path).resize((250, 160))
    tampered = Image.open(filepath).resize((250, 160))

 
    original.save(os.path.join(upload_folder, 'original_resized.png'))
    tampered.save(os.path.join(upload_folder, 'tampered_resized.png'))


    original_gray = cv2.imread(os.path.join(upload_folder, 'original_resized.png'), cv2.IMREAD_GRAYSCALE)
    tampered_gray = cv2.imread(os.path.join(upload_folder, 'tampered_resized.png'), cv2.IMREAD_GRAYSCALE)

    if original_gray is None or tampered_gray is None:
        msg = "Error loading images for SSIM comparison"
        return render_template("index.html", msg=msg), 400


    score, diff = structural_similarity(original_gray, tampered_gray, full=True)
    diff = (diff * 255).astype("uint8")
    print("SSIM: {}".format(score))
    return render_template("index.html", pscore=score*100)
