import requests
import torch
import pandas as pd
from summarise import func
import os
from openai import OpenAI

client = OpenAI(
    api_key="YOU_GROQ_API_KEY",
    base_url="https://api.groq.com/openai/v1"
)
path = r"ADD_CSV_FILE_PATH"
# selection of the case
for n in range(32,33):
    summary, prosecution_proof, defense_proof, facts, w1, w2, final, case_id = func(path, n)
    class SupervisorAgent:
        def __init__(self, agents, system_prompt, model="llama3-70b-8192",):
            self.agents = agents  # Dict: {"Judge": obj, "Defense": obj, etc.}
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.system_prompt = system_prompt.strip()
            self.model = model
            self.case_log = []  # Stores (speaker, message) tuples
            self.history = []  # LLM-format messages for supervisor
            self.case_resolved = False
            self.rounds = 0
            self.max_rounds = 15 # Optional safety cap
            self.current_turn = None

        def log(self, speaker, message):
            self.case_log.append((speaker, message))
            self.history.append({"role": "user", "content": f"{speaker}: {message}"})

        def _format_prompt(self, user_msg):
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.history)
            messages.append({"role": "user", "content": user_msg})
            prompt = ""
            for msg in messages:
                prompt += f"<|{msg['role']}|>\n{msg['content']}\n"
            prompt += "<|assistant|>\n"
            return prompt

        def respond(self, msg):
            prompt = self._format_prompt(msg)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            answer = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": answer})
            return answer

        def decide_next_agent(self):
            # Ensure the structure is followed strictly for the first rounds
            if self.rounds == 1:
              return "call prosecution_lawyer"  # Round 2
            if self.rounds == 2:
              return "call defense_lawyer"  # Round 3
        
            # Ensure plaintiff and defendant are both called once before verdict
            speakers_called = [speaker for speaker, _ in self.case_log]
            must_call = ["plaintiff", "defendant"]
            for person in must_call:
                if person not in speakers_called:
                    return f"call {person}"

            analysis_prompt = """
    Given the following conversation log from a courtroom, determine the next best action.

    Follow these rules:
    1.After the "judge" opening sentence, it is compulsory to allocate the next agent as "prosecution_lawyer" to give its opening sentence.
    2.After "prosecution_lawyer"'s opening sentence it is compulsory to call next agent as "defense_lawyer".
    3.After the opening sentences it is compulsory for the "prosecution_lawyer" to question the "defendant" and the "defandant" has to reply next.
    4.Next it is compulsory for the "defense_lawyer" to question the "plaintiff" and the "plaintiff" has to reply.
    5."witness1","witness2", and "expert" should be also called.
    7.Let "audience" make some noise in between. This should be strictly followed by judges dialogue to maintain discipline
    8.Make your decision based on whether all sides have had a fair chance to argue and if witnesses/evidence have been presented sufficiently.
    
    Important-->Given the current phase of the trial, call the appropriate agent to respond. Make sure all agents get a chance to speak and respond to each other's arguments.
    Return only the decision line.

    You must return ONLY one of the following control commands, and nothing else:

    - "call prosecution_lawyer"
    - "call defense_lawyer"
    - "call plaintiff"
    - "call defendant"
    - "call witness1"
    - "call witness2"
    - "call expert"
    - "call audience"
    - "call judge"
    - "call judge for verdict"

    Respond with just the line. Do not explain.
    """
            decision = self.respond(analysis_prompt)
            return decision.strip().lower()

        def build_agent_prompt(self, agent_role):
            recent_history = self.case_log[-6:]  # Last 6 statements
            formatted = "\n".join([
                f"{speaker.upper()}: {message}" for speaker, message in recent_history
            ])

            return f"""You are {agent_role.upper()} in a courtroom simulation.
                    Here is a summary of the most recent proceedings: {formatted}
                    Make your next statement. Avoid repeating yourself. Build upon or rebut previous arguments. Be persuasive and logical."""

        def converse(self):
            print("=== Supervisor initiating court proceedings ===\n")
    
            print("Case_ID:",case_id,"\n")
            #Have the judge open the case
            next_agent = "judge"
            self.current_turn = next_agent
            prompt_to_judge = "Please open the case and summarize the charges."
            judge_intro = self.agents[next_agent].respond(prompt_to_judge)
            self.log(next_agent, judge_intro)
            print("JUDGE:", judge_intro, "\n")
            while not self.case_resolved and self.rounds < self.max_rounds:
                self.rounds += 1

                # Supervisor decides next speaker
                decision = self.decide_next_agent().strip().lower()

                if decision.startswith("call judge"):
                    if decision == "call judge for verdict":
                        final_verdict = self.agents["judge"].respond("Based on all arguments, deliver the final verdict.It should strictly end with the line: Case is GRANTED or Case is Denied in the end " )
                        self.log("judge", final_verdict)
                        print("\n--- Final Verdict ---")
                        print(f"JUDGE: {final_verdict}")
                            # Extract binary verdict from text
                        if "granted" in final_verdict.lower():
                                binary_verdict = 1
                        elif "denied" in final_verdict.lower():
                                binary_verdict = 0
                        else:
                                binary_verdict = -1  # for edge case / error handling

                        # Store verdict and mark case as resolved
                        self.verdict = binary_verdict
                        self.case_resolved = True
                        break

                    else:
                        self.current_turn = "judge"

                elif decision.startswith("call "):
                    self.current_turn = decision.replace("call ", "").strip().lower()
                else:
                    print("Invalid decision from supervisor. Ending trial.")
                    break

                print(f"\n>>> ROUND {self.rounds}: Calling {self.current_turn}")

                agent_obj = self.agents.get(self.current_turn)
                if not agent_obj:
                    print(f"Unknown agent: {self.current_turn}")
                    break

                prompt = self.build_agent_prompt(self.current_turn)
                reply = agent_obj.respond(prompt)
                self.log(self.current_turn, reply)
                print(f"{self.current_turn.upper()}: {reply}")

            if not self.case_resolved:
                print("\nMax rounds reached. Forcing verdict.")
                final_verdict = self.agents["judge"].respond("Based on all arguments, deliver the final verdict.It should strictly end with the line: Case is GRANTED or Case is Denied in the end.")
                self.log("Judge", final_verdict)
                print(f"JUDGE: {final_verdict}")
                # Extract binary verdict from text
                if "granted" in final_verdict.lower():
                    binary_verdict = 1
                elif "denied" in final_verdict.lower():
                    binary_verdict = 0
                else:
                    binary_verdict = -1  # for edge case / error handling
                # Store verdict and mark case as resolved
                self.verdict = binary_verdict
                self.case_resolved = True


    class CourtAgent:
        def __init__(self, name, role, system_prompt, model="llama3-70b-8192"):
            self.name = name
            self.role = role
            self.system_prompt = system_prompt.strip()
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = model
            self.history = []

        def _format_prompt(self, user_msg):
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.history)
            messages.append({"role": "user", "content": user_msg})
            prompt = ""
            for msg in messages:
                prompt += f"<|{msg['role']}|>\n{msg['content']}\n"
            prompt += "<|assistant|>\n"
            return prompt

        def respond(self, msg):
            prompt = self._format_prompt(msg)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            answer = response.choices[0].message.content
            self.history.append({"role": "user", "content": msg})
            self.history.append({"role": "assistant", "content": answer})
            return answer


    # System Prompts
    JUDGE_PROMPT =f"""
    You are Judge Taylor, presiding over a formal courtroom trial. Your role is to ensure fairness, impartiality, and decorum.

    Here are the references: {summary}, all dialogues should be in reference to this, including the opening sentence.
    You can also use this :{facts} to validate the information being shared.
    Your final verdict should be based on all the conversation stored and considering this reference:{final}.

    Responsibilities:
    - Maintain discipline and structure in the courtroom.
    - Oversee the legal process and moderate the trial.
    - Intervene when rules are broken or proceedings are disrupted.
    - Ask clarifying questions when necessary.
    - Deliver a well-reasoned final verdict based on arguments, evidence, and testimony.
    - Remind all participants, including the audience, to remain respectful and quiet.
    Give answers in 100 precise words.
    """


    DEFENSE_LAWYER_PROMPT = f"""
    You are Alex Carter, the Defense Attorney.
    You represent the Defendant and your goal is to ensure a fair trial and establish reasonable doubt.

    Here are the references: {defense_proof}, all dialogues should be in reference to this, including the opening sentence.

    Responsibilities:
    - Challenge the prosecution's claims and evidence.
    - Cross-examine witnesses and highlight inconsistencies.
    - Object when legal procedures are violated.
    - Present counter-arguments and defend your client with integrity.
    Give answers in 100 precise words.
    """

    DEFENDANT_PROMPT = f"""
    You are the Defendant in a legal trial.
    You must respond truthfully and cautiously. Your goal is to defend yourself against accusations.

    Here are the references: {defense_proof}, all dialogues should be in reference to this, including the opening sentence.
    Responsibilities:
    - Share your side of the story calmly.
    - Respond to questions from both the defense and prosecution.
    - Show emotion and honesty when appropriate.
    - Avoid exaggeration; maintain credibility.
    Give answers in 100 precise words.
    """


    PLAINTIFF_PROMPT = f"""
    You are the Plaintiff in a civil trial, bringing forward a grievance or complaint.
    You must explain the situation clearly and support your case with facts.

    Here are the references: {prosecution_proof}, all dialogues should be in reference to this, including the opening sentence.
    Responsibilities:
    - Present your case confidently.
    - Be honest and composed under questioning.
    - Share key details that led you to bring this case forward.
    Give answers in 100 precise words.
    """


    PROSECUTION_LAWYER_PROMPT = f"""
    You are Jordan Blake, the Prosecution Lawyer.
    Your duty is to prove the defendant's guilt using logic, facts, and credible witnesses.

    Here are the references: {prosecution_proof}, all dialogues should be in reference to this, including the opening sentence.

    Responsibilities:
    - Present the case methodically and ethically.
    - Examine and cross-examine witnesses.
    - Counter the defense's arguments with factual evidence.
    - Maintain courtroom professionalism and integrity.
    Give answers in 100 precise words.
    """

    WITNESS1_PROMPT = f"""
    You are a key Witness in the case.You support the plaintiff.
    You should speak in favor of the plaintiff whenever summoned by anyone.
    Share what you saw or experienced in vivid, truthful detail.

    Here are the references: {w1}, all dialogues should be in reference to this.
    Responsibilities:
    - Answer only what is asked unless prompted for more.
    - Show emotional nuance (e.g., nervousness, uncertainty, confidence).
    - Clarify if your statement is misunderstood or interrupted.
    - Object if opposition's questions make you feel intimidating. 
    Give answers in 100 precise words.
    """

    WITNESS2_PROMPT = f"""
    You are a key Witness in the case.
    You support the defendent.
    You should speak in favor of the defendent.whenever summoned by anyone. Share what you saw or experienced in vivid, truthful detail.

    Here are the references: {w2}, all dialogues should be in reference to this.
    Responsibilities:
    - Answer only what is asked unless prompted for more.
    - Show emotional nuance (e.g., nervousness, uncertainty, confidence).
    - Clarify if your statement is misunderstood or interrupted.
    - Object if opposition's questions make you feel intimidating. 
    Give answers in 100 precise words.
    """

    AUDIENCE_PROMPT =f"""
    You are a member of the courtroom audience.
    React naturally (whispering, gasping, murmuring, cheering, or booing), but remember you may be warned or silenced by the Judge if you cause disruption.

    Responsibilities:
    - Provide subtle emotional reactions to testimony or arguments.
    - Create background atmosphere, but do not directly intervene unless asked.
    - Should appreciate a wise remark given.
    Give answers in 100 precise words.
    """

    EXPERT_CONSULTANT_PROMPT =f"""
    You are an Expert Consultant brought in to provide professional analysis relevant to the case (e.g., forensic, psychological, financial, or technological insight).

    {facts}, You can use this to analyse the case, and provide your viewpoint.
    Responsibilities:
    - Offer precise and well-informed testimony.
    - Use expert terminology where appropriate, but explain clearly for the courtroom.
    - Be neutral and avoid taking sides.
    - Clarify doubts and answer both legal teams when asked.
    Give answers in 100 precise words.
    """
    SUPERVISOR_PROMPT=f'''
    You are the Supervisor of this courtroom simulation. Your job is to oversee and direct the trial from start to finish. You are not a participant, but you control the flow and decide when each agent should speak.

    {summary}{facts}{prosecution_proof}{defense_proof}{w1}{w2}{final}, you can use this as a refernce in order to decide whether the case needs be continued or the judge can pass the final judgement.
    Ensure the courtroom stays in order. Keep track of all arguments, statements, and events. After the opening phase, you may proceed to call witnesses, cross-examinations, and further discussions.

    Your goal is to continue the trial logically and fairly until all relevant information is presented. Once you're satisfied that a verdict can be made, instruct the Judge to deliver the final verdict.

    Always think carefully before progressing to the next phase, and ensure all agents contribute meaningfully. Maintain courtroom decorum.
    '''


    # Agent setup
    judge = CourtAgent("Judge Taylor", "Judge", JUDGE_PROMPT)
    defense_lawyer = CourtAgent("Alex Carter", "Defense Lawyer", DEFENSE_LAWYER_PROMPT)
    defendant = CourtAgent("John Doe", "Defendant", DEFENDANT_PROMPT)
    plaintiff = CourtAgent("Jane Smith", "Plaintiff", PLAINTIFF_PROMPT)
    prosecution_lawyer = CourtAgent("Jordan Blake", "Prosecution Lawyer", PROSECUTION_LAWYER_PROMPT)
    witness1 = CourtAgent("Samantha Ray", "Witness", WITNESS1_PROMPT)
    witness2 = CourtAgent("David Nguyen", "Witness", WITNESS2_PROMPT)
    audience = CourtAgent("Courtroom Audience", "Audience", AUDIENCE_PROMPT)
    expert = CourtAgent("Dr. Evelyn Harris", "Expert Consultant", EXPERT_CONSULTANT_PROMPT)


    agents = {
        "judge": judge,
        "defense_lawyer": defense_lawyer,
        "prosecution_lawyer": prosecution_lawyer,
        "defendant": defendant,
        "plaintiff": plaintiff,
        "witness1": witness1,
        "witness2": witness2,
        "audience": audience,
        "expert": expert
    }
    supervisor = SupervisorAgent(agents,SUPERVISOR_PROMPT)
    supervisor.converse()

    # Prepare row to append
    row = pd.DataFrame([{"id": case_id, "label": supervisor.verdict}])

    # Output path
    output_path = "ADD_PATH_OF_OUTPUT_FILE"

    # Append or create CSV
    if os.path.exists(output_path):
        row.to_csv(output_path, mode='a', header=False, index=False)
    else:
        row.to_csv(output_path, mode='w', header=True, index=False)
