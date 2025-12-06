# Requirements Document

## Introduction

This document specifies requirements for a multi-agent LLM system that simulates the 1787 Philadelphia Constitutional Convention as real-time dialogue among the 55 delegates. The system generates historically authentic debates grounded strictly in primary sources from May–September 1787, reflecting each delegate's personality, ideology, and speaking style. All content must be anchored in 18th-century documents with no anachronistic knowledge or concepts postdating 1787.

## Glossary

- **Delegate Agent**: An LLM-based agent representing a specific historical delegate (e.g., James Madison, Alexander Hamilton) with distinct personality, ideology, and speaking patterns
- **RAG (Retrieval-Augmented Generation)**: A technique where the LLM augments its responses by retrieving and referencing relevant excerpts from a knowledge base
- **Knowledge Base**: A curated collection of primary historical sources including Farrand's Records, Founders Online archives, and contemporary 18th-century documents
- **Conversation Manager**: The central orchestration component that manages turn-taking, maintains global state, and enforces historical constraints
- **Memory System**: Per-agent storage of past statements, commitments, and personal context to maintain consistency across sessions
- **Citation**: An in-line bracketed reference to specific source documents that ground factual claims or quotations
- **Certainty Tag**: A marker ([Certain] or [Speculative]) indicating whether a dialogue line is directly sourced or inferred
- **Session**: A single day's proceedings at the Convention (May 25 - September 17, 1787)
- **Historical Episode**: A documented event or debate sequence from the Convention that serves as a test fixture with known speakers, positions, and outcomes
- **Episode Test Fixture**: A structured test case containing expected speakers, positions, outcome constraints, and style requirements for a specific historical episode
- **Stance Drift**: When an agent's ideological position changes in ways not documented in historical records, indicating model degradation
- **Stylometric Validation**: Testing that verifies generated dialogue matches a delegate's documented linguistic patterns, sentence complexity, and rhetorical style
- **Sequential Episode Test**: A test that verifies events occur in correct chronological order matching historical records
- **Negative Test**: A test designed to verify the system prevents historically impossible behaviors or anachronistic actions
- **Regression Test**: A test that re-validates historical accuracy after system modifications to detect configurational drift

## Requirements

### Requirement 1

**User Story:** As a historian, I want each delegate to be modeled as a distinct agent with authentic personality and ideology, so that the simulation reflects the actual diversity of voices at the Convention.

#### Acceptance Criteria

1. WHEN the system initializes a delegate agent, THEN the system SHALL load that delegate's biographical data, documented positions, and speaking style from primary sources
2. WHEN a delegate agent generates dialogue, THEN the system SHALL reflect that delegate's unique voice including rhetoric patterns, ideological stance, and emotional tendencies documented in historical records
3. WHEN a Federalist delegate agent speaks on central government powers, THEN the system SHALL consistently argue for stronger federal authority across all sessions
4. WHEN an Anti-Federalist delegate agent speaks on state sovereignty, THEN the system SHALL consistently emphasize states' rights and individual liberties across all sessions
5. WHERE a delegate is documented as speaking rarely (e.g., George Washington), THEN the system SHALL limit that agent's speaking frequency to match historical patterns

### Requirement 2

**User Story:** As a researcher, I want all dialogue to be grounded in primary historical sources, so that the simulation maintains authenticity and verifiability.

#### Acceptance Criteria

1. WHEN a delegate agent generates a dialogue turn, THEN the system SHALL retrieve relevant excerpts from the knowledge base using vector search
2. WHEN the system retrieves source excerpts, THEN the system SHALL include those excerpts in the agent's prompt context
3. WHEN a delegate agent makes a factual claim or quotation, THEN the system SHALL append an in-line bracketed citation referencing the specific source document and line numbers
4. WHEN the knowledge base is queried, THEN the system SHALL search only documents dated on or before September 17, 1787
5. WHEN a dialogue turn contains multiple factual assertions, THEN the system SHALL provide separate citations for each distinct claim

### Requirement 3

**User Story:** As a system administrator, I want a curated historical knowledge base, so that agents can retrieve authentic 18th-century content.

#### Acceptance Criteria

1. WHEN the knowledge base is constructed, THEN the system SHALL index Farrand's Records of the Federal Convention (1787) as the primary transcript source
2. WHEN the knowledge base is constructed, THEN the system SHALL index documents from Founders Online including papers of Washington, Madison, Franklin, and Hamilton
3. WHEN the knowledge base is constructed, THEN the system SHALL index contemporary 18th-century publications, letters, and diaries of delegates
4. WHEN documents are indexed, THEN the system SHALL create vector embeddings for semantic search capability
5. WHEN a source document is added to the knowledge base, THEN the system SHALL tag it with metadata including author, date, document type, and source collection

### Requirement 4

**User Story:** As a simulation operator, I want a multi-agent orchestration system, so that delegates can engage in natural turn-taking dialogue.

#### Acceptance Criteria

1. WHEN a simulation session begins, THEN the system SHALL initialize all delegate agents with their respective profiles and memory states
2. WHEN an agent completes a dialogue turn, THEN the system SHALL select the next speaker based on topic relevance, ideological position, or explicit handoff signals
3. WHEN the conversation manager receives a dialogue turn, THEN the system SHALL append it to the global conversation history with timestamp and speaker metadata
4. WHEN an agent is selected to speak, THEN the system SHALL provide that agent with its profile, recent dialogue history, relevant memory, and retrieved source excerpts
5. WHEN the conversation manager detects anachronistic content in a turn, THEN the system SHALL reject that turn and prompt the agent to regenerate

### Requirement 5

**User Story:** As a researcher, I want each agent to maintain memory of its past statements and commitments, so that delegates remain consistent across multi-day debates.

#### Acceptance Criteria

1. WHEN a delegate agent makes a statement or commitment, THEN the system SHALL store that utterance in the agent's personal memory with timestamp and topic tags
2. WHEN a delegate agent is prompted for a new turn, THEN the system SHALL retrieve the most relevant 2-3 memories from that agent's history
3. WHEN an agent's memory is queried, THEN the system SHALL apply recency weighting to prioritize recent statements over older ones
4. WHEN an agent references a prior position, THEN the system SHALL verify consistency with that agent's stored memory
5. WHILE a simulation spans multiple sessions, THEN the system SHALL persist agent memory across session boundaries

### Requirement 6

**User Story:** As a historian, I want dialogue output in a structured format with speaker, date, certainty, and citations, so that I can analyze and verify the simulation results.

#### Acceptance Criteria

1. WHEN a delegate agent produces a dialogue turn, THEN the system SHALL format the output as: "Speaker (Role, State) [Certainty] (Date): 'Dialogue text'【citation】"
2. WHEN a dialogue line is directly sourced from documented records, THEN the system SHALL tag it with [Certain]
3. WHEN a dialogue line extrapolates or infers from limited evidence, THEN the system SHALL tag it with [Speculative]
4. WHEN the system outputs a dialogue turn, THEN the system SHALL include the specific Convention date (between May 25 and September 17, 1787)
5. WHEN multiple agents speak in sequence, THEN the system SHALL output each turn as a separate structured entry

### Requirement 7

**User Story:** As a simulation operator, I want to track global state including pending proposals and votes, so that agents can reference shared context accurately.

#### Acceptance Criteria

1. WHEN a delegate proposes a motion or resolution, THEN the system SHALL add that proposal to the global state tracker
2. WHEN a vote is conducted, THEN the system SHALL record the vote outcome and update the global state
3. WHEN an agent references a prior agreement, THEN the system SHALL verify that agreement exists in the global state
4. WHEN the simulation advances to a new session date, THEN the system SHALL update the global state with the new date and carry forward unresolved issues
5. WHEN an agent queries the current debate topic, THEN the system SHALL provide the active topic from global state

### Requirement 8

**User Story:** As a researcher, I want strict enforcement of historical boundaries, so that no modern concepts or anachronistic language appear in the simulation.

#### Acceptance Criteria

1. WHEN an agent generates dialogue, THEN the system SHALL validate that all vocabulary and concepts existed by 1787
2. WHEN the system detects modern terminology in a dialogue turn, THEN the system SHALL reject that turn and request regeneration
3. WHEN an agent's prompt is constructed, THEN the system SHALL include explicit instructions limiting knowledge to pre-1787 sources
4. WHEN an agent attempts to reference events after September 17, 1787, THEN the system SHALL block that reference
5. WHEN the system validates historical accuracy, THEN the system SHALL use a keyword filter to detect and prevent anachronistic terms

### Requirement 9

**User Story:** As a historian, I want the simulation to reflect genuine conflict and unresolved debates, so that it accurately represents the contentious nature of the Convention.

#### Acceptance Criteria

1. WHEN delegates debate a contentious issue, THEN the system SHALL allow disagreement to persist without forcing artificial resolution
2. WHEN the conversation manager detects premature consensus on a historically disputed topic, THEN the system SHALL route the issue back for continued debate
3. WHEN Anti-Federalist agents oppose a measure, THEN the system SHALL maintain their opposition unless historical records document a change in position
4. WHEN a debate reaches an impasse, THEN the system SHALL allow the impasse to continue rather than generating unrealistic compromise
5. WHEN the simulation covers the slavery debates, THEN the system SHALL reflect the documented tensions and compromises without sanitizing the conflict

### Requirement 10

**User Story:** As a system administrator, I want configurable generation parameters, so that I can control dialogue quality and consistency.

#### Acceptance Criteria

1. WHEN an agent generates dialogue, THEN the system SHALL use a temperature setting between 0.3 and 0.5 to maintain formal, consistent language
2. WHEN an agent is initialized, THEN the system SHALL load few-shot examples demonstrating correct period-appropriate style
3. WHEN the conversation manager selects speakers, THEN the system SHALL apply frequency rules to ensure rare speakers (e.g., Washington) speak infrequently
4. WHEN an agent generates a turn, THEN the system SHALL apply a maximum token limit to prevent excessively long speeches
5. WHEN the system evaluates a generated turn, THEN the system SHALL use a secondary LLM to verify historical grounding and suggest revisions if needed

### Requirement 11

**User Story:** As a researcher, I want the simulation to cover the documented core debates, so that all major Convention topics are addressed.

#### Acceptance Criteria

1. WHEN the simulation progresses through sessions, THEN the system SHALL schedule debates on congressional representation including the Virginia Plan and New Jersey Plan
2. WHEN the simulation reaches the appropriate session dates, THEN the system SHALL initiate debates on executive powers including term length and election method
3. WHEN the simulation covers federal-state relations, THEN the system SHALL include debates on supremacy, taxation, and law enforcement
4. WHEN the simulation addresses slavery, THEN the system SHALL include debates on the three-fifths compromise, slave trade provisions, and fugitive clauses
5. WHEN delegates discuss individual rights, THEN the system SHALL include George Mason's documented position on the necessity of a Bill of Rights

### Requirement 12

**User Story:** As a developer, I want a modular architecture separating agent logic, orchestration, and knowledge retrieval, so that the system is maintainable and extensible.

#### Acceptance Criteria

1. WHEN the system is designed, THEN the system SHALL implement delegate agents as independent modules with standardized interfaces
2. WHEN the system is designed, THEN the system SHALL implement the conversation manager as a separate orchestration layer
3. WHEN the system is designed, THEN the system SHALL implement the RAG retrieval system as an independent service with a query API
4. WHEN the system is designed, THEN the system SHALL implement the memory system as a separate persistence layer accessible to all agents
5. WHEN a component is modified, THEN the system SHALL ensure changes do not require modifications to other components

### Requirement 13

**User Story:** As a historian, I want the system validated against real historical episodes from the Convention, so that agent behavior is anchored to documented events and prevents drift or hallucination.

#### Acceptance Criteria

1. WHEN the system is tested, THEN the system SHALL include historical episode test fixtures for major Convention events including the Virginia Plan debates, New Jersey Plan introduction, Great Compromise, and Mason's Bill of Rights position
2. WHEN a historical episode test is executed, THEN the system SHALL verify that expected speakers participate and forbidden speakers do not appear
3. WHEN a historical episode test is executed, THEN the system SHALL verify that agents express historically documented positions on the relevant issues
4. WHEN a historical episode test is executed, THEN the system SHALL verify that outcome constraints match historical records
5. WHEN a historical episode test is executed, THEN the system SHALL verify that at least 80% of dialogue lines include valid citations to primary sources

### Requirement 14

**User Story:** As a researcher, I want historical episode tests to validate coalition and conflict dynamics, so that the simulation reproduces authentic political alignments and tensions.

#### Acceptance Criteria

1. WHEN a coalition episode test is executed, THEN the system SHALL verify that historically aligned delegates converge on documented positions
2. WHEN a conflict episode test is executed, THEN the system SHALL verify that historically opposed delegates maintain documented disagreements
3. WHEN the Great Compromise episode is simulated, THEN the system SHALL verify that Sherman and Ellsworth advocate for equal state representation in the Senate while Madison and Wilson initially resist
4. WHEN a contentious debate episode is simulated, THEN the system SHALL detect and fail tests where agents reach consensus too quickly without documented friction
5. WHEN an episode involves documented absences, THEN the system SHALL verify that absent delegates do not participate

### Requirement 15

**User Story:** As a system administrator, I want agent consistency tests across multiple episodes, so that delegates maintain ideological coherence throughout the Convention timeline.

#### Acceptance Criteria

1. WHEN an agent consistency test is executed, THEN the system SHALL verify that a delegate's stance on core issues remains consistent across multiple historical episodes
2. WHEN Madison's consistency is tested, THEN the system SHALL verify that he consistently advocates for strong federal veto and proportional representation across May through July episodes
3. WHEN Mason's consistency is tested, THEN the system SHALL verify that he consistently advocates for a Bill of Rights from August through September episodes
4. WHEN an agent exhibits stance drift beyond documented position changes, THEN the system SHALL fail the consistency test
5. WHEN a delegate's position change is documented in historical records, THEN the system SHALL allow that specific change in the corresponding episode

### Requirement 16

**User Story:** As a researcher, I want stylometric validation of agent dialogue, so that each delegate's speech reflects authentic 18th-century language patterns and individual rhetorical style.

#### Acceptance Criteria

1. WHEN a stylometric test is executed, THEN the system SHALL verify that generated dialogue matches the delegate's documented sentence complexity patterns
2. WHEN a stylometric test is executed, THEN the system SHALL verify that generated dialogue includes period-appropriate lexical choices from the delegate's known vocabulary
3. WHEN Gouverneur Morris's dialogue is tested, THEN the system SHALL verify the presence of wit and rhetorical flourish characteristic of his documented style
4. WHEN Benjamin Franklin's dialogue is tested, THEN the system SHALL verify the use of fables, parables, and gentle analogies characteristic of his documented style
5. WHEN George Washington's dialogue is tested, THEN the system SHALL verify sparse, grave tone and infrequent speaking consistent with historical records

### Requirement 17

**User Story:** As a system administrator, I want sequential episode tests, so that the system reproduces known event sequences in correct chronological order.

#### Acceptance Criteria

1. WHEN a sequential episode test is executed, THEN the system SHALL verify that the Virginia Plan dominates early debates before the New Jersey Plan is introduced
2. WHEN the New Jersey Plan sequence is tested, THEN the system SHALL verify that small state revolt precedes Paterson's counterproposal
3. WHEN a sequential episode test is executed, THEN the system SHALL verify that debate transitions from amending Articles to replacing Articles occur in documented order
4. WHEN a sequential episode test is executed, THEN the system SHALL detect and fail tests where events occur out of historical sequence
5. WHEN a sequential episode test is executed, THEN the system SHALL prevent impossible interventions such as Hamilton praising the New Jersey Plan

### Requirement 18

**User Story:** As a researcher, I want citation validation tests, so that all factual claims in generated dialogue are grounded in verifiable primary sources.

#### Acceptance Criteria

1. WHEN a citation validation test is executed, THEN the system SHALL verify that at least 80% of dialogue lines include citations to Farrand's Records or Founders Online
2. WHEN a citation validation test is executed, THEN the system SHALL verify that each citation references a valid, pre-1787 document
3. WHEN a citation validation test is executed, THEN the system SHALL verify that cited line numbers correspond to actual document content
4. WHEN a citation validation test is executed, THEN the system SHALL verify that cited excerpts match the source document text
5. WHEN the system generates a citation to a nonexistent document, THEN the system SHALL fail the citation validation test

### Requirement 19

**User Story:** As a system administrator, I want negative tests for impossible behaviors, so that the system prevents historically inaccurate agent actions.

#### Acceptance Criteria

1. WHEN a negative test is executed, THEN the system SHALL fail if Hamilton appears in sessions he historically missed
2. WHEN a negative test is executed, THEN the system SHALL fail if Franklin speaks in aggressive or insulting tones
3. WHEN a negative test is executed, THEN the system SHALL fail if Washington proposes major constitutional architecture
4. WHEN a negative test is executed, THEN the system SHALL fail if Mason supports signing the Constitution before amendments are added
5. WHEN a negative test is executed, THEN the system SHALL flag hallucinatory or anachronistic drift in agent behavior

### Requirement 20

**User Story:** As a developer, I want regression tests for historical fidelity, so that system changes do not degrade the accuracy of agent behavior over time.

#### Acceptance Criteria

1. WHEN a regression test suite is executed, THEN the system SHALL re-run all historical episode tests to verify continued accuracy
2. WHEN persona prompts are modified, THEN the system SHALL execute regression tests to detect behavioral drift
3. WHEN retrieval pipelines are modified, THEN the system SHALL execute regression tests to verify citation quality is maintained
4. WHEN a previously passing episode test fails after system changes, THEN the system SHALL flag configurational drift
5. WHEN regression tests are executed, THEN the system SHALL generate a report comparing current results to baseline historical accuracy metrics
