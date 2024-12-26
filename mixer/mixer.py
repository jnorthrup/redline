from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def merge_models_weighted_average(model_tags, weights=None):
    """
    Merges models using a weighted average of their parameters.

    Args:
      model_tags: A list of Hugging Face model tags.
      weights: A list of weights for each model. If None, equal weights are used.

    Returns:
      The merged model.
    """
    if weights is None:
        weights = [1.0 / len(model_tags)] * len(model_tags)
    else:
        assert len(weights) == len(model_tags), "Number of weights must match number of models"
        assert sum(weights) == 1.0, "Weights must sum to 1.0"

    merged_state_dict = {}
    for i, model_tag in enumerate(model_tags):
        model = AutoModelForCausalLM.from_pretrained(model_tag)
        state_dict = model.state_dict()

        for name, param in state_dict.items():
            if name not in merged_state_dict:
                merged_state_dict[name] = torch.zeros_like(param)
            merged_state_dict[name] += weights[i] * param

    # Load the merged state dict into a new model
    # We use the first model in the list as a template
    merged_model = AutoModelForCausalLM.from_pretrained(model_tags[0])
    merged_model.load_state_dict(merged_state_dict)

    return merged_model

def mix_and_optimize(model_tags, weights=None):
    """
    Merges models using weighted averaging, and provides placeholders for
    optimization and format lowering.

    Args:
      model_tags: A list of Hugging Face model tags.
      weights: A list of weights for each model. If None, equal weights are used.

    Returns:
      The final mixed model.
    """
    merged_model = merge_models_weighted_average(model_tags, weights)

    # Placeholder for unsloth optimization
    # Example (not functional yet):
    # from unsloth import FastLanguageModel
    # model, tokenizer = FastLanguageModel.from_pretrained(...)
    # optimized_model = FastLanguageModel.get_peft_model(model, ...)

    # Placeholder for format lowering
    # Example (using torch.quantization):
    # quantized_model = torch.quantization.quantize_dynamic(
    #     merged_model, {torch.nn.Linear}, dtype=torch.qint8
    # )

    return merged_model

# Example usage (can be run directly in a Colab notebook):
if __name__ == "__main__":
    model_tags = ["gpt2", "gpt-neo-125M"]
    mixed_model = mix_and_optimize(model_tags)
    print(mixed_model)

    # To save the mixed model:
    # mixed_model.save_pretrained("mixed_model")

    # To use the mixed model for inference:
    # tokenizer = AutoTokenizer.from_pretrained(model_tags[0])
    # inputs = tokenizer("Hello, how are you?", return_tensors="pt")
    # outputs = mixed_model.generate(**inputs)
    # print(tokenizer.decode(outputs[0]))