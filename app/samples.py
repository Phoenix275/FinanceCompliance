"""Synthetic sample library — GE HealthCare-flavored finance & compliance scenarios.

Every policy, entity, person, and number below is fictional and written for
demo purposes. No real customer, employee, patient, vendor, or regulated data.
Canned results power demo mode so the app never breaks on stage.
"""

from .schemas import AnalysisResult, PolicyCitation, Sample

DISCLAIMER = (
    "AI-assisted analysis for internal triage only — not a final compliance, "
    "legal, or financial decision. A qualified compliance officer must review "
    "and approve any action. All data in this demo is synthetic."
)

SAMPLES: list[Sample] = [
    Sample(
        id="distributor-onboarding",
        title="Third-party distributor onboarding (anti-bribery due diligence)",
        policy_type="Third-party / anti-bribery",
        policy_text=(
            "Third-Party Intermediary Policy (synthetic excerpt).\n\n"
            "1. All distributors, agents, and resellers must complete anti-bribery "
            "due diligence before any agreement is signed or order is fulfilled.\n"
            "2. Required onboarding evidence: certificate of incorporation, "
            "beneficial ownership disclosure to the individual level, sanctions and "
            "watchlist screening results, and a signed anti-corruption certification.\n"
            "3. Intermediaries operating in markets rated high-risk on the corporate "
            "corruption index require enhanced due diligence and regional compliance "
            "officer approval.\n"
            "4. Any intermediary with government ownership, or whose beneficial owners "
            "include current or former government officials, requires senior compliance "
            "approval before engagement.\n"
            "5. Commission or discount structures above the regional standard rate "
            "must be documented with a written business justification."
        ),
        scenario_text=(
            "A prospective imaging-equipment distributor in a high-risk market has "
            "submitted its certificate of incorporation and a signed anti-corruption "
            "certification. Beneficial ownership disclosure is still pending, and the "
            "sales team notes one rumored owner previously served in the regional "
            "health ministry. The sales team wants to fulfill an initial order of 40 "
            "ultrasound units this quarter."
        ),
        question="Can we sign the distribution agreement and fulfill the first order now?",
    ),
    Sample(
        id="hcp-consulting",
        title="Healthcare professional consulting payment (anti-kickback / transparency)",
        policy_type="HCP interactions",
        policy_text=(
            "Healthcare Professional Engagement Policy (synthetic excerpt).\n\n"
            "1. Payments to healthcare professionals (HCPs) must reflect fair market "
            "value for documented, legitimate services under a written agreement "
            "executed before services begin.\n"
            "2. HCP consulting engagements require a documented business need approved "
            "by the medical affairs review board.\n"
            "3. All transfers of value to HCPs must be recorded for transparency "
            "reporting within 30 days of payment.\n"
            "4. Consulting fees may not be linked, directly or indirectly, to past or "
            "expected purchasing decisions of the HCP or their institution.\n"
            "5. Engagements with HCPs who sit on institutional purchasing committees "
            "require compliance pre-approval."
        ),
        scenario_text=(
            "A regional sales manager requests a $18,000 consulting agreement with a "
            "radiologist for advisory input on a new MRI workflow. The radiologist "
            "chairs the purchasing committee of a hospital currently evaluating a "
            "$2.4M imaging tender. No written agreement exists yet; the manager wants "
            "the first advisory session next week and notes the radiologist has been "
            "'very supportive' of the tender."
        ),
        question="Can this consulting engagement proceed as requested?",
    ),
    Sample(
        id="gifts-hospitality",
        title="Gifts & hospitality expense for hospital officials",
        policy_type="Gifts & hospitality",
        policy_text=(
            "Gifts, Meals and Hospitality Policy (synthetic excerpt).\n\n"
            "1. Business meals with customer representatives are permitted up to a "
            "per-person limit of $75, with a legitimate business purpose recorded on "
            "the expense report.\n"
            "2. Gifts of any value to government employees, including staff of public "
            "hospitals, are prohibited unless pre-approved by compliance.\n"
            "3. Entertainment (sporting events, concerts, sightseeing) for customer "
            "representatives involved in an active procurement is prohibited.\n"
            "4. Expenses must be booked to the correct cost category with itemized "
            "receipts; splitting invoices to stay under limits is prohibited.\n"
            "5. Repeated hospitality to the same individual within a quarter requires "
            "compliance review."
        ),
        scenario_text=(
            "An account executive submitted an expense report for a $640 dinner for "
            "four attendees, listed as 'project dinner'. Attendees include two "
            "procurement staff of a public hospital that has an open CT-scanner "
            "tender. The receipt is a single unitemized total, and a similar dinner "
            "with the same attendees was expensed five weeks ago."
        ),
        question="Should this expense report be approved, and does it raise a compliance issue?",
    ),
    Sample(
        id="export-sanctions",
        title="Export / sanctions screening for equipment shipment",
        policy_type="Trade compliance / sanctions",
        policy_text=(
            "Trade Compliance and Sanctions Policy (synthetic excerpt).\n\n"
            "1. All international shipments must be screened against applicable "
            "sanctions and restricted-party lists before release.\n"
            "2. Shipments to countries under comprehensive sanctions are prohibited "
            "absent a valid license or authorization reviewed by trade compliance.\n"
            "3. A match or partial match on a restricted-party list places the order "
            "on hold until trade compliance clears or blocks the transaction.\n"
            "4. End-user statements are required for products with dual-use "
            "classification.\n"
            "5. Employees may not restructure, reroute, or relabel a transaction to "
            "avoid screening or licensing requirements."
        ),
        scenario_text=(
            "Logistics flags an order of portable ultrasound units routed to a "
            "freight forwarder in a neighboring country, with final delivery "
            "documents naming a clinic in a comprehensively sanctioned territory. "
            "The reseller suggests re-invoicing through its regional office so the "
            "shipment can move this week. Restricted-party screening returned a "
            "partial name match on the consignee."
        ),
        question="Can logistics release this shipment as re-invoiced by the reseller?",
    ),
    Sample(
        id="tender-intermediary",
        title="Government tender — unusual intermediary fee",
        policy_type="Anti-bribery / finance controls",
        policy_text=(
            "Government Tender and Payments Policy (synthetic excerpt).\n\n"
            "1. Success fees or commissions tied to the award of government tenders "
            "require pre-approval by legal and compliance.\n"
            "2. Payments must be made to the contracting party's bank account in its "
            "country of incorporation; third-country payments require compliance "
            "approval.\n"
            "3. Consultant fees materially above market rate for comparable services "
            "must be supported by a written scope of work and deliverables.\n"
            "4. Requests for cash payments, or payments to personal accounts, are "
            "prohibited.\n"
            "5. Any request to backdate, split, or re-describe an invoice must be "
            "reported to compliance immediately."
        ),
        scenario_text=(
            "During a $5.6M government hospital tender, a local consultant who "
            "'knows the ministry' requests a 9% success fee (regional market rate for "
            "tender advisory is 2–3%), payable to an account in a third country, with "
            "the invoice described as 'logistics services'. The tender closes in 10 "
            "days and the sales director asks finance to expedite the payment setup."
        ),
        question="Should finance set up this consultant payment?",
    ),
]


# ---------------------------------------------------------------------------
# Canned high-quality results — used when no API key is configured or the
# provider call fails, so a live demo can never dead-end. Clearly badged as
# demo mode in the UI.
# ---------------------------------------------------------------------------

CANNED_RESULTS: dict[str, AnalysisResult] = {
    "distributor-onboarding": AnalysisResult(
        direct_answer=(
            "No — the policy does not permit signing the agreement or fulfilling the "
            "order yet. Beneficial ownership disclosure is incomplete, the market is "
            "high-risk (triggering enhanced due diligence), and the rumored former "
            "health-ministry owner triggers the senior compliance approval requirement."
        ),
        risk_level="High",
        policy_basis=[
            PolicyCitation(
                chunk_id=1,
                excerpt="due diligence before any agreement is signed or order is fulfilled",
                point="Onboarding must complete before signature or fulfillment, so the Q-close timeline cannot override it.",
            ),
            PolicyCitation(
                chunk_id=2,
                excerpt="beneficial ownership disclosure to the individual level",
                point="Beneficial ownership is a required evidence item and is still pending.",
            ),
            PolicyCitation(
                chunk_id=4,
                excerpt="beneficial owners include current or former government officials, requires senior compliance approval",
                point="The rumored former ministry official makes senior compliance approval mandatory if confirmed.",
            ),
        ],
        missing_information=[
            "Completed beneficial ownership disclosure to the individual level",
            "Sanctions and watchlist screening results for the entity and owners",
            "Verification of the rumored former government-official owner",
            "Regional compliance officer sign-off (high-risk market EDD)",
            "Proposed commission/discount structure vs. regional standard rate",
        ],
        escalation_required=True,
        escalation_reason=(
            "High-risk market plus potential former government official in the "
            "ownership chain requires enhanced due diligence and senior compliance approval."
        ),
        assumptions=[
            "The market's high-risk rating refers to the corporate corruption index cited in the policy.",
            "No agreement has been signed and no units have shipped yet.",
        ],
        internal_note=(
            "HOLD onboarding of prospective distributor (imaging, high-risk market). "
            "Received: certificate of incorporation, signed anti-corruption certification. "
            "Outstanding: individual-level BO disclosure, sanctions screening, EDD, "
            "senior compliance approval (possible ex-government-official owner). "
            "Do not sign or fulfill the 40-unit order until cleared. Owner: regional compliance."
        ),
        customer_safe_response=(
            "Thank you for the documents provided so far. To complete onboarding we "
            "still require your beneficial ownership disclosure, after which our "
            "standard review will proceed. We will confirm next steps as soon as the "
            "review is complete."
        ),
        disclaimer=DISCLAIMER,
    ),
    "hcp-consulting": AnalysisResult(
        direct_answer=(
            "No — the engagement cannot proceed as requested. There is no executed "
            "written agreement or documented business need, and the radiologist "
            "chairs the purchasing committee of a hospital with an active $2.4M "
            "tender, which requires compliance pre-approval. The 'very supportive' "
            "remark suggests a link to purchasing decisions, which the policy prohibits."
        ),
        risk_level="High",
        policy_basis=[
            PolicyCitation(
                chunk_id=1,
                excerpt="written agreement executed before services begin",
                point="The first session cannot occur next week without an executed agreement.",
            ),
            PolicyCitation(
                chunk_id=4,
                excerpt="may not be linked, directly or indirectly, to past or expected purchasing decisions",
                point="Tying the engagement to tender support would violate the anti-kickback provision outright.",
            ),
            PolicyCitation(
                chunk_id=5,
                excerpt="HCPs who sit on institutional purchasing committees require compliance pre-approval",
                point="The radiologist chairs the purchasing committee, so pre-approval is mandatory.",
            ),
        ],
        missing_information=[
            "Documented business need approved by the medical affairs review board",
            "Fair-market-value assessment supporting the $18,000 fee",
            "Written scope of services and deliverables",
            "Compliance pre-approval given the purchasing-committee role",
        ],
        escalation_required=True,
        escalation_reason=(
            "Active $2.4M tender plus purchasing-committee chair plus language "
            "linking the engagement to tender support raises anti-kickback concern."
        ),
        assumptions=[
            "No prior approved agreement exists for this radiologist.",
            "The $2.4M tender is still open during the proposed engagement.",
        ],
        internal_note=(
            "DO NOT PROCEED with proposed $18k HCP consulting engagement. Missing MA "
            "review-board need, FMV assessment, executed agreement, and compliance "
            "pre-approval (HCP chairs purchasing committee; active $2.4M tender). "
            "Sales manager's linkage of engagement to tender support flagged for "
            "compliance review. Track transparency reporting if any transfer of value occurs."
        ),
        customer_safe_response=(
            "We appreciate the interest in an advisory collaboration. Engagements of "
            "this type follow our standard review process, including documentation of "
            "scope and internal approvals, before any sessions are scheduled. We will "
            "follow up once that process is complete."
        ),
        disclaimer=DISCLAIMER,
    ),
    "gifts-hospitality": AnalysisResult(
        direct_answer=(
            "The expense should not be approved as submitted. At $160 per person it "
            "exceeds the $75 meal limit, the attendees include public-hospital "
            "procurement staff during an open tender, the receipt is unitemized, and "
            "it is a repeat hospitality event within the quarter — each independently "
            "requires review or makes the expense non-compliant."
        ),
        risk_level="High",
        policy_basis=[
            PolicyCitation(
                chunk_id=1,
                excerpt="per-person limit of $75",
                point="$640 for four attendees is $160 per person, more than double the limit.",
            ),
            PolicyCitation(
                chunk_id=3,
                excerpt="Entertainment ... for customer representatives involved in an active procurement is prohibited",
                point="Hospitality for procurement staff during the open CT tender is squarely restricted.",
            ),
            PolicyCitation(
                chunk_id=5,
                excerpt="Repeated hospitality to the same individual within a quarter requires compliance review",
                point="A similar dinner five weeks ago with the same attendees triggers mandatory review.",
            ),
        ],
        missing_information=[
            "Itemized receipt with attendee list and per-person amounts",
            "Documented business purpose beyond 'project dinner'",
            "Whether the public-hospital attendees are classified as government employees",
            "Details of the earlier dinner (amount, attendees, purpose)",
        ],
        escalation_required=True,
        escalation_reason=(
            "Over-limit hospitality for public-hospital procurement staff during an "
            "active tender, with a repeat pattern — potential improper-inducement exposure."
        ),
        assumptions=[
            "The four attendees include the submitting employee (per-person math uses 4).",
            "The CT-scanner tender was open on the dinner date.",
        ],
        internal_note=(
            "REJECT expense pending review: $640 dinner (4 pax, $160/pp vs $75 limit), "
            "attendees include public-hospital procurement staff with open CT tender; "
            "unitemized receipt; repeat event within quarter. Route to compliance for "
            "improper-inducement assessment; request itemization and prior-event details."
        ),
        customer_safe_response=(
            "This expense requires additional documentation and internal review under "
            "our hospitality policy before it can be processed. Please provide an "
            "itemized receipt, the full attendee list, and the specific business purpose."
        ),
        disclaimer=DISCLAIMER,
    ),
    "export-sanctions": AnalysisResult(
        direct_answer=(
            "No — the shipment must remain on hold. The end destination is a "
            "comprehensively sanctioned territory (prohibited absent a reviewed "
            "license), there is an unresolved partial restricted-party match, and the "
            "reseller's re-invoicing proposal is itself a prohibited restructuring to "
            "avoid screening."
        ),
        risk_level="High",
        policy_basis=[
            PolicyCitation(
                chunk_id=2,
                excerpt="comprehensive sanctions are prohibited absent a valid license",
                point="Final delivery documents name a clinic in a comprehensively sanctioned territory; no license is on file.",
            ),
            PolicyCitation(
                chunk_id=3,
                excerpt="partial match on a restricted-party list places the order on hold",
                point="The consignee partial match mandates a hold until trade compliance clears it.",
            ),
            PolicyCitation(
                chunk_id=5,
                excerpt="may not restructure, reroute, or relabel a transaction to avoid screening",
                point="Re-invoicing through the regional office to move the shipment is exactly what this clause prohibits.",
            ),
        ],
        missing_information=[
            "Trade-compliance adjudication of the partial restricted-party match",
            "Whether any license or humanitarian authorization applies",
            "Dual-use classification and end-user statement for the units",
            "Full end-to-end routing and ultimate consignee documentation",
        ],
        escalation_required=True,
        escalation_reason=(
            "Sanctioned end destination, unresolved screening match, and an evasion "
            "proposal from the reseller — immediate trade-compliance escalation required."
        ),
        assumptions=[
            "The delivery documents accurately reflect the ultimate destination.",
            "No license or authorization is currently on file for this order.",
        ],
        internal_note=(
            "HOLD order (portable ultrasound via freight forwarder). Ultimate "
            "consignee in comprehensively sanctioned territory; partial RPL match "
            "unresolved; reseller proposed re-invoicing to bypass — report as "
            "attempted evasion. Escalate to trade compliance; do not release, "
            "do not communicate clearance timelines to reseller."
        ),
        customer_safe_response=(
            "This order is undergoing our standard trade-compliance review and cannot "
            "be released at this time. We are unable to modify invoicing or routing "
            "while the review is in progress and will advise once it concludes."
        ),
        disclaimer=DISCLAIMER,
    ),
    "tender-intermediary": AnalysisResult(
        direct_answer=(
            "No — finance should not set up this payment. It combines four policy "
            "violations or red flags: an unapproved success fee tied to a government "
            "tender, a fee 3x the market rate without a scope of work, payment to a "
            "third-country account, and an invoice mis-described as 'logistics "
            "services' — the last of which must be reported to compliance immediately."
        ),
        risk_level="High",
        policy_basis=[
            PolicyCitation(
                chunk_id=1,
                excerpt="Success fees ... tied to the award of government tenders require pre-approval",
                point="No legal/compliance pre-approval exists for the 9% success fee.",
            ),
            PolicyCitation(
                chunk_id=2,
                excerpt="third-country payments require compliance approval",
                point="The requested account is outside the consultant's country of incorporation.",
            ),
            PolicyCitation(
                chunk_id=5,
                excerpt="re-describe an invoice must be reported to compliance immediately",
                point="Labeling tender advisory as 'logistics services' is an invoice mis-description and a mandatory report.",
            ),
        ],
        missing_information=[
            "Written scope of work and deliverables for the consultant",
            "Justification for 9% vs the 2–3% regional market rate",
            "Beneficial ownership and government ties of the consultant",
            "Legal/compliance pre-approval record (none on file)",
        ],
        escalation_required=True,
        escalation_reason=(
            "Classic bribery red-flag cluster on a $5.6M government tender: excessive "
            "success fee, third-country payment, and disguised invoice description."
        ),
        assumptions=[
            "The 2–3% figure is the correct regional benchmark for tender advisory.",
            "No pre-approval has been obtained by the sales team.",
        ],
        internal_note=(
            "BLOCK payment setup for tender consultant ($5.6M govt hospital tender). "
            "Red flags: 9% success fee (benchmark 2–3%), third-country account, "
            "invoice described as 'logistics services', urgency pressure before "
            "tender close. Mandatory immediate report to compliance under invoice "
            "re-description clause. Preserve correspondence."
        ),
        customer_safe_response=(
            "Consultant payments of this type require completion of our standard "
            "documentation and approval process, including a written scope of work "
            "and payment to the contracting entity's account of record. We can "
            "proceed once those requirements are met."
        ),
        disclaimer=DISCLAIMER,
    ),
}
