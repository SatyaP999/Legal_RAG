examples = [
    # --- single-hop: holding / disposition ---
    {
        "inputs": {"question": "Did the Ninth Circuit find that the persecutor bar contains an implied duress defense?"},
        "outputs": {"answer": "No. The panel held that the persecutor bar contains no implied duress defense, and denied Perez's petition for review."},
        "question_type": "single_hop",
        "gold_chunk_hint": "Summary section / Analysis Part III conclusion",
    },
    {
        "inputs": {"question": "What statute is at the center of the persecutor bar discussed in Perez-Castillo v. Blanche?"},
        "outputs": {"answer": "8 U.S.C. § 1231(b)(3)(B)(i), which bars immigration relief for anyone who ordered, incited, assisted, or otherwise participated in persecution on account of race, religion, nationality, political social group membership, or political opinion."},
        "question_type": "single_hop",
        "gold_chunk_hint": "Summary section, second paragraph",
    },
    {
        "inputs": {"question": "Under NACARA, what three requirements must an applicant meet to be eligible for special rule cancellation of removal?"},
        "outputs": {"answer": "Seven years of continuous physical presence in the United States at the time of adjudication, good moral character for that period, and extreme hardship to the applicant and/or qualifying family members."},
        "question_type": "single_hop",
        "gold_chunk_hint": "Analysis Part I, NACARA eligibility paragraph",
    },
    {
        "inputs": {"question": "What standard of deference did the panel apply to the Attorney General's interpretation in Negusie II, and why?"},
        "outputs": {"answer": "The panel applied Skidmore deference, not Chevron deference, because Loper Bright v. Raimondo eliminated Chevron deference to agency interpretations of ambiguous statutes. Under Skidmore, weight depends on the thoroughness, reasoning, and consistency of the agency's interpretation."},
        "question_type": "single_hop",
        "gold_chunk_hint": "Analysis Part II, weight discussion",
    },
    {
        "inputs": {"question": "Why did the panel give the Attorney General's interpretation only limited weight?"},
        "outputs": {"answer": "Because the government had taken diametrically opposed positions in Negusie I (recognizing a duress defense) and Negusie II (rejecting one) without providing a rational explanation for the change, which weakened its claim to deference."},
        "question_type": "single_hop",
        "gold_chunk_hint": "Analysis Part II, inconsistency discussion",
    },

    # --- multi-hop: requires connecting the Negusie history across the opinion ---
    {
        "inputs": {"question": "Trace how the interpretation of the persecutor bar's duress defense changed from the Supreme Court's Negusie decision through to this case."},
        "outputs": {"answer": "In 2009, the Supreme Court in Negusie v. Holder held the persecutor bar ambiguous on duress and remanded to the BIA. In Negusie I (2018), the BIA recognized a narrow duress defense. Attorney General Barr's Negusie II (2020) vacated that and held there is no duress exception. AG Garland stayed Negusie II in 2021 without issuing a new decision, and in 2025 AG Bondi vacated the stay and reinstated Negusie II. The Ninth Circuit here independently agreed that no implied duress defense exists, giving Negusie II only limited weight."},
        "question_type": "multi_hop",
        "gold_chunk_hint": "Analysis Part I history + Part II weight discussion (spans multiple paragraphs)",
    },
    {
        "inputs": {"question": "What evidence did the IJ rely on to find that Perez was not credible, and how did that finding affect his ability to rebut the persecutor bar?"},
        "outputs": {"answer": "The IJ found contradictions in Perez's testimony regarding the identity of his battalion, whether he fired his weapon, whether he was in combat, and whether he witnessed human rights abuses — including an admission that he lied to an asylum officer. Because Perez did not challenge this adverse credibility finding on appeal, and the burden was on him to disprove the persecutor bar once the government raised the inference of his involvement, the unrebutted credibility finding meant he failed to meet that burden."},
        "question_type": "multi_hop",
        "gold_chunk_hint": "Background section (credibility findings) + Analysis Part I (burden-shifting)",
    },
    {
        "inputs": {"question": "How did the panel use the structure of neighboring INA provisions to support its reading that the persecutor bar has no voluntariness requirement?"},
        "outputs": {"answer": "The panel noted that Congress used the term 'voluntarily' in several other INA provisions (e.g., voluntary departure under § 1229c(d)(1), voluntary return under § 1158(c)(2)(D), and voluntary membership in a totalitarian party under § 1424(a)(2)) but omitted that term from the persecutor bar itself. Under the interpretive presumption that Congress acts intentionally when it includes language in one provision but omits it in a related one, the panel concluded this omission was deliberate, reinforcing that no duress defense was intended."},
        "question_type": "multi_hop",
        "gold_chunk_hint": "Analysis Part III, statutory comparison paragraphs",
    },

    # --- adversarial: sounds plausible but is NOT answerable from this document ---
    {
        "inputs": {"question": "What did the Ninth Circuit rule in Perez-Castillo about eligibility for asylum under the Convention Against Torture's deferral of removal provision?"},
        "outputs": {"answer": "This document does not address a CAT deferral of removal ruling. It only notes in passing that persecutor-bar-ineligible individuals remain eligible to seek deferral of removal under the CAT — this was not an issue decided in this case, and the answer should not be inferred beyond that passing reference."},
        "question_type": "adversarial",
        "gold_chunk_hint": "not directly decided — only mentioned in background statutory overview",
    },
    {
        "inputs": {"question": "Did the Ninth Circuit panel rule on whether Gladys Albertina Funes Alvarado independently qualifies for NACARA relief apart from her husband's case?"},
        "outputs": {"answer": "The opinion does not separately analyze Funes Alvarado's eligibility; it only states she was included in Perez's original asylum application. No independent ruling on her eligibility appears in this document."},
        "question_type": "adversarial",
        "gold_chunk_hint": "not present — background mentions her only in passing",
    },
    {
        "inputs": {"question": "What sentencing guidelines did the court apply to Perez for his admitted perjury during immigration proceedings?"},
        "outputs": {"answer": "This is an immigration civil proceeding, not a criminal case, and the opinion does not discuss sentencing guidelines. The IJ cited Perez's perjury only as one basis (among three) for denying NACARA relief on good-moral-character grounds — there is no criminal sentencing discussion in this document."},
        "question_type": "adversarial",
        "gold_chunk_hint": "not present — no sentencing proceeding in this opinion",
    },
]