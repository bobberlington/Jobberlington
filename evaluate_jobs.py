from transformers import AutoTokenizer, AutoModelForCausalLM
from credentials import hf_token

def summarize_resume(tokenizer, model, resume_content):
    system_prompt = f"""
I will send my resume. Summarize the skills demonstrated in my experiences and output it in a list in bullet point format. On the first line, put a bullet for my educational status.
    """
    messages = [
  {"role": "system", "content": f"{system_prompt}"},
  {"role": "user", "content": f"{resume_content}"}
]
    inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

    outputs = model.generate(**inputs, max_new_tokens=1000)
    summary = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    return summary

def summarize_job(tokenizer, model, job, prompt=None):
    if prompt is None:
        prompt = """
        I will send a job description. Summarize the required skills in the description.
        """
    messages = [
    {"role": "system", "content": f"{prompt}"},
    {"role": "user", "content": f"{job}"}
  ]
    inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
    ).to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=2000)
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])


def evaluate_job_fitness(tokenizer, model, resume_skills, job, prompt=None):
    if prompt is None:
        prompt = """
        Would I be able to apply to this job? 
        Structure the output in json format, with 2 fields: 
        The first field is ANALYSIS: Do a 4 sentence analysis by seeing if my resume's skills match well to the job's skills. 
        The second field is CONFIDENCE: A single word: Answer 'HIGH' if the skills match well, 'MEDIUM' if only some skills match well, or 'LOW' if only a few skills are relevant. 
        Additionally, if the job asks for a degree greater than the one in my resume, answer LOW. 
        AFTER COMPLETING THE JSON, DO NOT WRITE ANYTHING ELSE.
        """
    tokenizer.pad_token = tokenizer.eos_token
    messages = [
        {"role": "system", "content": f"My resume shows that I have the following skills: <RESUME>{resume_skills}</RESUME> A job is asking for the requirements: <JOB>{job}</JOB>. "},
        {"role": "user", "content": f"{prompt}"}
    ]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=1000, use_cache=True, pad_token_id=tokenizer.eos_token_id)
    evaluation = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    begin, end = evaluation.find('{'), evaluation.rfind('}')
    evaluation = evaluation[begin: end+1].replace("\n", "")
    return evaluation