import numpy as np
import random

class Layer:

    def __init__(self, num_in, num_out):
        self.num_in = num_in
        self.num_out = num_out
        self.weights = []
        for _ in range(num_out):
            self.weights.append(np.random.uniform(-1.0, 1.0, num_in))
        self.biases = np.random.uniform(-1.0, 1.0, num_out)

    def process(self, inputs):
        inputs = np.array(inputs)
        assert inputs.size == self.num_in
        outputs = np.zeros(self.num_out)
        for i in range(self.num_out):
            weights = self.weights[i]
            bias = self.biases[i]
            z = np.dot(weights, inputs) + bias
            outputs[i] = np.tanh(z)
        return outputs
    
    def copy(self):
        cpy = Layer(self.num_in, self.num_out)
        cpy.weights.clear()
        for i in range(self.num_out):
            cpy.weights.append(np.copy(self.weights[i]))
        cpy.biases = np.copy(self.biases)
        return cpy

    def mutate(self, strength):
        for weights in self.weights:
            if random.random() > strength:
                continue
            for i in range(len(weights)):
                if random.random() > strength:
                    continue
                weights[i] += np.random.uniform(-strength, strength)
        for i in range(len(self.biases)):
            self.biases[i] += np.random.uniform(-strength, strength)

class Brain:

    def __init__(self):
        self.layers = []

    def add_layer(self, num_in, num_out):
        self.layers.append(Layer(num_in, num_out))

    def process(self, inputs):
        for layer in self.layers:
            inputs = layer.process(inputs)
        return inputs

    def basic(num_in, num_out, num_hidden):
        brain = Brain()
        brain.add_layer(num_in, num_hidden)
        brain.add_layer(num_hidden, num_out)
        return brain
    
    def copy(self):
        cpy = Brain()
        for layer in self.layers:
            cpy.layers.append(layer.copy())
        return cpy
    
    def mutate(self, strength):
        for layer in self.layers:
            layer.mutate(strength)

    def new_inputs(self):
        return np.zeros(self.layers[0].num_in)

