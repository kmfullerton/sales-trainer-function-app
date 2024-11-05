from vars import SPEECH_KEY, SPEECH_REGION
import azure.cognitiveservices.speech as speechsdk
import random
import logging
logger = logging.getLogger()


def create_speech_config(SPEECH_KEY:str, SPEECH_REGION:str)-> object:
    """
    Function generates an Azure Speech SDK speech config object 
    :inputs:
    SPEECH_KEY: Azure Speech Services Key
    SPEECH_REGION: Azure region
    :outputs:
    speech config object
    * This function assumes that the spoken language is US English
    * This function selects a random synthetic voice for the listed of supported voices.
    """
    logger.info("Creating speech config object.")
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language="en-US"
    # TODO: When implementing in production, need to make the voice random at the beginning of the convo and then consistent until end of convo
    speech_config.speech_synthesis_voice_name= select_random_voice()
    logger.info('Speech config object created.')
    return speech_config



def create_audio_config(use_default_speaker: bool)-> object:
    """
    Function generates an Azure Speech SDK audio config object
    :inputs:
    use_default_speaker: boolean specifying output to default speaker
    :outputs:
    audio config object   
    """
    logger.info('Creating audio config object.')
    logger.info(f'Using default speaker? {use_default_speaker}')
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=use_default_speaker)
    logger.info('Audio config object created.')
    return audio_config


def create_speech_synthesizer_object(speech_config: object, audio_config: object)-> object:
    """
    Function generates Azure Speech SDK speech synthesizer object.
    :inputs:
    speech_config
    audio_config
    :outputs:
    speech_synthesizer object
    """
    logger.info('Creating speech synthesizer object.')
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    logger.info('Speech synthesizer object created.')
    return speech_synthesizer


def generate_speech(speech_synthesizer: object, text: str):
    """
    Function executes speech synthesis request and plays synthesized speech
    :inputs:
    speech_synthesizer object
    text: string representing words to sythesize.
    :outputs:
    result_id from speech synthesis request
    """
    logger.info('Generating synthetic speech.')
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    return speech_synthesis_result.result_id


def select_random_voice()-> str:
    """
    Function selects random item from list of syntheic voices supported in Azure region East US 2
    :outputs: 
    voice_id: string representing voice specification
    """
    voices_list = ['en-US-AndrewMultilingualNeural', 'en-US-EmmaMultilingualNeural', 'en-US-BrianMultilingualNeural', 'en-US-AvaNeural', 'en-US-AndrewNeural', 'en-US-EmmaNeural', 'en-US-BrianNeural', 'en-US-JennyNeural', 'en-US-GuyNeural', 'en-US-AriaNeural', 'en-US-DavisNeural', 'en-US-JaneNeural', 'en-US-JasonNeural', 'en-US-SaraNeural', 'en-US-TonyNeural', 'en-US-NancyNeural', 'en-US-AmberNeural', 'en-US-AnaNeural', 'en-US-AshleyNeural', 'en-US-BrandonNeural', 'en-US-ChristopherNeural', 'en-US-CoraNeural', 'en-US-ElizabethNeural', 'en-US-EricNeural', 'en-US-JacobNeural', 'en-US-JennyMultilingualNeural', 'en-US-MichelleNeural', 'en-US-MonicaNeural', 'en-US-RogerNeural', 'en-US-RyanMultilingualNeural','en-US-SteffanNeural']
    voice = voices_list[random.randrange(0, len(voices_list)-1)]
    logger.info(f'Randomly selected voice: {voice}')
    return voice