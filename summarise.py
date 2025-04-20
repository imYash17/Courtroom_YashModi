import pandas as pd
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("models/gemini-2.0-flash")


def func(path,n):
    
    # Load the CSV file)
    df = pd.read_csv(path)
    # Pick a specific row 
    row_index = n  # Change this as needed
    case_text = df.iloc[row_index, 2]
    case_id=df.iloc[row_index, 1]

    # Generate summary
    prompt = f'''
    Summarize this legal case, in such a way that it contains:
    It contains the context of the whole case.
    It should contain about 150 words. No beating around the bush. Stay precise.
    {case_text[:30000]}'''
    response = model.generate_content(prompt)
    summary = response.text

    prompt = f'''
    Summarize this legal case, in such a way that it contains:
    It contains prosecution's arguements and proofs againts the defendent.
    It should contain about 150 words. No beating around the bush. Stay precise.
    {case_text[:30000]}
    '''
    response = model.generate_content(prompt)
    prosecution_proof = response.text

    prompt = f'''
    Summarize this legal case, in such a way that it contains:
    It contains Defense's arguements and proofs againts the plaintiff.
    It should contain about 150 words. No beating around the bush. Stay precise.
    {case_text[:30000]}
    '''
    response = model.generate_content(prompt)
    defense_proof = response.text

    prompt = f'''
    Summarize this legal case, in such a way that it contains:
    It contains factual data, time, references, minor details, law reference.
    It should contain about 150 words. No beating around the bush. Stay precise.
    {case_text[:30000]}
    '''
    response = model.generate_content(prompt)
    facts = response.text

    prompt = f'''
    Summarize this legal case, in such a way that it contains:
    It contains evidences that a witness has in support of the plaintiff.
    It should contain about 150 words. No beating around the bush. Stay precise.
    {case_text[:30000]}
    '''
    response = model.generate_content(prompt)
    w1 = response.text

    prompt = f'''
    Summarize this legal case, in such a way that it contains:
    It contains evidences that a witness has in support of the defense.
    It should contain about 150 words. No beating around the bush. Stay precise.
    {case_text[:30000]}
    '''
    response = model.generate_content(prompt)
    w2 = response.text

    prompt =f'''
    Summarize this legal case, in such a way that it contains:
    It concludes who should win the case accordin to the proofs and evidences it has.
    and also the punishment that should be given to the party that is guilty.
    It should contain about 150 words. No beating around the bush. Stay precise.
    f"{case_text[:30000]}
    '''
    response = model.generate_content(prompt)
    final= response.text

    return summary, prosecution_proof, defense_proof, facts, w1, w2, final,case_id

