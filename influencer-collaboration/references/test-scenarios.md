# Test scenarios

Use these scenarios to test the skill, CLI, templates, and campaign operations. Each scenario includes expected behavior.

## Core scoring

1. Local food creator in Haifa for a Haifa cafe  
   Expected: shortlist, high fit score, high Israeli relevance.

2. National fashion creator for a Haifa cafe  
   Expected: manual review or skip, niche mismatch noted.

3. Small parenting creator in the north for a toy store  
   Expected: shortlist when engagement and local audience are strong.

4. Large creator with 150,000 followers and 5 percent Israeli audience  
   Expected: low Israeli relevance and likely skip.

5. Creator with high followers but very low average views  
   Expected: risk note about metric pattern.

6. Creator with two competitor conflicts  
   Expected: lower risk score and manual review.

7. Budget of ₪500 for a multi-deliverable YouTube creator  
   Expected: low budget score and negotiation recommendation.

8. Story-only local flash offer  
   Expected: feasible plan with screenshot reporting requirement.

9. Creator with missing average views  
   Expected: fallback reach estimate and manual review if needed.

10. Creator profile with negative followers  
    Expected: validation error.

## Outreach and Hebrew

11. Professional tone for a freelancer lead campaign  
    Expected: concise Hebrew outreach with dates, deliverables, and disclosure.

12. Warm tone for a studio or local service  
    Expected: respectful but not overly casual Hebrew.

13. Direct tone for a formal supplier process  
    Expected: short message with business terms.

14. Missing disclosure in caption  
    Expected: disclosure validation fails.

15. Disclosure appears after a long caption  
    Expected: late disclosure issue.

16. English-only sponsorship tag in Hebrew caption  
    Expected: issue recommending Hebrew disclosure.

17. Budget line without tax clarity  
    Expected: revise to mention tax status where relevant.

18. Usage rights missing from outreach  
    Expected: add duration and written approval.

## Tracking and performance

19. Coupon code shared by all creators  
    Expected: attribution warning and one code per creator.

20. Story posted but analytics not saved  
    Expected: reporting failure and requirement for screenshots before expiry.

21. High clicks but zero leads  
    Expected: landing page troubleshooting recommendation.

22. Leads but no sales  
    Expected: inspect follow-up process and response time.

23. High ROAS on one creator and low ROAS on another  
    Expected: renew high performer and stop or renegotiate low performer.

24. Strong content but weak direct sales  
    Expected: consider limited content reuse only if rights are documented.

25. Product-only compensation  
    Expected: document product value, reporting, and invoice or receipt handling.

## Compliance and consumer protection

26. Health supplement claim with no evidence  
    Expected: escalate for review and avoid unverified claims.

27. Financial advice framed as guaranteed return  
    Expected: reject or escalate for professional review.

28. Campaign collects phone numbers from leads  
    Expected: privacy checklist and consent handling.

29. Giveaway with prize draw  
    Expected: review promotion rules before launch.

30. Consumer checks a sponsored recommendation  
    Expected: assess disclosure, claim quality, pressure tactics, and independent evidence.

## CLI and files

31. CSV with `91` instead of `0.91` for Israeli audience  
    Expected: validation or normalization fix before scoring.

32. CSV exported with broken Hebrew encoding  
    Expected: re-export as UTF-8.

33. `influencer-collaboration score` run without profile path  
    Expected: CLI argument error.

34. Example script run with `--env sandbox`  
    Expected: JSON output with Hebrew preserved.

35. Example script run with production environment variables  
    Expected: production values override defaults.
