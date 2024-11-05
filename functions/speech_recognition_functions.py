import azure.cognitiveservices.speech as speechsdk
from vars import SPEECH_KEY, SPEECH_REGION, STT_ENDPOINT
import logging
logger = logging.getLogger()


def create_speech_config(SPEECH_KEY:str, SPEECH_REGION:str, STT_ENDPOINT: str)-> object:
    """
    Function generates an Azure Speech SDK speech config object 
    :inputs:
    SPEECH_KEY: Azure Speech Services Key
    SPEECH_REGION: Azure region
    ENDPOINT: private endpoint associated with speech service
    :outputs:
    speech config object
    *this function assumes that the recognition language is US English
    """
    logger.info(f"Building speech config in {SPEECH_REGION} pointing to endpoint {STT_ENDPOINT}")
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.endpoint_id = STT_ENDPOINT
    speech_config.speech_recognition_language="en-US"
    return speech_config


def create_audio_config(use_default_microphone: bool)-> object:
    """
    Function generates an Azure Speech SDK audio config object
    :inputs:
    use_default_microphone: boolean specifying output to default microphone
    :outputs:
    audio config object  
    """
    audio_config = speechsdk.AudioConfig(use_default_microphone=use_default_microphone)
    return audio_config

def recognize_real_time_speech()-> str:
    """
    Function uses the Azure Speech SDK to transcribe audio from the default microphone.
    :inputs: None
    :outputs: 
    Speech recognition result text
    """
    logger.info(f"Building real-time speech recognition configuration.")
    speech_config = create_speech_config(SPEECH_KEY, SPEECH_REGION, STT_ENDPOINT)
    audio_config = create_audio_config(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    logger.info("Recognizing real-time speech.")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        logger.info(f"Recognized text: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        logger.error("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logger.error("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        logger.error("Error details: {}".format(cancellation_details.error_details))


def recognize_recorded_speech(audio_filename: str)-> str:
    """
    Function uses the Azure Speech SDK to transcribe audio from a WAV file
    :inputs:
    audio_filename: file path to WAV file
    :outputs:
    Speech recognition result text
    """
    logger.info(f"Building recording speech recognition configuration.")
    speech_config = create_speech_config(SPEECH_KEY, SPEECH_REGION, STT_ENDPOINT)
    audio_config = speechsdk.AudioConfig(filename=audio_filename)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    logger.info("Recognizing recorded speech.")
    result = speech_recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        logger.info(f"Recognized text: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        logger.error("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logger.error("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        logger.error("Error details: {}".format(cancellation_details.error_details))