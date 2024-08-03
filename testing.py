import re
import json
import torch
import numpy as np
from tqdm.auto import tqdm
from donut import JSONParseEvaluator
from datasets import load_dataset
from transformers import DonutProcessor, VisionEncoderDecoderModel

device = "cuda" if torch.cuda.is_available() else "cpu"


def evaluate_model(model_name, dataset):
    processor = DonutProcessor.from_pretrained(model_name)
    model = VisionEncoderDecoderModel.from_pretrained(model_name)

    model.eval()
    model.to(device)

    f1 = []
    accs = []
    recalls = []
    precisions = []

    evaluator = JSONParseEvaluator()

    for idx, sample in tqdm(enumerate(dataset), total=len(dataset)):
        # Prepare encoder inputs
        pixel_values = processor(
            sample["image"].convert("RGB"), return_tensors="pt"
        ).pixel_values
        pixel_values = pixel_values.to(device)
        # Prepare decoder inputs
        task_prompt = "<s_cord-v2>"
        decoder_input_ids = processor.tokenizer(
            task_prompt, add_special_tokens=False, return_tensors="pt"
        ).input_ids
        decoder_input_ids = decoder_input_ids.to(device)

        # Autoregressively generate sequence
        outputs = model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=model.decoder.config.max_position_embeddings,
            early_stopping=True,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
            bad_words_ids=[[processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

        # Turn into JSON
        seq = processor.batch_decode(outputs.sequences)[0]
        seq = seq.replace(processor.tokenizer.eos_token, "").replace(
            processor.tokenizer.pad_token, ""
        )
        seq = re.sub(
            r"<.*?>", "", seq, count=1
        ).strip()  # remove first task start token
        seq = processor.token2json(seq)

        ground_truth = json.loads(sample["ground_truth"])["gt_parse"]

        score = evaluator.cal_acc(seq, ground_truth)
        f1_value = evaluator.cal_f1(seq, ground_truth)

        total_tp, total_fp, total_fn = 0, 0, 0
        for pred, answer in zip(seq, ground_truth):
            pred, answer = evaluator.flatten(
                evaluator.normalize_dict(pred)
            ), evaluator.flatten(evaluator.normalize_dict(answer))
            answer_set = set(answer)
            pred_set = set(pred)

            tp = len(pred_set & answer_set)
            fp = len(pred_set - answer_set)
            fn = len(answer_set - pred_set)

            total_tp += tp
            total_fp += fp
            total_fn += fn

        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0

        accs.append(score)
        f1.append(f1_value)
        recalls.append(recall)
        precisions.append(precision)

    scores = {
        "mean_f1": np.mean(f1),
        "mean_accuracy": np.mean(accs),
        "recall": np.mean(recalls),
        "precisions": np.mean(precisions),
    }
    scores.update({n: 100 * scores[n] for n in scores.keys()})
    return scores


# Load dataset
dataset = load_dataset("katanaml-org/invoices-donut-data-v1", split="test")

# Evaluate models
scores_our = evaluate_model("your_model_name", dataset)
scores_others = evaluate_model("your_model_name_base", dataset)

# Create comparison DataFrame
import pandas as pd

comparison_data = {
    "Metric": ["mean_f1", "mean_accuracy", "recall", "precisions"],
    "Scores_Others": [
        scores_others["mean_f1"],
        scores_others["mean_accuracy"],
        scores_others["recall"],
        scores_others["precisions"],
    ],
    "Scores_Our": [
        scores_our["mean_f1"],
        scores_our["mean_accuracy"],
        scores_our["recall"],
        scores_our["precisions"],
    ],
}

df_comparison = pd.DataFrame(comparison_data)

# Display comparison DataFrame
print(df_comparison)
