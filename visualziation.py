import zarr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load Zarr store
store_path = '/home/wanglab/1_REF_ws/origin_git3_push6DOF/pushZ-master/data/demo_pusht_real/replay_buffer.zarr'
store = zarr.DirectoryStore(store_path)
root = zarr.open(store)

# Load datasets
try:
    left_jaw = root['data/left_jaw'][:]
    right_jaw = root['data/right_jaw'][:]
    timestamps = root['data/timestamp'][:]
except KeyError as e:
    print(f"Error loading data: {e}")
    raise SystemExit(e)

print("Left Jaw shape:", left_jaw.shape)
print("Right Jaw shape:", right_jaw.shape)
print("Timestamps shape:", timestamps.shape)

# Create DataFrame by accessing the first column
df = pd.DataFrame({
    'timestamps': timestamps,
    'left_jaw': left_jaw[:, 0],
    'right_jaw': right_jaw[:, 0]
})

# Plot Left Jaw and Right Jaw over time
plt.figure(figsize=(12, 6))
plt.plot(df['timestamps'], df['left_jaw'], label='Left Jaw')
plt.plot(df['timestamps'], df['right_jaw'], label='Right Jaw')
plt.title('Left and Right Jaw Positions over Time')
plt.xlabel('Time')
plt.ylabel('Jaw Position')
plt.legend()
plt.grid(True)
plt.show()