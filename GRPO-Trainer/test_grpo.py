#!/usr/bin/env python3
"""
Test script for GRPO trainer to verify basic functionality.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from grpo_trainer import GRPOConfig, GRPOTrainer


def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    try:
        from grpo_trainer import GRPOConfig, GRPOTrainer, BrickDataset
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration creation."""
    print("Testing configuration...")
    try:
        config = GRPOConfig(
            model_name_or_path="AvaLovelace/BrickGPT",
            max_samples=5,  # Very small for testing
            num_epochs=1,
            batch_size=1,
            use_wandb=False,
            output_dir="./test_outputs"
        )
        print("✓ Configuration created successfully")
        print(f"  - Model: {config.model_name_or_path}")
        print(f"  - Max samples: {config.max_samples}")
        print(f"  - Epochs: {config.num_epochs}")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False


def test_trainer_initialization():
    """Test trainer initialization."""
    print("Testing trainer initialization...")
    try:
        config = GRPOConfig(
            model_name_or_path="AvaLovelace/BrickGPT",
            max_samples=2,  # Very small for testing
            num_epochs=1,
            batch_size=1,
            use_wandb=False,
            output_dir="./test_outputs",
            use_gurobi=False  # Disable Gurobi for testing
        )
        
        trainer = GRPOTrainer(config)
        print("✓ Trainer initialized successfully")
        print(f"  - Device: {trainer.device}")
        print(f"  - Dataset size: {len(trainer.train_dataset)}")
        return True
    except Exception as e:
        print(f"✗ Trainer initialization failed: {e}")
        return False


def test_reward_calculation():
    """Test reward calculation with simple brick structure."""
    print("Testing reward calculation...")
    try:
        from brickgpt.data import BrickStructure, Brick
        
        config = GRPOConfig(use_gurobi=False)
        trainer = GRPOTrainer(config)
        
        # Create a simple brick structure
        bricks = BrickStructure([
            Brick(h=2, w=4, x=0, y=0, z=0),
            Brick(h=2, w=4, x=0, y=0, z=1)
        ])
        
        reward = trainer._calculate_reward(bricks)
        print(f"✓ Reward calculation successful: {reward:.4f}")
        return True
    except Exception as e:
        print(f"✗ Reward calculation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running GRPO trainer tests...\n")
    
    tests = [
        test_imports,
        test_config,
        test_trainer_initialization,
        test_reward_calculation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! GRPO trainer is ready to use.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
