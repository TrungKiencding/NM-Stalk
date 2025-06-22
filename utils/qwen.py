import os, gc, torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel, BitsAndBytesConfig
import torch
import torch.nn.functional as F
from peft import PeftModel

os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'



# Cấu hình quantization 8-bit
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=False,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model_name = "Qwen/Qwen3"
device = 'cuda'

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    quantization_config=quantization_config,
    device_map=device
)
# 2. Tải adapter LoRA
lora_model_path = "model/qwen_lora_summary_model"
lora_model = PeftModel.from_pretrained(model, lora_model_path)

# 3. Hợp nhất mô hình (merge)
# Hợp nhất các trọng số LoRA vào mô hình cơ sở
merged_model = lora_model.merge_and_unload()


system_prompt = '''Extract the most important phrases and key entities from the following social media post about technology.Your summary should be in english. Your summary should use only exact phrases and sentences from the original post, preserving the original wording.  Focus on capturing the main topics, technologies, products, companies, and any significant facts or statistics mentioned. Present the summary as a concise list of bullet points or a short paragraph, ensuring that only the most relevant information is included. Output format: One single paragraph 2-3 sentences, no line breaks, no special characters or bullet points.
Text to summarize:'''


def get_qwen_output(text):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"###User input text here###\n{text}"}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False # Switches between thinking and non-thinking modes. Default is True.
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = merged_model.generate(
        **model_inputs,
        max_new_tokens=32768
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    final_output = tokenizer.decode(output_ids, skip_special_tokens=True).split('</think>')[-1].strip()
    return final_output