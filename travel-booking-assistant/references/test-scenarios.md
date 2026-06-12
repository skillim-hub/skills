# Test Scenarios

Use these scenarios for QA, demos, regression testing, and production readiness reviews. Each scenario includes the expected behavior.

## 1. Eilat freelancer with VAT invoice
Input: One adult, Tel Aviv to Eilat, 12/06/2026 to 14/06/2026, business=true, needs VAT invoice.  
Expected: Recommend Ramon flight plus transfer; add hotel VAT invoice checklist; status quote only.

## 2. Eilat family with children
Input: Two adults, two children, stroller, hotel near North Beach.  
Expected: Include family room, stroller handling, transfer capacity, cancellation deadline.

## 3. Eilat peak holiday
Input: Eilat trip during school holiday.  
Expected: Warn about high demand, price volatility, stricter cancellation, transfer congestion.

## 4. Domestic rail to meeting
Input: Haifa to Tel Aviv, arrive by 09:30.  
Expected: Search by arrival time; add station and last-mile buffer.

## 5. Rail to airport
Input: Jerusalem to Ben Gurion Airport for 14:00 flight.  
Expected: Add international airport buffer; warn rail delay does not protect flight.

## 6. Shabbat domestic travel
Input: Friday afternoon rail itinerary.  
Expected: Flag Shabbat service risk; add taxi fallback.

## 7. Israeli hotel missing invoice
Input: Hotel confirmation but no חשבונית מס/קבלה.  
Expected: Generate Hebrew invoice request; flag accountant review if unsupported.

## 8. Foreign hotel invoice
Input: Berlin hotel invoice from foreign supplier.  
Expected: Store foreign invoice; do not promise Israeli VAT deduction; add FX evidence.

## 9. Outbound Berlin business
Input: TLV to Berlin, one adult, EUR prices.  
Expected: Convert EUR to ₪, add card markup estimate, city tax warning, passport prompts.

## 10. Passport near expiry
Input: International trip with passport expiring shortly after return.  
Expected: Require official entry-rule check; do not clear traveler automatically.

## 11. Visa unknown
Input: Destination requires possible visa but nationality missing.  
Expected: Ask for nationality and passport type; keep status pending.

## 12. Separate-ticket connection
Input: TLV-LCA and LCA-LON on separate bookings.  
Expected: Mark high risk; compare protected alternative; add baggage/security buffer.

## 13. Low-cost fare without baggage
Input: Cheapest fare to Athens.  
Expected: Detect missing checked baggage; compare fare with baggage included.

## 14. Dynamic currency conversion
Input: Supplier offers to charge in ₪ instead of EUR.  
Expected: Compare DCC versus card conversion; mark estimate.

## 15. Duplicate foreign card charge
Input: Two charges, EUR and ILS, same supplier.  
Expected: Distinguish authorization/capture; request payment ledger; track refund.

## 16. Offer expired during approval
Input: Old offer selected after valid_until.  
Expected: Re-price and request approval; do not book.

## 17. Hotel rate changed at payment
Input: Hotel returns RATE_CHANGED.  
Expected: Stop payment; recalculate; ask approval.

## 18. Late check-in
Input: Flight arrives after midnight.  
Expected: Request written late check-in confirmation; add emergency contact.

## 19. Accessibility requirement
Input: Traveler needs wheelchair assistance.  
Expected: Add accessibility prompts for airline/hotel/rail; require supplier confirmation.

## 20. Group booking
Input: Five employees, business trip, shared hotel.  
Expected: Track per-traveler and shared costs; require approval owner; avoid sensitive IDs in notes.

## 21. Cancellation near deadline
Input: Hotel free cancellation ends today at 18:00.  
Expected: Surface deadline in Israel and local time; prepare cancellation request.

## 22. Refund variance
Input: EUR booking refunded after exchange-rate move.  
Expected: Separate cancellation fee from FX variance and card fees.

## 23. Hebrew date parsing
Input: "נסיעה לאילת בין 12/06/2026 ל14/06/2026".  
Expected: Parse DD/MM/YYYY; output Hebrew summary with ₪.

## 24. Invalid date range
Input: End date before start date.  
Expected: Return INVALID_DATE_RANGE and no quote.

## 25. Missing traveler count
Input: Trip dates and destination only.  
Expected: Return MISSING_TRAVELER and ask for count.

## 26. Local tourist tax unknown
Input: Rome hotel quote without city tax details.  
Expected: Mark LOCAL_TAX_UNCONFIRMED and keep as estimate.

## 27. Mixed domestic and international
Input: Train from Beersheba to airport then flight to Paris.  
Expected: Build two legs; warn rail leg is not protected by airline.

## 28. Business approval required
Input: Book now without approval policy satisfied.  
Expected: Keep pending approval; do not perform payment.

## 29. Consumer non-refundable booking
Input: Cheap non-refundable hotel.  
Expected: Highlight cancellation risk and compare refundable option.

## 30. Supplier terms unavailable
Input: OTA returns price but no cancellation policy.  
Expected: Mark supplier terms unverified; do not recommend payment.
