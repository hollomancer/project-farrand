# Simulation System Overview

The goal is to recreate the 1787 Philadelphia Constitutional Convention as a real-time multi-agent dialogue rooted in primary sources. The system must generate secret, candid debates among the 55 delegates from May–September 1787, reflecting their personalities and historical context[1][2]. To ensure authenticity, all content is strictly grounded in 18th-century documents and theories (classical republicanism, Enlightenment political thought, Articles-of-Confederation experience) – no knowledge or ideology postdating 1787 may be used[3][4].

## Event Scope and Context

**Dates & Venue:** Official sessions between May 25 and September 17, 1787, in Philadelphia, at Independence Hall (then Congress Hall). Proceedings were secret; after-hours speculation is allowed but strictly within known behavior[1].

**Secret Proceedings:** Use Farrand's Records of the Federal Convention (1787) as the authoritative transcript proxy[1]. Though no verbatim transcripts exist, Madison's and other delegates' notes (compiled by Farrand) reconstruct the debates.[1]

**Topics & Debates:** Focus on the documented core issues: congressional representation (VA vs NJ Plans, Great Compromise), executive powers (one chief vs council, term, election method), federal-state balance (supremacy, taxing, laws), and slavery (three-fifths count, slave trade, fugitive clauses). We also include discussions of necessary features like a bill of rights (George Mason's position) and judiciary. These correspond to the "major debates" noted in convention histories[5].

## Historical Agents and Persona Modeling

**Delegates as Agents:** Model key figures (e.g. James Madison, A. Hamilton, B. Franklin, G. Washington, G. Morris, G. Mason, J. Wilson, etc.) as distinct LLM agents. Each agent's persona is built from biographies, letters, speeches and convention notes (via Founders Online and other Collections[6][1]).

**Speaking Style & Stance:** Encode each delegate's unique voice, rhetoric and ideological bent. For example, Morris and Wilson speak frequently and eloquently, Mason is staunchly Anti-Federalist (blocking without Bill of Rights), Washington speaks rarely but authoritatively. These traits must emerge from the model's behavior. Prompt guidelines should enforce that "the model should reflect the character's unique voice, including speaking style, tone, and emotional responses"[7]. Agents must not "know" anything beyond their 1787 experience (no modern concepts)[3].

**Personality Dimensions:** Following best practice in role-play modeling, each agent's LLM is tuned or prompted to recall factual knowledge (personal background, state interests) and values (federalist vs anti-federalist bias) and to maintain consistency over time[7]. For instance, Federalist voices should consistently argue for a stronger central government; Anti-Federalists emphasize states' rights and individual liberties.

## Knowledge Base and Historical Anchoring

**Primary Sources:** Integrate a curated historical knowledge base. Core collections include:

- Farrand's Records of the Federal Convention (1787) – the reconstructed proceedings of each day[1].
- Founders Online (U.S. Natl Archives) – searchable papers of Washington, Madison, Franklin, Hamilton, etc. (>184,000 documents)[6].
- Papers of the Founding Fathers (UVA Press and others) for letters/speeches of key delegates.
- Contemporary publications, diaries, and recognized secondary sources for context (used only for validation, not dialogue content).

**Retrieval Strategy:** Use Retrieval-Augmented Generation (RAG) to ground dialogue in these sources. Delegate agents send query prompts to a vector search index of the historical documents. For each new utterance, retrieve relevant excerpts (e.g. prior speeches on the same topic, or known correspondence) and include them in the prompt. This helps the LLM cite and paraphrase actual convention lines[8][9].

**Citation Embedding:** All retrieved facts or quotations embedded in a turn must be cited. As AWS notes, RAG enables "presenting accurate information with source attribution" – including citations in output increases trust[4]. The simulation's output will annotate claims: exact phrases or factual claims should be followed by bracketed references (footnote style) to the source document lines[4].

## Multi-Agent Dialogue Architecture

**Agent Orchestration:** Implement a multi-agent conversational framework (similar to LangChain or AutoGen) where each delegate is an independent agent that can speak or defer to others. LangChain's guidance suggests breaking complex tasks into specialized agents to collaborate on conversation[10]. We adopt a handoff pattern: the active agent generates a turn, then selects (or signals) the next speaker. This allows natural turn-taking among specialists (federalist vs anti-federalist voices)[10][11].

**Context Engineering:** Each agent's prompt includes (a) its own profile (name, state, stance), (b) relevant recent dialogue history, and (c) relevant retrieved excerpts. Carefully control what context each sees: an agent should never see others' private notes or future info. LangChain notes that "which parts of the conversation or state are passed to each agent" is key to quality[12]. We ensure only approved (public/session) content is shared among agents.

**Conversation State:** Use a central "conversation manager" to log each turn and maintain global state (e.g. which resolutions are pending). This manager enforces constraints (no modern topics, ideological consistency) and determines when to transition speakers. The manager also collects sources for in-text citations.

## Agent Memory and State Tracking

**Personal Memory:** Each agent has a structured memory of its own past statements and personal commitments. Following generative-agent models[13][14], we log every key utterance or decision an agent makes (e.g. "I will oppose this clause," or referencing state interest). Each memory entry is timestamped and tagged.

**Memory Ingestion & Recall:** On new turns, the system applies a decay or filtering (e.g. most recent 2–3 relevant memories) to feed into the agent's prompt[14]. This ensures consistency: if Mason previously vowed to hold out for a Bill of Rights, that persists as long-term intent. The memory system may be implemented via a vector database of dialogue lines with metadata[15][14].

**Shared Environment:** Aside from individual memory, maintain a global state (proposals on table, votes held) so agents can reference "as we agreed yesterday" or note changed context. Shared facts (e.g. Rhode Island's absence) are also tracked.

## Input and Output Schema

**Input (Prompt Structure):** The orchestrator prompt to the LLM (for an agent's turn) should be structured JSON or text, including:

- Agent Profile: Name, state, ideological stance.
- Session Info: Current date (day of convention), current topic or motion under debate.
- Recent Dialogue: A trimmed transcript of the last few turns (who said what).
- Relevant Memory: Curated snippets from that agent's memory and any public facts.
- Retrieved Excerpts: LLM-found relevant quotes or facts from sources, to ground statements.

**Output (Dialogue Turn):** Each agent's response must follow the required format. For example:

```
Speaker (Role, State) [Certain/Speculative] (Date: Month Day, 1787): "Dialogue line."【source†Lx-Ly】
```

- **Speaker and Role:** E.g. "James Madison (Delegate, Virginia)".
- **Date Tag:** The specific date of the Convention session.
- **Dialogue Line:** The spoken sentence or paragraph. Should sound period-appropriate.
- **Certainty Tag:** [Certain] if the line closely follows documented sources, [Speculative] if it extrapolates or fills gaps (e.g. paraphrasing tone).
- **Citations:** In-line bracketed footnotes refer to historical sources (Farrand, Founders, etc.) that support the content. Multiple citations if needed.

**Tagged Structure:** The system should always output in this structured format (e.g. as JSON or Markdown) so downstream processing can easily parse speaker, date, text, and citations.

## Retrieval and RAG Integration

**Knowledge Retrieval:** Before each turn, query the knowledge base with the current prompt (agent profile + topic). Convert query to an embedding and match against indexed source texts[8]. For example, if Madison is asked about the size of the House, retrieve relevant lines from Farrand or his letters on that subject.

**Augmented Prompt:** Append the retrieved excerpts (or summaries) to the LLM prompt, so the agent "knows" the exact reference. This follows RAG best practice: "the RAG model augments the user input by adding relevant retrieved data in context"[9].

**Citation Generation:** Instruct the LLM to use the retrieved snippets as evidence. For instance, include in the prompt: "When you quote or paraphrase, include a bracketed reference to the source." The LLM should then place 【Farrand vol1†L45-L50】 or similar after factual claims, as proof.

## Decoding Strategies and Consistency

**Temperature and Randomness:** Use low temperature (e.g. 0.3–0.5) to keep language formal and consistent. This avoids modern slang or over-dramatization.

**Role Emphasis:** Apply few-shot examples or system instructions that exemplify correct style and content. Each agent's prompt might begin with a brief persona guideline ("You are James Wilson, an eloquent Federalist…"), to steer tone.

**Turn-Taking Logic:** The conversation manager decides when an agent should speak or remain silent. For example, Washington speaks only occasionally (per instructions). Use logic in the orchestrator to skip or pass turns to rare speakers.

**Certainty Tagging:** Implement a rule or prompt for the LLM to assess how well a statement is grounded. If a line can be directly sourced (e.g. paraphrasing a recorded Madison statement), tag [Certain]. If it fills inference (e.g. Montgomery charlottes tone), tag [Speculative]. This can be a rule-based fallback or a simple heuristic based on presence of citations.

## Guardrails and Constraints

**Historical Accuracy:** Enforce no anachronistic content. The system prompt should explicitly say: "Only use ideas, language, and references available by 1787." Regular expressions or keyword filters can block modern terms.

**Ideological Boundaries:** Ensure each agent stays within their known ideological bounds (e.g. Federalist delegates always favor a stronger central government). Weaving in "personality" or "values" instructions as in[7] helps maintain this. If an agent tries an out-of-character stance, discard or flag the line.

**No Resolution Theater:** The spec prohibits neat compromises not supported by record. Our system will simulate genuine conflict: debates should not unrealistically resolve every issue. The orchestrator should detect unresolved issues and route them back for debate, mimicking the drawn-out nature of the actual Convention.

**Content Safety:** Even though this is historical, ensure no disallowed content (e.g. slurs) slips through. Filter for period-appropriate language.

## Technical Implementation Notes

**Frameworks:** Consider existing multi-agent libraries. For example, Microsoft's AutoGen supports role-playing agents in dialogue. LangChain or LangGraph can be used for context management and tool (sub-agent) orchestration. According to AIMultiple, "LLM orchestration frameworks…streamline prompt engineering, data retrieval, and state management," enabling multi-agent dialogue and RAG[16][17].

**Long-Context Management:** Because the Convention debates span months, implement long-term memory modules. Break dialogue into sessions (days), but allow agents to recall earlier arguments across sessions. Summarization of past sessions can be stored in memory to reduce prompt size.

**Input Schema Example:** An initial "episode" JSON might include: 
```json
{ 
  "date": "May 29 1787", 
  "topic": "Representation", 
  "agents": [
    { 
      "name": "Madison", 
      "state": "VA", 
      "stance": "Large State Federalist", 
      "characteristics": "..."
    }
  ], 
  "history": [] 
}
```
Each new turn appends to history.

**Output Example:**
```
James Madison (Delegate, Virginia) [Certain] (May 30, 1787): "If we establish one house with equal state votes, the people of populous states will be burthens."[1][5]
```

Each turn is serialized with speaker, date, tag, and citations.

## Source Citations and Validation

**In-Output Citations:** All factual claims or quotes in dialogue lines must cite historical texts as footnotes. For example, if Madison argues about "burthens" of equal representation, we attach Farrand's record lines[1]. This both grounds the simulation and provides verifiability.

**Research Mode:** The system should operate in a "grounded" generation mode: it is explicitly retrieving and quoting from the sources rather than relying solely on model recall. This aligns with the purpose of RAG – "optimizing LLM output so it references an authoritative knowledge base"[18].

**Evaluation and Iteration:** Include an evaluation step (possibly using another LLM) to check each turn against known records. If a turn contains unsourced assertions, the model should be prompted to revise or add citations.

## Conclusion

The specification combines a rich historical knowledge base with a sophisticated multi-agent LLM orchestration. Each delegate agent acts with a distinct voice (driven by personality tuning[7]), contributes to an ongoing debate (managed by a conversation controller), and grounds its statements in actual 1787 documents (via RAG and citations[4][19]). By carefully managing context, memory, and constraints, the system will simulate the Constitutional Convention as a dynamic, authentic interchange – faithful to the delegates' recorded words and disputes.

Sources: We draw on primary source collections (Farrand's convention records[1], Founders Online archives[6]) and best-practice LLM orchestration research[10][18][4][19][16] to ensure fidelity and technical feasibility.

## References

[1] The Records of the Federal Convention of 1787, 3vols. | Online Library of Liberty  
https://oll.libertyfund.org/titles/farrand-the-records-of-the-federal-convention-of-1787-3vols

[2] U.S. Senate: Constitutional Convention  
https://www.senate.gov/artandhistory/history/common/image/Constitutional_Convention.htm

[3] [7] Thinking Before Speaking: A Role-playing Model with Mindset  
https://arxiv.org/html/2409.13752v1

[4] [8] [9] [18] What is RAG? - Retrieval-Augmented Generation AI Explained - AWS  
https://aws.amazon.com/what-is/retrieval-augmented-generation/

[5] The Major Debates at the Constitutional Convention - CIVICS RENEWAL NETWORK  
https://www.civicsrenewalnetwork.org/resources/major-debates-constitutional-convention/

[6] Founders Online: Home  
https://founders.archives.gov/

[10] [11] [12] Multi-agent - Docs by LangChain  
https://docs.langchain.com/oss/python/langchain/multi-agent

[13] [14] [15] [19] LLM-Based Multi-Agent System for Simulating and Analyzing Marketing and Consumer Behavior  
https://arxiv.org/html/2510.18155v1

[16] [17] Compare Top 13 LLM Orchestration Frameworks  
https://research.aimultiple.com/llm-orchestration/
