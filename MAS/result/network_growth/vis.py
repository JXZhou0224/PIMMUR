import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
save_file = "result_degree_cumulative_distribution.csv"
##########
# file = "original.csv"
# data = pd.read_csv(file)
# ls = data['Friends'].tolist()
##########
file = "friendship_log.json"
data = json.load(open(file, "r"))
ls = [data[d] for d in data]
##########
max_val = len(data)
# Convert to numpy array for easier manipulation
ls = np.array(ls)

# Get unique values and their cumulative counts
x_temp = np.arange(0, ls.max() + 1)
y_temp = np.array([np.sum(ls <= xi) for xi in x_temp])

# Remove duplicates in y values (keep only where y changes)
# mask = np.concatenate(([True], np.diff(y_temp) > 0))
# x = x_temp[mask]
# y = y_temp[mask]

y = y_temp
x = x_temp

y = max_val - y

y = y / max_val

data = pd.DataFrame({"x": x, "y": y})
data.to_csv(save_file, index=False)

alpha = 1.2
ref_x = np.arange(3,x.max())
ref_y = -1.5/((ref_x)**alpha) + 1
ref_y = 1 - ref_y

# Create the plot
plt.figure(figsize=(10, 6))
plt.scatter(x, y, marker='o', s=10, color='blue', alpha=0.6)
plt.plot(ref_x, ref_y, linestyle='--', color='red', label=f'Reference line: y ~ x^{alpha}')

# Set both axes to log10 scale
plt.xscale('log')
plt.yscale('log')

# Add labels and title
plt.xlabel('x (log10 scale)')
plt.ylabel('Number of integers ≤ x (log10 scale)')
plt.title('Cumulative Distribution (Log-Log Scale)')
plt.grid(True, alpha=0.3)

# Add some styling
plt.tight_layout()

# Show the plot
plt.show()