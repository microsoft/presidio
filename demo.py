from presidio_analyzer import Pattern, PatternRecognizer

# Step 1: Pattern banao
dob_pattern = Pattern(
    name="dob",
    regex=(r"(\b(19|20)\d{2}" r"(0[1-9]|1[0-2])" r"(0[1-9]|[12]\d|3[01])\b)"),
    score=0.8,
)

# Step 2: Recognizer banao
rec = PatternRecognizer(
    name="DOB Recognizer",
    supported_entity="DATE_TIME",
    patterns=[dob_pattern],
    context=["DOB"],
)

# Step 3: Text analyze karo
text = "DOB: 19571012"
results = rec.analyze(text, ["DATE_TIME"], None)

print("Base results:")
for res in results:
    print(
        "Entity:",
        res.entity_type,
        "Score:",
        res.score,
        "Text:",
        text[res.start : res.end],
    )

# Step 4: Manual context boosting
for res in results:
    window = text[max(0, res.start - 20) : res.end + 20].lower()
    if "dob" in window:
        res.score = min(1.0, res.score + 0.2)

print("\nAfter manual boost:")
for res in results:
    print(
        "Entity:",
        res.entity_type,
        "Score:",
        res.score,
        "Text:",
        text[res.start : res.end],
    )
