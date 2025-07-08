1.	For all files: (SAM)
●	Titles
●	Publication/announcement date
●	Date of adoption

2.	From press_corner_summary_20250326_163741: (SAM)
●	Doctype (currently it’s too messy, ideally just to have there only type like “speech”, ”press release”, ”Statement” and so on)

3.	From df_press (EULT Search results all years 20 250 326): (JULIUS)
●	Current procedure status (expected unique: 'Ongoing', 'Adopted', nan, 'Withdrawn')
●	Current procedure stage (expected unique: 'Proposal', 'First reading', 'End of procedure', 'Second reading')
●	Proposal title (expected unique - a lot)
●	Date of adoption of the Commission proposal

Initial Model Testing Plan (RICHARD)
Test Questions
1. General Regulatory Timeline
Across all documents in eurolex-consolidated.csv, identify every entry related to customs enforcement actions under Regulation (EU) No 608/2013. For each, extract:
- Reference number (e.g., C(2024) 6154 final)
- Publication date

Produce a short chronological timeline summarizing the sequence of implementing regulations. (RICHARD)
2. Reporting Obligation Details
Find all documents (expected >25) that specify reporting obligations to the Customs Code Committee. From each, extract:
- Exact reporting requirement text
- Entity responsible
- Report frequency or deadline

Return the results as a structured table. (JULIUS)
2. Evaluation Criteria (relevant for Team 2)
•	Retrieval Completeness: Percentage of relevant documents correctly retrieved 
•	Extraction Accuracy: Field-level precision/recall on reference numbers, dates, and reporting details
•	Timeline Coherence: Manual verification that events are correctly ordered and complete.
•	Response Latency: Median query time should be around 3 seconds according to ChatGPT
•	Legal usefulness: check how useful the prompt is to getting a clear understanding about the questions
