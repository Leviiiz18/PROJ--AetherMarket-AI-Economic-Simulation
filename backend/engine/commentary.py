import os
from typing import Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class EconomicCommentator:
    """
    Uses an LLM to provide 'inner monologue' or justifications for agent actions.
    Supported by OpenRouter or OpenAI (Async).
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
        
    async def get_action_commentary(self, agent_id: str, last_action_idx: int, state: Dict) -> str:
        """
        Generates a 1-sentence explanation for the agent's behavior.
        Now async and aligns with the engine's action indices.
        """
        action_map = {
            0: "Idle",
            1: "Buying Food",
            2: "Selling Food",
            3: "Buying Energy",
            4: "Selling Energy",
            5: "Buying Materials",
            6: "Selling Materials",
            7: "Producing Food",
            8: "Consuming Food",
            9: "Generating Energy",
            10: "Mining Materials"
        }
        last_action = action_map.get(last_action_idx, "Unknown")

        prompt = f"""
        Agent {agent_id} in AI Economy.
        State: ₹{state['money']:.1f}, Food:{state['food']:.1f}, Energy:{state['energy']:.1f}.
        Action: {last_action}.
        
        Write 1 short, cool, 'inner monologue' justification for this action in the first person.
        Keep it under 10 words.
        """
        
        if not self.client:
            # Smart Fallback
            if last_action_idx == 1 and state["food"] < 2:
                return "Starvation is close. Securing sustenance now."
            if last_action_idx == 7:
                return "Conversion complete. Energy becoming resource."
            return f"{last_action} to remain operationally viable."

        try:
            model = "google/gemini-2.0-flash-001" if "openrouter" in self.base_url else "gpt-3.5-turbo"
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=40
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return f"Synchronizing {last_action} with market flow."

# Singleton instance
commentator = EconomicCommentator()
