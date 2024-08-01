import io
import re
from typing import Any
import urllib.request
from io import BytesIO

import torch
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DonutInference(metaclass=Singleton):
    def __init__(self, model_pth : str ,device: str = None):

        self.processor = DonutProcessor.from_pretrained(model_pth)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_pth)
        
        if device:
            self.device = device
            self.model.to(device)
            
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def __call__(self, image) -> Any:

        # prepare encoder inputs
        pixel_values = self.processor(image, return_tensors="pt").pixel_values

        # prepare decoder inputs
        task_prompt = "<s_cord-v2>"
        decoder_input_ids = self.processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids

        # generate answer
        outputs = self.model.generate(
            pixel_values.to(self.device),
            decoder_input_ids=decoder_input_ids.to(self.device),
            max_length=self.model.decoder.config.max_position_embeddings,
            early_stopping=True,
            pad_token_id=self.processor.tokenizer.pad_token_id,
            eos_token_id=self.processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
            bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

        # postprocess
        sequence = self.processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token, "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token

        return self.processor.token2json(sequence)