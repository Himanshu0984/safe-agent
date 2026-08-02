# Groq pricing (per 1M tokens) - as of 2025
PRICING = {
    "llama-3.1-8b-instant": {
        "input": 0.05,   # $0.05 per 1M input tokens
        "output": 0.08,  # $0.08 per 1M output tokens
    }
}

class CostTracker:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_calls = 0
        self.total_cost = 0.0
    
    def track(self, response, model="llama-3.1-8b-instant"):
        """Track token usage from a Groq response."""
        usage = response.usage
        in_tokens = usage.prompt_tokens
        out_tokens = usage.completion_tokens
        
        # Calculate cost
        prices = PRICING.get(model, PRICING["llama-3.1-8b-instant"])
        cost = (in_tokens * prices["input"] + out_tokens * prices["output"]) / 1_000_000
        
        self.total_input_tokens += in_tokens
        self.total_output_tokens += out_tokens
        self.total_calls += 1
        self.total_cost += cost
        
        return {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "cost_usd": cost
        }
    
    def report(self):
        """Print a summary report."""
        print("\n" + "="*50)
        print("💰 COST REPORT")
        print("="*50)
        print(f"Total LLM calls:     {self.total_calls}")
        print(f"Input tokens:        {self.total_input_tokens:,}")
        print(f"Output tokens:       {self.total_output_tokens:,}")
        print(f"Total tokens:        {self.total_input_tokens + self.total_output_tokens:,}")
        print(f"Total cost:          ${self.total_cost:.6f}")
        if self.total_calls > 0:
            print(f"Avg cost/call:       ${self.total_cost/self.total_calls:.6f}")
        print("="*50)


# ===== TEST =====
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from groq import Groq
    
    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    tracker = CostTracker()
    
    # Make 3 test calls
    for i in range(3):
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Say hello {i+1}"}]
        )
        stats = tracker.track(r)
        print(f"Call {i+1}: {stats['input_tokens']} in, {stats['output_tokens']} out, ${stats['cost_usd']:.6f}")
    
    tracker.report()