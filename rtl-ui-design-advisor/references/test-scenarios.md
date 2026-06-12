# RTL Test Scenarios

Run these scenarios before launching Hebrew or Arabic interfaces.

## Scenario 1: Hebrew page shell

Input: Open `/he/checkout`.

Expected: Root has `lang="he"` and `dir="rtl"`; heading is Hebrew.

## Scenario 2: Arabic page shell

Input: Open `/ar/checkout`.

Expected: Root has `lang="ar"` and `dir="rtl"`; Arabic shaping is correct.

## Scenario 3: English page shell

Input: Open `/en/checkout`.

Expected: Root has `lang="en"` and `dir="ltr"`; RTL styles do not leak.

## Scenario 4: Hebrew customer name

Input: Enter `דנה לוי`.

Expected: Name displays naturally in RTL.

## Scenario 5: English customer name

Input: Enter `Maya Cohen` in Hebrew UI.

Expected: Name remains isolated and readable.

## Scenario 6: Arabic customer name

Input: Enter `شركة القدس` in Hebrew UI.

Expected: Value remains readable and does not break punctuation.

## Scenario 7: Mixed business name

Input: Enter `כהן Web Studio בע"מ`.

Expected: Hebrew and English segments remain readable.

## Scenario 8: Email field

Input: Enter `client@example.co.il`.

Expected: Field is LTR and cursor movement is predictable.

## Scenario 9: Phone field

Input: Enter `050-123-4567`.

Expected: Field is LTR with `inputmode="tel"`.

## Scenario 10: URL field

Input: Enter `https://example.co.il/path?coupon=SUMMER-25`.

Expected: URL remains in order.

## Scenario 11: Coupon code in Hebrew sentence

Input: Render `SUMMER-25`.

Expected: Code is isolated LTR.

## Scenario 12: Order number

Input: Render `ORD-2026-0007`.

Expected: Hyphens and digits stay in order.

## Scenario 13: ILS amount

Input: Render amount `1250`.

Expected: ₪ amount is isolated and readable.

## Scenario 14: Negative refund

Input: Render `-45` as refund.

Expected: Minus sign and ₪ remain attached.

## Scenario 15: Israeli date

Input: Render `2026-06-03`.

Expected: Display follows DD/MM/YYYY as `03/06/2026`.

## Scenario 16: Invoice identifiers

Input: Render `INV-2026-0042` and `512345678`.

Expected: Both are LTR and isolated.

## Scenario 17: VAT summary

Input: Render subtotal, VAT, and total.

Expected: Labels are Hebrew; amounts are isolated; rate is not hard-coded in visual component.

## Scenario 18: Logical Tailwind card

Input: Use `p-4 ps-4 border-s-4 text-start`.

Expected: No physical left/right utility is needed.

## Scenario 19: Physical Tailwind detection

Input: Audit `ml-4 text-left left-0 space-x-2`.

Expected: Audit reports logical replacements.

## Scenario 20: Logical CSS spacing

Input: Use `padding-inline-start` and `margin-inline-end`.

Expected: No physical spacing issue is reported.

## Scenario 21: Physical CSS spacing

Input: Use `padding-left` and `right: 0`.

Expected: Audit flags physical properties.

## Scenario 22: Directional icon

Input: Show back arrow in Hebrew checkout.

Expected: Arrow follows back semantics.

## Scenario 23: Non-directional icon

Input: Show phone and calendar icons.

Expected: Icons are not mirrored.

## Scenario 24: Modal portal

Input: Open modal from Hebrew page.

Expected: Portal root has RTL direction and focus starts logically.

## Scenario 25: Dropdown placement

Input: Open account menu.

Expected: Menu aligns by logical side.

## Scenario 26: Keyboard navigation

Input: Tab through checkout.

Expected: Focus follows task order.

## Scenario 27: Screen reader labels

Input: Navigate payment form.

Expected: Labels and errors are announced in Hebrew.

## Scenario 28: Search field

Input: Search `ABC-123`, `חולצה`, and `مطعم`.

Expected: Search handles all values with `dir="auto"`.

## Scenario 29: Empty state

Input: Open an account with no orders.

Expected: Text aligns to start and action order is readable.

## Scenario 30: Error summary

Input: Submit invalid checkout.

Expected: Summary links to fields and preserves keyboard order.

## Scenario 31: PDF receipt

Input: Generate receipt for `דנה לוי`.

Expected: PDF preserves Hebrew, identifiers, date, and amount.

## Scenario 32: Transactional email

Input: Send order confirmation.

Expected: Email renders RTL and isolates links and amounts.

## Scenario 33: Narrow screen

Input: Use 360px viewport.

Expected: Buttons wrap with `gap` and do not clip.

## Scenario 34: Zoom

Input: Set browser zoom to 200%.

Expected: Content remains readable and focus visible.

## Scenario 35: Long Arabic text

Input: Paste long Arabic service description.

Expected: Line breaks preserve shaping.

## Scenario 36: English support code in Arabic

Input: Render `SUP-77-A`.

Expected: Code is isolated LTR inside Arabic text.

## Scenario 37: Address block

Input: Render `רח׳ הרצל 12, דירה 4, תל אביב-יפו`.

Expected: Street is RTL and numbers stay stable.

## Scenario 38: Map address link

Input: Link a Hebrew address to a map.

Expected: Link text is RTL; URL is not visually exposed or is isolated.

## Scenario 39: Chart labels

Input: Show sales chart with Hebrew labels.

Expected: Numeric axis is not blindly mirrored.

## Scenario 40: Locale switch

Input: Switch Hebrew to English and back.

Expected: `lang`, `dir`, alignment, icons, and validation messages update consistently.
