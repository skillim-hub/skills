# Migration Checklist: LTR to Hebrew or Arabic RTL

## Phase 1: Inventory

- [ ] List pages, templates, modals, drawers, emails, PDFs, embedded widgets, and print flows.
- [ ] Identify all user-generated text surfaces.
- [ ] Identify all forms and field types.
- [ ] Identify hard-coded visible strings.
- [ ] Identify third-party widgets.
- [ ] Identify icons with directional meaning.
- [ ] Identify charts, maps, timelines, steppers, breadcrumbs, and carousels.
- [ ] Identify CSS sources: global CSS, modules, CSS-in-JS, Tailwind, and component library overrides.

## Phase 2: Locale and direction architecture

- [ ] Add locale support for `he`, `he-IL`, `ar`, `ar-IL`, and existing LTR locales.
- [ ] Derive direction from locale through one helper.
- [ ] Set `lang` and `dir` at the root layout.
- [ ] Keep server and client initial direction identical.
- [ ] Add direction to portal roots.
- [ ] Define fallback behavior for unsupported locales.

## Phase 3: Text and terminology

- [ ] Replace hard-coded strings with translation keys.
- [ ] Translate labels, buttons, empty states, validation messages, and error summaries.
- [ ] Review Hebrew terms: חשבונית מס, קבלה, עוסק פטור, עוסק מורשה, ח"פ, מע"מ, מק"ט.
- [ ] Avoid Hebrew labels in Arabic UI.
- [ ] Review financial, tax, legal, and consumer-protection wording with qualified professionals where needed.

## Phase 4: CSS conversion

- [ ] Replace `margin-left` and `margin-right`.
- [ ] Replace `padding-left` and `padding-right`.
- [ ] Replace `border-left` and `border-right`.
- [ ] Replace `left` and `right`.
- [ ] Replace `text-align: left/right`.
- [ ] Replace float-based layouts.
- [ ] Replace margin spacing hacks with `gap`.
- [ ] Review transforms and animations.
- [ ] Review border-radius corners.
- [ ] Review background positions.
- [ ] Document justified exceptions.

## Phase 5: Tailwind conversion

- [ ] Replace `ml-*` and `mr-*`.
- [ ] Replace `pl-*` and `pr-*`.
- [ ] Replace `left-*` and `right-*`.
- [ ] Replace `text-left` and `text-right`.
- [ ] Replace `border-l*` and `border-r*`.
- [ ] Review `rounded-l*` and `rounded-r*`.
- [ ] Replace `space-x-*` with `gap-*` where possible.
- [ ] Use `rtl:` or `ltr:` variants only for real exceptions.

## Phase 6: Forms

- [ ] Names use `dir="auto"`.
- [ ] Business names use `dir="auto"`.
- [ ] Free-text fields use `dir="auto"`.
- [ ] Search uses `dir="auto"`.
- [ ] Email uses `dir="ltr"`.
- [ ] URL uses `dir="ltr"`.
- [ ] Phone uses `dir="ltr"` and `inputmode="tel"`.
- [ ] Amounts use LTR editing or isolated display.
- [ ] Israeli ID and business numbers use LTR.
- [ ] Bank details use LTR.
- [ ] Validation messages are localized.
- [ ] Required indicators do not rely on side alone.

## Phase 7: Dynamic content

- [ ] Wrap document numbers in `<bdi dir="ltr">`.
- [ ] Wrap order IDs in `<bdi dir="ltr">`.
- [ ] Wrap coupon codes in `<bdi dir="ltr">`.
- [ ] Wrap emails and URLs in `<bdi dir="ltr">`.
- [ ] Wrap user names in `<bdi dir="auto">`.
- [ ] Wrap amounts in `<bdi dir="ltr">`.
- [ ] Wrap dates in `<bdi dir="ltr">`.
- [ ] Avoid `unicode-bidi: bidi-override` for ordinary UI text.

## Phase 8: Israeli localization

- [ ] Format currency as ILS with ₪.
- [ ] Use an explicit date policy such as DD/MM/YYYY.
- [ ] Display phone numbers clearly and keep canonical forms where needed.
- [ ] Avoid hard-coded VAT rates inside UI components.
- [ ] Match entity labels to business context.
- [ ] Keep support phone and email easy to copy and activate.

## Phase 9: Accessibility and compliance checkpoints

- [ ] Verify `lang` and `dir`.
- [ ] Verify labels and controls.
- [ ] Verify error messages.
- [ ] Verify keyboard order.
- [ ] Verify focus indicator.
- [ ] Verify screen-reader output in Hebrew and Arabic.
- [ ] Verify high zoom and large text.
- [ ] Verify privacy, consumer, tax, and accessibility surfaces with qualified review where required.

## Phase 10: QA and rollout

- [ ] Run unit tests.
- [ ] Run static scans for physical CSS.
- [ ] Run visual regression in LTR and RTL.
- [ ] Run the scenarios in `test-scenarios.md`.
- [ ] Test generated emails and PDFs.
- [ ] Test mobile devices and mobile keyboards.
- [ ] Monitor locale-specific errors.
- [ ] Release gradually.
- [ ] Keep rollback plan.
