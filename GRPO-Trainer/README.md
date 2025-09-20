# GRPO Training for BrickGPT

This directory contains a Group Relative Policy Optimization (GRPO) training script for fine-tuning BrickGPT models using reinforcement learning with stability-based rewards.

## Overview

The GRPO trainer implements a novel approach to training language models for brick structure generation by:

1. **Group-based Advantage Estimation**: Uses groups of sequences to compute relative advantages, eliminating the need for value functions
2. **Stability-based Rewards**: Uses Gurobi optimization to calculate physical stability scores as rewards
3. **Two-step Action Space**: Implements a successive action space for brick placement:
   - Step 1: Choose a pivot brick from the current structure
   - Step 2: Choose an offset (dx, dy, dz) from the pivot brick
4. **Physics-informed Training**: Integrates real physics simulation through Gurobi optimization

## Key Features

- **Group Relative Policy Optimization**: More efficient than PPO for language model training
- **Stability Analysis**: Uses Gurobi solver for accurate physical stability assessment
- **Modular Design**: Easy to customize reward functions and training parameters
- **Comprehensive Logging**: Integration with Weights & Biases for experiment tracking
- **Checkpointing**: Automatic model saving and resuming capabilities

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have a valid Gurobi license for stability analysis (optional, falls back to connectivity analysis)

## Usage

### Basic Training

```python
from grpo_trainer import GRPOConfig, GRPOTrainer

# Create configuration
config = GRPOConfig(
    model_name_or_path="AvaLovelace/BrickGPT",
    num_epochs=10,
    batch_size=4,
    group_size=8,
    learning_rate=1e-5,
    use_gurobi=True
)

# Initialize trainer
trainer = GRPOTrainer(config)

# Start training
trainer.train()
```

### Command Line Usage

```bash
python grpo_trainer.py
```

### Configuration Options

The `GRPOConfig` class provides extensive customization options:

#### Model Configuration
- `model_name_or_path`: Hugging Face model identifier
- `world_dim`: Dimension of the 3D world (default: 20)
- `max_bricks`: Maximum number of bricks per structure (default: 100)
- `max_brick_rejections`: Maximum rejection sampling attempts (default: 50)

#### GRPO Parameters
- `group_size`: Number of sequences per group for advantage estimation (default: 8)
- `learning_rate`: Learning rate for optimization (default: 1e-5)
- `beta`: KL penalty coefficient (default: 0.1)
- `gamma`: Discount factor (default: 0.99)
- `clip_ratio`: PPO clipping ratio (default: 0.2)

#### Training Parameters
- `num_epochs`: Number of training epochs (default: 10)
- `batch_size`: Batch size for training (default: 4)
- `gradient_accumulation_steps`: Gradient accumulation steps (default: 4)
- `warmup_steps`: Learning rate warmup steps (default: 100)
- `save_steps`: Steps between checkpoint saves (default: 500)
- `logging_steps`: Steps between logging (default: 50)

#### Stability Analysis
- `use_gurobi`: Use Gurobi for stability analysis (default: True)
- `stability_weight`: Weight for stability reward (default: 1.0)
- `connectivity_weight`: Weight for connectivity reward (default: 0.5)

#### Action Space
- `max_offset_distance`: Maximum offset from pivot brick (default: 5)
- `num_brick_types`: Number of allowed brick dimensions (default: 14)

## Architecture

### GRPO Algorithm

The implementation follows the Group Relative Policy Optimization algorithm:

1. **Group Generation**: Generate multiple sequences for each caption
2. **Advantage Computation**: Compute group-relative advantages within caption groups
3. **Policy Update**: Update policy using GRPO loss with KL regularization
4. **Reward Calculation**: Use stability scores from Gurobi optimization

### Reward Function

The reward function combines multiple factors:

```python
total_reward = (
    stability_weight * stability_reward +  # Physical stability
    length_bonus +                        # Encourages longer structures
    quality_bonus                         # Penalizes collisions/out-of-bounds
)
```

### Two-step Action Space

1. **Pivot Selection**: Choose a brick from the current structure as reference
2. **Offset Selection**: Choose (dx, dy, dz) offset from the pivot brick
3. **Brick Placement**: Place new brick at pivot + offset position

## Monitoring and Logging

### Weights & Biases Integration

The trainer automatically logs:
- Training loss and reward curves
- Learning rate schedules
- Model performance metrics
- Stability score distributions

### Checkpointing

- Automatic checkpointing every `save_steps`
- Saves model, tokenizer, and training state
- Supports resuming from checkpoints

## Advanced Usage

### Custom Reward Functions

You can customize the reward function by modifying the `_calculate_reward` method:

```python
def _calculate_reward(self, bricks: BrickStructure) -> float:
    # Your custom reward logic here
    return custom_reward
```

### Custom Action Spaces

Modify the `_setup_action_space` method to implement different action spaces:

```python
def _setup_action_space(self):
    # Your custom action space setup
    pass
```

### Stability Analysis Configuration

Customize stability analysis parameters:

```python
self.stability_config = StabilityConfig(
    world_dimension=(config.world_dim,) * 3,
    g=9.8,  # Gravity
    T=100,  # Tension threshold
    print_log=False
)
```

## Troubleshooting

### Common Issues

1. **Gurobi License**: Ensure you have a valid Gurobi license for stability analysis
2. **Memory Issues**: Reduce batch size or group size for large models
3. **CUDA Out of Memory**: Use gradient accumulation or reduce sequence length

### Performance Tips

1. Use mixed precision training for faster training
2. Enable gradient checkpointing for memory efficiency
3. Use multiple GPUs with DataParallel for larger models

## Citation

If you use this GRPO trainer in your research, please cite:

```bibtex
@misc{brickgpt_grpo,
  title={Group Relative Policy Optimization for Brick Structure Generation},
  author={Your Name},
  year={2024},
  url={https://github.com/your-repo/brickgpt}
}
```

## License

This project is licensed under the same terms as the main BrickGPT project.
