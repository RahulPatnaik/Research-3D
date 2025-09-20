#!/usr/bin/env python3
"""
Example usage of the GRPO trainer for BrickGPT.

This script demonstrates how to:
1. Configure the GRPO trainer
2. Run training with custom parameters
3. Load and resume from checkpoints
4. Evaluate the trained model
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import BrickGPT modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from grpo_trainer import GRPOConfig, GRPOTrainer


def main():
    """Main example function."""
    
    # Configuration for a small-scale training run
    config = GRPOConfig(
        # Model settings
        model_name_or_path="AvaLovelace/BrickGPT",
        world_dim=10,  # Smaller world for faster training
        max_bricks=20,  # Fewer bricks for faster generation
        
        # GRPO settings
        group_size=4,  # Smaller groups for faster training
        learning_rate=5e-6,  # Conservative learning rate
        beta=0.1,  # KL penalty
        clip_ratio=0.2,  # PPO clipping
        
        # Training settings
        num_epochs=3,  # Few epochs for example
        batch_size=2,  # Small batch size
        gradient_accumulation_steps=2,
        warmup_steps=50,
        save_steps=100,
        logging_steps=10,
        
        # Dataset settings
        max_samples=50,  # Small dataset for example
        
        # Stability analysis
        use_gurobi=False,  # Use connectivity analysis instead for simplicity
        stability_weight=1.0,
        
        # Output settings
        output_dir="./example_outputs",
        use_wandb=False,  # Disable wandb for example
    )
    
    print("Starting GRPO training example...")
    print(f"Configuration: {config}")
    
    # Initialize trainer
    trainer = GRPOTrainer(config)
    
    # Train the model
    try:
        trainer.train()
        print("Training completed successfully!")
        
        # Example of loading a checkpoint
        checkpoint_path = os.path.join(config.output_dir, "checkpoint-100")
        if os.path.exists(checkpoint_path):
            print(f"Loading checkpoint from {checkpoint_path}")
            trainer.load_checkpoint(checkpoint_path)
            print("Checkpoint loaded successfully!")
        
    except Exception as e:
        print(f"Training failed with error: {e}")
        return 1
    
    return 0


def demonstrate_custom_reward():
    """Demonstrate how to use custom reward functions."""
    
    class CustomGRPOTrainer(GRPOTrainer):
        """Custom trainer with modified reward function."""
        
        def _calculate_reward(self, bricks):
            """Custom reward function that emphasizes height."""
            if len(bricks) == 0:
                return 0.0
            
            # Base reward from parent class
            base_reward = super()._calculate_reward(bricks)
            
            # Add height bonus
            max_height = max((brick.z for brick in bricks), default=0)
            height_bonus = min(max_height / 10.0, 1.0) * 0.5
            
            return base_reward + height_bonus
    
    # Use custom trainer
    config = GRPOConfig(
        model_name_or_path="AvaLovelace/BrickGPT",
        max_samples=10,
        num_epochs=1,
        output_dir="./custom_reward_outputs",
        use_wandb=False
    )
    
    trainer = CustomGRPOTrainer(config)
    print("Running custom reward trainer...")
    trainer.train()


def demonstrate_evaluation():
    """Demonstrate how to evaluate the trained model."""
    
    config = GRPOConfig(
        model_name_or_path="AvaLovelace/BrickGPT",
        output_dir="./example_outputs",
        use_wandb=False
    )
    
    trainer = GRPOTrainer(config)
    
    # Load the best checkpoint
    checkpoint_path = os.path.join(config.output_dir, "checkpoint-100")
    if os.path.exists(checkpoint_path):
        trainer.load_checkpoint(checkpoint_path)
    
    # Generate some examples
    test_captions = [
        "a simple table",
        "a small house",
        "a basic chair"
    ]
    
    print("Generating examples with trained model...")
    for caption in test_captions:
        try:
            result = trainer.brickgpt(caption)
            bricks = result["bricks"]
            reward = trainer._calculate_reward(bricks)
            
            print(f"\nCaption: {caption}")
            print(f"Generated {len(bricks)} bricks")
            print(f"Reward: {reward:.4f}")
            print("Bricks:")
            print(bricks.to_txt())
            
        except Exception as e:
            print(f"Failed to generate for '{caption}': {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GRPO Trainer Example")
    parser.add_argument("--mode", choices=["train", "custom_reward", "evaluate"], 
                       default="train", help="Mode to run")
    
    args = parser.parse_args()
    
    if args.mode == "train":
        exit(main())
    elif args.mode == "custom_reward":
        demonstrate_custom_reward()
    elif args.mode == "evaluate":
        demonstrate_evaluation()
