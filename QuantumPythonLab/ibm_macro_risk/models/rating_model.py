import numpy as np

# Rating states
ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "Default"]

# Transition probability matrix (example)
transition_matrix = np.array([
    [0.90, 0.08, 0.01, 0.00, 0.00, 0.00, 0.01],
    [0.02, 0.90, 0.06, 0.01, 0.00, 0.00, 0.01],
    [0.00, 0.03, 0.88, 0.06, 0.01, 0.00, 0.02],
    [0.00, 0.00, 0.05, 0.85, 0.05, 0.02, 0.03],
    [0.00, 0.00, 0.01, 0.05, 0.80, 0.10, 0.04],
    [0.00, 0.00, 0.00, 0.02, 0.08, 0.75, 0.15],
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00]
])

def simulate_rating(initial_state=2, years=5):

    state = initial_state
    history = [ratings[state]]

    for _ in range(years):
        state = np.random.choice(len(ratings), p=transition_matrix[state])
        history.append(ratings[state])

    return history


if __name__ == "__main__":
    result = simulate_rating(initial_state=2, years=5)
    print("Rating Path:", result)
