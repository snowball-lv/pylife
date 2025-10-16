import numpy as np
import random
import json

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

    def to_dict(self):
        obj = {}
        obj["inputs"] = self.num_in
        obj["outputs"] = self.num_out
        obj["weights"] = []
        for weights in self.weights:
            obj["weights"].append(list(weights))
        obj["biases"] = list(self.biases)
        return obj
    
    def from_dict(layer_dict):
        layer = Layer(layer_dict["inputs"], layer_dict["outputs"])
        layer.weights.clear()
        for weights_list in layer_dict["weights"]:
            layer.weights.append(np.array(weights_list))
        layer.biases = np.array(layer_dict["biases"])
        return layer

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

    def to_dict(self):
        obj = {}
        obj["layers"] = []
        for layer in self.layers:
            obj["layers"].append(layer.to_dict())
        return obj

    def from_dict(brain_dict):
        brain = Brain()
        for layer_dict in brain_dict["layers"]:
            brain.layers.append(Layer.from_dict(layer_dict))
        return brain

    def dump(self, path):
        with open(path, "w") as file:
            json.dump(self.to_dict(), file, indent = 4)

    def load(path):
        with open(path) as file:
            return Brain.from_dict(json.load(file))
        return None

