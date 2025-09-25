import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset, Dataset
from trl import GRPOConfig as TRLGRPOConfig, GRPOTrainer as TRLGRPOTrainer
import wandb
from peft import PeftModel

# Import BrickGPT components
sys.path.append(str(Path(__file__).parent.parent / "src"))
from brickgpt.models import BrickGPT, BrickGPTConfig, create_instruction
from brickgpt.data import BrickStructure, Brick, brick_library
from brickgpt.stability_analysis import stability_score, StabilityConfig


@dataclass
class BrickGRPOConfig:
    # Model configuration
    model_name_or_path: str = "AvaLovelace/BrickGPT"
    base_model_name: str = "meta-llama/Llama-3.2-1B-Instruct"
    world_dim: int = 20
    max_bricks: int = 100
    max_brick_rejections: int = 50
    
    # Dataset parameters
    dataset_name: str = "AvaLovelace/StableText2Brick"
    max_samples: int = 1000
    
    # Stability analysis parameters
    use_gurobi: bool = True
    stability_weight: float = 1.0
    connectivity_weight: float = 0.5
    
    # Training parameters - will be passed to TRLGRPOConfig
    learning_rate: float = 1e-5
    num_train_epochs: int = 10
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    save_steps: int = 500
    logging_steps: int = 50
    
    # GRPO specific parameters
    num_generations: int = 8  # Renamed from group_size to match TRL API
    beta: float = 0.1
    temperature: float = 0.7
    max_completion_length: int = 512
    
    # Output and logging
    output_dir: str = "./grpo_trl_outputs"
    use_wandb: bool = True
    project_name: str = "brickgpt-grpo-trl"
    
    # Output saving parameters
    save_outputs: bool = True
    save_outputs_every_n_calls: int = 5  # Save outputs every N reward function calls
    max_outputs_to_save: int = 3  # Save up to N outputs per call


# Global counter for tracking reward function calls
_reward_call_counter = 0

def brick_reward_function(completions, **kwargs):
    """
    Reward function for GRPO that calculates stability and connectivity scores.
    Compatible with TRL v0.23.0 expected signature.
    
    Args:
        completions: List of generated completion strings
        **kwargs: Additional arguments (prompts, completions_ids, trainer_state, etc.)
    
    Returns:
        List[float]: Reward scores for each completion
    """
    global _reward_call_counter
    _reward_call_counter += 1
    
    # Initialize configuration (could be passed as global or through kwargs)
    config = kwargs.get('config', BrickGRPOConfig())
    
    # Save outputs if enabled
    if config.save_outputs and _reward_call_counter % config.save_outputs_every_n_calls == 0:
        save_model_outputs(completions, config, _reward_call_counter, **kwargs)
    
    stability_config = StabilityConfig(
        world_dimension=(config.world_dim,) * 3,
        print_log=False
    )
    
    def parse_bricks_from_text(text: str) -> BrickStructure:
        """Parse brick structure from generated text."""
        try:
            brick_lines = [line.strip() for line in text.split('\n') if line.strip()]
            bricks = BrickStructure([])
            for line in brick_lines:
                if line and 'x' in line and '(' in line:
                    brick = Brick.from_txt(line)
                    bricks.add_brick(brick)
            return bricks
        except Exception as e:
            logging.warning(f"Failed to parse bricks from text: {e}")
            return BrickStructure([])
    
    def calculate_reward(bricks: BrickStructure) -> float:
        """Calculate reward based on stability and connectivity scores."""
        if len(bricks) == 0:
            return 0.0
        
        try:
            stability_reward = 0.0
            connectivity_reward = 0.0
            
            # Calculate stability score using Gurobi
            if config.use_gurobi and len(bricks) > 1:
                try:
                    stability_scores, _, _, _, _ = stability_score(
                        bricks.to_json(), 
                        brick_library, 
                        stability_config
                    )
                    stability_reward = 1.0 - np.mean(stability_scores)
                except Exception as e:
                    logging.warning(f"Gurobi stability calculation failed: {e}")
                    stability_reward = 0.0
            
            # Calculate connectivity scores
            try:
                connectivity_scores = bricks.connectivity_scores()
                connectivity_reward = 1.0 - np.mean(connectivity_scores)
            except Exception as e:
                logging.warning(f"Connectivity calculation failed: {e}")
                connectivity_reward = 0.0
            
            # Combine rewards
            total_reward = (
                config.stability_weight * stability_reward + 
                config.connectivity_weight * connectivity_reward
            )
            
            return max(0.0, total_reward)  # Ensure non-negative rewards
            
        except Exception as e:
            logging.warning(f"Failed to calculate reward: {e}")
            return 0.0
    
    # Calculate rewards for each completion
    rewards = []
    for completion in completions:
        bricks = parse_bricks_from_text(completion)
        reward = calculate_reward(bricks)
        rewards.append(reward)
    
    return rewards


def save_model_outputs(completions, config, call_counter, **kwargs):
    """
    Save model outputs to text files during training.
    
    Args:
        completions: List of generated completion strings
        config: BrickGRPOConfig instance
        call_counter: Current reward function call counter
        **kwargs: Additional arguments (may contain prompts, trainer_state, etc.)
    """
    try:
        # Create outputs directory
        outputs_dir = os.path.join(config.output_dir, "training_outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get prompts if available
        prompts = kwargs.get('prompts', ['[Prompt not available]'] * len(completions))
        
        # Get trainer state info if available
        trainer_state = kwargs.get('trainer_state', None)
        step_info = f"_step_{trainer_state.global_step}" if trainer_state else ""
        
        # Create filename
        filename = f"outputs_call_{call_counter:04d}{step_info}_{timestamp}.txt"
        filepath = os.path.join(outputs_dir, filename)
        
        # Save outputs
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== Model Outputs - Call {call_counter} ===\n")
            f.write(f"Timestamp: {timestamp}\n")
            if trainer_state:
                f.write(f"Training Step: {trainer_state.global_step}\n")
                f.write(f"Epoch: {trainer_state.epoch}\n")
            f.write(f"Number of completions: {len(completions)}\n")
            f.write("=" * 50 + "\n\n")
            
            # Save up to max_outputs_to_save completions
            num_to_save = min(len(completions), config.max_outputs_to_save)
            for i in range(num_to_save):
                f.write(f"--- Output {i+1}/{num_to_save} ---\n")
                f.write(f"Prompt: {prompts[i] if i < len(prompts) else '[Not available]'}\n")
                f.write(f"Completion:\n{completions[i]}\n")
                f.write("\n" + "-" * 30 + "\n\n")
        
        logging.info(f"Saved {num_to_save} model outputs to {filepath}")
        
    except Exception as e:
        logging.warning(f"Failed to save model outputs: {e}")


def prepare_dataset(config: BrickGRPOConfig) -> Dataset:
    """Prepare the dataset for GRPO training."""
    # Load the original dataset
    original_dataset = load_dataset(config.dataset_name, split="train")
    
    if config.max_samples > 0:
        original_dataset = original_dataset.select(range(min(config.max_samples, len(original_dataset))))
    
    # Convert to the format expected by TRL
    def format_example(example):
        caption = example["captions"][0] if isinstance(example["captions"], list) else example["captions"]
        instruction = create_instruction(caption)
        # TRL expects 'prompt' field for prompts
        return {"prompt": instruction}
    
    formatted_dataset = original_dataset.map(format_example, remove_columns=original_dataset.column_names)
    return formatted_dataset


def setup_model_and_tokenizer(config: BrickGRPOConfig):
    """Setup model and tokenizer with LoRA support."""
    try:
        # First try to load as a regular model
        tokenizer = AutoTokenizer.from_pretrained(config.model_name_or_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            config.model_name_or_path,
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        logging.info(f"Loaded model directly from {config.model_name_or_path}")
        return model, tokenizer
        
    except Exception as e:
        logging.warning(f"Failed to load model directly: {e}")
        logging.info("Trying to load as LoRA adapter...")
        
        try:
            # Load base model
            tokenizer = AutoTokenizer.from_pretrained(config.base_model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            base_model = AutoModelForCausalLM.from_pretrained(
                config.base_model_name,
                dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            # Load LoRA adapter
            model = PeftModel.from_pretrained(base_model, config.model_name_or_path)
            
            logging.info(f"Loaded LoRA adapter from {config.model_name_or_path} on base model {config.base_model_name}")
            return model, tokenizer
            
        except Exception as e2:
            logging.error(f"Failed to load LoRA adapter: {e2}")
            # Fallback to a working model
            logging.info("Falling back to a working model...")
            tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            model = AutoModelForCausalLM.from_pretrained(
                "microsoft/DialoGPT-medium",
                dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            logging.info("Using fallback model: microsoft/DialoGPT-medium")
            return model, tokenizer


def main():
    """Main function to run GRPO training with TRL."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize config
    config = BrickGRPOConfig()
    
    # Setup output directory
    os.makedirs(config.output_dir, exist_ok=True)
    
    # Initialize wandb if enabled
    if config.use_wandb:
        wandb.init(
            project=config.project_name,
            config=config.__dict__,
            name=f"grpo-trl-{config.model_name_or_path.split('/')[-1]}"
        )
    
    # Setup model and tokenizer
    model, tokenizer = setup_model_and_tokenizer(config)
    
    # Prepare dataset
    dataset = prepare_dataset(config)
    
    # Create reward function with config closure
    def reward_func_with_config(completions, **kwargs):
        return brick_reward_function(completions, config=config, **kwargs)
    
    # Configure TRL GRPO training arguments
    training_args = TRLGRPOConfig(
        output_dir=config.output_dir,
        learning_rate=config.learning_rate,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        warmup_steps=config.warmup_steps,
        save_steps=config.save_steps,
        logging_steps=config.logging_steps,
        beta=config.beta,
        gradient_checkpointing=True,
        dataloader_drop_last=True,
        remove_unused_columns=False,
        report_to="wandb" if config.use_wandb else None,
        # GRPO specific parameters
        num_generations=config.num_generations,
        temperature=config.temperature,
        # Additional TRL parameters for better training
        bf16=torch.cuda.is_available(),  # Use bf16 if CUDA available
        tf32=torch.cuda.is_available(),  # Use tf32 if CUDA available
        seed=42,
    )
    
    # Initialize GRPO trainer
    trainer = TRLGRPOTrainer(
        model=model,
        reward_funcs=reward_func_with_config,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    
    # Start training
    logging.info("Starting GRPO training with TRL...")
    trainer.train()
    
    # Save final model
    trainer.save_model(os.path.join(config.output_dir, "final_model"))
    tokenizer.save_pretrained(os.path.join(config.output_dir, "final_model"))
    
    logging.info("Training completed!")
    
    if config.use_wandb:
        wandb.finish()


if __name__ == "__main__":
    main()