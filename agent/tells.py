"""Known AI-writing tells, curated from 2025-2026 sources.

Severity levels:
  BAN   - near-certain AI tell in short professional messages; rewrite required
  FLAG  - strong tell; allowed only if the sender's own corpus uses it
  WATCH - weak tell; flag when several co-occur

Full sourcing in docs/research/05-ai-writing-tells.md. Word lists decay as
models get retuned; the structural checks in humanize.py age slower.
"""

BAN_PHRASES = [
    "i hope this email finds you well",
    "i hope this message finds you well",
    "i hope this finds you well",
    "i am writing to express my strong interest",
    "i am writing to express my interest",
    "your esteemed organization",
    "unique blend of skills",
    "passion, and dedication",
    "i thrive in fast-paced environments",
    "team player with a proven",
    "deeply resonates with me",
    "aligns with my values",
    "explore synergies",
    "leverage synergies",
    "it's important to note",
    "it is important to note",
    "it's worth mentioning",
    "it is worth noting",
    "in today's digital age",
    "in today's fast-paced world",
    "ever-evolving landscape",
    "in the ever-evolving",
    "serves as a testament",
    "stands as a testament",
    "is a testament to",
    "plays a vital role",
    "plays a pivotal role",
    "plays a crucial role",
    "rich tapestry",
    "vibrant tapestry",
    "in the realm of",
    "valuable insights",
    "in conclusion,",
    "in summary,",
    "to summarize,",
    "great question",
    "what a thoughtful",
    "i'd love to tell you more",
    "let me know if you need any modifications",
    "as an ai language model",
    "add numbers here",
    "[insert",
    "but here's the truth",
    "here's what nobody",
    "pick your brain",
]

FLAG_WORDS = [
    "delve", "tapestry", "testament", "realm", "paradigm", "synergy",
    "spearheaded", "leverage", "leveraging", "utilize", "utilizing",
    "foster", "fostering", "facilitate", "harness", "endeavor",
    "underscore", "underscores", "showcase", "showcasing",
    "meticulous", "meticulously", "intricate", "intricacies",
    "pivotal", "paramount", "unwavering", "commendable",
    "groundbreaking", "transformative", "cutting-edge", "tech-savvy", "adept",
    "seamless", "seamlessly", "holistic", "elevate", "empower",
    "results-driven", "boasts", "renowned", "esteemed", "plethora", "myriad",
]

FLAG_PHRASES = [
    "strong track record", "proven ability", "excellent communicator",
    "dynamic environment", "circle back", "touch base",
    "moreover,", "furthermore,", "additionally,", "notably,",
    "reach out to explore", "i wanted to reach out",
]

WATCH_WORDS = [
    "robust", "crucial", "comprehensive", "innovative",
    "landscape", "navigate", "navigating", "journey", "optimize",
    "enhance", "enhancing", "highlighting", "emphasizing",
    "compelling", "invaluable", "stakeholders",
    "ultimately,", "essentially,", "nevertheless,", "consequently,",
]

WATCH_PHRASES = [
    "align with", "resonate with", "serves as", "functions as",
    "contributing to", "setting the stage for", "marking a shift",
    "when it comes to", "at the end of the day", "key role",
]

# Regexes for structural tells live in humanize.py.
