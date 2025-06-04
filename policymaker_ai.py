import os
import asyncio
from typing import List, Dict
from openai import AsyncOpenAI

import json  # we’ll use the standard json module for parsing
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# 1. Configuration (async client)
# ─────────────────────────────────────────────────────────────────────────────
API_KEY = 
client = AsyncOpenAI(api_key=API_KEY)
LLM_MODEL = "gpt-4o-mini"  # or "gpt-4"/"gpt-4o" if available

# ─────────────────────────────────────────────────────────────────────────────
# 2. Agent A: Component Extractor (async)
# ─────────────────────────────────────────────────────────────────────────────
class ComponentExtractorAgent:
    def __init__(self, client: AsyncOpenAI, model: str = LLM_MODEL):
        self.client = client
        self.model = model

    async def extract_components(self, product_name: str) -> List[str]:
        system_prompt = (
            "You are an expert industrial engineer. "
            "When given a consumer product name, decompose it into its key modules and components. "
            "Return ONLY a JSON array of strings, e.g. [\"frame\", \"motor\", \"battery\"], "
            "with no additional commentary."
        )
        user_prompt = f"Decompose this product into its main components and include product name and component: \"{product_name}\"."

        # (1) Ask the LLM for a JSON array of components
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            timeout=30  # fail if no response in 30s
        )

        # (2) Extract the raw string
        text = response.choices[0].message.content.strip()

        # (3) Attempt to parse as JSON
        try:
            components = json.loads(text)
            if isinstance(components, list) and all(isinstance(item, str) for item in components):
                return components
            else:
                raise ValueError("LLM returned JSON, but not a list of strings.")
        except Exception:
            # Fallback: split by lines and strip bullets
            lines = [line.strip("-• ").strip() for line in text.splitlines() if line.strip()]
            return lines


# ─────────────────────────────────────────────────────────────────────────────
# 3. Agent B: NAICS Mapper (async)
# ─────────────────────────────────────────────────────────────────────────────
class NAICSMapperAgent:
    def __init__(self, client: AsyncOpenAI, model: str = LLM_MODEL):
        self.client = client
        self.model = model

    async def map_to_naics(
        self,
        product_name: str,
        component_name: str
    ) -> Dict[str, str]:
        """
        Given product_name and component_name, return a JSON dict:
            { "NAICS_code": "XXXXXX", "NAICS_label": "Some Official Label" }
        """
        system_prompt = (
            "You are an expert in U.S. NAICS code trade classifications.  \n"
            "Respond with _only_ a JSON object—no extra text or explanation.  \n"
            "The JSON must have exactly two keys:  \n"
            "  \"NAICS_code\" (a 6-digit string)  \n"
            "  \"NAICS_label\" (the official NAICS description)  \n"
            "For example:  \n"
            "{\"NAICS_code\":\"334111\",\"NAICS_label\":\"Electronic Computer Manufacturing\"}  \n"
            "Now, given a product and a component, pick the correct 6-digit NAICS code and its label."
        )

        user_prompt = (
            f"The product is: \"{product_name}\".\n"
            f"The component is: \"{component_name}\".\n"
            "Return exactly: {\"NAICS_code\":\"...\",\"NAICS_label\":\"...\"}"
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            timeout=30
        )

        text = response.choices[0].message.content.strip()
      

        # 1) Try strict JSON parse
        try:
            naics_obj = json.loads(text)
            if (
                isinstance(naics_obj, dict)
                and "NAICS_code" in naics_obj
                and "NAICS_label" in naics_obj
            ):
                return {
                    "NAICS_code": str(naics_obj["NAICS_code"]),
                    "NAICS_label": str(naics_obj["NAICS_label"])
                }
            # If keys missing or wrong type, fall back
            raise ValueError("Missing required keys in parsed JSON")
        except Exception:
            # 2) Fallback: scan line-by-line for the exact keys
            code = None
            label = None
            for line in text.splitlines():
                if '"NAICS_code"' in line:
                    # e.g.  "NAICS_code": "334111"
                    parts = [p.strip(' "{},') for p in line.split(":") if p.strip()]
                    if len(parts) >= 2 and parts[0] == "NAICS_code":
                        code = parts[1]
                if '"NAICS_label"' in line:
                    parts = [p.strip(' "{},') for p in line.split(":") if p.strip()]
                    if len(parts) >= 2 and parts[0] == "NAICS_label":
                        label = parts[1]
            return {
                "NAICS_code": code or "UNKNOWN",
                "NAICS_label": label or "UNKNOWN"
            }


# ─────────────────────────────────────────────────────────────────────────────
# 4. Orchestrator (async)
# ─────────────────────────────────────────────────────────────────────────────
class ProductToNAICSPipeline:
    def __init__(self, client: AsyncOpenAI):
        self.extractor = ComponentExtractorAgent(client)
        self.mapper    = NAICSMapperAgent(client)

    async def lookup_product(self, product_name: str) -> Dict[str, Dict[str, str]]:
        # 1) Decompose the product
        components = await self.extractor.extract_components(product_name)
        print(f"→ Components found: {components}")

        results: Dict[str, Dict[str, str]] = {}
        # 2) For each component, include the product context when mapping
        for comp in components:
            naics_info = await self.mapper.map_to_naics(product_name, comp)
            results[comp] = naics_info

        return results



# ─────────────────────────────────────────────────────────────────────────────
# 5. Async main entrypoint
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    while True:
        pipeline = ProductToNAICSPipeline(client)

        product_name = input("Enter a product name: ").strip()
        if product_name == 'quit':
            exit
        print(f"\nDecomposing \"{product_name}\" and mapping each component to NAICS:\n")

        mapping = await pipeline.lookup_product(product_name)
    
        cw = pd.read_csv('end_use.csv')
        cw['NAICS_code'] = cw['NAICS_code'].astype(str)
        components = pd.DataFrame.from_dict(mapping, orient='index').reset_index().rename(columns={'index': 'component'})
        components['NAICS_code'] = components['NAICS_code'].astype(str)
        
        components = components.merge(cw, on='NAICS_code')

        components = components[['NAICS_label','component', 'END_USE']]
        print(components)
    


    

if __name__ == "__main__":
    asyncio.run(main()) 