from tensorflow.keras.models import load_model

def DigitDetector():
    model = load_model('digitRecognition.keras')
    return model 