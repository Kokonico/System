"""sentience ring."""

# how this works
# 1. several AI models are given the same problem
# 2. each AI model likes to solve problems in a different way
# 3. once all AI models have responded, a "harmonizer" AI model is used to combine the responses into a single response
# 4. the combined response is then sent to a "step divider" AI model, which divides the response into steps
import ollama


class RingModel:
    """A single AI model in the sentience ring."""
    def __init__(self, prompt):
        self.model = ollama.Client(host="http://localhost:11434")
        self.prompt = f"You are a RingModel AI, you receive a problem and your goal is to solve it. you must only provide one solution. {prompt}"

    def solve(self, problem, extra_info=""):
        return self.model.chat(
            "dolphin-llama3",
            [
                {"role": "system", "content": self.prompt + f" {extra_info}"},
                {"role": "user", "content": problem}
            ]
        )["message"]["content"]

class SentienceRing:
    """A ring of AI models."""
    def __init__(self, models):
        self.models = models
        self.harmonizer = ollama.Client(host="http://localhost:11434")
        self.step_divider = ollama.Client(host="http://localhost:11434")

    def solve(self, problem, extra_info=""):
        responses = []
        for i, model in enumerate(self.models):
            response = model.solve(problem, extra_info)
            responses.append({"role": "model", "content": response})
            print(f"Model {i} responded")

        string_responses = ""
        for i, response in enumerate(responses):
            string_responses += f"Potential solution {i + 1}: {response['content']}\n\n"


        harmonized_solution = self.harmonizer.chat(
            "dolphin-llama3",
            [
                {"role": "system", "content": f"You are a Harmonizer, you will get a problem, and a bunch of "
                                              f"solutions, your goal is to combine them into a single solution, "
                                              f"PLEASE PROVIDE ONLY ONE SOLUTION. DO NOT ADD YOUR OWN SOLUTION"},
                {"role": "user", "content": string_responses},
            ]
        )["message"]["content"]

        return self.step_divider.chat(
            "dolphin-llama3",
            [
                {"role": "system", "content": f"You are a StepDivider, you will get a solution, your goal is to "
                                              f"divide the solution into steps, you must put each step on a new line. "
                                              f"do not use newlines for any other purpose. Also, don't enumerate the "
                                              f"steps. Only provide the steps, no additional information. that "
                                              f"includes saying \"to ..., follow these steps:\". Don't add that."},
                {"role": "user", "content": harmonized_solution}
            ]
        )["message"]["content"].split("\n")
