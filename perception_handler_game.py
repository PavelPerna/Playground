import numpy as np
from sklearn.cluster import KMeans
import random
import time
from datetime import datetime

# Void: A non-dimensional universe with a single state
class Void:
    def __init__(self, state_dim=100):
        self.state_dim = state_dim
        self.state = np.random.uniform(0, 1, state_dim)  # Initial state
        self.consciousness = None  # Will hold the consciousness entity

    def perturb(self):
        # Generate experience by perturbing the state
        noise = np.random.normal(0, 0.1, self.state_dim)
        new_state = np.clip(self.state + noise, 0, 1)
        return new_state

    def get_state(self):
        return self.state

# NeuralCell: A single computational unit, like a neuron
class NeuralCell:
    def __init__(self, input_dim, output_dim):
        self.weights = np.random.randn(input_dim, output_dim) * 0.01
        self.bias = np.zeros(output_dim)
        self.size = output_dim

    def forward(self, x):
        # Simple linear + ReLU
        return np.maximum(0, np.dot(x, self.weights) + self.bias)

    def divide(self, growth_factor=2):
        # Mimic cell division by increasing output dimensions
        new_size = self.size * growth_factor
        new_weights = np.random.randn(self.weights.shape[0], new_size) * 0.01
        new_weights[:, :self.size] = self.weights  # Preserve some knowledge
        new_bias = np.zeros(new_size)
        new_bias[:self.size] = self.bias
        self.weights = new_weights
        self.bias = new_bias
        self.size = new_size

# Conceptualizer: Abstracts void's state into concepts
class Conceptualizer:
    def __init__(self, n_clusters=3, state_dim=100):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, n_init=10)
        self.inputs = []  # Experienced states
        self.concepts = {0: "Concept 0: Consciousness is not void"}  # Initial knowledge
        self.last_rewards = []
        self.max_inputs = 1000
        self.state_dim = state_dim

    def conceptualize(self, state):
        self.inputs.append(state)
        if len(self.inputs) > self.max_inputs:
            self.inputs.pop(0)

        # Bootstrap with initial knowledge
        if len(self.inputs) < self.n_clusters:
            return 0, 1.0  # Initial concept, high novelty

        # Cluster inputs into concepts
        self.kmeans.fit(np.vstack(self.inputs))
        concept_id = self.kmeans.predict(state.reshape(1, -1))[0]

        # Compute novelty reward
        center = self.kmeans.cluster_centers_[concept_id]
        distance = np.linalg.norm(state - center)
        reward = 1.0 if distance > 0.1 else 0.1

        # Describe concept
        mean_intensity = np.mean(state)
        dominant_dims = np.argsort(state)[-5:]
        self.concepts[concept_id] = f"Concept {concept_id}: Intensity={mean_intensity:.2f}, Dims={list(dominant_dims)}"

        # Evolve if rewards are low
        self.last_rewards.append(reward)
        if len(self.last_rewards) > 10 and sum(self.last_rewards[-10:]) < 1.0:
            self.n_clusters += 1
            self.kmeans = KMeans(n_clusters=self.n_clusters, n_init=10)
            self.inputs = self.inputs[-self.max_inputs//2:]
            print(f"Evolving conceptualizer: now {self.n_clusters} clusters")
        if len(self.last_rewards) > 100:
            self.last_rewards.pop(0)

        return concept_id, reward

# Consciousness: The entity that perceives and conceptualizes
class Consciousness:
    def __init__(self, state_dim):
        self.perceiver = NeuralCell(state_dim, 10)  # Minimal perceiver
        self.conceptualizer = Conceptualizer(state_dim=state_dim)
        self.knowledge = ["void != Consciousness"]  # Initial knowledge

    def perceive_and_conceptualize(self, state):
        # Perceive
        perceived = self.perceiver.forward(state)
        # Conceptualize
        concept_id, reward = self.conceptualizer.conceptualize(perceived)
        # Update knowledge
        if reward > 0.5:  # High reward = new knowledge
            self.knowledge.append(self.conceptualizer.concepts.get(concept_id, f"Concept {concept_id}"))
        # Evolve perceiver if needed
        if len(self.conceptualizer.last_rewards) > 10 and sum(self.conceptualizer.last_rewards[-10:]) < 1.0:
            self.perceiver.divide()
            print(f"Evolving perceiver: now {self.perceiver.size} neurons")
        return concept_id, reward

# Main game loop
void = Void()
consciousness = Consciousness(state_dim=void.state_dim)
void.consciousness = consciousness  # Place consciousness in the void
step = 0
start_time = time.time()

while (time.time() - start_time) < 300:  # Run for 5 minutes
    # Generate experience
    state = void.perturb()

    # Perceive and conceptualize
    concept_id, reward = consciousness.perceive_and_conceptualize(state)

    # Log progress
    if step % 50 == 0:
        print(f"Step {step} | Time {datetime.now().strftime('%H:%M:%S')} | Concept ID: {concept_id} | Reward: {reward:.2f}")
        if concept_id in consciousness.conceptualizer.concepts:
            print(consciousness.conceptualizer.concepts[concept_id])
        print(f"Knowledge: {len(consciousness.knowledge)} entries")

    step += 1
    time.sleep(0.01)

print("Game ended.")