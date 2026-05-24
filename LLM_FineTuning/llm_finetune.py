"""
LLM Fine-Tuning Pipeline — based on "I Spent 3 Months Learning LLM Fine-Tuning"
Covers: Tokenization, SFT, LoRA, overfitting detection, catastrophic forgetting prevention.
Example task: Medical Q&A bot using a small causal LM (distilgpt2 by default).

Requirements:
    pip install transformers datasets peft accelerate torch scikit-learn
"""

import os
import json
import math
import random
import warnings
import numpy as np
import torch
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    get_linear_schedule_with_warmup,
)
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from datasets import Dataset as HFDataset

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# 1. TOKENIZATION DEMO  (Article Part 2, Step 1)
# ─────────────────────────────────────────────────────────────────────────────

def demo_tokenization(model_name: str = "distilgpt2") -> None:
    """Show how text becomes token IDs — and why token count matters for cost."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    examples = [
        "Hello world",
        "Antidisestablishmentarianism",
        "The capital of France is",
        "What are the symptoms of hypertension?",
    ]

    print("=" * 60)
    print("TOKENIZATION DEMO")
    print("=" * 60)
    for text in examples:
        ids = tokenizer.encode(text)
        tokens = tokenizer.convert_ids_to_tokens(ids)
        print(f"\nText   : {text!r}")
        print(f"Token IDs : {ids}")
        print(f"Tokens    : {tokens}")
        print(f"Count     : {len(ids)}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# 2. DATASET CONSTRUCTION
#    70% specialty (medical) + 30% general  →  prevents catastrophic forgetting
# ─────────────────────────────────────────────────────────────────────────────

MEDICAL_QA: List[Dict[str, str]] = [
    {
        "question": "What are the common symptoms of hypertension?",
        "answer": (
            "Common symptoms of hypertension (high blood pressure) include "
            "headaches, shortness of breath, nosebleeds, and in severe cases "
            "chest pain or visual changes. Many patients are asymptomatic."
        ),
    },
    {
        "question": "What is the difference between Type 1 and Type 2 diabetes?",
        "answer": (
            "Type 1 diabetes is an autoimmune condition where the pancreas "
            "produces no insulin. Type 2 is a metabolic disorder where cells "
            "become insulin resistant. Type 1 requires insulin therapy; "
            "Type 2 is often managed with lifestyle changes and oral medication."
        ),
    },
    {
        "question": "What does a complete blood count (CBC) measure?",
        "answer": (
            "A CBC measures red blood cells (oxygen transport), white blood cells "
            "(immune response), haemoglobin, haematocrit, and platelets "
            "(clotting). It helps diagnose anaemia, infections, and blood disorders."
        ),
    },
    {
        "question": "What is myocardial infarction?",
        "answer": (
            "Myocardial infarction (heart attack) occurs when blood flow to part "
            "of the heart muscle is blocked, usually by a clot in a coronary "
            "artery. Tissue dies without oxygen. Symptoms: chest pain, "
            "sweating, nausea, arm/jaw pain."
        ),
    },
    {
        "question": "How does penicillin work?",
        "answer": (
            "Penicillin inhibits bacterial cell-wall synthesis by binding to "
            "penicillin-binding proteins, preventing cross-linking of "
            "peptidoglycan chains. This weakens the cell wall, causing lysis "
            "in actively dividing bacteria."
        ),
    },
    {
        "question": "What is BMI and what are the categories?",
        "answer": (
            "BMI (Body Mass Index) = weight(kg) / height(m)². Categories: "
            "Underweight <18.5, Normal 18.5–24.9, Overweight 25–29.9, "
            "Obese ≥30. It is a screening tool, not a direct measure of body fat."
        ),
    },
    {
        "question": "What are the stages of wound healing?",
        "answer": (
            "Wound healing has four stages: (1) Haemostasis — clot formation; "
            "(2) Inflammation — immune cells clean debris; "
            "(3) Proliferation — new tissue and collagen deposited; "
            "(4) Remodelling — collagen reorganises, scar matures over months."
        ),
    },
]

GENERAL_QA: List[Dict[str, str]] = [
    {"question": "What is 2 + 2?", "answer": "2 + 2 equals 4."},
    {"question": "What is the capital of France?", "answer": "The capital of France is Paris."},
    {
        "question": "Write a short Python function to reverse a string.",
        "answer": "def reverse_string(s: str) -> str:\n    return s[::-1]",
    },
    {
        "question": "Explain Newton's first law of motion.",
        "answer": (
            "Newton's first law states that an object at rest stays at rest, "
            "and an object in motion stays in motion at constant velocity, "
            "unless acted upon by a net external force."
        ),
    },
    {
        "question": "What is the speed of light?",
        "answer": "The speed of light in a vacuum is approximately 299,792,458 metres per second (≈3×10⁸ m/s).",
    },
]


def build_dataset(
    medical: List[Dict],
    general: List[Dict],
    tokenizer,
    max_length: int = 256,
    medical_ratio: float = 0.70,
) -> HFDataset:
    """
    Mix specialty and general data at medical_ratio to prevent catastrophic forgetting.
    Format: <|question|> ... <|answer|> ... <|endoftext|>
    """
    random.seed(42)
    all_samples = []

    # Determine counts that honour the ratio
    n_medical = len(medical)
    n_general = max(1, round(n_medical * (1 - medical_ratio) / medical_ratio))
    general_sample = random.choices(general, k=min(n_general, len(general)))

    for item in medical + general_sample:
        text = (
            f"<|question|>{item['question']}<|answer|>{item['answer']}<|endoftext|>"
        )
        all_samples.append({"text": text})

    random.shuffle(all_samples)

    def tokenize(batch):
        encoded = tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )
        encoded["labels"] = encoded["input_ids"].copy()
        return encoded

    hf_dataset = HFDataset.from_list(all_samples)
    hf_dataset = hf_dataset.map(tokenize, batched=True, remove_columns=["text"])
    hf_dataset.set_format(type="torch")
    return hf_dataset


# ─────────────────────────────────────────────────────────────────────────────
# 3. LoRA CONFIGURATION  (Article Part 5 — "paint and handles" analogy)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LoRASettings:
    r: int = 8                     # rank — lower = fewer trainable params
    lora_alpha: int = 16           # scaling factor
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])  # GPT-2 attention proj
    task_type: str = "CAUSAL_LM"


def apply_lora(model, settings: LoRASettings):
    """Wrap a causal LM with LoRA adapters — trains ~1% of parameters."""
    config = LoraConfig(
        r=settings.r,
        lora_alpha=settings.lora_alpha,
        lora_dropout=settings.lora_dropout,
        target_modules=settings.target_modules,
        task_type=TaskType.CAUSAL_LM,
        bias="none",
    )
    peft_model = get_peft_model(model, config)
    trainable, total = peft_model.get_nb_trainable_parameters()
    print(f"LoRA applied — trainable params: {trainable:,} / {total:,} "
          f"({100 * trainable / total:.2f}%)")
    return peft_model


# ─────────────────────────────────────────────────────────────────────────────
# 4. OVERFITTING MONITOR  (Article Part 4 — train vs validation loss)
# ─────────────────────────────────────────────────────────────────────────────

class OverfitMonitor:
    """
    Tracks train/eval loss ratio.
    Flags overfitting when eval loss diverges from train loss.
    """

    def __init__(self, threshold: float = 1.5):
        self.threshold = threshold  # ratio eval_loss / train_loss that triggers warning
        self.history: List[Dict[str, float]] = []

    def record(self, epoch: int, train_loss: float, eval_loss: float) -> None:
        ratio = eval_loss / (train_loss + 1e-9)
        status = "OVERFIT" if ratio > self.threshold else "OK"
        self.history.append(
            {"epoch": epoch, "train": train_loss, "eval": eval_loss,
             "ratio": ratio, "status": status}
        )
        print(
            f"  Epoch {epoch:2d} | train_loss={train_loss:.4f} | "
            f"eval_loss={eval_loss:.4f} | ratio={ratio:.2f} | {status}"
        )

    def summary(self) -> None:
        print("\nOverfitting summary:")
        overfit_epochs = [h for h in self.history if h["status"] == "OVERFIT"]
        if overfit_epochs:
            print(f"  ⚠  Overfitting detected at epochs: "
                  f"{[h['epoch'] for h in overfit_epochs]}")
            print("  Suggestion: reduce epochs, add more data, or lower learning rate.")
        else:
            print("  No overfitting detected — train and eval loss stayed close.")


# ─────────────────────────────────────────────────────────────────────────────
# 5. TRAINING — SFT with LoRA
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TrainConfig:
    model_name: str = "distilgpt2"
    output_dir: str = "./llm_finetuned"
    num_epochs: int = 3
    batch_size: int = 2
    learning_rate: float = 2e-4
    max_length: int = 256
    eval_split: float = 0.2
    seed: int = 42


def train(cfg: TrainConfig) -> None:
    print("=" * 60)
    print("LLM FINE-TUNING PIPELINE")
    print("=" * 60)

    # ── Tokenizer ───────────────────────────────────────────────────────────
    print("\n[1/5] Loading tokenizer & model …")
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    tokenizer.pad_token = tokenizer.eos_token  # GPT-style models have no pad token

    # ── Dataset ─────────────────────────────────────────────────────────────
    print("[2/5] Building dataset (70% medical + 30% general) …")
    full_dataset = build_dataset(MEDICAL_QA, GENERAL_QA, tokenizer, cfg.max_length)
    split = full_dataset.train_test_split(test_size=cfg.eval_split, seed=cfg.seed)
    train_dataset, eval_dataset = split["train"], split["test"]
    print(f"      Train: {len(train_dataset)} samples | Eval: {len(eval_dataset)} samples")

    # ── Model + LoRA ─────────────────────────────────────────────────────────
    print("[3/5] Loading base model and applying LoRA adapters …")
    base_model = AutoModelForCausalLM.from_pretrained(cfg.model_name)
    model = apply_lora(base_model, LoRASettings())

    # ── Training args ────────────────────────────────────────────────────────
    print("[4/5] Training …\n")
    monitor = OverfitMonitor(threshold=1.5)

    training_args = TrainingArguments(
        output_dir=cfg.output_dir,
        num_train_epochs=cfg.num_epochs,
        per_device_train_batch_size=cfg.batch_size,
        per_device_eval_batch_size=cfg.batch_size,
        learning_rate=cfg.learning_rate,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        seed=cfg.seed,
        report_to="none",
        fp16=torch.cuda.is_available(),
        no_cuda=not torch.cuda.is_available(),
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    class LoggingTrainer(Trainer):
        """Subclass that feeds each epoch's losses to the overfit monitor."""

        def __init__(self, *args, monitor: OverfitMonitor, **kwargs):
            super().__init__(*args, **kwargs)
            self._monitor = monitor
            self._epoch_logs: List[Dict] = []

        def log(self, logs: Dict, start_time=None) -> None:
            super().log(logs)
            if "loss" in logs and "eval_loss" in logs:
                epoch = int(logs.get("epoch", len(self._epoch_logs) + 1))
                self._monitor.record(epoch, logs["loss"], logs["eval_loss"])

    trainer = LoggingTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        monitor=monitor,
    )

    trainer.train()

    # ── Save ─────────────────────────────────────────────────────────────────
    print(f"\n[5/5] Saving model to {cfg.output_dir} …")
    model.save_pretrained(cfg.output_dir)
    tokenizer.save_pretrained(cfg.output_dir)

    monitor.summary()
    print("\nTraining complete.")


# ─────────────────────────────────────────────────────────────────────────────
# 6. INFERENCE
# ─────────────────────────────────────────────────────────────────────────────

def load_and_infer(
    model_dir: str,
    base_model_name: str,
    questions: List[str],
    max_new_tokens: int = 120,
) -> None:
    print("\n" + "=" * 60)
    print("INFERENCE WITH FINE-TUNED MODEL")
    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    tokenizer.pad_token = tokenizer.eos_token

    base = AutoModelForCausalLM.from_pretrained(base_model_name)
    model = PeftModel.from_pretrained(base, model_dir)
    model.eval()

    for question in questions:
        prompt = f"<|question|>{question}<|answer|>"
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        full_text = tokenizer.decode(output_ids[0], skip_special_tokens=False)
        # Extract only the answer portion
        answer_start = full_text.find("<|answer|>") + len("<|answer|>")
        answer = full_text[answer_start:].split("<|endoftext|>")[0].strip()

        print(f"\nQ: {question}")
        print(f"A: {answer or '[model produced no answer — try more epochs]'}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. DECISION FRAMEWORK (Article Part 6)
# ─────────────────────────────────────────────────────────────────────────────

def print_decision_framework() -> None:
    """Interactive decision guide matching the article's flowchart."""
    print("\n" + "=" * 60)
    print("FINE-TUNING DECISION FRAMEWORK")
    print("=" * 60)

    framework = {
        "Step 1 — Do you have a pre-trained base model?": {
            "No": "→ You need pre-training (enterprise-only, millions $)",
            "Yes": "→ Continue to Step 2",
        },
        "Step 2 — Does your task have right/wrong answers?": {
            "Yes (code / math)": "→ Use RLVR (automated correctness checks)",
            "No": "→ Continue to Step 3",
        },
        "Step 3 — What is your primary goal?": {
            "Learn domain knowledge": "→ CPT (Continued Pre-Training) + SFT",
            "Adapt behaviour / style": "→ SFT",
            "Align with human preferences": "→ SFT + DPO or RLHF",
        },
        "Step 4 — What is your compute budget?": {
            "Unlimited": "→ Full fine-tuning",
            "Consumer GPU (≤24GB VRAM)": "→ LoRA / QLoRA (this script)",
            "Very limited / no GPU": "→ Prompting or rent a cloud GPU",
        },
    }

    for step, options in framework.items():
        print(f"\n{step}")
        for condition, recommendation in options.items():
            print(f"  [{condition}]  {recommendation}")

    print(
        "\nThis script implements: SFT + LoRA  (cheapest, most versatile starting point)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cfg = TrainConfig()

    # 1. Show the decision framework
    print_decision_framework()

    # 2. Tokenization demo
    demo_tokenization(cfg.model_name)

    # 3. Train
    train(cfg)

    # 4. Inference — test both medical and general questions
    test_questions = [
        "What are the common symptoms of hypertension?",   # specialty
        "What is 2 + 2?",                                  # general (forgetting test)
        "What is the capital of France?",                  # general (forgetting test)
        "How does penicillin work?",                       # specialty
    ]
    load_and_infer(cfg.output_dir, cfg.model_name, test_questions)
