import torch
import torch.nn as nn
import wandb

model = nn.Linear(10, 2)
torch.save(model.state_dict(), "model.th")

wandb.init(project="test-save")
wandb.save("*.th")
wandb.finish()
