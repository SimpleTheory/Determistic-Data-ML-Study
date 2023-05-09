import torch
import torch.nn as nn
import deterministic_data.equations.generate_string as gs



data = gs.generate_dataset(100_000, to_np_array=True)
model = nn.RNN(480, 1, 12, 5)
